import logging, sys
import collections
LOG = logging.getLogger(__name__)
import inspect
from . import utils
__prog__name__ = "Flake8"
NO_GROUP_FOUND = object()

class FailedToLoadPlugin(Exception):
    """Exception raised when a plugin fails to load."""

    FORMAT = '%(prog_name)s failed to load plugin "%(name)s" due to %(exc)s.'

    def __init__(self, plugin, exception):
        # type: (Plugin, Exception) -> None
        """Initialize our FailedToLoadPlugin exception."""
        self.prog_name = __prog__name__
        self.plugin = plugin
        self.ep_name = self.plugin.name
        self.original_exception = exception
        super(FailedToLoadPlugin, self).__init__(plugin, exception)

    def __str__(self):  # type: () -> str
        """Format our exception message."""
        return self.FORMAT % {
            "prog_name": self.prog_name,
            "name": self.ep_name,
            "exc": self.original_exception,
        }

class Plugin(object):
    """Wrap an EntryPoint from setuptools and other logic."""

    def __init__(self, name, entry_point, local=False, namespace="", label=""):
        """Initialize our Plugin.

        :param str name:
            Name of the entry-point as it was registered with setuptools.
        :param entry_point:
            EntryPoint returned by setuptools.
        :type entry_point:
            setuptools.EntryPoint
        :param bool local:
            Is this a repo-local plugin?
        """
        self.name = name
        self.entry_point = entry_point
        self.local = local
        self.namespace = namespace
        self.label = label
        self._plugin = None  # type: Any
        self._parameters = None
        self._parameter_names = None
        self._group = None
        self._plugin_name = None
        self._version = None

    def __repr__(self):
        """Provide an easy to read description of the current plugin."""
        return f"Plugin(name={self.name}, entry_point={self.entry_point})"

    def to_dictionary(self):
        """Convert this plugin to a dictionary."""
        return {
            "namespace": self.namespace,
            "name": self.name,
            "label": self.label,
            "parameters": self.parameters,
            "parameter_names": self.parameter_names,
            "plugin": self.plugin,
            "plugin_name": self.plugin_name,
            "group": self.group,
        }

    def is_in_a_group(self):
        """Determine if this plugin is in a group.

        :returns:
            True if the plugin is in a group, otherwise False.
        :rtype:
            bool
        """
        return self.group is not None

    @property
    def group(self):
        """Find and parse the group the plugin is in."""
        if self._group is None:
            name = self.name.split(".", 1)
            if len(name) > 1:
                self._group = name[0]
            else:
                self._group = NO_GROUP_FOUND
        if self._group is NO_GROUP_FOUND:
            return None
        return self._group

    @property
    def parameters(self):
        """List of arguments that need to be passed to the plugin."""
        if self._parameters is None:
            self._parameters = self.parameters_for(self)
        return self._parameters

    def parameters_for(self, plugin):
        # type: (Plugin) -> Dict[str, bool]
        """Return the parameters for the plugin.
    
        This will inspect the plugin and return either the function parameters
        if the plugin is a function or the parameters for ``__init__`` after
        ``self`` if the plugin is a class.
    
        :param plugin:
            The internal plugin object.
        :type plugin:
            flake8.plugins.manager.Plugin
        :returns:
            A dictionary mapping the parameter name to whether or not it is
            required (a.k.a., is positional only/does not have a default).
        :rtype:
            dict([(str, bool)])
        """
        func = plugin.plugin
        is_class = not inspect.isfunction(func)
        if is_class:  # The plugin is a class
            func = plugin.plugin.__init__
    
        parameters = collections.OrderedDict(
            [
                (parameter.name, parameter.default is parameter.empty)
                for parameter in inspect.signature(func).parameters.values()
                if parameter.kind == parameter.POSITIONAL_OR_KEYWORD
            ]
        )
    
        if is_class:
            parameters.pop("self", None)
    
        return parameters


    @property
    def parameter_names(self):
        """List of argument names that need to be passed to the plugin."""
        if self._parameter_names is None:
            self._parameter_names = list(self.parameters)
        return self._parameter_names

    @property
    def plugin(self):
        """Load and return the plugin associated with the entry-point.

        This property implicitly loads the plugin and then caches it.
        """
        self.load_plugin()
        return self._plugin

    @property
    def version(self):
        """Return the version of the plugin."""
        if self._version is None:
            if self.is_in_a_group():
                self._version = self.version_for(self)
            else:
                try:
                    self._version = self.plugin.version
                except:
                    self._version = self.version_for(self)

        return self._version

    def version_for(self, plugin):
        # (Plugin) -> Optional[str]
        """Determine the version of a plugin by its module.
    
        :param plugin:
            The loaded plugin
        :type plugin:
            Plugin
        :returns:
            version string for the module
        :rtype:
            str
        """
        return getattr(utils.get_module(self.plugin), "__version__", None)

    @property
    def plugin_name(self):
        """Return the name of the plugin."""
        if self._plugin_name is None:
            if self.is_in_a_group():
                self._plugin_name = self.group
            else:
                self._plugin_name = self.plugin.name

        return self._plugin_name

    def _load(self):
        self._plugin = self.entry_point.load()
        if not callable(self._plugin):
            msg = (
                "Plugin %r is not a callable. It might be written for an older version of %s and might not work with this version" % (self._plugin, __prog__name__)
            )
            LOG.critical(msg)
            raise TypeError(msg)

    def load_plugin(self):
        """Retrieve the plugin for this entry-point.

        This loads the plugin, stores it on the instance and then returns it.
        It does not reload it after the first time, it merely returns the
        cached plugin.

        :returns:
            Nothing
        """
        if self._plugin is None:
            LOG.info('Loading plugin "%s" from entry-point.', self.name)
            try:
                self._load()
            except Exception as load_exception:
                LOG.exception(load_exception)
                failed_to_load = FailedToLoadPlugin(
                    plugin=self, exception=load_exception
                )
                LOG.critical(str(failed_to_load))
                raise failed_to_load



    def register_CLI_args(self, argparser):
        """Register the plugin's command-line arguments.

        :param argparser:
            Instantiated argparse.ArgumentParser to register options on.
        :returns:
            Nothing
        """
        func = getattr(self.plugin, "CLI__add_argument", None)
        if func is not None:
            LOG.debug(
                'Registering options from plugin "%s" on CLI argparser %r',
                self.name,
                argparser,
            )
            self.plugin().CLI__add_argument(argparser)

    def register_CLI_default_args(self, argparser):
        func = getattr(self.plugin, "CLI__set_defaults", None)
        if func is not None:
            LOG.debug(
                'Registering default options from plugin "%s" on CLI argparser %r',
                self.name,
                argparser,
            )
            self.plugin().CLI__set_defaults(argparser)


    def register_CONFIG_args(self, argparser):
        """Register the plugin's command-line arguments.

        :param argparser:
            Instantiated argparse.ArgumentParser to register options on.
        :returns:
            Nothing
        """
        func = getattr(self.plugin, "CONFIG__add_argument", None)
        if func is not None:
            LOG.debug(
                'Registering options from plugin "%s" on CONFIG argparser %r',
                self.name,
                argparser,
            )
            self.plugin().CONFIG__add_argument(argparser)

    def register_CONFIG_default_args(self, argparser):
        func = getattr(self.plugin, "CONFIG__set_defaults", None)
        if func is not None:
            LOG.debug(
                'Registering default options from plugin "%s" on CONFIG argparser %r',
                self.name,
                argparser,
            )
            self.plugin().CONFIG__set_defaults(argparser)
