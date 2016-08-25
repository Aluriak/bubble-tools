"""Routines for bubble format validation"""

import itertools as it
from collections import Counter

import bbltree
import utils


def validate(bblfile:str, profiling=False):
    """Yield lines of warnings and errors about input bbl file.

    profiling -- yield also info lines about input bbl file.

    """
    bubble = tuple(sorted(tuple(utils.file_lines(bblfile))))
    data = tuple(utils.line_data(line) for line in bubble)
    types = tuple(utils.line_type(line) for line in bubble)
    # launch profiling
    if profiling:
        ltype_counts = Counter(types)
        for ltype, count in ltype_counts.items():
            yield 'INFO {} lines of type {}'.format(count, ltype)
    # launch validation
    for errline in (l for l, t in zip(bubble, types) if t == 'ERROR'):
        yield 'ERROR line is not bubble: "{}"'.format(errline)
    tree = bbltree.from_bubble_data(data)
    edges, inclusions, roots = tree
    # print('edges:', edges)
    # print('roots:', roots)
    cc, subroots = bbltree.connected_components(tree)
    # print('cc:', cc)
    # print('subroots:', subroots)
    if profiling:
        yield 'INFO {} top (power)nodes'.format(len(roots))
        yield 'INFO {} connected components'.format(len(cc))
        yield 'INFO {} nodes are defined, {} are used'.format(
            ltype_counts['NODE'], len(tuple(bbltree.nodes(tree))))
        yield 'INFO {} powernodes are defined, {} are used'.format(
            ltype_counts['SET'], len(tuple(bbltree.powernodes(tree))))

    yield from inclusions_validation(tree)


def inclusions_validation(tree:(dict, dict, frozenset)) -> iter:
    """Yield message about inclusions inconsistancies"""
    edges, inclusions, roots = tree
    # search for powernode overlapping
    for one, two in it.combinations(inclusions, 2):
        one_inc = set(included(one, inclusions))
        two_inc = set(included(two, inclusions))
        common_inc = one_inc & two_inc
        if len(common_inc) == one_inc:
            if not two in one_inc:
                yield ("ERROR inconsistency in inclusions: {} is both"
                       " included and not included in {}.".format(two, one))
        if len(common_inc) == two_inc:
            if not one in two_inc:
                yield ("ERROR inconsistency in inclusions: {} is both"
                       " included and not included in {}.".format(one, two))
        if len(common_inc) > 0:  # one and two are not disjoint
            if len(common_inc) == two_inc or len(common_inc) == two_inc:
                # one is included in the other
                pass
            else:  # problem: some nodes are shared, but not all
                yield ("ERROR overlapping powernodes:"
                       " {} nodes are shared by {} and {},"
                       " which are not in inclusion."
                       " Shared nodes are {}".format(
                           len(common_inc), one, two, common_inc))


def included(powernode:str, inclusions:dict, nodes_only=False) -> iter:
    """Yield (power)nodes below given powernode (contained by it,
    or contained by a powernode contained by it, etc).

    >>> sorted(included('p1', {'p1': ('p2', 1), 'p2': (3,), 1: (), 3: ()}), key=str)
    [1, 3, 'p2']
    >>> sorted(included('p1', {'p1': ('p2', 1), 'p2': (3,), 1: (), 3: ()}, nodes_only=True), key=str)
    [1, 3]

    """
    if nodes_only:
        condition = lambda e: e != powernode and inclusions[e] == ()
    else:
        condition = lambda e: e != powernode
    yield from (elem for elem in utils.walk(powernode, (inclusions,))
                if condition(elem))
