import os
from importlib import import_module
from tests import config_testfiles

from common.config import Config

CONFIG_TESTFILES_DIR = "config_testfiles"
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_TESTFILES_PATH = os.path.join(THIS_DIR, CONFIG_TESTFILES_DIR)


class BasicConfigTestBase:

    def setup_method(self, method):
        self._os_environ_env_stage_before = os.environ.get('ENV_STAGE', '')
        os.environ['ENV_STAGE'] = 'testing'

        self.config = Config(config_root=CONFIG_TESTFILES_PATH)
        self.absolute_path = os.path.join(CONFIG_TESTFILES_PATH, "dev.py")
        self.relative_path = "dev.py"

    def _assert_dev_config(self, config):
        assert config['MY_VAR'] == 'wonderful'
        assert config['MY_VAR2'] == 23
        assert 'private_variable' not in config

    def teardown_method(self):
        os.environ['ENV_STAGE'] = self._os_environ_env_stage_before


class TestUpdatingConfig(BasicConfigTestBase):
    """ Test updating config from different sources. """

    def test_from_pyfile_absolute(self):
        """ Should load up the config object. """
        self.config.from_pyfile(self.absolute_path)
        self._assert_dev_config(self.config)

    def test_from_pyfile_relative(self):
        """ Should load up the config object. """
        self.config.from_pyfile(self.relative_path)
        self._assert_dev_config(self.config)

    def test_from_envvar_absolute(self):
        """ Should load up the config object. """
        os.environ["CONFIG_FILE_LOCATION"] = self.absolute_path
        self.config.from_envvar("CONFIG_FILE_LOCATION")
        self._assert_dev_config(self.config)

    def test_from_envvar_relative(self):
        """ Should load up the config object. """
        os.environ["CONFIG_FILE_LOCATION"] = self.relative_path
        self.config.from_envvar("CONFIG_FILE_LOCATION")
        self._assert_dev_config(self.config)

    def test_from_object_a_module_string(self):
        """ Should import the module. """
        dev_module_str = f"tests.{CONFIG_TESTFILES_DIR}.dev"
        self.config.from_object(dev_module_str)
        self._assert_dev_config(self.config)

    def test_from_object_a_module(self):
        """ Should import the module. """
        import tests.config_testfiles.dev as dev_module
        self.config.from_object(dev_module)
        self._assert_dev_config(self.config)

    def test_from_mapping(self):
        """ Should import the dict and/or kwargs. """
        data = dict(MY_VAR='wonderful', private_variable='invisible')
        self.config.from_mapping(data, MY_VAR2=23)
        self._assert_dev_config(self.config)


class TestNamespace(BasicConfigTestBase):
    """ Test the ability to namespace variables. """

    def test_get_namespace(self):
        """ Should return a dictionary of that namespace with default lowercase and trimmed. """
        # load up the config
        self.config.from_pyfile(self.relative_path)
        my_vars = self.config.get_namespace("MY_")
        assert my_vars == {'var': 'wonderful', 'var2': 23}


class TestConfigFromEnvStage(BasicConfigTestBase):

    def setup_method(self):
        self.original_value = os.environ.get("ENV_STAGE")
        os.environ["ENV_STAGE"] = "dev"
        self.config = Config.new_from_env_stage(CONFIG_TESTFILES_PATH)

    def teardown_method(self):
        if self.original_value is None:
            os.environ.pop('ENV_STAGE')
        else:
            os.environ['ENV_STAGE'] = self.original_value

    def test_env_stage(self):
        """ Should set the config based on the value of this env variable. """
        self._assert_dev_config(self.config)

    def test_injects_env_stage(self):
        """ Should add "ENV_STAGE" to the config. """
        self._assert_dev_config(self.config)
        assert self.config['ENV_STAGE'] == 'dev'

    def test_using_module_from_import(self):
        """ Can specify the root with a dot path. """
        config = Config.new_from_env_stage(config_testfiles)
        self._assert_dev_config(config)

    def test_using_importlib_module(self):
        module = import_module('tests.config_testfiles')
        config = Config.new_from_env_stage(module)
        self._assert_dev_config(config)
        """ Can specify the root with a dot path. """
        module = import_module('tests.config_testfiles')
        config = Config.new_from_env_stage(config_testfiles)
        self._assert_dev_config(config)
