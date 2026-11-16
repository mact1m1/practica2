"""CLI operations for the five practical-work stages."""

import argparse
from dataclasses import asdict
import sys

from .config import AppError, read_config
from .graph import build_graph, reverse_dependencies, select_target
from .registry import Registry
from .testrepo import TestRepository
from .versions import Version


def parser():
    """Build the interface; analysis settings come only from TOML."""
    result = argparse.ArgumentParser(description="Cargo graph, variant 19")
    result.add_argument("config", help="Path to TOML configuration")
    result.add_argument(
        "command", choices=["config", "direct", "graph", "reverse"]
    )
    result.add_argument("--target", help="Reverse query: name or name@version")
    return result


def main(argv=None):
    """Print configuration, returning a nonzero code for invalid input."""
    args = parser().parse_args(argv)
    if args.target and args.command != 'reverse':
        parser().error("--target is valid only for reverse")
    try:
        config = read_config(args.config)
        Version.parse(config.version)
        execute(config, args.command, args.target)
        return 0
    except (AppError, OSError, RecursionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def execute(config, command, target=None):
    """Dispatch the configuration and direct-dependency stage commands."""
    if command == 'config':
        for key, value in asdict(config).items():
            print(f"{key}={value}")
        return
    registry = repository_for(config)
    root = registry.exact(config.package, config.version)
    if command == 'reverse':
        print_reverse(config, registry, root, target)
        return
    if command == 'graph':
        graph = build_graph(registry, [root], config.exclude)
        for node, children in graph.items():
            print(f"{node}: {', '.join(map(str, sorted(children)))}")
        return
    print(f"Direct dependencies of {root}:")
    for dependency in registry.dependencies(root):
        print(f"{dependency.name} {dependency.requirement} "
              f"[{dependency.kind}, optional={dependency.optional}, "
              f"target={dependency.target}]")


def repository_for(config):
    """Select the real sparse index or an offline test repository."""
    if config.test_mode:
        return TestRepository(config.repository, config.version)
    return Registry(config.repository)


def print_reverse(config, repository, root, target):
    """Search the complete test graph or the real root's analyzed closure."""
    roots = repository.all_nodes() if config.test_mode else [root]
    graph = build_graph(repository, roots, config.exclude)
    chosen = select_target(graph, target or str(root))
    result = reverse_dependencies(graph, chosen)
    scope = 'complete test repository' if config.test_mode else str(root)
    print(f"Reverse dependencies of {chosen} (scope: {scope}):")
    for node in sorted(set(result) - {chosen}):
        print(node)
