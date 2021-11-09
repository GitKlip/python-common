from collections import defaultdict
from itertools import chain
from itertools import combinations
from itertools import islice
from itertools import tee


def group_by(func, values):
    """ Groups values by func.

    Returns
      (dict): Keys produced by func pointing to lists of the values grouped.
    """
    groups = defaultdict(list)
    for value in values:
        groups[func(value)].append(value)
    return dict(groups)


def index_by(func, values):
    """ Indexes values by func.

    Returns
      (dict): Keys produced by func, each pointing to one value.
    """
    return {func(value): value for value in values}


def each_cons(size, iterable):
    """ Moves a sliding window along the iterable and yields consecutive windows.

    Example:
      for window in each_cons(3, [1,2,3,4,5]):
          print(chunk)

      # output:
      [1, 2, 3]
      [2, 3, 4]
      [3, 4, 5]

    Taken from: https://stackoverflow.com/a/54110047/422075
    """
    iterators = tee(iterable, size)
    iterators = [islice(iterator, i, None) for i, iterator in enumerate(iterators)]
    yield from zip(*iterators)


def each_slice(size, iterable):
    """ Chunks the iterable into size elements at a time, each yielded as a list.

    Example:
      for chunk in each_slice(2, [1,2,3,4,5]):
          print(chunk)

      # output:
      [1, 2]
      [3, 4]
      [5]
    """
    current_slice = []
    for item in iterable:
        current_slice.append(item)
        if len(current_slice) >= size:
            yield current_slice
            current_slice = []
    if current_slice:
        yield current_slice


def each_slice_or_size(iterable, max_len: int, max_bytes: float):
    current_slice = []

    for item in iterable:
        if sys.getsizeof(current_slice) + sys.getsizeof(item) >= max_bytes:
            yield current_slice
            current_slice = []

        current_slice.append(item)

        if len(current_slice) >= max_len:
            yield current_slice
            current_slice = []

    if current_slice:
        yield current_slice


def all_combinations(iterable, min_size=1, max_size=None):
    """ Returns combinations of all lengths up to the size of iterable.

    Args:
        iterable (iterable): Anything that can be turned into a list.
        min_size (int): The min size of a combination.
        max_size (int): The max size of a combination.  If None, defaults to
            len(list(iterable)).

    Returns:
        (iterator): An iterator returning all requested combinations.

    Example:
        iterator = all_combinations([1, 2, 3])

        # output of list(iterator):
        [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    min_size = max(min_size, 0)
    as_list = list(iterable)
    size = len(as_list)
    max_size = size if max_size is None else max_size
    max_size = min(size, max_size)
    return chain.from_iterable(combinations(as_list, size) for size in range(min_size, max_size + 1))


def compact(iterable, generator=False):
    """ Returns a list where all None values have been discarded. """
    if generator:
        return (val for val in iterable if val is not None)
    else:
        return [val for val in iterable if val is not None]
