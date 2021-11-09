import sys
import os
import pathlib
import pickle


def ensure_yaml():
    try:
        import yaml
        yaml.SafeDumper.ignore_aliases = lambda *args: True
    except (NameError, ModuleNotFoundError) as exc:
        print(exc, file=sys.stderr)
        print("You will need to add `pyyaml` as a dev dependency to use `Yamlfier`", file=sys.stderr)
        print("[not a normal dependency of this package]", file=sys.stderr)
    return yaml


class PicklerBase:
    EXT = ''
    DATA_DIR = "data_files"

    def __init__(self, path, data_dir=DATA_DIR, ext=EXT):
        dirpath = os.path.dirname(os.path.realpath(path)) if os.path.isfile(path) else path
        self._data_dir_path = os.path.join(dirpath, data_dir)
        pathlib.Path(self._data_dir_path).mkdir(parents=True, exist_ok=True)

    def _get_serialized_data(self, filename):
        with open(filename) as infile:
            return self._load_file(infile)

    def _load_from_filename(self, infile):
        pass

    def _get_filename(self, key):
        return os.path.join(self._data_dir_path, key + self.EXT)

    def get_from_key(self, key, template_if_missing=None):
        filename = self._get_filename(key)
        return self._load_from_filename(filename)

    def write_to_key(self, key, data):
        filename = self._get_filename(key)
        self._dump_to_filename(filename, data)


class Yamlfier(PicklerBase):
    """
    Example:
        def test_my_stuff():
            data = {'one': 'cat'}

            yamlfier = Yamlfier(__file__)

            # to write data to your yaml file:
            yamlfier.write_to_key('cattest', data)

            # to pull data from yaml
            yamlfier.get_from_key('cattest')
    """
    EXT = ".yml"

    def _load_from_filename(self, infile):
        yaml = ensure_yaml()
        with open(infile) as infile:
            return yaml.safe_load(infile)

    def _dump_to_filename(self, filename, data):
        yaml = ensure_yaml()
        with open(filename, 'w') as outfile:
            print(yaml.safe_dump(data), file=outfile, end='')


class Pickler(PicklerBase):
    """
    Example:
        def test_my_stuff():
            data = {'one': 'cat'}

            pickler = Pickler(__file__)

            # to write data to your yaml file:
            pickler.write_to_key('cattest', data)

            # to pull data from yaml
            pickler.get_from_key('cattest')
    """
    EXT = ".pickle"

    def _load_from_filename(self, filename):
        with open(filename, 'rb') as infile:
            return pickle.load(infile)

    def _dump_to_filename(self, filename, data):
        with open(filename, 'wb') as out:
            pickle.dump(data, out)
