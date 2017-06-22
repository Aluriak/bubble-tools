"""Functions related to the tree depicted by bubble

"""


import functools
import itertools as it
from collections import defaultdict, namedtuple

from bubbletools import utils


# Powernode data aggregation
Powernode = namedtuple('Powernode', 'size contained contained_pnodes contained_nodes')


class BubbleTree:
    """Model of a power graph, that can eventually be oriented.

    """

    def __init__(self, edges:dict, inclusions:dict, roots:frozenset,
                 oriented:bool=False):
        self._edges, self._inclusions = dict(edges), dict(inclusions)
        self._roots = frozenset(roots)
        self._oriented = bool(oriented)
        self._edge_reduction = None  # computed on time

    def compute_edge_reduction(self) -> float:
        """Compute the edge reduction. Costly computation"""
        nb_init_edge = self.init_edge_number()
        nb_poweredge = self.edge_number()
        return (nb_init_edge - nb_poweredge) / (nb_init_edge)

    def init_edge_number(self) -> int:
        """Return the number of edges present in the non-compressed graph"""
        return len(frozenset(frozenset(edge) for edge in self.initial_edges()))

    def initial_edges(self) -> iter:
        """Yield edges in the initial (uncompressed) graphs. Possible doublons."""
        nodes_in = lambda n: ([n] if self.is_node(n) else self.nodes_in(n))
        for node, succs in self.edges.items():
            twos = tuple(two for succ in succs for two in nodes_in(succ))
            for one in nodes_in(node):
                for two in twos:
                    yield one, two

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

    @property
    def edge_reduction(self) -> int:
        if self._edge_reduction is None:
            self._edge_reduction = self.compute_edge_reduction()
        return self._edge_reduction


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


    def assert_powernode(self, name:str) -> None or ValueError:
        """Do nothing if given name refers to a powernode in given graph.
        Raise a ValueError in any other case.

        """
        if name not in self.inclusions:
            raise ValueError("Powernode '{}' does not exists.".format(name))
        if self.is_node(name):
            raise ValueError("Given name '{}' is a node.".format(name))


    def powernode_data(self, name:str) -> Powernode:
        """Return a Powernode object describing the given powernode"""
        self.assert_powernode(name)
        contained_nodes = frozenset(self.nodes_in(name))
        return Powernode(
            size=len(contained_nodes),
            contained=frozenset(self.all_in(name)),
            contained_pnodes=frozenset(self.powernodes_in(name)),
            contained_nodes=contained_nodes,
        )


    def node_number(self, *, count_pnode=True) -> int:
        """Return the number of node"""
        return (sum(1 for n in self.nodes())
                + (sum(1 for n in self.powernodes()) if count_pnode else 0))

    def edge_number(self) -> int:
        """Return the number of (power) edges"""
        edges = set()
        for node, succs in self.edges.items():
            for succ in succs:
                edges.add(frozenset((node, succ)))
        return len(edges)

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

    def nodes_in(self, name) -> iter:
        """Yield all nodes contained in given (power) node"""
        yield from (node for node in self.all_in(name) if self.is_node(node))

    def powernodes_in(self, name) -> iter:
        """Yield all power nodes contained in given (power) node"""
        yield from (node for node in self.all_in(name) if self.is_powernode(node))

    def all_in(self, name) -> iter:
        """Yield all (power) nodes contained in given (power) node"""
        for elem in self.inclusions[name]:
            yield elem
            yield from self.all_in(elem)


    def powernodes_containing(self, name, directly=False) -> iter:
        """Yield all power nodes containing (power) node of given *name*.

        If *directly* is True, will only yield the direct parent of given name.

        """
        if directly:
            yield from (node for node in self.all_in(name)
                        if name in self.inclusions[node])
        else:
            # This algorithm is very bad. Inverting the inclusion dict could
            #  be far better.
            @functools.lru_cache(maxsize=self.node_number(count_pnode=True))
            def contains_target(node, target):
                succs = self.inclusions[node]
                if target in succs:
                    return True
                else:
                    return any(contains_target(succ, target) for succ in succs)
            # populate the cache
            for root in self.roots:
                contains_target(root, name)
            # output all that contains target at some level
            yield from (node for node in self.inclusions.keys()
                        if contains_target(node, name))


    def write_bubble(self, filename:str):
        """Write in given filename the lines of bubble describing this instance"""
        from bubbletools import converter
        converter.tree_to_bubble(self, filename)


    @staticmethod
    def from_bubble_file(bblfile:str, oriented:bool=False) -> 'BubbleTree':
        """Extract data from given bubble file,
        then call from_bubble_data method
        """
        return BubbleTree.from_bubble_data(utils.data_from_bubble(bblfile),
                                           oriented=bool(oriented))


    @staticmethod
    def from_bubble_lines(bbllines:iter, oriented:bool=False) -> 'BubbleTree':
        """Return a BubbleTree instance.

        bbllines -- iterable of raw line, bubble-formatted
        oriented -- True: returned BubbleTree is oriented

        """
        return BubbleTree.from_bubble_data((utils.line_data(line)
                                            for line in bbllines),
                                           oriented=bool(oriented))


    @staticmethod
    def from_bubble_data(bbldata:iter, oriented:bool=False) -> 'BubbleTree':
        """Return a BubbleTree instance.

        bbldata -- lines in bubble bbltree
        oriented -- True: returned BubbleTree is oriented

        """
        # get structure as two dicts
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
                if ltype not in {'COMMENT', 'EMPTY', 'ERROR'}:
                    raise ValueError("The following line is not a valid "
                                     "type ({}): '{}'".format(ltype, payload))
                else:  # it's a comment, an empty line or an error
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
        not_root = set(it.chain.from_iterable(inclusions.values()))
        roots = frozenset(frozenset(inclusions.keys()) - not_root)

        # build the (oriented) bubble tree
        if not oriented:
            edges = utils.completed_graph(edges)
        return BubbleTree(edges=edges, inclusions=dict(inclusions),
                          roots=roots, oriented=oriented)
