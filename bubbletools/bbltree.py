"""Functions related to the tree depicted by bubble

"""


import itertools as it
from collections import defaultdict

from bubbletools import utils


class BubbleTree:
    """Model of a powergraph, that can eventually be oriented.

    """

    def __init__(self, edges:dict, inclusions:dict, roots:frozenset,
                 oriented:bool=False):
        self._edges, self._inclusions = dict(edges), dict(inclusions)
        self._roots = frozenset(roots)
        self._oriented = bool(oriented)

    @property
    def oriented(self) -> bool:
        return self._oriented

    @property
    def edges(self) -> dict:
        return self._edges

    @property
    def inclusions(self) -> dict:
        return self._inclusions

    @property
    def roots(self) -> frozenset:
        return self._roots


    def connected_components(self) -> (dict, dict):
        """Return for one root of each connected component all
        the linked objects, and the mapping linking a connected component
        root with the roots that it contains."""
        inclusions = utils.completed_graph(self.inclusions)  # allow bottom-up movement
        edges = utils.completed_graph(self.edges) if self.oriented else self.edges
        cc = {}  # maps cc root with nodes in the cc
        subroots = defaultdict(set)  # maps cc root with other roots of the cc
        walked_roots = set()  # all roots that have been walked already
        for root in self.roots:
            if root in walked_roots: continue  # this cc have been done already
            # walk in the graph starting at root
            cc[root] = set([root])
            walked = cc[root]
            stack = list(edges.get(root, ())) + list(inclusions.get(root, ()))
            while len(stack) > 0:
                *stack, curr = stack
                walked.add(curr)
                if curr in self.roots:  # don't do the walk for already found roots
                    walked_roots.add(curr)
                    subroots[root].add(curr)
                for succ in it.chain(edges.get(curr, ()), inclusions.get(curr, ())):
                    if succ not in walked:
                        stack.append(succ)
        return cc, dict(subroots)


    def nodes(self) -> iter:
        """Yield all nodes in the graph (not the powernodes)"""
        yield from (elem for elem, subs in self.inclusions.items() if subs == ())


    def powernodes(self) -> iter:
        """Yield all powernodes in the graph (not the nodes)"""
        yield from (elem for elem, subs in self.inclusions.items() if subs != ())

    def is_powernode(self, identifier:str) -> bool:
        """True if given identifier is a powernode inside the power graph"""
        return self.inclusions[identifier] != ()

    def is_node(self, identifier:str) -> bool:
        """True if given identifier is a node inside the power graph"""
        return self.inclusions[identifier] == ()

    def nodes_in(self, name):
        """Yield all nodes contained in given (power) node"""
        yield from (node for node in self.all_in(name) if self.is_node(node))

    def powernodes_in(self, name):
        """Yield all power nodes contained in given (power) node"""
        yield from (node for node in self.all_in(name) if self.is_powernode(node))

    def all_in(self, name):
        """Yield all (power) nodes contained in given (power) node"""
        for elem in self.inclusions[name]:
            yield elem
            yield from self.all_in(elem)

    @staticmethod
    def from_bubble_file(bblfile:str, oriented:bool=False) -> 'BubbleTree':
        """Extract data from given bubble file,
        then call from_bubble_data method
        """
        return BubbleTree.from_bubble_data(utils.data_from_bubble(bblfile),
                                           oriented=bool(oriented))


    @staticmethod
    def from_bubble_data(bbldata:iter, oriented:bool=False) -> 'BubbleTree':
        """Return dict of edges and dict of inclusion of given bubble and roots

        bbldata -- lines in bubble bbltree
        oriented -- True: returned BubbleTree is oriented

        Nodes are keys in inclusions, but with an empty tuple instead of a set.

        """
        # get structure as two dict
        edges, inclusions = defaultdict(set), defaultdict(set)
        used_in_edges = set()
        for line in bbldata:
            if not line: continue
            ltype, *payload = line
            if ltype == 'EDGE':
                source, target = payload
                edges[source].add(target)
                used_in_edges.add(source)
                used_in_edges.add(target)
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

        # all (power)nodes used in edges should be present in inclusions tree
        for node in used_in_edges:
            if node not in inclusions:  # contains nothing, so its a node
                inclusions[node] = ()

        # all pure nodes needs to be a key in inclusions
        for node in set(it.chain.from_iterable(inclusions.values())):
            # an element that is not in inclusion is either:
            #  - a node not explicitely defined in a NODE line
            #  - a powernode that contains nothing and not explicitely defined in a SET line
            # the second case is meaningless : this is the case for any unused powernode name.
            # Consequently, elements not in inclusions are nodes.
            if node not in inclusions:
                inclusions[node] = ()

        # find the roots
        not_root = set(contained for contained in
                       it.chain.from_iterable(inclusions.values()))
        roots = frozenset(set(inclusions.keys()) - not_root)

        if not oriented:
            edges = utils.completed_graph(edges)
        return BubbleTree(edges=edges, inclusions=dict(inclusions),
                          roots=roots, oriented=oriented)
