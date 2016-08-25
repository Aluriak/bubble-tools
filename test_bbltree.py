

import bbltree

def test_from_bubble_data():
    tree = bbltree.from_bubble_data((
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
    ))
    edges, inclusions, roots = tree

    assert edges == {'p2': {'k'}, 'k': {'p2', 'p1'}, 'p3': {'p4'}, 'p1': {'k'}, 'p4': {'p3'}}
    assert inclusions == {'p2': {'h', 'g', 'p4'}, 'p3': {'a', 'b'}, 'k': (), 'p1': {'c', 'd', 'p3'}, 'p4': {'f', 'e'}}
    assert roots == {'p2', 'k', 'p1'}

    cc, subroots = bbltree.connected_components(tree)
    assert len(cc) == 1
    assert next(iter(cc.values())) == {'p2', 'e', 'd', 'g', 'c', 'b', 'f', 'p3', 'k', 'h', 'a', 'p1', 'p4'}
    assert len(subroots) == 1
    assert len(next(iter(subroots.values()))) == 2
    assert next(iter(subroots.keys())) == next(iter(cc.keys()))
