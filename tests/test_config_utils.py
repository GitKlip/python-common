import os
from contextlib import contextmanager
from pathlib import Path

import pytest
from common import config_utils
from common.path_utils import chdir
from common.config import Config

EXPECTED_ROOT_FILES = ["README.md", "pyproject.toml"]


@contextmanager
def env_stage_testing(*args, **kwargs):
    """ Ensure that env variable ENV_STAGE is set to testing before the test. """
    _os_environ_env_stage_before = os.environ.get('ENV_STAGE', '')
    os.environ['ENV_STAGE'] = 'testing'

    try:
        yield
    finally:
        os.environ['ENV_STAGE'] = _os_environ_env_stage_before


@contextmanager
def fake_env_var(key, val):
    previous = os.environ[key]
    os.environ[key] = val
    try:
        yield
    finally:
        os.environ[key] = previous


def _is_root(path):
    with chdir(path):
        return all(Path(path).joinpath(file_).exists() for file_ in EXPECTED_ROOT_FILES)


def test_find_repo_root_with_file():
    """ Should return the repo root directory. """
    this_dir_path = os.path.dirname(os.path.realpath(__file__))

    with chdir(this_dir_path):
        root = config_utils.find_repo_root(__file__)
        assert _is_root(root)


def test_find_repo_root_with_root_dir():
    """ Should still return the repo root directory. """
    root = config_utils.find_repo_root(__file__)
    refound = config_utils.find_repo_root(str(root))
    assert _is_root(refound)


def test_get_pyproject_config():
    """ Should return a config object. """
    config = config_utils.get_pyproject_config()
    # assumes we are using poetry
    assert "tool.poetry" in config


def test_get_project_name():
    """ Should return the name of the current project. """
    name = config_utils.get_project_name()
    # assumes the name of this package
    assert name == 'common'


def test_setup_config():

    with env_stage_testing():
        myconf = Config()
        config_utils.setup_config(myconf, __file__, relative_config_path="config_testfiles")
        assert myconf['MYVAR'] == 1


class TestConfigFinder:

    def setup_method(self):
        self._prev_env_var = os.environ.get(config_utils.ENV_STAGE_VAR)
        os.environ[config_utils.ENV_STAGE_VAR] = "testing"

    def teardown_method(self):
        if self._prev_env_var:
            os.environ[config_utils.ENV_STAGE_VAR] = self._prev_env_var

    def _setup_config(self, tmp_path):
        self.config_dir = tmp_path / "config"
        self.config_dir.mkdir()
        default = self.config_dir / "default.py"
        default.write_text("DEBUG = False")

        local = self.config_dir / "local.py"
        self.config_dir / "__init__.py"
        local.write_text("DEBUG = True")

    def test_get_allowed_stages(self, tmp_path):
        """ Should return a list of allowed stages. """
        self._setup_config(tmp_path)
        finder = config_utils.ConfigFinder(self.config_dir)

        stages = finder.get_allowed_stages()
        assert 'local' in stages
        assert 'default' in stages
        assert '__init__' not in stages

    def test_get_stage(self, tmp_path, capsys):
        """ Should return the stage and print it to stdout. """
        self._setup_config(tmp_path)
        finder = config_utils.ConfigFinder(self.config_dir)

        with fake_env_var(config_utils.ENV_STAGE_VAR, "booyah"):
            assert finder.get_stage() == "booyah"

    def test_no_stage(self, tmp_path, capsys):
        os.environ[config_utils.ENV_STAGE_VAR] = ""
        self._setup_config(tmp_path)
        finder = config_utils.ConfigFinder(self.config_dir)
        with pytest.raises(EnvironmentError):
            finder.get_stage()

    def test_get_config_path(self, tmp_path):
        """ Returns a pathlib.Path object with full path to proper config file. """
        with fake_env_var(config_utils.ENV_STAGE_VAR, "local"):
            self._setup_config(tmp_path)
            finder = config_utils.ConfigFinder(self.config_dir)
            config_path = finder.get_config_path()
            assert config_path.name == 'local.py'
            assert config_path.parent.name == 'config'
            assert config_path.is_absolute()
