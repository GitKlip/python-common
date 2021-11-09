
import types

from common.json.io import read
from common.json.io import read_jsonl
from common.json.io import write


class TestRead:

    def _write(self, tmp_path, filename, contents):
        """ Writes to file and returns filename. """
        path = tmp_path / filename
        path.write_text(contents)
        return str(path.resolve())

    def test_read(self, tmp_path):
        """ Reads data from a file. """
        filename = self._write(tmp_path, "okay.json", '{"dog": "cat", "bone": 3}')
        assert read(filename) == {'dog': 'cat', 'bone': 3}

    def test_read_jsonl(self, tmp_path):
        """ Properly reads jsonl files. """
        filename = self._write(tmp_path, "okay.jsonl", '{"dog": "cat", "bone": 3}\n{"cat": "dog", "yeup": 3}')
        assert read(filename) == [{'bone': 3, 'dog': 'cat'}, {'cat': 'dog', 'yeup': 3}]

    def test_read_jsonl_as_generator(self, tmp_path):
        """ Reads jsonl files and returns a generator. """
        filename = self._write(tmp_path, "okay.jsonl", '{"dog": "cat", "bone": 3}\n{"cat": "dog", "yeup": 3}')
        generator = read_jsonl(filename, generator=True)
        assert isinstance(generator, types.GeneratorType)
        assert list(generator) == [{'bone': 3, 'dog': 'cat'}, {'cat': 'dog', 'yeup': 3}]

    def test_read_jsonl_trailing_newlines(self, tmp_path):
        """ Properly reads jsonl files. """
        filename = self._write(tmp_path, "okay.jsonl", '{"dog": "cat", "bone": 3}\n{"cat": "dog", "yeup": 3}\n\n')
        assert read(filename) == [{'bone': 3, 'dog': 'cat'}, {'cat': 'dog', 'yeup': 3}]


class TestWrite:

    def _assert_file(self, filename, expected):
        with open(filename) as infile:
            file_contents = infile.read()
            assert file_contents == expected

    def test_write(self, tmp_path):
        """ Writes data as json to a file. """
        path = tmp_path / "dog.json"
        name = str(path.resolve())
        data = {'dog': 'cat', 'bone': 3}
        write(name, data)
        self._assert_file(name, '{"dog": "cat", "bone": 3}')

    def test_write_jsonl(self, tmp_path):
        """ Writes many data objects to a jsonl file. """
        path = tmp_path / "dog.jsonl"
        name = str(path.resolve())
        data = [{'bone': 3, 'dog': 'cat'}, {'cat': 'dog', 'yeup': 3}]
        write(name, data)
        expected = '{"bone": 3, "dog": "cat"}\n{"cat": "dog", "yeup": 3}\n'
        self._assert_file(name, expected)
