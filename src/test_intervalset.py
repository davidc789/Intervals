import pytest
from intervalset import IntervalSet, Interval


@pytest.fixture
def empty_interval_set():
    return IntervalSet()


@pytest.fixture
def interval_set():
    return IntervalSet([2, 7, Interval.greater_than(8), 2, 6, 34])


def test_init(empty_interval_set, interval_set):
    assert len(empty_interval_set) == 0
    assert len(interval_set) == 4


def test_repr(empty_interval_set, interval_set):
    assert repr(empty_interval_set) == "IntervalSet([])"
    assert repr(interval_set) == "IntervalSet([2, 6, 7, (8...), 34])"


def test_add(empty_interval_set):
    empty_interval_set.add(4)
    assert repr(empty_interval_set) == "IntervalSet([4])"
    empty_interval_set.add(Interval(23, 39, lower_closed=False))
    assert repr(empty_interval_set) == "IntervalSet([4, (23..39]])"


def test_remove(interval_set):
    interval_set.remove(2)
    assert repr(interval_set) == "IntervalSet([6, 7, (8...), 34])"
    interval_set.remove(Interval.greater_than(8))
    assert repr(interval_set) == "IntervalSet([2, 6, 7, 34])"


def test_difference_update(interval_set):
    interval_set.difference_update([2, 6])
    assert repr(interval_set) == "IntervalSet([7, (8...), 34])"


def test_clear(interval_set):
    interval_set.clear()
    assert repr(interval_set) == "IntervalSet([])"


def test_update(empty_interval_set):
    empty_interval_set.update([4, Interval(23, 39, lower_closed=False)])
    assert repr(empty_interval_set) == "IntervalSet([4, (23..39]])"


def test_intersection_update(interval_set):
    interval_set.intersection_update([2, 6])
    assert repr(interval_set) == "IntervalSet([2, 6])"


def test_symmetric_difference_update(interval_set):
    interval_set.symmetric_difference_update([2, 6])
    assert repr(interval_set) == "IntervalSet([7, (8...), 34])"


def test_pop(interval_set):
    assert interval_set.pop() == 34
    assert interval_set.pop() == Interval.greater_than(8)
    assert len(interval_set) == 2


def test_delitem(interval_set):
    del interval_set[0]
    assert repr(interval_set) == "IntervalSet([6, 7, (8...), 34])"
    with pytest.raises(IndexError):
        del interval_set[4]


@pytest.fixture
def empty_interval_set():
    return IntervalSet()


@pytest.fixture
def interval_set():
    return IntervalSet([2, 7, Interval.greater_than(8), 2, 6, 34])


def test_init(empty_interval_set, interval_set):
    assert len(empty_interval_set) == 0
    assert len(interval_set) == 4


def test_repr(empty_interval_set, interval_set):
    assert repr(empty_interval_set) == "IntervalSet([])"
    assert repr(interval_set) == "IntervalSet([2, 6, 7, (8...), 34])"


def test_add(empty_interval_set):
    empty_interval_set.add(4)
    assert repr(empty_interval_set) == "IntervalSet([4])"
    empty_interval_set.add(Interval(23, 39, lower_closed=False))
    assert repr(empty_interval_set) == "IntervalSet([4, (23..39]])"


def test_remove(interval_set):
    interval_set.remove(2)
    assert repr(interval_set) == "IntervalSet([6, 7, (8...), 34])"
    interval_set.remove(Interval.greater_than(8))
    assert repr(interval_set) == "IntervalSet([2, 6, 7, 34])"


def test_difference_update(interval_set):
    interval_set.difference_update([2, 6])
    assert repr(interval_set) == "IntervalSet([7, (8...), 34])"


def test_clear(interval_set):
    interval_set.clear()
    assert repr(interval_set) == "IntervalSet([])"


def test_update(empty_interval_set):
    empty_interval_set.update([4, Interval(23, 39, lower_closed=False)])
    assert repr(empty_interval_set) == "IntervalSet([4, (23..39]])"


def test_intersection_update(interval_set):
    interval_set.intersection_update([2, 6])
    assert repr(interval_set) == "IntervalSet([2, 6])"


def test_symmetric_difference_update(interval_set):
    interval_set.symmetric_difference_update([2, 6])
    assert repr(interval_set) == "IntervalSet([7, (8...), 34])"


def test_pop(interval_set):
    assert interval_set.pop() == 34
    assert interval_set.pop() == Interval.greater_than(8)
    assert len(interval_set) == 2


def test_delitem(interval_set):
    del interval_set[0]
    assert repr(interval_set) == "IntervalSet([6, 7, (8...), 34])"
    with pytest.raises(IndexError):
        del interval_set[4]


def test_discard(interval_set):
    interval_set.discard(7)
    assert repr(interval_set) == "IntervalSet([2, 6, (8...), 34])"
    interval_set.discard(5)
    assert repr(interval_set) == "IntervalSet([2, 6, 7, (8...), 34])"


def test_contains(interval_set):
    assert 7 in interval_set
    assert 5 not in interval_set


def test_difference(interval_set):
    result = interval_set.difference([2, 6])
    assert repr(result) == "IntervalSet([(8...), 34])"


def test_intersection(interval_set):
    result = interval_set.intersection([2, 6])
    assert repr(result) == "IntervalSet([2, 6])"


def test_issubset(interval_set):
    assert interval_set.issubset([2, 6, 7, 8, 34])


def test_issuperset(interval_set):
    assert interval_set.issuperset([2, 6])


def test_union(interval_set):
    result = interval_set.union([2, 6, 40])
    assert repr(result) == "IntervalSet([2, 6, 7, (8...), 34, 40])"


def test_copy(interval_set):
    copied_interval_set = interval_set.copy()
    assert copied_interval_set == interval_set
    assert copied_interval_set is not interval_set


def test_len(empty_interval_set, interval_set):
    assert len(empty_interval_set) == 0
    assert len(interval_set) == 4


def test_iter(interval_set):
    assert list(iter(interval_set)) == [2, 6, 7, Interval.greater_than(8)]
