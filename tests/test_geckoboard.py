import pytest

from common.geckoboard import Dataset
from common.geckoboard import Field
from common.geckoboard import Types


TEST_SCHEMA_DATA = dict(
    timestamp=Field(Types.DATETIME, unique=True),
    tpl=Field(Types.STRING),
    num_orders=Field(required=True),
)


class SimpleSchema:
    """ A simple schema for testing schema creation. """
    timestamp = Field(type=Types.DATETIME, unique=True)
    tpl = Field(type=Types.STRING)
    num_orders = Field(name="Number of Orders", required=True)


class TestDataset:
    """ Test the geckoboard Dataset. """
    DATASET_ID = 'john.test.dataset'

    # INSERT YOUR REAL geckoboard API key here if you need to run live (e.g., to
    # refresh pytest.mark.vcr cassettes)
    API_KEY = "XXXXXXX"
    dataset = Dataset(DATASET_ID, api_key=API_KEY)

    def teardown_method(self):
        try:
            self.dataset.delete()
        except:  # noqa: E722
            ...

    def _create_test_schema(self):
        self.dataset.create_schema(TEST_SCHEMA_DATA)

    @pytest.mark.vcr()
    def test_create_schema_from_dict(self):
        """ Create a schema from dictionary. """
        # this depends on a dict implementation of _create_test_schema
        assert self._create_test_schema() is None

    @pytest.mark.vcr()
    def test_create_schema_from_class(self):
        """ Create a template. """
        self.dataset.create_schema(SimpleSchema)

    @pytest.mark.vcr()
    def test_create_schema_from_instance(self):
        """ Create a template. """
        self.dataset.create_schema(SimpleSchema())

    @pytest.mark.vcr()
    def test_get_schema(self):
        """ Retrieves schema data by id. """
        self._create_test_schema()
        expected = {
            "id": self.DATASET_ID,
            "fields": {
                "num_orders": {"type": "number", "optional": False, "name": "num_orders"},
                "timestamp": {"type": "datetime", "optional": False, "name": "timestamp"},
                "tpl": {"type": "string", "optional": False, "name": "tpl"},
            },
            "unique_by": ["timestamp"],
            # "created_at": "2020-07-10T23:56:59.373702Z",
            # "updated_at": "2020-07-10T23:56:59.373702Z",
        }
        schema_data = self.dataset.get_schema()
        schema_data.pop('created_at')
        schema_data.pop('updated_at')
        assert schema_data == expected

    @pytest.mark.vcr()
    def test_get_schemas(self):
        """ Retrieves schemas. """
        self._create_test_schema()
        schemas = Dataset.get_schemas(api_key='fba040a0ff80d4ea9c5283b805d34df8')
        assert len(schemas) == 12
        assert schemas[0]['id'] == self.DATASET_ID

    @pytest.mark.vcr()
    def test_get_schema_ids(self):
        """ Retrieves schemas. """
        schemas = Dataset.get_schema_ids(api_key='fba040a0ff80d4ea9c5283b805d34df8')
        assert len(schemas) == 12
        assert isinstance(schemas[0], str)

    @pytest.mark.vcr()
    def test_delete(self):
        """ Deletes the template. """
        self._create_test_schema()
        response = self.dataset.delete()
        assert response is None

    @pytest.mark.vcr()
    def test_overwrite(self):
        """ Overwrites any existing data. """
        self._create_test_schema()
        response = self.dataset.overwrite(
            [dict(num_orders=8, timestamp='2020-01-02T00:00:00', tpl='mytpl')]
        )
        assert response is None

    @pytest.mark.vcr()
    def test_append(self):
        """ Overwrites any existing data. """
        self._create_test_schema()
        first = [dict(num_orders=8, timestamp='2020-01-02T00:00:00', tpl='mytpl')]
        second = [dict(num_orders=7, timestamp='2020-01-03T00:00:00', tpl='mytpl')]

        response = self.dataset.append(first)
        assert response is None
        response = self.dataset.append(second)
        assert response is None

    @pytest.mark.vcr()
    def test_clear(self):
        """ Deletes existing data. """
        self._create_test_schema()
        data = [dict(num_orders=8, timestamp='2020-01-02T00:00:00', tpl='mytpl')]
        self.dataset.append(data)
        self.dataset.clear()
