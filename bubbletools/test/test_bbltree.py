

import pytest
from bubbletools import bbltree


BUBBLE_DATA = (
    ('EDGE', 'k', 'p1'),
    ('EDGE', 'k', 'p2'),
    ('EDGE', 'p3', 'p4'),
    ('IN', 'a', 'p3'),
    ('IN', 'b', 'p3'),
    ('IN', 'c', 'p1'),
    ('IN', 'd', 'p1'),
    ('IN', 'e', 'p4'),
    ('IN', 'f', 'p4'),
    ('IN', 'g', 'p2'),
    ('IN', 'h', 'p2'),
    ('IN', 'p3', 'p1'),
    ('IN', 'p4', 'p2'),
    ('NODE', 'k'),
    ('SET', 'p1'),
    ('SET', 'p3'),
)


@pytest.fixture
def powergraph():
    return bbltree.BubbleTree.from_bubble_data(BUBBLE_DATA)

@pytest.fixture
def oriented_powergraph():
    return bbltree.BubbleTree.from_bubble_data(BUBBLE_DATA, oriented=True)


def test_containment_primitives(powergraph):
    assert not set(powergraph.nodes_in('k'))
    assert set(powergraph.nodes_in('p2')) == {'h', 'g', 'f', 'e'}
    assert set(powergraph.powernodes_in('p1')) == {'p3'}


def test_powernode_data(powergraph):
    data = powergraph.powernode_data('p2')
    assert data.size == 4
    assert data.contained == {'h', 'g', 'p4', 'f', 'e'}
    assert data.contained_pnodes == {'p4'}
    assert data.contained_nodes == {'h', 'g', 'f', 'e'}


def test_no_powernode_data(powergraph):
    with pytest.raises(ValueError):
        powergraph.powernode_data('k')


def test_from_bubble_data(powergraph):
    edges, inclusions, roots = powergraph.edges, powergraph.inclusions, powergraph.roots

    assert edges == {'p2': {'k'}, 'k': {'p2', 'p1'}, 'p3': {'p4'}, 'p1': {'k'}, 'p4': {'p3'}}
    assert inclusions == {'p2': {'h', 'g', 'p4'}, 'p3': {'a', 'b'},
                          'k': (), 'p1': {'c', 'd', 'p3'},
                          'p4': {'f', 'e'}, 'a': (), 'b': (), 'c': (),
                          'd': (), 'e': (), 'f': (), 'g': (), 'h': ()}
    assert roots == {'p2', 'k', 'p1'}

    cc, subroots = powergraph.connected_components()
    assert len(cc) == 1
    assert next(iter(cc.values())) == {'p2', 'e', 'd', 'g', 'c', 'b', 'f', 'p3', 'k', 'h', 'a', 'p1', 'p4'}
    assert len(subroots) == 1
    assert len(next(iter(subroots.values()))) == 2
    assert next(iter(subroots.keys())) == next(iter(cc.keys()))


def test_from_oriented_bubble_data(oriented_powergraph):
    powergraph = oriented_powergraph
    edges, inclusions, roots = powergraph.edges, powergraph.inclusions, powergraph.roots

    assert edges == {'k': {'p2', 'p1'}, 'p3': {'p4'}}
    assert inclusions == {'p2': {'h', 'g', 'p4'}, 'p3': {'a', 'b'},
                          'k': (), 'p1': {'c', 'd', 'p3'},
                          'p4': {'f', 'e'}, 'a': (), 'b': (), 'c': (),
                          'd': (), 'e': (), 'f': (), 'g': (), 'h': ()}
    assert roots == {'p2', 'k', 'p1'}

    cc, subroots = powergraph.connected_components()
    assert len(cc) == 1
    assert next(iter(cc.values())) == {'p2', 'e', 'd', 'g', 'c', 'b', 'f', 'p3', 'k', 'h', 'a', 'p1', 'p4'}
    assert len(subroots) == 1
    assert len(next(iter(subroots.values()))) == 2
    assert next(iter(subroots.keys())) == next(iter(cc.keys()))
