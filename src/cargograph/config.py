"""Read and validate the six user settings from a TOML file."""

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit


class AppError(ValueError):
    """An actionable configuration, repository or graph error."""


@dataclass(frozen=True)
class Config:
    """Validated analysis settings; relative paths use the TOML directory."""

    package: str
    repository: str
    test_mode: bool
    version: str
    ascii_tree: bool
    exclude: str


def read_config(path):
    """Load a complete flat TOML configuration, rejecting unknown keys."""
    try:
        with Path(path).open("rb") as stream:
            values = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise AppError(f"Cannot read TOML: {error}") from error
    expected = set(Config.__annotations__)
    if set(values) != expected:
        missing = sorted(expected - set(values))
        unknown = sorted(set(values) - expected)
        raise AppError(f"Settings: missing={missing}, unknown={unknown}")
    config = Config(**values)
    validate_types(config)
    validate_values(config)
    return resolve_repository(config, Path(path).resolve().parent)


def validate_types(config):
    """Reject implicit conversions, especially string boolean values."""
    for key, value in asdict(config).items():
        expected = bool if key in {"test_mode", "ascii_tree"} else str
        if type(value) is not expected:
            raise AppError(f"{key}: expected {expected.__name__}")


def validate_values(config):
    """Check package names, exact versions and visible filter characters."""
    from .versions import Version

    pattern = r"[A-Z]+" if config.test_mode else r"[A-Za-z][\w-]*"
    if not re.fullmatch(pattern, config.package, flags=re.ASCII):
        raise AppError("package: invalid name for the selected mode")
    Version.parse(config.version)
    if any(not char.isprintable() for char in config.exclude):
        raise AppError("exclude: control characters are not allowed")
    if config.exclude and config.exclude in config.package:
        raise AppError("exclude: the root package would be excluded")
    if not config.repository.strip():
        raise AppError("repository: must not be empty")


def resolve_repository(config, directory):
    """Resolve a test path or validate an HTTP(S) sparse registry URL."""
    values = asdict(config)
    if config.test_mode:
        path = directory / config.repository
        if not path.is_file():
            raise AppError(f"repository: test file not found: {path}")
        values["repository"] = str(path.resolve())
    else:
        url = parse_url(config.repository)
        if url.scheme not in {"http", "https"} or not url.hostname:
            raise AppError("repository: expected an HTTP(S) sparse URL")
        if url.username or url.password or url.query or url.fragment:
            raise AppError("repository: credentials/query/fragment forbidden")
    return Config(**values)


def parse_url(text):
    """Report malformed host/port syntax as a configuration error."""
    try:
        url = urlsplit(text)
        url.port
    except ValueError as error:
        raise AppError(f"repository: invalid URL: {error}") from error
    if any(char.isspace() or not char.isprintable() for char in text):
        raise AppError("repository: whitespace/control characters forbidden")
    return url
