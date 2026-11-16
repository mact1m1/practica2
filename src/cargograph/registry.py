"""Read Cargo sparse index JSON Lines over HTTP with the standard library."""

from dataclasses import dataclass
import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import AppError
from .versions import Version, matches


MAX_INDEX_BYTES = 32 * 1024 * 1024
TIMEOUT_SECONDS = 30
THREE_LETTER_NAME = 3


@dataclass(frozen=True, order=True)
class Node:
    """A graph vertex distinguishes versions of the same crate."""

    name: str
    version: str

    def __str__(self):
        """Return a stable human-readable vertex identifier."""
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class Dependency:
    """A declared production/build dependency from an index record."""

    name: str
    requirement: str
    kind: str
    optional: bool
    target: str | None


def index_path(name):
    """Derive the official Cargo index shard for a lowercase crate name."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
        raise AppError(f"Invalid crate name: {name}")
    name = name.lower()
    short_paths = {1: f"1/{name}", 2: f"2/{name}"}
    if len(name) in short_paths:
        return short_paths[len(name)]
    if len(name) == THREE_LETTER_NAME:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


def fetch_records(url):
    """Fetch one bounded index file; never invoke Cargo or another tool."""
    request = Request(url, headers={"User-Agent": "cargograph-variant19/1"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content = response.read(MAX_INDEX_BYTES + 1)
        if len(content) > MAX_INDEX_BYTES:
            raise AppError(f"Index file exceeds size limit: {url}")
        records = [json.loads(line) for line in content.splitlines() if line]
    except (OSError, URLError, ValueError) as error:
        raise AppError(f"Cannot read index {url}: {error}") from error
    if not records:
        raise AppError(f"Empty index file: {url}")
    return records


class Registry:
    """Sparse-index access with an in-memory cache per application run."""

    def __init__(self, url):
        """Use a configurable HTTP(S) sparse index base URL."""
        self.url = url.removeprefix('sparse+').rstrip('/')
        self.cache = {}

    def records(self, name):
        """Load and validate index entries for one crate."""
        key = name.lower()
        if key not in self.cache:
            records = fetch_records(f"{self.url}/{index_path(key)}")
            for record in records:
                validate_record(record, key)
            self.cache[key] = records
        return self.cache[key]

    def exact(self, name, version):
        """Find the requested root release, even if it was yanked."""
        for record in self.records(name):
            if record['vers'] == version:
                return Node(record['name'], version)
        raise AppError(f"Release not found: {name}@{version}")

    def resolve(self, name, requirement):
        """Choose the highest non-yanked release matching an edge."""
        versions = [
            r for r in self.records(name)
            if not r.get('yanked', False) and matches(r['vers'], requirement)
        ]
        if not versions:
            raise AppError(f"No release matches {name} {requirement}")
        chosen = max(versions, key=lambda r: Version.parse(r['vers']))
        return Node(chosen['name'], chosen['vers'])

    def dependencies(self, node):
        """Read all normal/build edges, including optional/platform edges."""
        record = next(
            (r for r in self.records(node.name) if r['vers'] == node.version),
            None
        )
        if record is None:
            raise AppError(f"Release not found: {node}")
        dependencies = []
        for value in record['deps']:
            if value.get('kind') == 'dev':
                continue
            if value.get('registry'):
                raise AppError("Cross-registry dependencies unsupported")
            dependencies.append(read_dependency(value))
        return dependencies


def validate_record(record, name):
    """Reject corrupted index metadata before constructing graph nodes."""
    if not isinstance(record, dict):
        raise AppError("Index record must be an object")
    if str(record.get('name', '')).lower() != name:
        raise AppError(f"Index name mismatch: {name}")
    if not isinstance(record.get('vers'), str):
        raise AppError("Index record needs a version")
    Version.parse(record['vers'])
    dependencies = record.get('deps')
    if not isinstance(dependencies, list):
        raise AppError("Index record needs a dependency array")
    for value in dependencies:
        read_dependency(value)


def read_dependency(value):
    """Decode a dependency, respecting a renamed crate's package field."""
    if not isinstance(value, dict):
        raise AppError("Dependency must be an object")
    name = value.get('package') or value.get('name')
    requirement = value.get('req')
    if not isinstance(name, str) or not isinstance(requirement, str):
        raise AppError("Dependency needs a name and requirement")
    index_path(name)
    matches('0.0.0', requirement)
    kind = value.get('kind') or 'normal'
    if kind not in {'normal', 'build', 'dev'}:
        raise AppError(f"Unknown dependency kind: {kind}")
    return Dependency(
        name, requirement, kind, value.get('optional', False),
        value.get('target')
    )
