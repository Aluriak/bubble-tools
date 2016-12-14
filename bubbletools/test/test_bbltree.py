

from bubbletools import bbltree

BBL_DATA_TEST = (
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

def test_from_bubble_data():
    tree = bbltree.BubbleTree.from_bubble_data(BBL_DATA_TEST)
    edges, inclusions, roots = tree.edges, tree.inclusions, tree.roots

    assert edges == {'p2': {'k'}, 'k': {'p2', 'p1'}, 'p3': {'p4'}, 'p1': {'k'}, 'p4': {'p3'}}
    assert inclusions == {'p2': {'h', 'g', 'p4'}, 'p3': {'a', 'b'},
                          'k': (), 'p1': {'c', 'd', 'p3'},
                          'p4': {'f', 'e'}, 'a': (), 'b': (), 'c': (),
                          'd': (), 'e': (), 'f': (), 'g': (), 'h': ()}
    assert roots == {'p2', 'k', 'p1'}

    cc, subroots = tree.connected_components()
    assert len(cc) == 1
    assert next(iter(cc.values())) == {'p2', 'e', 'd', 'g', 'c', 'b', 'f', 'p3', 'k', 'h', 'a', 'p1', 'p4'}
    assert len(subroots) == 1
    assert len(next(iter(subroots.values()))) == 2
    assert next(iter(subroots.keys())) == next(iter(cc.keys()))


def test_from_oriented_bubble_data():
    # same data, but understood as oriented
    tree = bbltree.BubbleTree.from_bubble_data(BBL_DATA_TEST, oriented=True)
    edges, inclusions, roots = tree.edges, tree.inclusions, tree.roots

    assert edges == {'k': {'p2', 'p1'}, 'p3': {'p4'}}
    assert inclusions == {'p2': {'h', 'g', 'p4'}, 'p3': {'a', 'b'},
                          'k': (), 'p1': {'c', 'd', 'p3'},
                          'p4': {'f', 'e'}, 'a': (), 'b': (), 'c': (),
                          'd': (), 'e': (), 'f': (), 'g': (), 'h': ()}
    assert roots == {'p2', 'k', 'p1'}

    cc, subroots = tree.connected_components()
    assert len(cc) == 1
    assert next(iter(cc.values())) == {'p2', 'e', 'd', 'g', 'c', 'b', 'f', 'p3', 'k', 'h', 'a', 'p1', 'p4'}
    assert len(subroots) == 1
    assert len(next(iter(subroots.values()))) == 2
    assert next(iter(subroots.keys())) == next(iter(cc.keys()))
