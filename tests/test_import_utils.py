
import pytest

from common.import_utils import ImportStringError
from common.import_utils import import_string


class TestImportUtils:

    def test_import_string(self):
        """ Should return the class imported. """
        cls = import_string("common.picklers.Yamlfier")
        assert cls.__name__ == 'Yamlfier'

    def test_bad_import_string(self):
        """ Should raise an ImportStringError. """
        with pytest.raises(ImportStringError):
            import_string("common.picklers.NotAnExistingClass")
