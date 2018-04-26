"""Implementation of various bubbletree comparers.

"""


from bubbletools import BubbleTree


def topology_differences(atree, btree) -> bool:
    """Return a BubbleTree containing only the topology difference between
    given bubble trees.

    For instance, an edge in atree but not in btree with be in returned graph.

    """


def same_network(atree, btree) -> bool:
    """True if given trees share the same structure of powernodes,
    independently of (power)node names,
    and same edge topology between (power)nodes.

    """
    return same_hierarchy(atree, btree) and same_topology(atree, btree)


def set_from_tree(root:str, graph:dict) -> frozenset:
    """Return a recursive structure describing given tree"""
    Node = namedtuple('Node', 'id succs')
    succs = graph[root]
    if succs:
        return (len(succs), sorted(tuple(set_from_tree(succ, graph) for succ in succs)))
    else:
        return 0, ()
