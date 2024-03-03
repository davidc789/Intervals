"""Provides the Interval and IntervalSet classes

The interval module provides the Interval and IntervalSet data types.   
Intervals describe continuous ranges that can be open, closed, half-open,
or infinite.  IntervalSets contain zero to many disjoint sets of 
Intervals.

Intervals don't have to pertain to numbers.  They can contain any data 
that is comparable via the Python operators <, <=, ==, >=, and >.  Here's 
an example of how strings can be used with Intervals:

>>> volume1 = Interval.between("A", "Foe")
>>> volume2 = Interval.between("Fog", "McAfee")
>>> volume3 = Interval.between("McDonalds", "Space")
>>> volume4 = Interval.between("Spade", "Zygote")
>>> encyclopedia = IntervalSet([volume1, volume2, volume3, volume4])
>>> mySet = IntervalSet([volume1, volume3, volume4])
>>> "Meteor" in encyclopedia
True
>>> "Goose" in encyclopedia
True
>>> "Goose" in mySet
False
>>> volume2 in (encyclopedia ^ mySet)
True

Here's an example of how times can be used with Intervals:

>>> officeHours = IntervalSet.between("08:00", "17:00")
>>> myLunch = IntervalSet.between("11:30", "12:30")
>>> myHours = IntervalSet.between("08:30", "19:30") - myLunch
>>> myHours.issubset(officeHours)
False
>>> "12:00" in myHours
False
>>> "15:30" in myHours
True
>>> inOffice = officeHours & myHours
>>> print inOffice
['08:30'..'11:30'),('12:30'..'17:00']
>>> overtime = myHours - officeHours
>>> print overtime
('17:00'..'19:30']
"""

import copy

from interval import Interval, SupportsRichComparison
from sortedcontainers import SortedList
from typing import Generic, TypeVar

T = TypeVar("T", bound=Interval[SupportsRichComparison])


class BaseIntervalSet(object):
    """Base class for IntervalSet and FrozenIntervalSet."""

    def __init__(self, items=()):
        """Initializes a BaseIntervalSet

        This function initializes an IntervalSet.  It takes an iterable
        object, such as a set, list, or generator.  The elements returned 
        by the iterator are interpreted as intervals for Interval objects 
        and discrete values for all other values.

        If no parameters are provided, then an empty IntervalSet is 
        constructed.

        >>> print IntervalSet() # An empty set
        <Empty>

        Interval objects arguments are added directly to the IntervalSet.

        >>> print IntervalSet([Interval(4, 6, lower_closed=False)])
        (4..6]
        >>> print IntervalSet([Interval.less_than_or_equal_to(2)])
        (...2]

        Each non-Interval value of an iterator is added as a discrete 
        value.

        >>> print IntervalSet(set([3, 7, 2, 1]))
        1,2,3,7
        >>> print IntervalSet(["Bob", "Fred", "Mary"])
        'Bob','Fred','Mary'
        >>> print IntervalSet(range(10))
        0,1,2,3,4,5,6,7,8,9
        >>> print IntervalSet(
        ...   Interval.between(l, u) for l, u in [(10, 20), (30, 40)])
        [10..20],[30..40]
        """
        self.intervals = SortedList()
        for i in items:
            self._add(i)

    def __len__(self):
        """Returns the number of intervals contained in the object

        >>> len(IntervalSet.empty())
        0
        >>> len(IntervalSet.all())
        1
        >>> len(IntervalSet([2, 6, 34]))
        3
        >>> len(IntervalSet.greater_than(0))
        1
        >>> nonempty = IntervalSet([3])
        >>> if IntervalSet.empty():
        ...     print "Non-empty"
        >>> if nonempty:
        ...     print "Non-empty"
        Non-empty
        """
        return len(self.intervals)

    def __str__(self):
        """Returns a string representation of the object

        This function shows a string representation of an IntervalSet.  
        The string is shown sorted, with all intervals normalized.

        >>> print IntervalSet()
        <Empty>
        >>> print IntervalSet([62])
        62
        >>> print IntervalSet([62, 56])
        56,62
        >>> print IntervalSet([23, Interval(26, 32, upper_closed=False)])
        23,[26..32)
        >>> print IntervalSet.less_than(3) + IntervalSet.greater_than(3)
        (...3),(3...)
        >>> print IntervalSet([Interval.less_than_or_equal_to(6)])
        (...6]
        """
        if len(self.intervals) == 0:
            return "<Empty>"
        else:
            return ",".join(str(r) for r in self.intervals)

    def __getitem__(self, index):
        """Gets the interval at the given index

        Unlike sets, which do not have ordering, BaseIntervalSets do.  Therefore,
        indexing was implemented.  Intervals are stored in order, starting with
        that with the left-most lower bound to that with the right-most.

        >>> IntervalSet()[0]
        Traceback (most recent call last):
            ...
        IndexError: Index is out of range
        >>> interval = IntervalSet.greater_than(5)
        >>> print interval[0]
        (5...)
        >>> print interval[1]
        Traceback (most recent call last):
            ...
        IndexError: Index is out of range
        >>> print interval[-1]
        (5...)
        >>> interval = IntervalSet([3, 6])
        >>> print interval[1]
        6
        >>> print interval[0]
        3
        >>> print interval[2]
        Traceback (most recent call last):
            ...
        IndexError: Index is out of range
        """
        try:
            return self.intervals[index]
        except IndexError:
            raise IndexError("Index is out of range")

    def __iter__(self):
        """Returns an iterator to iterate through the intervals

        Unlike sets, which do not have ordering, BaseIntervalSets do.  Therefore,
        iterating was implemented.  Intervals are stored in order, starting with
        that with the left-most lower bound to that with the right-most.

        >>> for i in IntervalSet():
        ...     print i
        ...
        >>> for i in IntervalSet.between(3, 5):
        ...     print i
        ...
        [3..5]
        >>> for i in IntervalSet([2, 5, 3]):
        ...     print i
        ...
        2
        3
        5
        """
        return self.intervals.__iter__()

    def lower_bound(self):
        """Returns the lower boundary of the BaseIntervalSet

        >>> IntervalSet([Interval.between(4, 6), 2, 12]).lower_bound()
        2
        >>> IntervalSet().lower_bound()
        Traceback (most recent call last):
            ...
        IndexError: The BaseIntervalSet is empty
        >>> IntervalSet.all().lower_bound()
        -Inf
        """
        if len(self.intervals) > 0:
            return self.intervals[0].lower_bound
        raise IndexError("The BaseIntervalSet is empty")

    def upper_bound(self):
        """Returns the upper boundary of the BaseIntervalSet

        >>> IntervalSet([Interval.between(4, 6), 2, 12]).upper_bound()
        12
        >>> IntervalSet().upper_bound()
        Traceback (most recent call last):
            ...
        IndexError: The BaseIntervalSet is empty
        >>> IntervalSet.all().upper_bound()
        Inf
        """
        if len(self.intervals) > 0:
            return self.intervals[-1].upper_bound
        raise IndexError("The BaseIntervalSet is empty")

    def lower_closed(self):
        """Returns a boolean telling whether the lower bound is closed or not

        >>> IntervalSet([Interval.between(4, 6), 2, 12]).lower_closed()
        True
        >>> IntervalSet().lower_closed()
        Traceback (most recent call last):
            ...
        IndexError: The BaseIntervalSet is empty
        >>> IntervalSet.all().lower_closed()
        False
        """
        if len(self.intervals) > 0:
            return self.intervals[0].lower_closed
        raise IndexError("The BaseIntervalSet is empty")

    def upper_closed(self):
        """Returns a boolean telling whether the upper bound is closed or not

        >>> IntervalSet([Interval.between(4, 6), 2, 12]).upper_closed()
        True
        >>> IntervalSet().upper_closed()
        Traceback (most recent call last):
            ...
        IndexError: The BaseIntervalSet is empty
        >>> IntervalSet.all().upper_closed()
        False
        """
        if len(self.intervals) > 0:
            return self.intervals[0].upper_closed
        raise IndexError("The BaseIntervalSet is empty")

    def bounds(self):
        """Returns an interval that encompasses the entire BaseIntervalSet

        >>> print IntervalSet([Interval.between(4, 6), 2, 12]).bounds()
        [2..12]
        >>> print IntervalSet().bounds()
        <Empty>
        >>> print IntervalSet.all().bounds()
        (...)
        """
        if len(self.intervals) == 0:
            return Interval.none()

        return Interval(
            self.lower_bound(), self.upper_bound(),
            lower_closed=self.lower_closed(),
            upper_closed=self.upper_closed()
        )

    def issubset(self, other):
        """Tells if the given object is a subset of the object

        Returns true if self is a subset of other.  other can be any 
        iterable object.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero.issubset(positives)
        False
        >>> zero.issubset(naturals)
        True
        >>> positives.issubset(zero)
        False
        >>> r.issubset(zero)
        False
        >>> r.issubset(positives)
        True
        >>> positives.issubset(r)
        False
        >>> negatives.issubset(IntervalSet.all())
        True
        >>> r2.issubset(negatives)
        True
        >>> negatives.issubset(positives)
        False
        >>> zero.issubset([0, 1, 2, 3])
        True
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self <= operand

    def issuperset(self, other):
        """Tells whether the given object is a superset of the object

        Returns true if self is a superset of other.  other can be any
        iterable object.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero.issuperset(positives)
        False
        >>> zero.issuperset(naturals)
        False
        >>> positives.issuperset(zero)
        False
        >>> r.issuperset(zero)
        False
        >>> r.issuperset(positives)
        False
        >>> positives.issuperset(r)
        True
        >>> negatives.issuperset(IntervalSet.all())
        False
        >>> r2.issuperset(negatives)
        False
        >>> negatives.issuperset(positives)
        False
        >>> negatives.issuperset([-2, -632])
        True
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self >= operand

    def __contains__(self, obj):
        """Tells whether the BaseIntervalSet contains the given value

        Returns True if obj is contained in self.  obj can be either a 
        discrete value, a sequence, or an Interval.

        >>> some = IntervalSet([
        ...   2, 8, Interval(12, 17, upper_closed=False),
        ...   Interval.greater_than(17)])
        >>> all = IntervalSet.all()
        >>> empty = IntervalSet.empty()
        >>> 17 in empty
        False
        >>> 17 in all
        True
        >>> 17 in some
        False
        >>> r = Interval(100, 400, upper_closed=False)
        >>> r in empty
        False
        >>> r in all
        True
        >>> r in some
        True
        """
        result = False
        for r in self.intervals:
            if obj in r:
                result = True
                break
        return result

    def __add__(self, other):
        """Returns the union of two IntervalSets

        >>> empty     = IntervalSet()
        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> print evens + positives
        -8,-6,-4,-2,[0...)
        >>> print negatives + zero
        (...0]
        >>> print empty + negatives
        (...0)
        >>> print empty + naturals
        [0...)
        >>> print nonzero + evens
        (...)
        """
        return self.__or__(other)

    def __sub__(self, other):
        """Subtracts intervals in the given object from the object and returns
        the result

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> all       = IntervalSet.all()
        >>> print evens - nonzero
        0
        >>> print empty - naturals
        <Empty>
        >>> print zero - naturals
        <Empty>
        >>> print positives - zero
        (0...)
        >>> print naturals - negatives
        [0...)
        >>> print all - zero
        (...0),(0...)
        >>> all - zero == nonzero
        True
        >>> naturals - [0]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for -: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            result = IntervalSet(self)
            for j in other.intervals:
                temp = IntervalSet()
                for i in result.intervals:
                    if i.overlaps(j):
                        if i in j:
                            pass
                        elif j in i:
                            if j.lower_bound != None:
                                temp.add(Interval(
                                    i.lower_bound, j.lower_bound,
                                    lower_closed=i.lower_closed,
                                    upper_closed=not j.lower_closed))
                            if j.upper_bound != None:
                                temp.add(Interval(
                                    j.upper_bound, i.upper_bound,
                                    lower_closed=not j.upper_closed,
                                    upper_closed=i.upper_closed))
                        elif j.comes_before(i):
                            temp.add(Interval(
                                j.upper_bound, i.upper_bound,
                                lower_closed=not j.upper_closed,
                                upper_closed=i.upper_closed))
                        else:
                            temp.add(Interval(
                                i.lower_bound, j.lower_bound,
                                lower_closed=i.lower_closed,
                                upper_closed=not j.lower_closed))
                    else:
                        temp.add(copy.deepcopy(i))
                result = temp
        else:
            raise TypeError(
                "unsupported operand type(s) for -: expected BaseIntervalSet")
        return self.__class__(result)

    def difference(self, other):
        """Returns the difference between the object and the given object

        Returns all values of self minus all matching values in other.  It
        is identical to the - operator, only it accepts any iterable as 
        the operand.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> all       = IntervalSet.all()
        >>> print evens.difference(nonzero)
        0
        >>> print empty.difference(naturals)
        <Empty>
        >>> print zero.difference(naturals)
        <Empty>
        >>> print positives.difference(zero)
        (0...)
        >>> print naturals.difference(negatives)
        [0...)
        >>> print all.difference(zero)
        (...0),(0...)
        >>> all.difference(zero) == nonzero
        True
        >>> naturals.difference([0]) == positives
        True
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self - operand

    def __and__(self, other):
        """Returns the intersection of self and other.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> print naturals and naturals
        [0...)
        >>> print evens & zero
        0
        >>> print negatives & zero
        <Empty>
        >>> print nonzero & positives
        (0...)
        >>> print empty & zero
        <Empty>
        >>> positives & [0]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for &: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            result = IntervalSet()
            for j in other.intervals:
                for i in self.intervals:
                    if i.overlaps(j):
                        if i in j:
                            result.add(copy.deepcopy(i))
                        elif j in i:
                            result.add(copy.deepcopy(j))
                        elif j.comes_before(i):
                            result.add(Interval(
                                i.lower_bound, j.upper_bound,
                                lower_closed=i.lower_closed,
                                upper_closed=j.upper_closed))
                        else:
                            result.add(Interval(
                                j.lower_bound, i.upper_bound,
                                lower_closed=j.lower_closed,
                                upper_closed=i.upper_closed))
            # Convert IntervalSet to correct type
            result = self.__class__(result)
        else:
            raise TypeError(
                "unsupported operand type(s) for &: expected BaseIntervalSet")
        return result

    def intersection(self, other):
        """Returns the intersection between the object and the given value

        This function returns the intersection of self and other.  It is
        identical to the & operator, except this function accepts any 
        iterable as an operand, and & accepts only another 
        BaseIntervalSet.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> print naturals.intersection(naturals)
        [0...)
        >>> print evens.intersection(zero)
        0
        >>> print negatives.intersection(zero)
        <Empty>
        >>> print nonzero.intersection(positives)
        (0...)
        >>> print empty.intersection(zero)
        <Empty>
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self & operand

    def __or__(self, other):
        """Returns the union of two IntervalSets.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> all       = IntervalSet.all()
        >>> print evens | positives
        -8,-6,-4,-2,[0...)
        >>> print negatives | zero
        (...0]
        >>> print empty | negatives
        (...0)
        >>> print empty | naturals
        [0...)
        >>> print nonzero | evens
        (...)
        >>> print negatives | range(5)
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for |: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            union = IntervalSet(self)
            for r in other.intervals:
                union.add(r)
        else:
            raise TypeError(
                "unsupported operand type(s) for |: expected BaseIntervalSet")
        return self.__class__(union)

    def union(self, other):
        """Returns the union of the given value with the object

        This function returns the union of a BaseIntervalSet and an 
        iterable object.  It is identical to the | operator, except that 
        | only accepts a BaseIntervalSet operand and union accepts any 
        iterable.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> all       = IntervalSet.all()
        >>> print evens.union(positives)
        -8,-6,-4,-2,[0...)
        >>> print negatives.union(zero)
        (...0]
        >>> print empty.union(negatives)
        (...0)
        >>> print empty.union(naturals)
        [0...)
        >>> print nonzero.union(evens)
        (...)
        >>> print negatives.union(range(5))
        (...0],1,2,3,4
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self | operand

    def __xor__(self, other):
        """Returns the exclusive or of two IntervalSets.  

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> print nonzero ^ naturals
        (...0]
        >>> print zero ^ negatives
        (...0]
        >>> print positives ^ empty
        (0...)
        >>> print evens ^ zero
        -8,-6,-4,-2,2,4,6,8
        >>> negatives ^ [0]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for ^: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            return (self | other) - (self & other)
        else:
            raise TypeError(
                "unsupported operand type(s) for ^: expected BaseIntervalSet")

    def symmetric_difference(self, other):
        """Returns the exclusive or of the given value with the object

        This function returns the exclusive or of two IntervalSets.  
        It is identical to the ^ operator, except it accepts any iterable
        object for the operand.

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> empty     = IntervalSet.empty()
        >>> print nonzero.symmetric_difference(naturals)
        (...0]
        >>> print zero.symmetric_difference(negatives)
        (...0]
        >>> print positives.symmetric_difference(empty)
        (0...)
        >>> print evens.symmetric_difference(zero)
        -8,-6,-4,-2,2,4,6,8
        >>> print evens.symmetric_difference(range(0, 9, 2))
        -8,-6,-4,-2
        """
        if isinstance(other, BaseIntervalSet):
            operand = other
        else:
            operand = self.__class__(other)
        return self ^ operand

    def __invert__(self):
        """Returns the disjoint set of self

        >>> negatives = IntervalSet.less_than(0)
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals  = IntervalSet.greater_than_or_equal_to(0)
        >>> evens     = IntervalSet([-8, -6, -4, -2, 0, 2, 4, 6, 8])
        >>> zero      = IntervalSet([0])
        >>> nonzero   = IntervalSet.not_equal_to(0)
        >>> print ~(IntervalSet.empty())
        (...)
        >>> ~negatives == naturals
        True
        >>> print ~positives
        (...0]
        >>> ~naturals == negatives
        True
        >>> print ~evens
        (...-8),(-8..-6),(-6..-4),(-4..-2),(-2..0),(0..2),(2..4),(4..6),(6..8),(8...)
        >>> ~zero == nonzero
        True
        >>> ~nonzero == zero
        True
        """
        return self.__class__.all() - self

    def __cmp__(self, other):
        """Compares two BaseIntervalSets

        Like set, raises a TypeError when invoked.
        >>> IntervalSet().__cmp__(IntervalSet())
        Traceback (most recent call last):
        ...
        TypeError: cannot compare BaseIntervalSets using cmp()
        """
        raise TypeError("cannot compare BaseIntervalSets using cmp()")

    def __eq__(self, other):
        """Tests if two BaseIntervalSets are equivalent

        Two IntervalSets are identical if they contain the exact same 
        sets.

        >>> IntervalSet([4]) == IntervalSet([1])
        False
        >>> IntervalSet([5]) == IntervalSet([5])
        True
        >>> s1 = IntervalSet.between(4, 7)
        >>> s2 = IntervalSet([Interval(4, 7, upper_closed=False)])
        >>> s1 == s2
        False
        >>> s2.add(7)
        >>> s1 == s2
        True
        >>> s1.clear()
        >>> s1 == IntervalSet.empty()
        True

        An IntervalSet, when compared to a non-BaseIntervalSet, yields 
        False

        >>> s1 == [0, 2, 7, 4]
        False
        >>> IntervalSet([3, 4, 5]) == set([3, 4, 5])
        False
        >>> IntervalSet([3, 4, 5]) == [3, 4, 5, 3]
        False
        >>> IntervalSet([3]) == 3
        False
        """
        if isinstance(other, BaseIntervalSet):
            # If len(other) != len(operand), then that means extra objects were
            # discarded from other.  Thus it can't be equal to any sort of set.
            result = self.issubset(other) and other.issubset(self)
        else:
            result = False
        return result

    def __ne__(self, other):
        """Tests if two BaseIntervalSets are not equivalent

        Two IntervalSets are not identical if they contain different 
        values or Intervals.

        >>> IntervalSet([4]) != IntervalSet([1])
        True
        >>> IntervalSet([5]) != IntervalSet([5])
        False
        >>> s1 = IntervalSet.between(4, 7)
        >>> s2 = IntervalSet([Interval(4, 7, upper_closed=False)])
        >>> s1 != s2
        True
        >>> s2.add(7)
        >>> s1 != s2
        False
        >>> s1.clear()
        >>> s1 != IntervalSet.empty()
        False

        An IntervalSet can also be compared to any other value.  The result
        is always True.

        >>> s1 != [0, 2, 7, 4]
        True
        >>> IntervalSet([3, 4, 5]) != set([3, 4, 5])
        True
        >>> IntervalSet([3, 4, 5]) != [3, 4, 5, 3]
        True
        """
        return not (self == other)

    def __lt__(self, other):
        """Tests if the given operand is a subset of the object

        To test if a set is a subset that's not equal to another, you can 
        use the < operator.  I don't like this, personally, but in my 
        attempt to implement a set-like object, I've duplicated this 
        functionality.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero < positives
        False
        >>> zero < naturals
        True
        >>> positives < zero
        False
        >>> r < zero
        False
        >>> r < positives
        True
        >>> positives < r
        False
        >>> negatives < IntervalSet.all()
        True
        >>> r2 < negatives
        True
        >>> negatives < positives
        False
        >>> zero < [0, 2, 6, 7]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for <: expected BaseIntervalSet
        >>> positives < positives
        False
        """
        if isinstance(other, BaseIntervalSet):
            return (self <= other and not self == other)
        else:
            raise TypeError(
                "unsupported operand type(s) for <: expected BaseIntervalSet")

    def __le__(self, other):
        """Tests if the given operand is a subset or is equal to the object

        To test if a set is a subset of another, you can use the <= 
        operator.  I don't like this, personally, but in my attempt
        to implement a set-like object, I've duplicated this 
        functionality.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero <= positives
        False
        >>> zero <= naturals
        True
        >>> positives <= zero
        False
        >>> r <= zero
        False
        >>> r <= positives
        True
        >>> positives <= r
        False
        >>> negatives <= IntervalSet.all()
        True
        >>> r2 <= negatives
        True
        >>> negatives <= positives
        False
        >>> zero <= [0, 2, 6, 7]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for <=: expected BaseIntervalSet
        >>> positives <= positives
        True
        """
        if isinstance(other, BaseIntervalSet):
            result = True
            for i in self.intervals:
                if i not in other:
                    result = False
                    break
        else:
            raise TypeError(
                "unsupported operand type(s) for <=: expected BaseIntervalSet")
        return result

    def __ge__(self, other):
        """Tests if the given operand is a superset or is equal to the object

        To test if a set is a superset of another, you can use the >=
        operator.  I don't like this, personally, but in my attempt
        to implement a set-like object, I've duplicated this 
        functionality.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero >= positives
        False
        >>> zero >= naturals
        False
        >>> positives >= zero
        False
        >>> r >= zero
        False
        >>> r >= positives
        False
        >>> positives >= r
        True
        >>> negatives >= IntervalSet.all()
        False
        >>> r2 >= negatives
        False
        >>> negatives >= positives
        False
        >>> negatives >= [-2, -63]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for >=: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            result = True
            for i in other.intervals:
                if i not in self:
                    result = False
                    break
        else:
            raise TypeError(
                "unsupported operand type(s) for >=: expected BaseIntervalSet")
        return result

    def __gt__(self, other):
        """Tests if the given operand is a superset of the object

        To test if a set is a superset of another, but not equal to it,
        you can use the > operator.  I don't like this, personally, but in 
        my attempt to implement a set-like object, I've duplicated this 
        functionality.

        >>> zero = IntervalSet([0])
        >>> positives = IntervalSet.greater_than(0)
        >>> naturals = IntervalSet.greater_than_or_equal_to(0)
        >>> negatives = IntervalSet.less_than(0)
        >>> r = IntervalSet.between(3, 6)
        >>> r2 = IntervalSet.between(-8, -2)
        >>> zero > positives
        False
        >>> zero > naturals
        False
        >>> positives > zero
        False
        >>> r > zero
        False
        >>> r > positives
        False
        >>> positives > r
        True
        >>> negatives > IntervalSet.all()
        False
        >>> r2 > negatives
        False
        >>> negatives > positives
        False
        >>> positives > positives
        False
        >>> negatives > [-2, -63]
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for >: expected BaseIntervalSet
        """
        if isinstance(other, BaseIntervalSet):
            return self >= other and not self == other
        else:
            raise TypeError(
                "unsupported operand type(s) for >: expected BaseIntervalSet")

    def _add(self, obj):
        """Appends an Interval or BaseIntervalSet to the object"""
        if isinstance(obj, Interval):
            r = obj
        else:
            r = Interval.equal_to(obj)

        # Don't bother appending an empty Interval
        if r:
            # If r continuously joins with any of the other
            newIntervals = []
            for i in self.intervals:
                if i.overlaps(r) or i.adjacent_to(r):
                    r = r.join(i)
                else:
                    newIntervals.append(i)
            newIntervals.append(r)
            self.intervals = newIntervals
            self.intervals.sort()

    def copy(self):
        """Returns a copy of the object

        >>> s = IntervalSet(
        ...   [7, 2, 3, 2, 6, 2, Interval.greater_than(3)])
        >>> s2 = s.copy()
        >>> s == s2
        True
        >>> s = FrozenIntervalSet(
        ...   [7, 2, 3, 2, 6, 2, Interval.greater_than(3)])
        >>> s2 = s.copy()
        >>> s == s2
        True
        """
        return copy.copy(self)

    @classmethod
    def less_than(cls, n):
        """Returns an IntervalSet containing values less than the given value

        >>> print IntervalSet.less_than(0)
        (...0)
        >>> print IntervalSet.less_than(-23)
        (...-23)
        """
        return cls([Interval.less_than(n)])

    @classmethod
    def less_than_or_equal_to(cls, n, closed=False):
        """Returns an IntervalSet containing values less than or equal to the 
        given value

        >>> print IntervalSet.less_than_or_equal_to(0)
        (...0]
        >>> print IntervalSet.less_than_or_equal_to(-23)
        (...-23]
        """
        return cls([Interval.less_than_or_equal_to(n)])

    @classmethod
    def greater_than(cls, n):
        """Returns an IntervalSet containing values greater than the given value

        >>> print IntervalSet.greater_than(0)
        (0...)
        >>> print IntervalSet.greater_than(-23)
        (-23...)
        """
        return cls([Interval.greater_than(n)])

    @classmethod
    def greater_than_or_equal_to(cls, n):
        """Returns an IntervalSet containing values greater than or equal to 
        the given value

        >>> print IntervalSet.greater_than_or_equal_to(0)
        [0...)
        >>> print IntervalSet.greater_than_or_equal_to(-23)
        [-23...)
        """
        return cls([Interval.greater_than_or_equal_to(n)])

    @classmethod
    def not_equal_to(cls, n):
        """Returns an IntervalSet of all values not equal to n

        >>> print IntervalSet.not_equal_to(0)
        (...0),(0...)
        >>> print IntervalSet.not_equal_to(-23)
        (...-23),(-23...)
        """
        return cls([Interval.less_than(n), Interval.greater_than(n)])

    @classmethod
    def between(cls, a, b, closed=True):
        """Returns an IntervalSet of all values between a and b.

        If closed is True, then the endpoints are included; otherwise, they 
        aren't.

        >>> print IntervalSet.between(0, 100)
        [0..100]
        >>> print IntervalSet.between(-1, 1)
        [-1..1]
        """
        return cls([Interval.between(a, b, closed)])

    @classmethod
    def all(cls):
        """Returns an interval set containing all values

        >>> print IntervalSet.all()
        (...)
        """
        return cls([Interval.all()])

    @classmethod
    def empty(cls):
        """Returns an interval set containing no values.

        >>> print IntervalSet.empty()
        <Empty>
        """
        return cls()


class IntervalSet(BaseIntervalSet):
    """The mutable version of BaseIntervalSet

    IntervalSet is a class representing sets of continuous values, as 
    opposed to a discrete set, which is already implemented by the set 
    type in Python.

    IntervalSets can be bounded, unbounded, and non-continuous.  They were 
    designed to accomodate any sort of mathematical set dealing with
    continuous values.  This will usually mean numbers, but any Python 
    type that has valid comparison operations can be used in an 
    IntervalSet.

    Because IntervalSets are mutable, it cannot be used as a dictionary 
    key.

    >>> {IntervalSet([3, 66]) : 52}
    Traceback (most recent call last):
        ...
    TypeError: unhashable instance
    """

    def __init__(self, items=()):
        "Initializes the IntervalSet"
        BaseIntervalSet.__init__(self, items)

    def __repr__(self):
        """Returns an evaluable representation of the object

        >>> IntervalSet([Interval()])
        IntervalSet([Interval(-Inf, Inf, lower_closed=False, upper_closed=False)])
        >>> IntervalSet()
        IntervalSet([])
        >>> IntervalSet([2, 4])
        IntervalSet([Interval(2, 2, lower_closed=True, upper_closed=True), Interval(4, 4, lower_closed=True, upper_closed=True)])
        """
        return "IntervalSet([%s])" % (
            ", ".join(repr(i) for i in self.intervals),)

    def __delitem__(self, index):
        """Removes the interval at the given index from the IntervalSet

        >>> interval = IntervalSet()
        >>> del interval[0]
        Traceback (most recent call last):
            ...
        IndexError: Index is out of range
        >>> interval = IntervalSet.between(-12, 2)
        >>> del interval[1]
        Traceback (most recent call last):
            ...
        IndexError: Index is out of range
        >>> len(interval)
        1
        >>> del interval[0]
        >>> len(interval)
        0
        >>> interval = IntervalSet([2, 7, -2])
        >>> len(interval)
        3
        >>> del interval[1]
        >>> len(interval)
        2
        >>> print interval
        -2,7
        """
        try:
            del self.intervals[index]
        except IndexError:
            raise IndexError("Index is out of range")

    def add(self, obj):
        """Adds an Interval or discrete value to the object

        >>> r = IntervalSet()
        >>> r.add(4)
        >>> print r
        4
        >>> r.add(Interval(23, 39, lower_closed=False))
        >>> print r
        4,(23..39]
        >>> r.add(Interval.less_than(25))
        >>> print r
        (...39]
        """
        BaseIntervalSet._add(self, obj)

    def remove(self, obj):
        """Removes a value from the object

        This function removes an Interval, discrete value, or set 
        from an IntervalSet.  If the object is not in the set, a KeyError
        is raised.

        >>> r = IntervalSet.all()
        >>> r.remove(4)
        >>> print r
        (...4),(4...)
        >>> r.remove(Interval(23, 39, lower_closed=False))
        >>> print r
        (...4),(4..23],(39...)
        >>> r.remove(Interval.less_than(25))
        Traceback (most recent call last):
            ...
        KeyError: '(...25)'
        """
        if obj in self:
            self.discard(obj)
        else:
            raise KeyError(str(obj))

    def discard(self, obj):
        """Removes a value from the object

        This function removes an Interval or discrete value from an
        IntervalSet.

        >>> r = IntervalSet.all()
        >>> r.discard(4)
        >>> print r
        (...4),(4...)
        >>> r.discard(Interval(23, 39, lower_closed=False))
        >>> print r
        (...4),(4..23],(39...)
        >>> r.discard(Interval.less_than(25))
        >>> print r
        (39...)
        """
        diff = self - IntervalSet([obj])
        self.intervals = diff.intervals

    def difference_update(self, other):
        """Removes any elements in the given value from the object

        This function removes the elements in other from self.  other can
        be any iterable object.

        >>> r = IntervalSet.all()
        >>> r.difference_update([4])
        >>> print r
        (...4),(4...)
        >>> r.difference_update(
        ...   IntervalSet([Interval(23, 39, lower_closed=False)]))
        >>> print r
        (...4),(4..23],(39...)
        >>> r.difference_update(IntervalSet.less_than(25))
        >>> print r
        (39...)
        >>> r2 = IntervalSet.all()
        >>> r.difference_update(r2)
        >>> print r
        <Empty>
        """
        diff = self.difference(other)
        self.intervals = diff.intervals

    def clear(self):
        """Removes all Intervals from the object

        >>> s = IntervalSet([2, 7, Interval.greater_than(8), 2, 6, 34])
        >>> print s
        2,6,7,(8...)
        >>> s.clear()
        >>> print s
        <Empty>
        """
        self.intervals = []

    def update(self, other):
        """Adds elements from the given value to the object

        Adds elements from other to self.  other can be any iterable 
        object.

        >>> r = IntervalSet()
        >>> r.update([4])
        >>> print r
        4
        >>> r.update(IntervalSet([Interval(23, 39, lower_closed=False)]))
        >>> print r
        4,(23..39]
        >>> r.update(IntervalSet.less_than(25))
        >>> print r
        (...39]
        >>> r2 = IntervalSet.all()
        >>> r.update(r2)
        >>> print r
        (...)
        """
        union = self.union(other)
        self.intervals = union.intervals

    def intersection_update(self, other):
        """Removes values not found in the parameter

        Removes elements not found in other.  other can be any iterable
        object

        >>> r = IntervalSet.all()
        >>> r.intersection_update([4])
        >>> print r
        4
        >>> r = IntervalSet.all()
        >>> r.intersection_update(
        ...   IntervalSet([Interval(23, 39, lower_closed=False)]))
        >>> print r
        (23..39]
        >>> r.intersection_update(IntervalSet.less_than(25))
        >>> print r
        (23..25)
        >>> r2 = IntervalSet.all()
        >>> r.intersection_update(r2)
        >>> print r
        (23..25)
        """
        intersection = self.intersection(other)
        self.intervals = intersection.intervals

    def symmetric_difference_update(self, other):
        """Updates the object as though doing an xor with the parameter

        Removes elements found in other and adds elements in other that 
        are not in self.  other can be any iterable object.

        >>> r = IntervalSet.empty()
        >>> r.symmetric_difference_update([4])
        >>> print r
        4
        >>> r.symmetric_difference_update(
        ...   IntervalSet([Interval(23, 39, lower_closed=False)]))
        >>> print r
        4,(23..39]
        >>> r.symmetric_difference_update(IntervalSet.less_than(25))
        >>> print r
        (...4),(4..23],[25..39]
        >>> r2 = IntervalSet.all()
        >>> r.symmetric_difference_update(r2)
        >>> print r
        4,(23..25),(39...)
        """
        xor = self.symmetric_difference(other)
        self.intervals = xor.intervals

    def pop(self):
        """Returns and discards an Interval or value from the IntervalSet

        >>> s = IntervalSet([7, Interval.less_than(2), 2, 0])
        >>> l = []
        >>> l.append(str(s.pop()))
        >>> l.append(str(s.pop()))
        >>> "(...2)" in l
        False
        >>> "(...2]" in l
        True
        >>> "7" in l
        True
        >>> print s
        <Empty>
        >>> i = s.pop()
        Traceback (most recent call last):
            ...
        KeyError: 'pop from an empty IntervalSet'
        """
        if len(self.intervals) > 0:
            i = self.intervals.pop()
            if i.lower_bound == i.upper_bound:
                i = i.lower_bound
        else:
            raise KeyError("pop from an empty IntervalSet")
        return i

    def __hash__(self):
        "Raises an error since IntervalSets are mutable"
        raise TypeError("unhashable instance")


class FrozenIntervalSet(BaseIntervalSet):
    """An immutable version of BaseIntervalSet

    FrozenIntervalSet is like IntervalSet, only add and remove are not
    implemented, and hashes can be generated.

    >>> fs = FrozenIntervalSet([3, 6, 2, 4])
    >>> fs.add(12)
    Traceback (most recent call last):
    ...
    AttributeError: 'FrozenIntervalSet' object has no attribute 'add'
    >>> fs.remove(4)
    Traceback (most recent call last):
    ...
    AttributeError: 'FrozenIntervalSet' object has no attribute 'remove'
    >>> fs.clear()
    Traceback (most recent call last):
    ...
    AttributeError: 'FrozenIntervalSet' object has no attribute 'clear'

    Because FrozenIntervalSets are immutable, they can be used as a 
    dictionary key.

    >>> d = {
    ...   FrozenIntervalSet([3, 66]) : 52, 
    ...   FrozenIntervalSet.less_than(3) : 3
    ... }
    """

    def __new__(cls, items=()):
        """Constructs a new FrozenInteralSet

        Object creation is just like with a regular IntervalSet, except for
        the special case where another FrozenIntervalSet is passed as the
        initializer iterable.  If it is, then the result points to the 
        same object.

        >>> fs1 = FrozenIntervalSet.greater_than(12)
        >>> fs2 = FrozenIntervalSet(fs1)
        >>> id(fs1) == id(fs2)
        True
        """
        if (cls == FrozenIntervalSet) and isinstance(items, FrozenIntervalSet):
            result = items
        else:
            s = IntervalSet(items)
            result = super(FrozenIntervalSet, cls).__new__(cls, items)
            result.intervals = s.intervals
        return result

    def __init__(self, items=()):
        """Initializes the FrozenIntervalSet"""
        super().__init__(items)

    def __repr__(self):
        """Returns an evaluable representation of the object

        >>> FrozenIntervalSet([Interval()])
        FrozenIntervalSet([Interval(-Inf, Inf, lower_closed=False, upper_closed=False)])
        >>> FrozenIntervalSet()
        FrozenIntervalSet([])
        >>> FrozenIntervalSet([2, 4])
        FrozenIntervalSet([Interval(2, 2, lower_closed=True, upper_closed=True), Interval(4, 4, lower_closed=True, upper_closed=True)])
        """
        return "FrozenIntervalSet([%s])" % (
            ", ".join(repr(i) for i in self.intervals),)

    def __hash__(self):
        """Generates a 32-bit hash key

        >>> fs = FrozenIntervalSet([4, 7, 3])
        >>> key = hash(fs)
        """
        h = 0
        for i in self.intervals:
            h = h ^ hash(i)
        return h

    def copy(self):
        """Duplicates the object

        For FrozenIntervalSet objects, since they're immutable, a 
        reference, not a copy, of self is returned.

        >>> s = FrozenIntervalSet(
        ...   [7, 2, 3, 2, 6, 2, Interval.greater_than(3)])
        >>> s2 = s.copy()
        >>> s == s2
        True
        >>> id(s) == id(s2)
        True
        """
        if self.__class__ == FrozenIntervalSet:
            return self
        else:
            copy.copy(self)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
