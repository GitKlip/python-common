""" Unless specified, all methods return aware datetimes. """
import datetime
import re

import pytz

MINUTES_IN_HOUR = 60


WMS_TIMEZONE_TO_OLSON = {
    "eastern": "America/New_York",
    "central": "America/Chicago",
    "mountain": "America/Denver",
    "arizona": "America/Phoenix",
    "pacific": "America/Los_Angeles",
    "alaska": "America/Anchorage",
    "hawaii": "Pacific/Honolulu",
    "utc": "UTC",
}


def ensure_timezone(value):
    return pytz.timezone(value) if isinstance(value, str) else value


def create_localized_datetime(*args, timezone='UTC', **kwargs):
    """ Creates an aware time in the given timezone.

    The intuitive way of doing this will give you the wrong answer:
        https://stackoverflow.com/questions/24856643/unexpected-results-converting-timezones-in-python

    So, this method does it correctly.

    Args:
      naive_datetime (datetime): A timezone naive datetime.
      timezone (str or pytz.timezone): A pytz timezone object or an Olson
          timezone name (hint: the name used to make timezones).
    """
    casted_timezone = ensure_timezone(timezone)
    value = datetime.datetime(*args, **kwargs)
    return casted_timezone.localize(value)


def now(timezone='UTC'):
    """ Returns an aware datetime with the proper timezone.

    Args:
      timezone (str or pytz.timezone): A pytz timezone object or an Olson
          timezone name (hint: the name used to make timezones).
    """
    casted_timezone = ensure_timezone(timezone)
    return datetime.datetime.now(casted_timezone)


# we allow these 3 main patterns: "UTC-4", "UTC+12", and "UTC 12"
# The "UTC 12" means someone forgot to url-encode "UTC+12",
# but since it's unambiguous, we'll accept it
UTC_OFFSET_RE = re.compile(r'UTC([\-\+ ])(\d+)')


def pytz_timezone_from_wms_timezone(timezone_description: str):
    """ Converts a 3plcentral wms timezone description into a pytz timezone.

    3plcentral has ad-hoc-ish timezone descriptions.  The english ones
    represent Olson deprecated US timezones and can be converted easily into
    Olson timezone database identifiers.  Others represent fixed UTC offsets
    and these can be represetned by a pytz FixedOffset() style timezone.

    Returns:
      (pytz.timezone): A pytz timezone object or None if not possible to
      create a timezone object from the string.
    """
    lowered_timezone_str = timezone_description.lower()
    if lowered_timezone_str in WMS_TIMEZONE_TO_OLSON:
        return pytz.timezone(WMS_TIMEZONE_TO_OLSON[lowered_timezone_str])
    elif timezone_description.startswith('UTC'):
        match = UTC_OFFSET_RE.match(timezone_description)
        if match:
            sign_str, hour_offset_str = match.groups()
            seconds = int(hour_offset_str) * MINUTES_IN_HOUR
            signed_seconds = -seconds if sign_str == '-' else seconds
            return pytz.FixedOffset(signed_seconds)

    # last ditch, see if pytz will take it
    try:
        return pytz.timezone(timezone_description)
    except pytz.UnknownTimeZoneError as exc:
        raise pytz.UnknownTimeZoneError(f"require 3plcentral or Olson DB tz designation, instead got: {str(exc)}")
