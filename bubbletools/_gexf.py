"""Conversion from a powergraph tree to a gexf representation"""


GEXF_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
     <graph mode="static" defaultedgetype="undirected">
        <nodes>
            {}
        </nodes>
        <edges>
            {}
        </edges>
    </graph>
</gexf>
"""


def tree_to_file(tree:'BubbleTree', outfile:str):
    """Compute the gexf representation of given power graph,
    and push it into given file."""
    with open(outfile, 'w') as fd:
        fd.write(tree_to_gexf(tree))


def tree_to_gexf(tree:'BubbleTree') -> str:
    """Compute the gexf representation of given power graph,
    and push it into given file.

    See https://gephi.org/gexf/format/index.html
    for format doc.

    """
    output_nodes, output_edges = '', ''

    def build_node(node:str) -> str:
        """Yield strings describing given node, recursively"""
        if tree.inclusions[node]:  # it's a powernode
            yield '<node id="{}" label="{}">'.format(node, node)
            yield '<nodes>'
            for sub in tree.inclusions[node]:
                yield from build_node(sub)
            yield '</nodes>'
            yield '</node>'
        else:  # it's a regular node
            yield '<node id="{}" label="{}"/>'.format(node, node)
        return

    # build full hierarchy from the roots
    output_nodes += '\n'.join('\n'.join(build_node(root)) for root in tree.roots)

    # # add the edges to the final graph
    for idx, (source, targets) in enumerate(tree.edges.items()):
        for target in targets:
            if source <= target:  # edges dict is complete. This avoid multiple edges.
                output_edges += '<edge id="{}" source="{}" target="{}" />\n'.format(idx, source, target)

    return GEXF_TEMPLATE.format(output_nodes, output_edges)
