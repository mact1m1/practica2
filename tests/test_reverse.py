"""Transitive inverse queries use the shared recursive DFS."""

import unittest

from cargograph.config import AppError
from cargograph.graph import reverse_dependencies, select_target
from cargograph.registry import Node


def node(name):
    """Create a named fixture vertex."""
    return Node(name, '1.0.0')


class ReverseTests(unittest.TestCase):
    """Check transitivity, cycles, isolated nodes and ambiguous versions."""

    def test_transitive(self):
        """Both direct and indirect dependents are found exactly once."""
        graph = {node('A'): {node('B')}, node('B'): {node('C')},
                 node('C'): set(), node('Z'): set()}
        result = reverse_dependencies(graph, node('C'))
        self.assertEqual(set(result), {node(n) for n in 'ABC'})
        self.assertEqual(result[node('C')], {node('B')})

    def test_cycle(self):
        """Reverse traversal terminates on cyclic graphs and self-loops."""
        graph = {node('A'): {node('B')}, node('B'): {node('A'), node('B')}}
        self.assertEqual(set(reverse_dependencies(graph, node('A'))),
                         {node('A'), node('B')})

    def test_isolated(self):
        """No dependents is a valid single-node reverse graph."""
        self.assertEqual(reverse_dependencies({node('A'): set()}, node('A')),
                         {node('A'): set()})

    def test_target(self):
        """A version is required when the graph has several named releases."""
        graph = {node('A'): set(), Node('A', '2.0.0'): set()}
        self.assertEqual(select_target(graph, 'A@1.0.0'), node('A'))
        for target in ['A', 'Z']:
            with self.subTest(target=target), self.assertRaises(AppError):
                select_target(graph, target)
        with self.assertRaises(AppError):
            reverse_dependencies(graph, node('Z'))
