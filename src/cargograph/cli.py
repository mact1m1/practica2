"""CLI operations for the five practical-work stages."""

import argparse
from dataclasses import asdict
import sys

from .config import AppError, read_config
from .registry import Registry
from .versions import Version


def parser():
    """Build the interface; analysis settings come only from TOML."""
    result = argparse.ArgumentParser(description="Cargo graph, variant 19")
    result.add_argument("config", help="Path to TOML configuration")
    result.add_argument("command", choices=["config", "direct"])
    return result


def main(argv=None):
    """Print configuration, returning a nonzero code for invalid input."""
    args = parser().parse_args(argv)
    try:
        config = read_config(args.config)
        Version.parse(config.version)
        execute(config, args.command)
        return 0
    except (AppError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def execute(config, command):
    """Dispatch the configuration and direct-dependency stage commands."""
    if command == 'config':
        for key, value in asdict(config).items():
            print(f"{key}={value}")
        return
    if config.test_mode:
        raise AppError("Test graph support is implemented in stage 3")
    registry = Registry(config.repository)
    root = registry.exact(config.package, config.version)
    print(f"Direct dependencies of {root}:")
    for dependency in registry.dependencies(root):
        print(f"{dependency.name} {dependency.requirement} "
              f"[{dependency.kind}, optional={dependency.optional}, "
              f"target={dependency.target}]")
