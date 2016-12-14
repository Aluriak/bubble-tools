"""Routines for bubble format validation"""

import os
import itertools as it
from collections import Counter

from bubbletools.bbltree import BubbleTree
from bubbletools import utils


def validate(bbllines:iter, *, profiling=False):
    """Yield lines of warnings and errors about input bbl lines.

    profiling -- yield also info lines about input bbl file.

    If bbllines is a valid file name, it will be read.
    Else, it should be an iterable of bubble file lines.

    """
    if isinstance(bbllines, str):
        if os.path.exists(bbllines):  # filename containing bubble
            bbllines = utils.file_lines(bbllines)
        elif '\n' not in bbllines or '\t' not in bbllines:
            # probably a bad file name: let's rise the proper error
            bbllines = utils.file_lines(bbllines)
        else:  # bubble itself
            bbllines = bbllines.split('\n')
    bubble = tuple(bbllines)
    data = tuple(utils.line_data(line) for line in bubble)
    types = tuple(utils.line_type(line) for line in bubble)
    # launch profiling
    if profiling:
        ltype_counts = Counter(types)
        for ltype, count in ltype_counts.items():
            yield 'INFO {} lines of type {}'.format(count, ltype)
        yield 'INFO {} lines of payload'.format(
            ltype_counts['EDGE'] + ltype_counts['IN'] +
            ltype_counts['NODE'] + ltype_counts['SET'])
    # launch validation
    for errline in (l for l, t in zip(bubble, types) if t == 'ERROR'):
        yield 'ERROR line is not bubble: "{}"'.format(errline)
    tree = BubbleTree.from_bubble_data(data)
    cc, subroots = tree.connected_components()
    # print('cc:', cc)
    # print('subroots:', subroots)
    if profiling:
        yield 'INFO {} top (power)nodes'.format(len(tree.roots))
        yield 'INFO {} connected components'.format(len(cc))
        yield 'INFO {} nodes are defined, {} are used'.format(
            ltype_counts['NODE'], len(tuple(tree.nodes())))
        yield 'INFO {} powernodes are defined, {} are used'.format(
            ltype_counts['SET'], len(tuple(tree.powernodes())))

    yield from inclusions_validation(tree)


def inclusions_validation(tree:BubbleTree) -> iter:
    """Yield message about inclusions inconsistancies"""
    # search for powernode overlapping
    for one, two in it.combinations(tree.inclusions, 2):
        assert len(one) == len(one.strip())
        assert len(two) == len(two.strip())
        one_inc = set(included(one, tree.inclusions))
        two_inc = set(included(two, tree.inclusions))
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
    for pwn in tree.powernodes():
        # search for empty powernodes
        if len(tree.inclusions[pwn]) == 0:
            yield ("WARNING empty powernode: {} is defined,"
                   " but contains nothing".format(pwn))
        # search for singleton powernodes
        if len(tree.inclusions[pwn]) == 1:
            yield ("WARNING singleton powernode: {} is defined,"
                   " but contains only {}".format(pwn, tree.inclusions[pwn]))
    # search for cycles
    nodes_in_cycles = utils.have_cycle(tree.inclusions)
    if nodes_in_cycles:
        yield ("ERROR inclusion cycle: the following {}"
               " nodes are involved: {}".format(
                   len(nodes_in_cycles), set(nodes_in_cycles)))


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
