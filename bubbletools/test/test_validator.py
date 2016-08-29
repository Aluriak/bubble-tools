

from bubbletools import validator


def test_validate_loop():
    data = (
        "IN	a	p1",
        "IN	p1	p2",
        "IN	p2	p3",
        "IN	p3	p1",
    )
    expected = {
        "INFO 4 lines of type IN",
        "INFO 4 lines of payload",
        "INFO 0 top (power)nodes",
        "INFO 0 connected components",
        "INFO 0 nodes are defined, 1 are used",
        "INFO 0 powernodes are defined, 3 are used",
        "ERROR overlapping powernodes",
        "ERROR overlapping powernodes",
        "ERROR overlapping powernodes",
        "WARNING singleton powernode",
        "WARNING singleton powernode",
        "ERROR inclusion cycle: the following 4 nodes are involved",
    }
    results = tuple(validator.validate(data, profiling=True))
    # delete the mutable part (order within the sets)
    results = {result[:result.rfind(':')] if ':' in result else result
               for result in results}
    assert set(results) == expected


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
