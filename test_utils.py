

import pytest
import utils


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
