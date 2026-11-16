"""Recursive depth-first graph construction with cycle-safe visitation."""


def build_graph(repository, roots, exclude=''):
    """Construct a versioned graph using recursive DFS from one/many roots."""
    graph = {}

    def visit(node):
        """Mark a node before descending, preserving cyclic edges."""
        if node in graph:
            return
        graph[node] = set()
        dependencies = repository.dependencies(node)
        for dependency in dependencies:
            if exclude and exclude in dependency.name:
                continue
            child = repository.resolve(
                dependency.name, dependency.requirement
            )
            graph[node].add(child)
            visit(child)

    for root in roots:
        if not exclude or exclude not in root.name:
            visit(root)
    return graph
