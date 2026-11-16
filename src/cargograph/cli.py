"""CLI operations for the five practical-work stages."""

import argparse
from dataclasses import asdict
import sys

from .config import AppError, read_config


def parser():
    """Build the interface; analysis settings come only from TOML."""
    result = argparse.ArgumentParser(description="Cargo graph, variant 19")
    result.add_argument("config", help="Path to TOML configuration")
    result.add_argument("command", choices=["config"])
    return result


def main(argv=None):
    """Print configuration, returning a nonzero code for invalid input."""
    args = parser().parse_args(argv)
    try:
        config = read_config(args.config)
        for key, value in asdict(config).items():
            print(f"{key}={value}")
        return 0
    except (AppError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
