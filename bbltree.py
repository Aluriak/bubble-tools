"""Functions related to the tree depicted by bubble"""

import itertools as it
from collections import defaultdict

import utils


def from_bubble_data(bbldata:iter) -> (dict, dict, frozenset):
    """Return dict of edges and dict of inclusion of given bubble and roots

    edges -- {predecessor: {successors}}
    inclusions -- {container: {directly contained}}
    roots -- {(power)node contained by nothing}
    """
    # get structure as two dict
    edges, inclusions = defaultdict(set), defaultdict(set)
    for line in bbldata:
        if not line: continue
        ltype, *payload = line
        if ltype == 'EDGE':
            source, target = payload
            edges[source].add(target)
        elif ltype == 'SET':
            setname = payload[0]
            inclusions[setname]  # create it if not already populated
        elif ltype == 'NODE':
            nodename = payload[0]
            inclusions[nodename] = ()  # a node can't contain anything
        elif ltype == 'IN':
            contained, container = payload
            inclusions[container].add(contained)
        else:  # comment, empty or error
            assert ltype in ('COMMENT', 'EMPTY', 'ERROR')
            pass

    # find the roots
    not_root = set(contained for contained in
                   it.chain.from_iterable(inclusions.values()))
    roots = frozenset(set(inclusions.keys()) - not_root)

    return utils.completed_graph(edges), dict(inclusions), roots


def connected_components(tree:(dict, dict, frozenset)) -> (dict, dict):
    """Return for one root of each connected component all
    the linked objects, and the mapping linking a connected component
    root with the roots that it contains."""
    edges, inclusions, roots = tree
    inclusions = utils.completed_graph(inclusions)  # allow bottom-up movement
    cc = {}  # maps cc root with nodes in the cc
    subroots = defaultdict(set)  # maps cc root with other roots of the cc
    walked_roots = set()  # all roots that have been walked already
    for root in roots:
        if root in walked_roots: continue  # this cc have been done already
        # walk in the graph
        cc[root] = set([root])
        walked = cc[root]
        stack = list(edges.get(root, ())) + list(inclusions.get(root, ()))
        while len(stack) > 0:
            *stack, curr = stack
            walked.add(curr)
            if curr in roots:  # don't do the walk for already found roots
                walked_roots.add(curr)
                subroots[root].add(curr)
            for succ in it.chain(edges.get(curr, ()), inclusions.get(curr, ())):
                if succ not in walked:
                    stack.append(succ)
    return cc, dict(subroots)
