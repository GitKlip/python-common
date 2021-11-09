""" config utils

config system uses the default.py config file as base.  it then will overlay
any settings from the config file that matches the ENV_STAGE setting.
(local.py,dev.py,staging.py, etc)
"""
import configparser
import os
from pathlib import Path

ENV_STAGE_VAR = "ENV_STAGE"
PYPROJECT_FILENAME = "pyproject.toml"


def setup_config(config, current_file_path, relative_config_path="config"):
    """ Sets up a flask-like config object with config-file variables.

    Example:
        # given this kind of file structure:
        # myproject
        #  ├── README.md
        #  └── myproject
        #      ├── app.py
        #      └── config
        #          ├── dev.py
        #          ├── testing.py
        #          └── production.py

        # And working inside app.py

        from common.config_utils import setup_config

        app = Flask(__name__)
        setup_config(app.config, __file__)

    If the structure is different just change relative_config_path

    Args:
        config (Config): A Flask app config file or common.config.Config object or
            something that responds to `from_pyfile`
        current_file_path (str): Typically __file__ from the invoking python file.
        relative_config_path (str): The path relative to current_file_path
            where the config directory is found.  The config directory is the one
            housing different environment files.
    """
    project_path = Path(os.path.dirname(os.path.realpath(current_file_path)))
    config_dir = project_path.joinpath(relative_config_path)
    config_file_path = ConfigFinder(config_dir).get_config_path()
    config.from_pyfile(str(config_file_path))


def find_repo_root(filename):
    """ Walks up the path heirarchy from here until no __init__.py.

    Args:
      filename (str): Typically will be __file__ (of the caller).

    Returns:
      (Path): A pathlib.Path object.
    """
    path = os.path.realpath(filename)
    dir_path = path if os.path.isdir(str(path)) else os.path.dirname(path)
    path = Path(dir_path)
    return next((parent for parent in [path, *path.parents] if not parent.joinpath("__init__.py").exists()))


def get_pyproject_config(some_path=None, filename_=PYPROJECT_FILENAME):
    """ Returns a ConfigParser instance for the pyproject.toml.

    Args:
      some_path (str): A path inside the package of interest.  If none
        provided, then uses os.getcwd().  __file__ is helpful if you merely
        want the package for wherever you are coding (as opposed to wherever
        you are at during execution.)
      filename (str): The name of the configuration file.
    """
    config = configparser.ConfigParser()

    some_path = some_path or os.getcwd()
    repo_root_path = find_repo_root(some_path)
    pyproject_config = repo_root_path.joinpath(filename_)
    config.read(str(pyproject_config))
    return config


def get_project_name(some_path=None):
    """ Returns the name of the project under the 'name' of the tool.poetry section.

    Args:
      some_path (str): A path inside the package of interest.  If none
        provided, then uses os.getcwd().  Use __file__ if you merely want the
        package for wherever you are coding (as opposed to wherever you are at
        during execution, which is the default)
    """
    config = get_pyproject_config(some_path)
    return config["tool.poetry"]["name"].strip('"\'')


class ConfigFinder:
    def __init__(self, config_path):
        """
        Args:
          config_path (pathlib.Path): the config directory as Path object.
        """
        self.config_path = config_path

    def get_allowed_stages(self):
        return [path.stem for path in self.config_path.glob("*.py") if not str(path.stem).startswith("_")]

    def get_stage(self):
        ENV_STAGE = os.environ.get(ENV_STAGE_VAR)
        if not ENV_STAGE:
            raise EnvironmentError(
                f'$ENV_STAGE is required. Allowed values are {self.get_allowed_stages()}.  export ENV_STAGE=<value>'
            )
        return ENV_STAGE

    def get_config_path(self, env_stage=None):
        """
        Args:
          env_stage (str): One of the allowed stages from get_allowed_stages().

        Returns:
          (pathlib.Path): A resolved path to the config file (which is
          guaranteed to exist).
        """
        env_stage = env_stage or self.get_stage()
        config_file = self.config_path.joinpath(f"{env_stage}.py")
        config_file_abs = config_file.resolve()
        if not config_file_abs.exists():
            raise FileNotFoundError(f'unable to find config file: [{str(config_file_abs)}]')
        return config_file_abs
