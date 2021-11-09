import os

from common.picklers import Yamlfier
from common.picklers import Pickler


class TestYamlfier:

    def test_get_from_key(self):
        """ Should retrieve the contents of the yaml file based on the key. """
        ymlfier = Yamlfier(__file__)
        assert {'one': 2} == ymlfier.get_from_key('trial')

    def test_write_to_key(self):
        ymlfier = Yamlfier(__file__)
        ymlfier.write_to_key('writetest', {'one': 2})
        filename = ymlfier._get_filename('writetest')
        with open(filename) as infile:
            assert infile.read() == 'one: 2\n'

        os.remove(filename)


class TestPickler:

    def test_get_from_key(self):
        """ Should retrieve the contents of the pickle file based on the key. """
        pickler = Pickler(__file__)
        assert {'one': 2} == pickler.get_from_key('trial')

    def test_write_to_key(self):
        pickler = Pickler(__file__)
        pickler.write_to_key('writetest', {'one': 2})
        filename = pickler._get_filename('writetest')
        data = pickler.get_from_key('writetest')
        assert data == {'one': 2}

        os.remove(filename)
