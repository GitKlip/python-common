from collections.abc import Iterable
from collections.abc import Mapping


def make_json_friendly(data):
    """ Recursively transform data so that the output only contains objects readily json-ifiable.

    Right now, converts anything iterable (but not a mapping) to a list and
    anything that's a Mapping to a dict.

    Returns a completely new copy of data.
    """
    if isinstance(data, Iterable) and not isinstance(data, str):
        if isinstance(data, Mapping):
            return {key: make_json_friendly(val) for key, val in data.items()}
        else:
            return [make_json_friendly(val) for val in data]
    else:
        return data
