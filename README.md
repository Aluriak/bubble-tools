# bubble-tools
python routines related to bubble format, usable in CLI or as a library.

## Installation

    pip install bubbletools

See below for usage.


## TODO
- [X] bubble to python
- [ ] python to bubble
- [X] bubble to dot  (via [graphviz](http://graphviz.readthedocs.io/en/latest/))
- [ ] dot to python


## CLI
`bubble-tools` is usable through CLI.

### validation
usage:

    python3 bubble-tool.py validate path/to/bubble/file

Try hard to find errors and inconsistancies in the given bubble file

Spot powernode overlapping, inclusions inconsistancies
and empty or singleton powernodes.
Profiling gives general informations about the file data.

### conversion to dot
usage:

    python3 bubble-tool.py dot path/to/bubble/file path/to/output/file

Convert given bubble file in dot format.


## python API
Submodules `validator` and `converter` provides the functionnalities described above for CLI:

    from bubbletools import validate, convert

    for log in validate(open('path/to/bubble.lp'), profiling=True):
        print(log)
    convert.to_dot(open('path/to/bubble.lp'), dotfile='path/to/dot.dot')

### python representation of the graph
A lower level interface is the `bbltree` submodule, allowing one to manipulate the graph depicted by bubble data as python object.

    from bubbletools import bbltree

    tree = bbltree.from_bubble_data(open('path/to/bubble.lp'))
    edges, inclusions, roots = tree

`edges` is a mapping `predecessor -> set of successors`,
`inclusions` is a mapping `(power)node -> set of (power)nodes directly contained`,
and `roots` is a set of (power)nodes that are contained by nothing.

This representation holds all the data necessary for most work on the bubble.
The `bbltree.connected_components` function maps a graph with its connected components:

    cc, subroots = bbltree.connected_components(tree)

Where `cc` and `subroots` are both mapping, respectively linking *the* root of a connected component with all nodes of the connected component,
and *the* root of a connected component with the other roots of the same connected component.
Thus, connected components are identified by one of their roots, which is key is both dictionaries.
