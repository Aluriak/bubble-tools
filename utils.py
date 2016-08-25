"""Various functions"""

import re
import itertools as it
from collections import defaultdict, OrderedDict


LINE_TYPES = OrderedDict((
    (r'(EDGE)\t([^\t]+)\t([^\t]+)\t[0-9]*\.?[0-9]+', 'EDGE'),
    (r'(SET)\t([^\t]+)\t[0-9]*\.?[0-9]+', 'SET'),
    (r'(IN)\t([^\t]+)\t([^\t]+)', 'IN'),
    (r'(NODE)\t([^\t]+)', 'NODE'),
    (r'\s*#.*', 'COMMENT'),
    (r'', 'EMPTY'),
    (r'.*', 'ERROR'),
))


def reversed_graph(graph:dict) -> dict:
    """Return given graph reversed"""
    ret = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            ret[succ].add(node)
    return dict(ret)


def completed_graph(graph:dict) -> dict:
    """Return given graph completed"""
    ret = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            ret[node].add(succ)
            ret[succ].add(node)
    return dict(ret)


def walk(start:list, graphs:iter) -> iter:
    """walk on given graphs, beginning on start.
    Yield all found nodes, including start.

    All graph are understood as a single one,
    with merged keys and values.

    """
    walked = set([start])
    stack = [start]
    while len(stack) > 0:
        *stack, curr = stack
        yield curr
        succs = it.chain.from_iterable(graph.get(curr, ()) for graph in graphs)
        for succ in succs:
            if succ not in walked:
                walked.add(curr)
                stack.append(succ)


def have_cycle(graph:dict) -> frozenset:
    """Perform a topologic sort to detect any cycle.

    Return the set of unsortable nodes. If at least one item,
    then there is cycle in given graph.

    """
    # topological sort
    walked = set()  # walked nodes
    nodes = frozenset(it.chain(it.chain.from_iterable(graph.values()), graph.keys()))  # all nodes of the graph
    preds = reversed_graph(graph)  # succ: preds
    last_walked_len = -1
    while last_walked_len != len(walked):
        last_walked_len = len(walked)
        for node in nodes - walked:
            if len(preds.get(node, set()) - walked) == 0:
                walked.add(node)
    return frozenset(nodes - walked)


def bubble_file_data(bblfile:str) -> iter:
    """Yield data found in given bubble file"""
    yield from (line_data(line) for line in file_lines(bblfile))


def file_lines(bblfile:str) -> iter:
    """Yield lines found in given file"""
    with open(bblfile) as fd:
        yield from (line.rstrip() for line in fd if line.rstrip())


def line_type(line:str) -> str:
    """Give type of input line, as defined in LINE_TYPES

    >>> line_type('IN\\ta\\tb')
    'IN'
    >>> line_type('')
    'EMPTY'

    """
    for regex, ltype in LINE_TYPES.items():
        if re.fullmatch(regex, line):
            return ltype
    raise ValueError("Input line \"{}\" is not bubble formatted".format(line))


def line_data(line:str) -> tuple:
    """Return groups found in given line

    >>> line_data('IN\\ta\\tb')
    ('IN', 'a', 'b')
    >>> line_data('')
    ()

    """
    for regex, _ in LINE_TYPES.items():
        match = re.fullmatch(regex, line)
        if match:
            return match.groups()
    raise ValueError("Input line \"{}\" is not bubble formatted".format(line))
