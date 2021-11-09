import types

from common.enumerable import all_combinations
from common.enumerable import each_cons
from common.enumerable import compact
from common.enumerable import each_slice
from common.enumerable import group_by
from common.enumerable import index_by


class TestGroupBy:
    """ Test the group_by function. """
    BOB1 = dict(name='Bob', size=1)
    BOB2 = dict(name='Bob', size=2)
    SALLY = dict(name='Sally')

    OBJECTS = [BOB1, BOB2, SALLY]

    def test_basic_usage(self):
        """ Should return a dict with objects grouped, in order, by the function. """
        grouped = group_by(lambda obj: obj['name'], self.OBJECTS)
        expected = {'Bob': [self.BOB1, self.BOB2], 'Sally': [self.SALLY]}
        assert grouped == expected


class TestIndexBy:
    """ Test the index_by function. """
    BOB = dict(name='Bob')
    JOE = dict(name='Joe')
    SALLY = dict(name='Sally')

    OBJECTS = [BOB, JOE, SALLY]

    def test_basic_usage(self):
        """ Should return a dict with objects indexed by the result of the function. """
        grouped = index_by(lambda obj: obj['name'], self.OBJECTS)
        expected = {'Bob': self.BOB, 'Joe': self.JOE, 'Sally': self.SALLY}
        assert grouped == expected


class TestEachSlice:
    """ Test the each_slice function. """

    def test_basic_usage(self):
        """ Should yield slices according the the specified size. """
        response = each_slice(3, range(10))
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        assert isinstance(response, types.GeneratorType)
        assert list(response) == expected


class TestAllCombinations:
    """ Test all_combinations. """
    _no_kwargs = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    _min_zero = [tuple()] + _no_kwargs

    EXPECTED = dict(
        no_kwargs=_no_kwargs,
        min_2=[(1, 2), (1, 3), (2, 3), (1, 2, 3)],
        min_zero=_min_zero,
        lt_zero=_min_zero,
        max_size_2=[(1,), (2,), (3,), (1, 2), (1, 3), (2, 3)]
    )

    def setup_method(self):
        self.iterable = [1, 2, 3]

    def test_basic(self):
        combinations = all_combinations(self.iterable)
        assert list(combinations) == self.EXPECTED['no_kwargs']

    def test_min_size(self):
        """ Should only return combinations at or larger than min_size. """
        combinations = all_combinations(self.iterable, min_size=2)
        assert list(combinations) == self.EXPECTED['min_2']

    def test_min_size_zero(self):
        """ Should return combinations?"""
        combinations = all_combinations(self.iterable, min_size=0)
        assert list(combinations) == self.EXPECTED['min_zero']

    def test_min_size_lt_zero(self):
        """ Should act like min_size=0. """
        combinations = all_combinations(self.iterable, min_size=-1)
        assert list(combinations) == self.EXPECTED['lt_zero']

    def test_min_size_gt_size(self):
        """ Returns an empty generator. """
        combinations = all_combinations(self.iterable, min_size=20)
        assert list(combinations) == []

    def test_max_size(self):
        """ Returns combinations lte to max_size. """
        combinations = all_combinations(self.iterable, max_size=2)
        assert list(combinations) == self.EXPECTED['max_size_2']

    def test_max_size_lt_min_size(self):
        """ Returns empty iterator. """
        combinations = all_combinations(self.iterable, min_size=2, max_size=1)
        assert list(combinations) == []

    def test_high_max_size(self):
        """ Returns iterator as if max_size is len(iterable). """
        combinations = all_combinations(self.iterable, max_size=20)
        assert list(combinations) == self.EXPECTED['no_kwargs']


class TestEachCons:
    """ Test the each_cons function. """
    EXPECTED = [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]

    def setup_method(self):
        self.iterable = [1, 2, 3, 4, 5, 6]

    def test_basic(self):
        """ Should yield a window slice of tuples along the iterable. """
        assert list(each_cons(3, self.iterable)) == self.EXPECTED


class TestCompact:
    """ Test the compact function. """
    EXPECTED = [0, 1]

    def setup_method(self):
        self.iterable = [None, 0, None, 1, None]

    def test_basic(self):
        """ Should return a list without None. """
        assert compact(self.iterable) == self.EXPECTED

    def test_generator(self):
        """ If generator is True, should return a generator without None. """
        compacted = compact(self.iterable, generator=True)
        assert isinstance(compacted, types.GeneratorType)
        assert list(compacted) == self.EXPECTED
