""" Useful codecs for json conversion. """
import json
from datetime import date
from datetime import datetime


class SetAsListJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class DatetimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat().replace(' ', 'T')
        elif isinstance(obj, date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
