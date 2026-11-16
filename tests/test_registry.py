"""Sparse registry unit tests with no external network calls."""

import unittest
from unittest.mock import patch

from cargograph.config import AppError
from cargograph.registry import Node, Registry, index_path


def record(version='1.0.0', **values):
    """Create a minimal valid Cargo index record."""
    return dict(name='demo', vers=version, deps=[], **values)


class RegistryTests(unittest.TestCase):
    """Verify shard paths, version selection and metadata validation."""

    def test_paths(self):
        """Implement all four official crate-name shard cases."""
        for name, path in [('a', '1/a'), ('ab', '2/ab'),
                           ('abc', '3/a/abc'), ('Demo', 'de/mo/demo')]:
            self.assertEqual(index_path(name), path)
        with self.assertRaises(AppError):
            index_path('../escape')

    @patch('cargograph.registry.fetch_records')
    def test_selection_and_cache(self, fetch):
        """Yanked versions are excluded from resolution but exact roots work."""
        fetch.return_value = [record(), record('1.9.0', yanked=True),
                              record('1.2.0'), record('2.0.0')]
        registry = Registry('https://index.example')
        self.assertEqual(registry.resolve('demo', '^1').version, '1.2.0')
        self.assertEqual(registry.exact('demo', '1.9.0').version, '1.9.0')
        self.assertEqual(fetch.call_count, 1)
        with self.assertRaises(AppError):
            registry.resolve('demo', '^3')
        with self.assertRaises(AppError):
            registry.exact('demo', '4.0.0')

    @patch('cargograph.registry.fetch_records')
    def test_dependency_metadata(self, fetch):
        """Include optional/build/target dependencies and honor renaming."""
        item = record()
        item['deps'] = [
            dict(name='alias', package='real', req='^1', optional=True),
            dict(name='builder', req='1', kind='build', target='cfg(unix)'),
            dict(name='tester', req='1', kind='dev'),
        ]
        fetch.return_value = [item]
        deps = Registry('https://index.example').dependencies(
            Node('demo', '1.0.0')
        )
        self.assertEqual([dep.name for dep in deps], ['real', 'builder'])
        self.assertTrue(deps[0].optional)
        self.assertEqual(deps[1].target, 'cfg(unix)')

    @patch('cargograph.registry.fetch_records')
    def test_corrupt_records(self, fetch):
        """Report malformed remote records with an application error."""
        for item in [None, {}, record('bad'), dict(name='other'),
                     dict(name='demo', vers='1.0.0', deps=[None])]:
            fetch.return_value = [item]
            with self.subTest(item=item), self.assertRaises(AppError):
                Registry('https://index.example').records('demo')
