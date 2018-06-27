# bubble-tools
python routines related to bubble format, usable in CLI or as a library.

## Installation

    pip install bubbletools

See below for usage.


## Features
- [X] bubble to python
- [X] bubble to [gexf](https://gephi.org/gexf/format/)
- [ ] bubble to cytoscape.js
    - [X] working implementation
    - [X] test on fully valid bubble
    - [ ] unit testing
    - [ ] test on big graphs, for benchmarking (will probably not scale)
- [ ] bubble to dot (via [graphviz](http://graphviz.readthedocs.io/en/latest/))
    - [X] working implementation
    - [X] test on fully valid bubble
    - [ ] unit testing
    - [ ] test on big graphs, for benchmarking (will probably not scale)
- [ ] python to bubble
- [ ] dot to python
- [ ] unit testing on bubble describing cliques


## CLI
`bubble-tools` is usable through CLI.

### validation
usage:

    python3 -m bubbletools validate path/to/bubble/file

Try hard to find errors and inconsistancies in the given bubble file

Spot powernode overlapping, inclusions inconsistancies
and empty or singleton powernodes.
Profiling gives general informations about the file data.

### conversion to dot
usage:

    python3 bubble-tool.py dot path/to/bubble/file path/to/output/file

Convert given bubble file in dot format.
The optional `--render` flag can be used to show the graph after saving.

Same API is available for gexf format.

### conversion to cytoscape.js
usage:

    python3 -m bubbletools js path/to/bubble/file path/to/output/dir

Convert given bubble file in a fully working website using cytoscape.js to render the graph.
The optional `--run` flag can be used to run the default web browser on the generated website.
See Makefile recipe `js` for a usage example.

A website is a collection of files (css, js, html), with only one of them (`js/graph.js`)
that changes according to the input data.

If the `path/to/output/dir` has a `.js` extension, only the `js/graph.js` file will be generated.
This allow one to generates only the changing parts, not the full website each time.
See Makefile recipe `js-per-file` for a usage example.


## python API
Submodules `validator` and `converter` provides the functionnalities described above for CLI:

    from bubbletools import validate, convert

    for log in validate(open('path/to/bubble.lp'), profiling=True):
        print(log)
    convert.to_dot(open('path/to/bubble.lp'), dotfile='path/to/dot.dot')

### python representation of the graph
A lower level interface is the `BubbleTree` object, allowing one to manipulate the graph depicted by bubble data as python object.
See [unit tests](bubbletools/test/test_bbltree.py) for example of `BubbleTree` usage.

    from bubbletools import BubbleTree

    tree = BubbleTree.from_bubble_file('path/to/bubble.lp')
    print(tree.edges, tree.inclusions, tree.roots)

`edges` is a mapping `predecessor -> set of successors`,
`inclusions` is a mapping `(power)node -> set of (power)nodes directly contained`,
and `roots` is a set of (power)nodes that are contained by nothing.

This representation holds all the data necessary for most work on the bubble.
The `BubbleTree.connected_components` function maps a graph with its connected components:

    cc, subroots = BubbleTree.connected_components()

Where `cc` and `subroots` are both mappings, respectively linking *the* root of a connected component with all nodes of the connected component,
and *the* root of a connected component with the other roots of the same connected component.
Thus, connected components are identified by one of their roots, which is key is both dictionaries.


### access powernodes and their data
Follow an example of `BubbleTree` usage, retrieving data on powernodes:

    tree = BubbleTree.from_bubble_file('bubbles/basic.bbl')
    for pnode in tree.powernodes:
        data = tree.powernode_data(pnode)
        print(
            "{} contains nodes {{{}}}, and powernodes {{{}}}."
            "".format(pnode, data.contained_nodes, data.contained_pnodes)
        )

