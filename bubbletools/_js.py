"""Convert bubble files into JS file for cytoscape.js.
Handle a superset of bubble format, allowing for FALSEDGE lines,
indicating edges that do not exists in the graph, but are covered by a poweredge.

usage:
    python make_from_bubble.py <bblfile> <output file>

TODO:

- when hover/click an incomplete poweredge, show related false edges
  - hide false edges
- when hover/click a poweredge/powernode, show related info (cover, annotations)

"""

import os
import sys
import shutil
import itertools
import pkg_resources
from bubbletools import utils
from bubbletools.bbltree import BubbleTree
from bubbletools.utils import reversed_graph
from bubbletools._js_data import (JS_HEADER, JS_MIDDLE, JS_FOOTER, JS_NODE_LINE,
                                  JS_EDGE_LINE, JS_FALSEDGE_LINE,
                                  JS_MOUSEOVER_SHOW_CALLBACKS,
                                  JS_MOUSEOVER_WIDTH_CALLBACKS)


def bbl_to_cys(bblfile:str, oriented:bool=False, width_as_cover:bool=True,
               show_cover:str='cover: {}', false_edge_on_hover:bool=True,
               default_poweredge_width:int=5):
    """Yield lines of js to write in output file"""
    # False edges in clique
    with open(bblfile) as fd:
        falsedges = tuple(
            (src, trg) for _, src, trg in
            (l.strip().split('\t') for l in fd if l.startswith('FALSEDGE'))
        )
    if false_edge_on_hover:
        nodes_in_false_edges = set(itertools.chain.from_iterable(falsedges))
    # Detect incomplete power edges
    with open(bblfile) as fd:
        falsepoweredges = {}
        for line in fd:
            if line.startswith('FALSEPOWEREDGE'):
                _, seta, setb, src, trg = line.strip().split('\t')
                falsepoweredges.setdefault(frozenset((seta, setb)), set()).add((src, trg))
                if false_edge_on_hover:
                    nodes_in_false_edges.add(src)
                    nodes_in_false_edges.add(trg)

    # Build node hierarchy
    tree = BubbleTree.from_bubble_file(bblfile, symmetric_edges=False, oriented=oriented)
    def isclique(node): return node in tree.edges.get(node, ())
    def handle_node(node, parent=None):
        clique = isclique(node)
        if false_edge_on_hover and clique:
            falsedges = ((src, trg) for src, trg in itertools.combinations(tuple(tree.nodes_in(node)), r=2)
                         if src in nodes_in_false_edges and trg in nodes_in_false_edges)
        else: falsedges = ()
        return JS_NODE_LINE(node, parent, clique=clique, falsedges=falsedges)

    yield from JS_HEADER

    for node in tree.roots:
        yield handle_node(node)
        yield JS_NODE_LINE(node, clique=isclique(node))
    parents = reversed_graph(tree.inclusions)  # (power)node -> direct parent
    for node, parents in parents.items():
        assert len(parents) == 1, {node: parents}
        yield handle_node(node, parent=next(iter(parents)))

    yield from JS_MIDDLE

    use_cover = width_as_cover or show_cover
    if use_cover:
        def coverof(source, target) -> int:
            source_cover = sum(1 for _ in tree.nodes_in(source))
            target_cover = sum(1 for _ in tree.nodes_in(target))
            return (source_cover or 1) * (target_cover or 1)
        def labelof(cover:int) -> str or None:
            if cover > 1:  # it's a power edge
                return show_cover.format(cover)
    # Now, (power) edges
    powernodes = frozenset(tree.powernodes())
    for source, targets in tree.edges.items():
        for target in targets:
            if target == source:  continue  # cliques are not handled this way
            label, attrs, isreflexive = None, {}, False
            ispower = source in powernodes or target in powernodes
            if use_cover:
                cover = coverof(source, target)
                label, attrs = labelof(cover), {'width': 2+cover if width_as_cover else default_poweredge_width}
            if ispower and frozenset((source, target)) in falsepoweredges:
                attrs['falsedges'] = list(map(list, falsepoweredges[frozenset((source, target))]))
            yield ' '*8 + JS_EDGE_LINE(source, target, ispower, label=label, attrs=attrs)

    # If asked so, add false edges in the file as regular edges
    if not false_edge_on_hover:
        for source, target in falsedges:
            yield ' '*8 + JS_FALSEDGE_LINE(source, target)
        for edges in falsepoweredges.values():
            for source, target in edges:
                yield ' '*8 + JS_FALSEDGE_LINE(source, target)

    yield from JS_FOOTER

    if false_edge_on_hover:
        yield from JS_MOUSEOVER_SHOW_CALLBACKS
    else:
        yield from JS_MOUSEOVER_WIDTH_CALLBACKS


def bubble_to_dir(bblfile:str, jsdir:str, oriented:bool=False, **style):
    """

    bblfile -- filename containing bubble data
    jsdir -- a directory in which put the website, or the graph.js to fill,
             or the .html to fill with everything
    oriented -- True if the power graph oriented
    style -- options for bbl_to_cys

    """
    extension = os.path.splitext(jsdir)[1]
    mode = 'w'
    if not extension:  # it's a directory: copy the directory template and fill it
        if os.path.exists(jsdir):
            shutil.rmtree(jsdir)
        father_dir = os.path.split(jsdir.rstrip('/'))[0]
        if father_dir:
            assert os.path.isdir(father_dir), '{} must be a directory'.format(father_dir)
        template_dir = pkg_resources.resource_filename('bubbletools', '_js_dir_template')
        shutil.copytree(template_dir, jsdir, copy_function=shutil.copy)
        code_js_file = os.path.join(jsdir, 'js/graph.js')
    elif extension == '.html':  # write everything in a single file
        code_js_file, mode = jsdir, 'a'
        template_dir = pkg_resources.resource_filename('bubbletools', '_js_dir_template')
        with open(code_js_file, 'w') as ofd, open(template_dir+'/index.html') as hfd:
            basehtml = hfd.read()
            script_to_replace = '<script src="js/graph.js"></script>'
            start = basehtml.find(script_to_replace)
            stop = start + len(script_to_replace)
            ofd.write(basehtml[:start].strip() + '\n<script>')
    else:  # it's a file: let's write directly the code in it
        code_js_file = jsdir
    with open(code_js_file, mode) as fd:
        for line in bbl_to_cys(bblfile, oriented=oriented, **style):
            fd.write(line + '\n')
    if extension == '.html':
        with open(code_js_file, 'a') as fd:
            fd.write('</script>' + basehtml[stop:])
