
import json
from datetime import date
from datetime import datetime
from datetime import timezone

from common.json.codecs import DatetimeJSONEncoder
from common.json.codecs import SetAsListJSONEncoder


class TestSetAsListJSONEncoder:
    """ Test SetAsListJSONEncoder. """

    def test_basic(self):
        data = dict(dog={1, 2, 3})
        as_json = json.dumps(data, cls=SetAsListJSONEncoder)
        assert json.loads(as_json) == {"dog": [1, 2, 3]}


class TestDatetimeJSONEncoder:
    """ Test DatetimeJSONEncoder. """

    def test_basic(self):
        data = dict(
            someday=date(2020, 1, 1),
            sometime=datetime(2020, 1, 1, 18, 50, tzinfo=timezone.utc)
        )
        expected = {"someday": "2020-01-01", "sometime": "2020-01-01T18:50:00+00:00"}
        as_json = json.dumps(data, cls=DatetimeJSONEncoder)
        assert json.loads(as_json) == expected
