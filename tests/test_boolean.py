import pytest

from common.boolean import to_bool


class TestToBool:
    """ Test the to_bool function. """

    EXPECTED = {
        True: [True, 1, 'y', 'yes', 't', 'true', 'on', '1'],
        False: [False, 0, 'n', 'no', 'f', 'false', 'off', '0'],
    }
    RAISES = ['asdf', 14, -1, 'trueish', 'falseishy', '10', 'tr', 'fa']

    def _upper_if_possible(self, value):
        if hasattr(value, 'upper'):
            return value.upper()
        return value

    def test_to_bool_successes(self):
        """ All the expected values should be True or False. """
        for expected, values in self.EXPECTED.items():
            for value in values:
                assert to_bool(value) is expected
                assert to_bool(self._upper_if_possible(value)) is expected

    def test_to_bool_failures(self):
        """ Anything not expected truth-y will raise a ValueError. """
        for value in self.RAISES:
            with pytest.raises(ValueError):
                to_bool(value)
            with pytest.raises(ValueError):
                to_bool(self._upper_if_possible(value))
