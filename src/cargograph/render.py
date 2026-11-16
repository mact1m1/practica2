"""Deterministic Graphviz DOT and cycle-safe ASCII visualization."""

import json


def dot_graph(graph):
    """Return valid Graphviz source with quoted versioned identifiers."""
    def quote(node):
        """Escape a versioned identifier for a DOT string literal."""
        return json.dumps(str(node), ensure_ascii=True)

    lines = ['digraph dependencies {', '  rankdir=LR;']
    for node in sorted(graph):
        lines.append(f'  {quote(node)};')
    for parent in sorted(graph):
        for child in sorted(graph[parent]):
            lines.append(f'  {quote(parent)} -> {quote(child)};')
    return '\n'.join(lines + ['}'])


def ascii_tree(graph, root):
    """Render a spanning tree, marking cycles and shared subgraphs."""
    lines = [str(root)]
    seen = {root}

    def visit(node, prefix, ancestors):
        """Expand each vertex once, with distinct cycle/shared markers."""
        children = sorted(graph[node])
        for index, child in enumerate(children):
            last = index == len(children) - 1
            connector = '`-- ' if last else '|-- '
            marker = ''
            if child in ancestors:
                marker = ' [cycle]'
            elif child in seen:
                marker = ' [shared]'
            lines.append(f'{prefix}{connector}{child}{marker}')
            if not marker:
                seen.add(child)
                continuation = '    ' if last else '|   '
                visit(child, prefix + continuation, ancestors | {child})

    visit(root, '', {root})
    return '\n'.join(lines)
