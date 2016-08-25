

import validator


def test_validate():
    pass


def test_included():
    inclusions = {'p1': ('p2', 1), 'p2': (3,), 1: (), 3: ()}
    result = tuple(validator.included('p1', inclusions))
    assert len(result) == len(set(result))  # no doublon expected
    assert set(result) == {1, 3, 'p2'}
