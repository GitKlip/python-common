
import os
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict

import requests

from common.dicts import Objectview


class ResponseError(Exception):
    def __init__(self, *args, response, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response


class Types:
    DATETIME = 'datetime'
    DATE = 'date'
    NUMBER = 'number'
    PERCENTAGE = 'percentage'
    MONEY = 'money'
    STRING = 'string'


@dataclass
class Field:
    """ A field specification. """
    name: str = None
    type: str = Types.NUMBER
    required: bool = False
    unique: bool = False


class Dataset:
    """ Simple object to ease interaction with geckoboard.

    The main python geckoboard client
    (https://github.com/geckoboard/geckoboard-python) requires the template to
    even *retrieve* a dataset, which is ridiculous.  So, this is a rewrite
    that does not require a template before executing actions on the dataset.

    Example usage:
        from common.geckoboard import Dataset, Field, Types
        # Examples below assume you've set GECKOBOARD_API_KEY
        # Could also pass in api key directly: Dataset('some.id', api_key='abc14cdga1415ga1aagt1')

        # dataset *data* operations
        dataset = Dataset('some.id')
        dataset.overwrite([dict(tpl='13', timestamp=datetime, num_orders=54)])
        dataset.append([dict(tpl='14', timestamp=datetime, num_orders=22)])
        dataset.clear()

        # individual dataset *schema* operations
        dataset = Dataset('some.id')

        class MySchema:
            tpl = Field(Types.STRING, required=True, unique=True),
            timestamp = Field(Types.DATETIME, required=True),
            num_orders = Field(Types.NUMBER),

        dataset.create_schema(MySchema)
        schema = dataset.get_schema()
        dataset.delete()

        # get all the schemas
        lots_of_schemas = Dataset.get_schemas()
    """
    KEY_NAME = "GECKOBOARD_API_KEY"
    BASE_URL = "https://api.geckoboard.com"
    DATASETS_ENDPOINT = BASE_URL + "/datasets"
    DATASETS_ENDPOINT_FORMAT_STR = BASE_URL + "/datasets/{}"
    DATA_ENDPOINT_FORMAT_STR = f"{DATASETS_ENDPOINT}/{{}}/data"

    @classmethod
    def get_schemas(cls, filter_on_ids: list = None, only_return_ids: bool = False, api_key: str = None):
        """ Return all the datasets/schemas.

        Args:
            filter_on_ids: a list of ids to filter on.
            only_return_ids: whether to only return a list of ids.
            api_key: the api key (can be None if have set env var)
        """

        auth_params = cls._get_auth_params(api_key)
        response = requests.get(cls.DATASETS_ENDPOINT, **auth_params)
        cls._ensure_response_ok(response)
        schemas = response.json()['data']

        if only_return_ids:
            return [scheme['id'] for scheme in schemas]

        if filter_on_ids:
            schemas = [scheme for scheme in schemas if scheme['id'] in filter_on_ids]

        return schemas

    @classmethod
    def get_schema_ids(cls, api_key: str = None):
        """ Only return the ids of datasets. """
        return cls.get_schemas(only_return_ids=True, api_key=api_key)

    @staticmethod
    def _get_api_key(api_key: str = None):
        if not api_key:
            api_key = os.environ[Dataset.KEY_NAME]
        return api_key

    @staticmethod
    def _get_auth_params(api_key: str = None):
        api_key = Dataset._get_api_key(api_key)
        return dict(auth=(api_key, ''))

    def _key_from_auth_params(self):
        return self.auth_params['auth'][0]

    def __init__(self, dataset_id: str, api_key: str = None):
        self.auth_params = self._get_auth_params(api_key)
        self.dataset_id = dataset_id

    def _field_to_field_def(self, key: str, field: Field) -> Dict[str, dict]:
        """ Convert a Field into proper schema. """
        return {
            key: dict(
                # could uppercase and put spaces for underscores or something here
                name=field.name or key,
                type=field.type,
                required=field.required
            )
        }

    def create_schema(self, schema: Any = None):
        """ Creates the template

        Args
            schema: An instance or class that has Field instances as
                attributes.  Or can be a dict-like object that has keys (the field
                names) and values that are Field instances.

        Returns:
            None if successful.

        Raises:
            ResponseError if any problems.

        Example:
            class MySchema:
                first = Field(Types.STRING)
                second = Field()  # numeric by default
                timestamp = Field(Types.DATETIME, required=True, unique=True)

            dataset.create_schema(MySchema)

            # could also be a dictionary
            my_schema = dict(
                first=Field(Types.STRING),
                second=Field()  # numeric by default
                timestamp=Field(Types.DATETIME, required=True, unique=True)
            )
        """
        if isinstance(schema, dict):
            schema = Objectview(schema)

        fields = {
            att: getattr(schema, att)
            for att in dir(schema)
            if not att.startswith("_") and isinstance(getattr(schema, att), Field)
        }

        all_fields = {}
        for name, field in fields.items():
            all_fields.update(self._field_to_field_def(name, field))

        unique_by = [name for name, field in fields.items() if field.unique]
        template = dict(
            fields=all_fields,
            unique_by=unique_by,
        )
        response = requests.put(
            self.DATASETS_ENDPOINT_FORMAT_STR.format(self.dataset_id), json=template, **self.auth_params
        )
        self._ensure_response_ok(response)

    def overwrite(self, data):
        return self._upload(data, append=False)

    def append(self, data):
        return self._upload(data, append=True)

    def delete(self):
        """ Delete the schema and all data in it.

        Returns:
            None if successful, the response object if unsuccessful.
        """
        url = self.DATASETS_ENDPOINT_FORMAT_STR.format(self.dataset_id)
        response = requests.delete(url, **self.auth_params)
        self._ensure_response_ok(response)

    def clear(self):
        """ Clears the data in the dataset without changing the schema. """
        self.overwrite([])

    def _date_like_to_isoformat(self, value):
        """ Transforms date or datetime to isoformat. """
        if isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, datetime):
            return value.isoformat().replace(' ', 'T')
        else:
            return value

    def dates_to_isoformat(self, data):
        return [{key: self._date_like_to_isoformat(value) for key, value in datum.items()} for datum in data]

    def _upload(self, data, append):
        """ Appends data. """
        url = self.DATA_ENDPOINT_FORMAT_STR.format(self.dataset_id)
        method = 'post' if append else 'put'
        processed_data = self.dates_to_isoformat(data)
        payload = dict(data=processed_data)
        response = getattr(requests, method)(url, json=payload, **self.auth_params)
        self._ensure_response_ok(response)

    @staticmethod
    def _ensure_response_ok(response):
        # print("STATUS CODE", response.status_code)
        # print("RESPONSE", response.json())
        if not response.ok:
            raise ResponseError(response=response)

    def get_schema(self):
        api_key = self._key_from_auth_params()
        schemas = self.get_schemas(filter_on_ids=[self.dataset_id], api_key=api_key)
        if schemas:
            return schemas[0]
