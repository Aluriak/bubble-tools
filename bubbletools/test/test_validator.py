

from bubbletools import validator


def test_validate_empty_pwn():
    data = (
        "EDGE	a	p1	1.0",
        "SET	p1	1.0",
    )
    expected = {
        "INFO 1 lines of type EDGE",
        "INFO 1 lines of type SET",
        "INFO 2 lines of payload",
        "INFO 2 top (power)nodes",
        "INFO 1 connected components",
        "INFO 0 nodes are defined, 1 are used",
        "INFO 1 powernodes are defined, 1 are used",
        "WARNING empty powernode: p1 is defined, but contains nothing",
    }
    result = tuple(validator.validate(data, profiling=True))
    assert len(result) == len(expected)
    assert set(result) == expected



def test_included():
    inclusions = {'p1': ('p2', 1), 'p2': (3,), 1: (), 3: ()}
    result = tuple(validator.included('p1', inclusions))
    assert len(result) == len(set(result))  # no doublon expected
    assert set(result) == {1, 3, 'p2'}
