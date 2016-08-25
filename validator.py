"""Routines for bubble format validation"""

from collections import Counter

import bbltree
import utils


def validate(bblfile:str, profiling=False):
    """Yield lines of warnings and errors about input bbl file.

    profiling -- yield also info lines about input bbl file.

    """
    bubble = tuple(sorted(tuple(utils.file_lines(bblfile))))
    data = tuple(utils.line_data(line) for line in bubble)
    # launch profiling
    if profiling:
        counter = Counter(utils.line_type(line) for line in bbl)
        for ltype, count in profile.items():
            yield 'INFO {} lines of type {}'.format(count, ltype)
    # launch validation
    edges, inclusions, roots = bbltree.from_bubble_data(data)
    print('edges:', edges)
    print('inclusions:', inclusions)
    print('roots:', roots)
    cc, subroots = bbltree.connected_components((edges, inclusions, roots))
    print('cc:', cc)
    print('subroots:', subroots)
