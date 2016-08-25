"""Various functions"""

import re
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


def completed_graph(graph:dict) -> dict:
    """Return given graph completed"""
    ret = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            ret[node].add(succ)
            ret[succ].add(node)
    return dict(ret)


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
