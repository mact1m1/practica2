"""Recursive depth-first graph construction and inverse dependencies."""

from .config import AppError


def build_graph(repository, roots, exclude=''):
    """Construct a versioned graph using recursive DFS from one/many roots."""
    def children(node):
        """Resolve retained edges before the recursive walk visits them."""
        return {
            repository.resolve(dep.name, dep.requirement)
            for dep in repository.dependencies(node)
            if not exclude or exclude not in dep.name
        }

    retained = [r for r in roots if not exclude or exclude not in r.name]
    return recursive_dfs(retained, children)


def recursive_dfs(roots, children):
    """Use the same recursive DFS for forward and reverse adjacency."""
    graph = {}

    def visit(node):
        """Mark a node before descending, preserving cyclic edges."""
        if node in graph:
            return
        graph[node] = set()
        for child in sorted(children(node)):
            graph[node].add(child)
            visit(child)

    for root in sorted(roots):
        visit(root)
    return graph


def reverse_dependencies(graph, target):
    """Find all transitive dependents within an explicitly supplied graph."""
    if target not in graph:
        raise AppError(f"Target is absent from the analyzed graph: {target}")
    inverted = {node: set() for node in graph}
    for parent, children in graph.items():
        for child in children:
            inverted[child].add(parent)
    return recursive_dfs([target], lambda node: inverted[node])


def select_target(graph, text):
    """Accept a unique name or a name@version, rejecting ambiguity."""
    matches = [node for node in graph if text in {node.name, str(node)}]
    if len(matches) != 1:
        raise AppError(f"Target missing or ambiguous; use name@version: {text}")
    return matches[0]
