""" A collection of tools. """

from abc import ABC, abstractmethod
from typing import TypeVar, Generic


class SupportsRichComparison(ABC):
    """An abstract interface that supports comparison operators"""

    @abstractmethod
    def __eq__(self, other: object) -> bool: pass

    @abstractmethod
    def __ne__(self, other: object) -> bool: pass

    @abstractmethod
    def __lt__(self, other: object) -> bool: pass

    @abstractmethod
    def __le__(self, other): pass

    @abstractmethod
    def __gt__(self, other: object) -> bool: pass

    @abstractmethod
    def __ge__(self, other: object) -> bool: pass


ComparableT = TypeVar("ComparableT", bound=SupportsRichComparison)


class Smallest(SupportsRichComparison):
    """Represents the smallest value

    This type doesn't do much; it implements a pseudo-value that's smaller
    than everything but itself.

    >>> negInf = Smallest()
    >>> smallest = Smallest()
    >>> -264 < negInf
    False
    >>> -264 == negInf
    False
    >>> -264 > negInf
    True
    >>> negInf < negInf
    False
    >>> negInf == smallest
    True
    """

    def __neg__(self) -> 'Largest':
        """Returns the largest value

        The opposite of negative infinity is infinity, the largest value.

        >>> print -Smallest()
        ~
        """
        return Largest()

    def __cmp__(self, other: object) -> int:
        """Compares this with another object

        Always indicates that self is less than other, unless both are of
        type Smallest, in which case they are equal.

        >>> 0 < Smallest()
        False
        >>> -9999999 < Smallest()
        False
        >>> Smallest() < -9999999
        True
        >>> Smallest() < Smallest()
        False
        >>> Smallest() == Smallest()
        True
        """
        if other.__class__ == self.__class__:
            retval = 0
        else:
            retval = -1
        return retval

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Smallest)

    def __ne__(self, other: object) -> bool:
        return not isinstance(other, Smallest)

    def __lt__(self, other: object) -> bool:
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other: object) -> bool:
        return False

    def __ge__(self, other: object) -> bool:
        return isinstance(other, Smallest)

    def __str__(self) -> str:
        """Returns a printable representation of this value

        The string for the smallest number is -~, which means negative infinity.

        >>> print Smallest()
        -~
        """
        return "-~"

    def __repr__(self) -> str:
        """Returns an evaluable representation of the object

        The representation of the smallest number is -Inf, which means
        negative infinity.

        >>> Smallest()
        -Inf
        """
        return "-Inf"


class Largest(SupportsRichComparison):
    """Class representing the universal largest value

    This type doesn't do much; it implements a pseudo-value that's larger
    than everything but itself.

    >>> infinity = Largest()
    >>> greatest = Largest()
    >>> 6234 < infinity
    True
    >>> 6234 == infinity
    False
    >>> 6234 > infinity
    False
    >>> infinity > infinity
    False
    >>> infinity == greatest
    True
    """

    def __neg__(self):
        """Returns the smallest universal value

        The opposite of infinity is negative infinity, the smallest value.

        >>> print -Largest()
        -~
        """
        return Smallest()

    def __cmp__(self, other):
        """Compares object with another object

        Always indicates that self is greater than other, unless both are of
        type Largest, in which case they are equal.

        >>> 0 > Largest()
        False
        >>> Largest() < 9999999
        False
        >>> Largest() > 9999999
        True
        >>> Largest() < Largest()
        False
        >>> Largest() == Largest()
        True
        """
        if other.__class__ == self.__class__:
            retval = 0
        else:
            retval = 1
        return retval

    def __eq__(self, other):
        return isinstance(other, Largest)

    def __ne__(self, other):
        return not isinstance(other, Largest)

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return isinstance(other, Largest)

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __str__(self):
        """Returns a string representation of the object

        The largest number is displayed as ~ (it sort of looks like infinity...)

        >>> print Largest()
        ~
        """
        return "~"

    def __repr__(self):
        """Returns an evaluable expression representing this object

        >>> Largest()
        Inf
        """
        return "Inf"


# Use -Inf for the smallest value
Inf = Largest()


class Interval(Generic[ComparableT], SupportsRichComparison):
    """Represents a continuous range of values

    An Interval is composed of the lower bound, a closed lower bound
    flag, an upper bound, and a closed upper bound flag.  The attributes
    are called lower_bound, lower_closed, upper_bound, and upper_closed,
    respectively.  For an infinite interval, the bound is set to inf or
    -inf.  IntervalSets are composed of zero to many Intervals.
    """

    def __init__(self,
                 lower_bound: ComparableT = -Inf,
                 upper_bound: ComparableT = Inf,
                 closed: bool = True,
                 lower_closed: bool = True,
                 upper_closed: bool = True):
        """Initializes an interval

        Parameters
        ==========
        - lower_bound: The lower bound of an interval (default -Inf)
        - upper_bound: The upper bound of an interval (default Inf)
        - closed: Boolean telling whether both ends of the interval are closed
        (default True).  Setting this sets both lower_closed and upper_closed
        - lower_closed: Boolean telling whether the lower end of the interval
        is closed (default True)
        - upper_closed: Boolean telling whether the upper end of the interval
        is closed (default True)

        An Interval can represent an infinite set.

        >>> r = Interval(-Inf, Inf) # All values

        An Interval can represent sets unbounded on an end.

        >>> r = Interval(upper_bound=62, closed=False)
        >>> r = Interval(upper_bound=37)
        >>> r = Interval(lower_bound=246)
        >>> r = Interval(lower_bound=2468, closed=False)

        An Interval can represent a set of values up to, but not including a
        value.

        >>> r = Interval(25, 28, closed=False)

        An Interval can represent a set of values that have an inclusive
        boundary.

        >>> r = Interval(29, 216)

        An Interval can represent a single value

        >>> r = Interval(82, 82)

        Intervals that are not normalized, i.e. that have a lower bound
        exceeding an upper bound, are silently normalized.

        >>> print Interval(5, 2, lower_closed=False)
        [2..5)

        Intervals can represent an empty set.

        >>> r = Interval(5, 5, closed=False)

        Intervals can only contain hashable (immutable) objects.

        >>> r = Interval([], 12)
        Traceback (most recent call last):
        ...
        TypeError: lower_bound is not hashable.
        >>> r = Interval(12, [])
        Traceback (most recent call last):
        ...
        TypeError: upper_bound is not hashable.
        """
        if not isinstance(lower_bound, SupportsRichComparison):
            raise TypeError("lower_bound is not comparable.")
        if not isinstance(upper_bound, SupportsRichComparison):
            raise TypeError("upper_bound is not comparable.")
        if upper_bound < lower_bound:
            raise ValueError("Upper bound cannot be greater than lower bound.")

        lower_closed = (closed or lower_closed)
        upper_closed = (closed or upper_closed)

        if (lower_bound == -Inf and lower_closed) or (upper_bound == Inf and upper_closed):
            raise ValueError("Unbound ends cannot be included in an interval.")

        self.lower_bound = lower_bound
        self.lower_closed = lower_closed
        self.upper_bound = upper_bound
        self.upper_closed = upper_closed

    def __hash__(self):
        """Returns a hashed value of the object

        Intervals are to be considered immutable.  Thus, a 32-bit hash can
        be generated for them.

        >>> h = hash(Interval.less_than(5))
        """
        return hash((
            self.lower_bound, self.lower_closed,
            self.upper_bound, self.upper_closed))

    def __repr__(self):
        """Returns an evaluable expression that can reproduce the object

        >>> Interval(3, 6)
        Interval(3, 6, lower_closed=True, upper_closed=True)
        >>> Interval(3, 6, closed=False)
        Interval(3, 6, lower_closed=False, upper_closed=False)
        >>> Interval(3, 6, lower_closed=False)
        Interval(3, 6, lower_closed=False, upper_closed=True)
        >>> Interval()
        Interval(-Inf, Inf, lower_closed=False, upper_closed=False)
        """
        return "Interval(%s, %s, lower_closed=%s, upper_closed=%s)" % (
            repr(self.lower_bound), repr(self.upper_bound),
            self.lower_closed, self.upper_closed)

    def __str__(self):
        """Returns a string representation of the object

        This function yields a graphical representation of an Interval.
        It is included in the __str__ of an IntervalSet.  Non-inclusive
        boundaries are bordered by a ( or ).  Inclusive boundaries are
        bordered by [ or ].  Unbound values are shown as ....  Intervals
        consisting of only a single value are shown as that value.  Empty
        intervals are shown as the string <Empty>

        >>> print Interval.all()
        (...)
        >>> print Interval.less_than(100)
        (...100)
        >>> print Interval.less_than_or_equal_to(2593)
        (...2593]
        >>> print Interval.greater_than(2378)
        (2378...)
        >>> print Interval.between(26, 8234, False)
        (26..8234)
        >>> print Interval(237, 2348, lower_closed=False)
        (237..2348]
        >>> print Interval.greater_than_or_equal_to(347)
        [347...)
        >>> print Interval(237, 278, upper_closed=False)
        [237..278)
        >>> print Interval.between(723, 2378)
        [723..2378]
        >>> print Interval.equal_to(5)
        5
        >>> print Interval.none()
        <Empty>
        """
        if self.lower_bound == self.upper_bound:
            if self.lower_closed or self.upper_closed:
                retval = repr(self.lower_bound)
            else:
                retval = "<Empty>"
        else:
            between = ".."

            if self.lower_closed:
                lbchar = '['
            else:
                lbchar = '('

            if self.lower_bound == -Inf:
                lstr = ""
                between = "..."
            else:
                lstr = repr(self.lower_bound)

            if self.upper_closed:
                ubchar = ']'
            else:
                ubchar = ')'

            if self.upper_bound == Inf:
                ustr = ""
                between = "..."
            else:
                ustr = repr(self.upper_bound)

            retval = "".join([lbchar, lstr, between, ustr, ubchar])
        return retval

    def __nonzero__(self):
        """Tells whether the interval is empty

        >>> if Interval(12, 12, closed=False):
        ...   print "Non-empty"
        >>> if Interval(12, 12, upper_closed=False):
        ...   print "Non-empty"
        >>> if Interval(12, 12):
        ...   print "Non-empty"
        Non-empty
        """
        return self.lower_bound != self.upper_bound \
            or (self.upper_closed and self.lower_closed)

    def __cmp__(self, other):
        """Compares two intervals for ordering purposes

        >>> Interval.equal_to(-1) < Interval.equal_to(2)
        True
        >>> Interval.equal_to(-1) == Interval.equal_to(2)
        False
        >>> Interval.equal_to(-1) > Interval.equal_to(2)
        False
        >>> Interval.between(2, 5) > Interval.between(2, 4)
        True
        >>> Interval.between(2, 5) == Interval.between(2, 4)
        False
        >>> Interval.between(2, 5) == Interval.between(2, 5)
        True
        >>> Interval.between(2, 5) >= Interval.between(2, 5)
        True
        """
        if self == other:
            result = 0
        elif self.comes_before(other):
            result = -1
        else:
            result = 1
        return result

    def __eq__(self, other):
        """Returns true if the two intervals are the same.

        >>> Interval.between(2, 5) == Interval.between(2, 5)
        True
        """
        return (
                isinstance(other, Interval) and
                self.upper_bound == other.upper_bound and
                self.lower_bound == other.lower_bound and
                self.upper_closed == other.upper_closed and
                self.lower_closed == other.lower_closed
        )

    def __lt__(self, other):
        return self.comes_before(other)

    def __gt__(self, other):
        return other.comes_before(self)

    def __and__(self, other):
        """Returns the intersection of two intervals

        >>> print Interval.greater_than(3) & Interval.greater_than(5)
        (5...)
        >>> print Interval.greater_than(3) & Interval.equal_to(3)
        <Empty>
        >>> print Interval.greater_than_or_equal_to(3) & Interval.equal_to(3)
        3
        >>> print Interval.all() & Interval.all()
        (...)
        >>> print Interval.greater_than(3) & Interval.less_than(10)
        (3..10)
        """
        if self == other:
            result = Interval()
            result.lower_bound = self.lower_bound
            result.upper_bound = self.upper_bound
            result.lower_closed = self.lower_closed
            result.upper_closed = self.upper_closed
        elif self.comes_before(other):
            if self.overlaps(other):
                if self.lower_bound == other.lower_bound:
                    lower = self.lower_bound
                    lower_closed = min(self.lower_closed, other.lower_closed)
                elif self.lower_bound > other.lower_bound:
                    lower = self.lower_bound
                    lower_closed = self.lower_closed
                else:
                    lower = other.lower_bound
                    lower_closed = other.lower_closed

                if self.upper_bound == other.upper_bound:
                    upper = self.upper_bound
                    upper_closed = min(self.upper_closed, other.upper_closed)
                elif self.upper_bound < other.upper_bound:
                    upper = self.upper_bound
                    upper_closed = self.upper_closed
                else:
                    upper = other.upper_bound
                    upper_closed = other.upper_closed

                result = Interval(
                    lower, upper,
                    lower_closed=lower_closed, upper_closed=upper_closed)
            else:
                result = Interval.none()
        else:
            result = other & self
        return result

    @classmethod
    def none(cls):
        """Returns an empty interval

        >>> print Interval.none()
        <Empty>
        """
        return cls(0, 0, closed=False)

    @classmethod
    def all(cls):
        """Returns an interval encompassing all values

        >>> print Interval.all()
        (...)
        """
        return cls()

    @classmethod
    def between(cls, a, b, closed=True):
        """Returns an interval between two values

        Returns an interval between values a and b.  If closed is True,
        then the endpoints are included.  Otherwise, the endpoints are
        excluded.

        >>> print Interval.between(2, 4)
        [2..4]
        >>> print Interval.between(2, 4, False)
        (2..4)
        """
        return cls(a, b, closed=closed)

    @classmethod
    def equal_to(cls, a):
        """Returns an point interval

        Returns an interval containing only a.

        >>> print Interval.equal_to(32)
        32
        """
        return cls(a, a)

    @classmethod
    def less_than(cls, a):
        """Returns interval of all values less than the given value

        Returns an interval containing all values less than a.  If closed
        is True, then all values less than or equal to a are returned.

        >>> print Interval.less_than(32)
        (...32)
        """
        return cls(upper_bound=a, upper_closed=False)

    @classmethod
    def less_than_or_equal_to(cls, a):
        """Returns an interval containing the given values and everything less

        >>> print Interval.less_than_or_equal_to(32)
        (...32]
        """
        return cls(upper_bound=a, upper_closed=True)

    @classmethod
    def greater_than(cls, a):
        """Returns interval of all values greater than the given value

        >>> print Interval.greater_than(32)
        (32...)
        """
        return cls(lower_bound=a, lower_closed=False)

    @classmethod
    def greater_than_or_equal_to(cls, a):
        """Returns interval of all values greater than or equal to the given value

        >>> print Interval.greater_than_or_equal_to(32)
        [32...)
        """
        return cls(lower_bound=a, lower_closed=True)

    def comes_before(self, other):
        """Tells whether an interval lies before the object

        self comes before other when sorted if its lower bound is less
        than other's smallest value.  If the smallest value is the same,
        then the Interval with the smallest upper bound comes first.
        Otherwise, they are equal.

        >>> Interval.equal_to(1).comes_before(Interval.equal_to(4))
        True
        >>> Interval.less_than_or_equal_to(1).comes_before(Interval.equal_to(4))
        True
        >>> Interval.less_than_or_equal_to(5).comes_before(
        ...   Interval.less_than(5))
        False
        >>> Interval.less_than(5).comes_before(
        ...   Interval.less_than_or_equal_to(5))
        True
        >>> Interval.all().comes_before(Interval.all())
        False
        """
        if self == other:
            result = False
        elif self.lower_bound < other.lower_bound:
            result = True
        elif self.lower_bound > other.lower_bound:
            result = False
        elif self.lower_closed == other.lower_closed:
            if self.upper_bound < other.upper_bound:
                result = True
            elif self.upper_bound > other.upper_bound \
                    or self.upper_closed == other.upper_closed \
                    or self.upper_closed:
                result = False
            else:
                result = True
        elif self.lower_closed:
            result = True
        else:
            result = False

        return result

    def join(self, other):
        """Combines two continous Intervals

        Combines two continuous Intervals into one Interval.  If the two
        Intervals are disjoint, then an exception is raised.

        >>> r1  = Interval.less_than(-100)
        >>> r2  = Interval.less_than_or_equal_to(-100)
        >>> r3  = Interval.less_than(100)
        >>> r4  = Interval.less_than_or_equal_to(100)
        >>> r5  = Interval.all()
        >>> r6  = Interval.between(-100, 100, False)
        >>> r7  = Interval(-100, 100, lower_closed=False)
        >>> r8  = Interval.greater_than(-100)
        >>> r9  = Interval.equal_to(-100)
        >>> r10 = Interval(-100, 100, upper_closed=False)
        >>> r11 = Interval.between(-100, 100)
        >>> r12 = Interval.greater_than_or_equal_to(-100)
        >>> r13 = Interval.greater_than(100)
        >>> r14 = Interval.equal_to(100)
        >>> r15 = Interval.greater_than_or_equal_to(100)
        >>> print r13.join(r15)
        [100...)
        >>> print r7.join(r6)
        (-100..100]
        >>> print r11.join(r2)
        (...100]
        >>> print r4.join(r15)
        (...)
        >>> print r8.join(r8)
        (-100...)
        >>> print r3.join(r7)
        (...100]
        >>> print r5.join(r10)
        (...)
        >>> print r9.join(r1)
        (...-100]
        >>> print r12.join(r5)
        (...)
        >>> print r13.join(r1)
        Traceback (most recent call last):
        ...
        ArithmeticError: The Intervals are disjoint.
        >>> print r14.join(r2)
        Traceback (most recent call last):
        ...
        ArithmeticError: The Intervals are disjoint.
        """
        if self.overlaps(other) or self.adjacent_to(other):
            if self.lower_bound < other.lower_bound:
                lbound = self.lower_bound
                linc = self.lower_closed
            elif self.lower_bound == other.lower_bound:
                lbound = self.lower_bound
                linc = max(self.lower_closed, other.lower_closed)
            else:
                lbound = other.lower_bound
                linc = other.lower_closed

            if self.upper_bound > other.upper_bound:
                ubound = self.upper_bound
                uinc = self.upper_closed
            elif self.upper_bound == other.upper_bound:
                ubound = self.upper_bound
                uinc = max(self.upper_closed, other.upper_closed)
            else:
                ubound = other.upper_bound
                uinc = other.upper_closed
            return Interval(
                lbound, ubound, upper_closed=uinc, lower_closed=linc)
        else:
            raise ArithmeticError("The Intervals are disjoint.")

    def __contains__(self, obj):
        """Returns True if obj lies wholly within the Interval.

        >>> all    = Interval.all()
        >>> lt     = Interval.less_than(10)
        >>> le     = Interval.less_than_or_equal_to(10)
        >>> some   = Interval(10, 20, lower_closed=False)
        >>> single = Interval.equal_to(10)
        >>> ge     = Interval.greater_than_or_equal_to(10)
        >>> gt     = Interval.greater_than(10)
        >>> ne     = Interval.equal_to(17)
        >>> 10 in all
        True
        >>> 10 in lt
        False
        >>> 10 in le
        True
        >>> 10 in some
        False
        >>> 10 in single
        True
        >>> 10 in ge
        True
        >>> 10 in gt
        False
        >>> 10 in ne
        False
        >>> all in some
        False
        >>> lt in all
        True
        >>> lt in some
        False
        >>> single in ge
        True
        >>> ne in some
        True
        """
        if isinstance(obj, Interval):
            if obj.lower_bound < self.lower_bound:
                insideLower = False
            elif obj.lower_bound == self.lower_bound:
                insideLower = (obj.lower_closed <= self.lower_closed)
            else:
                insideLower = True

            if obj.upper_bound > self.upper_bound:
                insideUpper = False
            elif obj.upper_bound == self.upper_bound:
                insideUpper = (obj.upper_closed <= self.upper_closed)
            else:
                insideUpper = True

            result = insideLower and insideUpper
        else:
            result = Interval.equal_to(obj) in self
        return result

    def overlaps(self, other):
        """Tells whether the given interval overlaps the object

        Returns True if the one Interval overlaps another.  If they are
        immediately adjacent, then this returns False.  Use the adjacent_to
        function for testing for adjacent Intervals.

        >>> r1  = Interval.less_than(-100)
        >>> r2  = Interval.less_than_or_equal_to(-100)
        >>> r3  = Interval.less_than(100)
        >>> r4  = Interval.less_than_or_equal_to(100)
        >>> r5  = Interval.all()
        >>> r6  = Interval.between(-100, 100, False)
        >>> r7  = Interval(-100, 100, lower_closed=False)
        >>> r8  = Interval.greater_than(-100)
        >>> r9  = Interval.equal_to(-100)
        >>> r10 = Interval(-100, 100, upper_closed=False)
        >>> r11 = Interval.between(-100, 100)
        >>> r12 = Interval.greater_than_or_equal_to(-100)
        >>> r13 = Interval.greater_than(100)
        >>> r14 = Interval.equal_to(100)
        >>> r15 = Interval.greater_than_or_equal_to(100)
        >>> r8.overlaps(r9)
        False
        >>> r12.overlaps(r6)
        True
        >>> r7.overlaps(r8)
        True
        >>> r8.overlaps(r4)
        True
        >>> r14.overlaps(r11)
        True
        >>> r10.overlaps(r13)
        False
        >>> r5.overlaps(r1)
        True
        >>> r5.overlaps(r2)
        True
        >>> r15.overlaps(r6)
        False
        >>> r3.overlaps(r1)
        True
        """
        if self == other:
            result = True
        elif other.comes_before(self):
            result = other.overlaps(self)
        elif other.lower_bound < self.upper_bound:
            result = True
        elif other.lower_bound == self.upper_bound:
            result = (other.lower_closed and self.upper_closed)
        else:
            result = False
        return result

    def adjacent_to(self, other):
        """Tells whether an Interval is adjacent to the object without overlap

        Returns True if self is adjacent to other, meaning that if they
        were joined, there would be no discontinuity.  They cannot
        overlap.

        >>> r1  = Interval.less_than(-100)
        >>> r2  = Interval.less_than_or_equal_to(-100)
        >>> r3  = Interval.less_than(100)
        >>> r4  = Interval.less_than_or_equal_to(100)
        >>> r5  = Interval.all()
        >>> r6  = Interval.between(-100, 100, False)
        >>> r7  = Interval(-100, 100, lower_closed=False)
        >>> r8  = Interval.greater_than(-100)
        >>> r9  = Interval.equal_to(-100)
        >>> r10 = Interval(-100, 100, upper_closed=False)
        >>> r11 = Interval.between(-100, 100)
        >>> r12 = Interval.greater_than_or_equal_to(-100)
        >>> r13 = Interval.greater_than(100)
        >>> r14 = Interval.equal_to(100)
        >>> r15 = Interval.greater_than_or_equal_to(100)
        >>> r1.adjacent_to(r6)
        False
        >>> r6.adjacent_to(r11)
        False
        >>> r7.adjacent_to(r9)
        True
        >>> r3.adjacent_to(r10)
        False
        >>> r5.adjacent_to(r14)
        False
        >>> r6.adjacent_to(r15)
        True
        >>> r1.adjacent_to(r8)
        False
        >>> r12.adjacent_to(r14)
        False
        >>> r6.adjacent_to(r13)
        False
        >>> r2.adjacent_to(r15)
        False
        >>> r1.adjacent_to(r4)
        False
        """
        if self.comes_before(other):
            if self.upper_bound == other.lower_bound:
                result = (self.upper_closed != other.lower_closed)
            else:
                result = False
        elif self == other:
            result = False
        else:
            result = other.adjacent_to(self)
        return result
