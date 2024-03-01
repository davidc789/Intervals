import pytest
from interval import Interval
from math import inf


def test_interval_creation():
    r = Interval(-inf, inf)
    assert r.lower_bound == -inf
    assert r.lower_closed 
    assert r.upper_bound == inf
    assert r.upper_closed 


def test_unbounded_intervals():
    r = Interval(upper_bound=62, closed=False)
    assert r.upper_bound == 62
    assert not r.upper_closed

    r = Interval(upper_bound=37)
    assert r.upper_bound == 37
    assert r.upper_closed 

    r = Interval(lower_bound=246)
    assert r.lower_bound == 246
    assert r.lower_closed 

    r = Interval(lower_bound=2468, closed=False)
    assert r.lower_bound == 2468
    assert not r.lower_closed


def test_open_interval():
    r = Interval(25, 28, closed=False)
    assert r.lower_bound == 25
    assert not r.lower_closed
    assert r.upper_bound == 28
    assert not r.upper_closed


def test_closed_interval():
    r = Interval(29, 216)
    assert r.lower_bound == 29
    assert r.lower_closed 
    assert r.upper_bound == 216
    assert r.upper_closed 


def test_single_value_interval():
    r = Interval(82, 82)
    assert r.lower_bound == 82
    assert r.lower_closed 
    assert r.upper_bound == 82
    assert r.upper_closed 


def test_normalized_interval():
    r = Interval(5, 2, lower_closed=False)
    assert r.lower_bound == 2
    assert r.lower_closed 
    assert r.upper_bound == 5
    assert not r.upper_closed


def test_empty_interval():
    with pytest.raises(ValueError):
        r = Interval(5, 5, closed=False)


def test_non_hashable_types():
    with pytest.raises(TypeError):
        r = Interval([], 12)

    with pytest.raises(TypeError):
        r = Interval(12, [])


def test_immutable_intervals():
    r1 = Interval.less_than(5)
    r2 = Interval.less_than(5)
    assert hash(r1) == hash(r2)


def test_interval_comparison():
    r1 = Interval.equal_to(-1)
    r2 = Interval.equal_to(2)
    assert r1 < r2
    assert not (r1 == r2)
    assert not (r1 > r2)

    r3 = Interval.between(2, 5)
    r4 = Interval.between(2, 4)
    assert r3 > r4
    assert not (r3 == r4)

    r5 = Interval.between(2, 5)
    r6 = Interval.between(2, 5)
    assert r5 == r6
    assert r5 >= r6


def test_interval_intersection():
    r1 = Interval.greater_than(3)
    r2 = Interval.greater_than(5)
    result = r1 & r2
    assert result.lower_bound == 5
    assert result.upper_bound == inf
    assert result.lower_closed 
    assert not result.upper_closed


def test_empty_interval_intersection():
    r1 = Interval.greater_than(3)
    r2 = Interval.equal_to(3)
    result = r1 & r2
    assert result.lower_bound == 3
    assert result.upper_bound == 3
    assert not result.lower_closed
    assert not result.upper_closed


def test_point_interval_intersection():
    r1 = Interval.greater_than_or_equal_to(3)
    r2 = Interval.equal_to(3)
    result = r1 & r2
    assert result.lower_bound == 3
    assert result.upper_bound == 3
    assert result.lower_closed 
    assert result.upper_closed 


def test_all_interval_intersection():
    r1 = Interval.all()
    r2 = Interval.all()
    result = r1 & r2
    assert result.lower_bound == -inf
    assert result.upper_bound == inf
    assert result.lower_closed 
    assert result.upper_closed 


def test_general_interval_intersection():
    r1 = Interval.greater_than(3)
    r2 = Interval.less_than(10)
    result = r1 & r2
    assert result.lower_bound == 3
    assert result.upper_bound == 10
    assert result.lower_closed 
    assert not result.upper_closed


def test_empty_interval():
    r = Interval.none()
    assert r.lower_bound == 0
    assert r.upper_bound == 0
    assert not r.lower_closed
    assert not r.upper_closed


def test_all_interval():
    r = Interval.all()
    assert r.lower_bound == -inf
    assert r.upper_bound == inf
    assert r.lower_closed 
    assert r.upper_closed 


def test_between_interval():
    r = Interval.between(2, 4)
    assert r.lower_bound == 2
    assert r.upper_bound == 4
    assert r.lower_closed 
    assert r.upper_closed 

    r = Interval.between(2, 4, False)
    assert r.lower_bound == 2
    assert r.upper_bound == 4
    assert not r.lower_closed
    assert not r.upper_closed


def test_point_interval():
    r = Interval.equal_to(32)
    assert r.lower_bound == 32
    assert r.upper_bound == 32
    assert r.lower_closed 
    assert r.upper_closed 


def test_less_than_interval():
    r = Interval.less_than(32)
    assert r.lower_bound == -inf
    assert r.upper_bound == 32
    assert not r.lower_closed
    assert not r.upper_closed


def test_less_than_or_equal_to_interval():
    r = Interval.less_than_or_equal_to(32)
    assert r.lower_bound == -inf
    assert r.upper_bound == 32
    assert not r.lower_closed
    assert r.upper_closed 


def test_greater_than_interval():
    r = Interval.greater_than(32)
    assert r.lower_bound == 32
    assert r.upper_bound == inf
    assert not r.lower_closed
    assert not r.upper_closed


def test_greater_than_or_equal_to_interval():
    r = Interval.greater_than_or_equal_to(32)
    assert r.lower_bound == 32
    assert r.upper_bound == inf
    assert r.lower_closed 
    assert not r.upper_closed


def test_interval_comes_before():
    r1 = Interval.equal_to(1)
    r2 = Interval.equal_to(4)
    assert r1.comes_before(r2)

    r3 = Interval.less_than_or_equal_to(1)
    r4 = Interval.equal_to(4)
    assert r3.comes_before(r4)

    r5 = Interval.less_than_or_equal_to(5)
    r6 = Interval.less_than(5)
    assert r5.comes_before(r6)
