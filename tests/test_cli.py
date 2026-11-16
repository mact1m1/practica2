"""End-to-end CLI tests run the module from outside the repository."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Validate command output channels, exit codes and relative paths."""

    def run_cli(self, command, config='test', extra=()):
        """Run with an explicit source path and an unrelated cwd."""
        env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'))
        with TemporaryDirectory() as directory:
            return subprocess.run(
                [sys.executable, '-m', 'cargograph',
                 str(ROOT / f'examples/{config}.toml'), command, *extra],
                cwd=directory, env=env, capture_output=True, text=True,
                check=False
            )

    def test_graph_streams(self):
        """DOT alone goes to stdout, ASCII goes to stderr."""
        result = self.run_cli('graph')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('digraph dependencies {'))
        self.assertNotIn('[shared]', result.stdout)
        self.assertIn('[shared]', result.stderr)

    def test_commands(self):
        """Configuration, direct edges and inverse queries are available."""
        result = self.run_cli('config')
        self.assertEqual(len(result.stdout.splitlines()), 6)
        self.assertEqual(result.returncode, 0)
        result = self.run_cli('direct')
        self.assertIn('B 1.0.0', result.stdout)
        self.assertIn('C 1.0.0', result.stdout)
        result = self.run_cli('reverse', extra=['--target', 'D'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('E@1.0.0', result.stdout)

    def test_errors(self):
        """Invalid targets return 1; invalid CLI usage returns 2."""
        result = self.run_cli('reverse', extra=['--target', 'UNKNOWN'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('Error:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        result = self.run_cli('graph', extra=['--target', 'A'])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.run_cli('bad-command').returncode, 2)

    def test_ascii_disabled(self):
        """The TOML switch suppresses the ASCII stream entirely."""
        result = self.run_cli('graph', config='dot-only')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')
        self.assertIn('digraph', result.stdout)
