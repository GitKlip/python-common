""" Code to automatically load config files. """
import errno
import os
import types
from types import ModuleType

from common.config_utils import find_repo_root
from common.import_utils import import_string


class ConfigAttribute(object):
    """ Makes an attribute forward to the config

    Copied from flask/config.py
    """

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.

    Either you can fill the config from a config file::

        app.config.from_pyfile('yourconfig.cfg')

    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::

        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)

    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.

    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::

        app.config.from_envvar('YOURAPPLICATION_SETTINGS')

    In this case before launching the application you have to set this
    environment variable to the file you want to use.  On Linux and OS X
    use the export statement::

        export YOURAPPLICATION_SETTINGS='/path/to/config/file'

    On windows use `set` instead.

    :param config_root_dir: path to which config files are read relative
        from.  By default, this will be `<run-time root directory>/config`
    :param defaults: an optional dictionary of default values

    Copied, with a few modifications, from flask/config.py (see LICENSE.txt)
    """
    DEFAULT_CONFIG_DIR = "config"
    STAGE_VAR = 'ENV_STAGE'

    @classmethod
    def new_from_env_stage(cls, config_root=None, env_stage_var=STAGE_VAR):
        """ Creates a new configuration object by loading the file pointed to by the ENV_STAGE env variable.

        Args:
          config_root (see __init__)
          env_stage_var (str): The name of the variable to use to determine
              the stage.

        Example:
          # assumes that the env variable `ENV_STAGE` is set
          config = Config.new_from_env_stage()
          config['SOME_SETTING']
        """
        config = Config(config_root=config_root)
        config.from_env_stage(env_stage_var)
        return config

    def from_env_stage(self, env_stage_var=STAGE_VAR):
        """ Creates a new configuration object by loading the file pointed to by the ENV_STAGE env variable.

        Example:
          config = Config()
          config.from_env_stage()
          config['SOME_SETTING']
        """
        file_no_ext = os.environ[env_stage_var]
        return_val = self.from_pyfile(f"{file_no_ext}.py")
        self.from_mapping({env_stage_var: file_no_ext})
        return return_val and True

    def __init__(self, config_root=None, defaults=None):
        """

        Args:
          config_root (str or Path or module): Something representing the
            config directory or a file within it.
        """
        dict.__init__(self, defaults or {})

        if config_root is None:
            repo_root = find_repo_root(os.getcwd())
            config_root_path = str(repo_root.joinpath(self.DEFAULT_CONFIG_DIR))

        config_root_path = config_root.__file__ if isinstance(config_root, ModuleType) else str(config_root)

        if os.path.isfile(config_root_path):
            config_root_dir = os.path.dirname(os.path.realpath(config_root_path))
        else:
            config_root_dir = config_root_path
        self.config_root_dir = config_root_dir

    def from_envvar(self, variable_name, silent=False):
        """Loads a configuration from an environment variable pointing to
        a configuration file.  This is basically just a shortcut with nicer
        error messages for this line of code::

            app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: name of the environment variable
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        :return: bool. ``True`` if able to load config, ``False`` otherwise.
        """
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError(
                "The environment variable %r is not set "
                "and as such configuration could not be "
                "loaded.  Set this variable and make it "
                "point to a configuration file" % variable_name
            )
        return self.from_pyfile(rv, silent=silent)

    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         config_root_dir.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.

        .. versionadded:: 0.7
           `silent` parameter.
        """
        filename = os.path.join(self.config_root_dir, filename)
        dir_ = types.ModuleType("config")
        dir_.__file__ = filename
        try:
            with open(filename, mode="rb") as config_file:
                exec(compile(config_file.read(), filename, "exec"), dir_.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        self.from_object(dir_)
        return True

    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:

        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly

        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.

        Example of module-based configuration::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        Nothing is done to the object before loading. If the object is a
        class and has ``@property`` attributes, it needs to be
        instantiated before being passed to this method.

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        See :ref:`config-dev-prod` for an example of class-based configuration
        using :meth:`from_object`.

        :param obj: an import name or object
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.

        .. versionadded:: 0.11
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], "items"):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                "expected at most 1 positional argument, got %d" % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self[key] = value
        return True

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::

            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')

        The resulting dictionary `image_store_config` would look like::

            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }

        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.

        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
                          dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
                          dictionary should not include the namespace

        .. versionadded:: 0.11
        """
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))
