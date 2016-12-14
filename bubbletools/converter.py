"""Routines for bubble to dot conversion"""


import os

from graphviz import Graph

from bubbletools.bbltree import BubbleTree
from bubbletools import utils

from bubbletools import _gexf as gexf_converter


def bubble_to_dot(bblfile:str, dotfile:str=None, render:bool=False,
                  oriented:bool=False):
    """Write in dotfile a graph equivalent to those depicted in bubble file"""
    tree = BubbleTree.from_bubble_data(utils.data_from_bubble(bblfile),
                                       oriented=bool(oriented))
    return tree_to_dot(tree, dotfile, render=render)


def bubble_to_gexf(bblfile:str, gexffile:str=None, oriented:bool=False):
    """Write in dotfile a graph equivalent to those depicted in bubble file"""
    tree = BubbleTree.from_bubble_data(utils.data_from_bubble(bblfile),
                                       oriented=bool(oriented))
    gexf_converter.tree_to_file(tree, gexffile)
    return gexffile


def tree_to_dot(tree:BubbleTree, dotfile:str=None, render:bool=False):
    """Write in dotfile a graph equivalent to those depicted in bubble file

    See http://graphviz.readthedocs.io/en/latest/examples.html#cluster-py
    for graphviz API

    """
    graph = tree_to_graph(tree)
    path = None
    if dotfile:  # first save the dot file.
        path = graph.save(dotfile)
    if render:  # secondly, show it.
        # As the dot file is known by the Graph object,
        # it will be placed around the dot file.
        graph.view()
    return path


def tree_to_graph(bbltree:BubbleTree) -> Graph:
    """Compute as a graphviz.Graph instance the given graph.

    See http://graphviz.readthedocs.io/en/latest/examples.html#cluster-py
    for graphviz API

    """
    def create(name:str):
        """Return a graphviz graph figurating a powernode"""
        ret = Graph('cluster_' + name)
        # dirty hack to get links between clusters: add a blank node inside
        # so the subgraph don't take it's name directly, but the blank node do.
        # ret.body.append('label = "{}"'.format(name))  # replaced by:
        ret.node(name, style='invis', shape='point')
        # ret.body.append('style=plaintext')
        ret.body.append('color=lightgrey')
        ret.body.append('label=""')
        ret.body.append('shape=ellipse')
        ret.body.append('penwidth=2')
        ret.body.append('pencolor=black')
        return ret
    nodes = frozenset(bbltree.nodes)
    subgraphs = {}
    # build for each powernode the associated subgraph, and add its successors
    for powernode in bbltree.powernodes:
        if powernode not in subgraphs:
            subgraphs[powernode] = create(powernode)
        for succ in bbltree.inclusions[powernode]:
            if succ not in subgraphs:
                if succ not in nodes:
                    subgraphs[succ] = create(succ)
                else:
                    subgraphs[powernode].node(succ)
    # add to Graph instances the Graph of successors as subgraphs 
    for powernode, succs in bbltree.inclusions.items():
        for succ in succs:
            if succ not in nodes:
                subgraphs[powernode].subgraph(subgraphs[succ])
    # build the final graph by adding to it subgraphs of roots
    graph = Graph('graph', graph_attr={'compound': 'true'})
    for root in bbltree.roots:
        if root in subgraphs:
            graph.subgraph(subgraphs[root])
    # add the edges to the final graph
    for source, targets in bbltree.edges.items():
        for target in targets:
            if source <= target:
                attrs = {}
                if source not in nodes:
                    attrs.update({'ltail': 'cluster_' + source})
                if target not in nodes:
                    attrs.update({'lhead': 'cluster_' + target})
                graph.edge(source, target, **attrs)
    # print(graph)  # debug line
    # graph.view()  # debug line
    return graph
