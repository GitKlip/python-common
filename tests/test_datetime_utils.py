
import datetime
import pytest

import pytz

from common.datetime_utils import create_localized_datetime
from common.datetime_utils import pytz_timezone_from_wms_timezone
from common.datetime_utils import now


class TestCreateLocalizedDatetime:
    """ Test the create_localized_datetime function. """

    def test_default_behavior(self):
        """ Should return a properly localized datetime with no dangling minutes. """
        for timezone in ["America/Denver", pytz.timezone("America/Denver")]:
            dt = create_localized_datetime(2019, 3, 10, 2, timezone=timezone)
            assert isinstance(dt, datetime.datetime)
            assert dt.isoformat() == "2019-03-10T02:00:00-07:00"
            dt = create_localized_datetime(2019, 3, 10, 3, timezone=timezone)
            assert dt.isoformat() == "2019-03-10T03:00:00-06:00"


class TestNow:
    """ Test the now() function. """

    def test_default(self):
        """ Should return aware UTC. """
        dt = now()
        datetime_str = dt.isoformat()
        assert "+00:00" in datetime_str

    def test_with_timezone(self):
        for timezone in ["America/Denver", pytz.timezone("America/Denver")]:
            dt = now(timezone)
            datetime_str = dt.isoformat()
            assert any(offset in datetime_str for offset in ["-06:00", "-07:00"])


class TestPytzTimezoneFromWmsTimezone:
    """ Test the pytz_timezone_from_wms_timezone function. """

    def _assert_timezone(self, timezone, expected_offset):
        # TODO: remove dependency on create_localized_datetime for these tests
        datetime_ = create_localized_datetime(2019, 4, 1, timezone=timezone)
        assert datetime_.isoformat().endswith(expected_offset)

    @pytest.mark.parametrize(
        "timezone_description,expected_offset",
        [
            ("Pacific", "-07:00"),
            ("Mountain", "-06:00"),
            ("Arizona", "-07:00"),
            ("Central", "-05:00"),
            ("Eastern", "-04:00"),
            ("Alaska", "-08:00"),
            ("Hawaii", "-10:00"),
        ]
    )
    def test_typical_us_deprecated_timezones(self, timezone_description, expected_offset):
        """ Should be translated into canonical Olson DB names and then the timezone object. """
        self._assert_timezone(
            pytz_timezone_from_wms_timezone(timezone_description), expected_offset
        )

    @pytest.mark.parametrize(
        "timezone_description,expected_offset",
        [
            # This is the set in WMS
            ("UTC-1", "-01:00"),
            ("UTC-2", "-02:00"),
            ("UTC-11", "-11:00"),
            ("UTC-12", "-12:00"),
            ("UTC+1", "+01:00"),
            ("UTC+2", "+02:00"),
            ("UTC+3", "+03:00"),
            ("UTC+4", "+04:00"),
            ("UTC+5", "+05:00"),
            ("UTC+6", "+06:00"),
            ("UTC+7", "+07:00"),
            ("UTC+8", "+08:00"),
            ("UTC+9", "+09:00"),
            ("UTC+10", "+10:00"),
            ("UTC+11", "+11:00"),
            ("UTC+12", "+12:00"),
            ("UTC+13", "+13:00"),
            ("UTC+14", "+14:00"),
            ("UTC 1", "+01:00"),
            ("UTC 2", "+02:00"),
            ("UTC 3", "+03:00"),
            ("UTC 4", "+04:00"),
            ("UTC 5", "+05:00"),
            ("UTC 6", "+06:00"),
            ("UTC 7", "+07:00"),
            ("UTC 8", "+08:00"),
            ("UTC 9", "+09:00"),
            ("UTC 10", "+10:00"),
            ("UTC 11", "+11:00"),
            ("UTC 12", "+12:00"),
            ("UTC 13", "+13:00"),
            ("UTC 14", "+14:00"),

        ]
    )
    def test_utc_offsets(self, timezone_description, expected_offset):
        """ Should provide the correct offset when localizing datetimes. """
        self._assert_timezone(
            pytz_timezone_from_wms_timezone(timezone_description), expected_offset
        )

    def test_utc_alone(self):
        """ Should use +00:00 offset. """
        self._assert_timezone(pytz_timezone_from_wms_timezone('UTC'), "+00:00")

    def test_olson_values(self):
        """ Will accept Olson DB values. """
        to_test = {
            'America/Denver': "-06:00",
            'America/Los_Angeles': "-07:00",
        }
        for timezone_str, expected_offset in to_test.items():
            self._assert_timezone(pytz_timezone_from_wms_timezone(timezone_str), expected_offset)

    def test_bad_values(self):
        """ Should raise a pytz.UnknownTimeZoneError. """
        to_test = ["UTC1354", "DGOG", "asdfg"]
        for timezone_str in to_test:
            # todo: make sure error msg is sensible
            with pytest.raises(pytz.UnknownTimeZoneError):
                pytz_timezone_from_wms_timezone(timezone_str)
