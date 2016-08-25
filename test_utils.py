

import pytest
import utils


def test_completed_graph():
    assert utils.completed_graph({1: (2, 3), 3: (1, 4, 2)}) == {
        1: {2, 3}, 2: {1, 3}, 3: {1, 2, 4}, 4: {3}
    }


def test_reversed_graph():
    assert utils.reversed_graph({1: (2, 3), 3: (1, 4, 2)}) == {
        2: {1, 3}, 3: {1}, 4: {3}, 1: {3}
    }


def test_line_type():
    lt = utils.line_type

    assert lt('this is non valid bubble') == 'ERROR'

    for number in ('1.0', '0.0', '0.57', '40.99'):
        assert lt('EDGE\tapi-34-c\t"GO829"\t' + number) == 'EDGE'

    assert lt('IN\tab\tcd') == 'IN'
    assert lt('SET\tas\t1.0') == 'SET'
    assert lt('NODE\tabcd') == 'NODE'
    assert lt('') == 'EMPTY'
    assert lt(' # hi !') == 'COMMENT'
    assert lt(' hi !') == 'ERROR'


def test_walk():
    grapha = utils.completed_graph({
        1: {11, 12, 13},
        2: {21, 22},
        21: {211, 212},
    })
    graphb = utils.completed_graph({
        22: {3},  # introduce a loop
        3: {1},
        4: {5},  # introduce a connected component
    })
    cc = {1, 11, 12, 13, 2, 21, 22, 211, 212, 3}
    for start in cc:
        result = tuple(utils.walk(start, (grapha, graphb)))
        assert len(result) == len(set(result))  # no doublon expected
        assert set(result) == cc

    result = tuple(utils.walk(5, (grapha, graphb)))
    assert len(result) == len(set(result))  # no doublon expected
    assert set(result) == {4, 5}


def test_have_cycle():
    assert utils.have_cycle({1: {2, 3}, 2: {3}}) == set()
    assert utils.have_cycle({1: {2}, 2: {3}, 3: {1}}) == {1, 2, 3}
