def tree_to_file(tree:'BubbleTree', outfile:str):
    """Compute the bubble representation of given power graph,
    and push it into given file."""
    with open(outfile, 'w') as fd:
        fd.write(tree_to_bubble(tree))


def tree_to_bubble(tree:'BubbleTree') -> str:
    """Compute the gexf representation of given power graph,
    and push it into given file.

    """
    return '\n'.join(lines_from_tree(tree))


def lines_from_tree(tree, nodes_and_set:bool=False) -> iter:
    """Yield lines of bubble describing given BubbleTree"""
    NODE = 'NODE\t{}'
    INCL = 'IN\t{}\t{}'
    EDGE = 'EDGE\t{}\t{}\t1.0'
    SET  = 'SET\t{}'

    if nodes_and_set:
        for node in tree.nodes():
            yield NODE.format(node)

        for node in tree.powernodes():
            yield SET.format(node)

    for node, includeds in tree.inclusions.items():
        for included in includeds:
            yield INCL.format(included, node)

    for node, succs in tree.edges.items():
        for succ in succs:
            yield EDGE.format(node, succ)

