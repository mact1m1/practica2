"""Visualization tests preserve all edges without infinite tree expansion."""

import unittest

from cargograph.registry import Node
from cargograph.render import ascii_tree, dot_graph


def node(name):
    """Create a fixture vertex."""
    return Node(name, '1.0.0')


class RenderTests(unittest.TestCase):
    """Check DOT syntax structure, deterministic output and tree markers."""

    def test_dot(self):
        """Represent edges and isolated nodes with quoted identifiers."""
        graph = {node('B'): set(), node('A'): {node('B')}, node('Z'): set()}
        text = dot_graph(graph)
        self.assertIn('"A@1.0.0" -> "B@1.0.0";', text)
        self.assertIn('"Z@1.0.0";', text)
        self.assertEqual(text, dot_graph(dict(reversed(list(graph.items())))))

    def test_escaping(self):
        """Quote labels rather than interpolating unsafe DOT fragments."""
        text = dot_graph({node('a"b'): set()})
        self.assertIn('a\\"b', text)

    def test_tree(self):
        """Distinguish ancestor cycles from previously expanded diamonds."""
        graph = {node('A'): {node('B'), node('C')},
                 node('B'): {node('D')}, node('C'): {node('D')},
                 node('D'): {node('A')}}
        text = ascii_tree(graph, node('A'))
        self.assertIn('A@1.0.0 [cycle]', text)
        self.assertIn('D@1.0.0 [shared]', text)
        self.assertEqual(len(text.splitlines()), 6)

    def test_leaf(self):
        """An isolated vertex renders without connectors."""
        self.assertEqual(ascii_tree({node('A'): set()}, node('A')),
                         'A@1.0.0')
