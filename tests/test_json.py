import json
from contextlib import contextmanager

import pytest

from common.json import make_json_friendly


@contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f"DID raise {exception}")


def test_make_json_friendly():
    """ Should return data which is easily jsonifiable. """
    to_test = dict(
        simple=({1: 2, 3: [1, 23]}, {1: 2, 3: [1, 23]}),
        with_sets=({1: 2, 3: {1, 23}}, {1: 2, 3: [1, 23]}),
        nested_dict_sets=(
            {"somekey": {"subkey": [{'A'}, {'B'}]}},
            {"somekey": {"subkey": [['A'], ['B']]}},
        )
    )
    for data, expected in to_test.values():
        json_friendly = make_json_friendly(data)
        assert json_friendly == expected
        with not_raises(Exception):
            json.dumps(json_friendly)
