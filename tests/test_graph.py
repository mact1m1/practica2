"""DFS behavior for cycles, shared descendants and filtered vertices."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cargograph.config import AppError
from cargograph.graph import build_graph
from cargograph.registry import Node
from cargograph.testrepo import TestRepository, validate_graph


def node(name):
    """Construct a fixture vertex with the test release version."""
    return Node(name, '1.0.0')


class GraphTests(unittest.TestCase):
    """Read real offline fixtures, exercising the same interface as HTTP."""

    def build(self, data, exclude=''):
        """Create a temporary repository and build its A closure."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'repo.json'
            path.write_text(json.dumps(data), encoding='utf-8')
            repo = TestRepository(path, '1.0.0')
            return build_graph(repo, [repo.exact('A', '1.0.0')], exclude)

    def test_diamond(self):
        """A shared descendant appears once and both incoming edges remain."""
        graph = self.build(dict(A=['B', 'C'], B=['D'], C=['D'], D=[]))
        self.assertEqual(set(graph), {node(n) for n in 'ABCD'})
        self.assertEqual(graph[node('B')], {node('D')})
        self.assertEqual(graph[node('C')], {node('D')})

    def test_cycles(self):
        """Self-loops and multi-node cycles terminate without dropping edges."""
        graph = self.build(dict(A=['A', 'B'], B=['C'], C=['A']))
        self.assertIn(node('A'), graph[node('A')])
        self.assertEqual(graph[node('C')], {node('A')})

    def test_filter_prunes_subtree(self):
        """Excluded names and their exclusive descendants are never visited."""
        graph = self.build(dict(A=['B'], B=['C'], C=[]), 'B')
        self.assertEqual(graph, {node('A'): set()})

    def test_isolated(self):
        """An isolated root remains a valid single-node graph."""
        self.assertEqual(self.build(dict(A=[], Z=[])), {node('A'): set()})

    def test_invalid_repository(self):
        """Reject malformed JSON structures and dangling references."""
        for data in [[], {}, {'a': []}, {'A': 'B'}, {'A': ['B']},
                     {'A': [{}]}, {'A': [1]}]:
            with self.subTest(data=data), self.assertRaises(AppError):
                validate_graph(data)

    def test_versioned_vertices(self):
        """Different releases of the same crate are distinct graph vertices."""
        self.assertNotEqual(node('A'), Node('A', '2.0.0'))
