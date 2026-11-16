"""Configuration validation, including each of the six settings."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cargograph.config import AppError, read_config


BASE = '''package = "A"
repository = "graph.json"
test_mode = true
version = "1.0.0"
ascii_tree = true
exclude = ""
'''


class ConfigTests(unittest.TestCase):
    """Exercise TOML parsing, type checks and relative path handling."""

    def load(self, content):
        """Read a config in an isolated directory containing a test file."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "graph.json").write_text('{}', encoding="utf-8")
            path = root / "config.toml"
            path.write_text(content, encoding="utf-8")
            return read_config(path)

    def test_valid_config(self):
        """Paths are resolved against the configuration location."""
        config = self.load(BASE)
        self.assertEqual(config.package, "A")
        self.assertTrue(Path(config.repository).is_absolute())

    def test_bad_settings(self):
        """Reject invalid values of every user-configurable setting."""
        changes = [
            ('package = "A"', 'package = "a"'),
            ('repository = "graph.json"', 'repository = "missing"'),
            ('test_mode = true', 'test_mode = "true"'),
            ('version = "1.0.0"', 'version = "latest"'),
            ('ascii_tree = true', 'ascii_tree = 1'),
            ('exclude = ""', 'exclude = false'),
            ('exclude = ""', 'exclude = "A"'),
            ('exclude = ""', 'exclude = "\\n"'),
        ]
        for before, after in changes:
            with self.subTest(after=after), self.assertRaises(AppError):
                self.load(BASE.replace(before, after))

    def test_schema_errors(self):
        """Reject missing, unknown and duplicate TOML settings."""
        for content in [BASE + 'x=1', BASE + 'package="B"', 'package="A"']:
            with self.subTest(content=content), self.assertRaises(AppError):
                self.load(content)

    def test_url_validation(self):
        """Only clean HTTP(S) sparse-index URLs are allowed."""
        base = BASE.replace('test_mode = true', 'test_mode = false')
        for url in ['file:///tmp/index', 'https://', 'https://u:p@host']:
            content = base.replace('graph.json', url)
            with self.subTest(url=url), self.assertRaises(AppError):
                self.load(content)

    def test_missing_file(self):
        """Missing configurations produce an application error."""
        with self.assertRaises(AppError):
            read_config('/nonexistent/cargograph/config.toml')
