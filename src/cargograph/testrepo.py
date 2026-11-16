"""Offline repository with uppercase Latin package names and JSON edges."""

import json
from pathlib import Path
import re

from .config import AppError
from .registry import Dependency, Node


class TestRepository:
    """A complete finite repository; all packages use the configured version."""

    def __init__(self, path, version):
        """Read and validate an adjacency list, including referenced nodes."""
        try:
            self.data = json.loads(Path(path).read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            raise AppError(f"Cannot read test repository: {error}") from error
        validate_graph(self.data)
        self.version = version

    def exact(self, name, version):
        """Resolve a test vertex or report an unknown package/version."""
        if name not in self.data or version != self.version:
            raise AppError(f"Test package not found: {name}@{version}")
        return Node(name, version)

    def resolve(self, name, requirement):
        """Resolve a test edge, whose version is fixed by the TOML file."""
        return self.exact(name, requirement)

    def dependencies(self, node):
        """Return deterministic direct edges from the test adjacency list."""
        self.exact(node.name, node.version)
        return [Dependency(name, self.version, 'normal', False, None)
                for name in sorted(set(self.data[node.name]))]

    def all_nodes(self):
        """Enumerate the complete test repository for reverse queries."""
        return [Node(name, self.version) for name in sorted(self.data)]


def validate_graph(data):
    """Require a nonempty mapping of uppercase names to defined nodes."""
    if not isinstance(data, dict) or not data:
        raise AppError("Test graph must be a nonempty JSON object")
    for name, edges in data.items():
        if not re.fullmatch(r'[A-Z]+', name):
            raise AppError(f"Test package must use uppercase Latin: {name}")
        if not isinstance(edges, list):
            raise AppError(f"Dependencies of {name} must be an array")
        for dependency in edges:
            if not isinstance(dependency, str) or dependency not in data:
                raise AppError(f"Undefined test dependency: {dependency}")
