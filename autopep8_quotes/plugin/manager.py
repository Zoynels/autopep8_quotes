import entrypoints
import sys, pathlib, re
from types import SimpleNamespace
from . import utils

from .plugin import Plugin
import logging
LOG = logging.getLogger(__name__)

class PluginManager(object):
    """Find and manage plugins consistently.
    https://gitlab.com/pycqa/flake8 (MIT)

    Another ideas could be found (but not used):
    https://github.com/benhoff/pluginmanager
    https://stackoverflow.com/questions/7417997/plugin-manager-in-python
    https://gist.github.com/mepcotterell/6004997
    """

    def __init__(self):
        """Initialize the manager."""
        self.plugins = {}  # type: Dict[str, Plugin]
        self.names = []  # type: List[str]

    def load_local(self, local_plugins=None, label="", path=""):
        """Load local plugins from config.

        :param list local_plugins:
            Plugins from config (as "X = path.to:Plugin" strings).
        """
        
        self.add_external_path(path)
        for plugin_str in utils.to_list(local_plugins):
            try:
                name, _, entry_str = str(plugin_str).partition("=")
                name, entry_str = name.strip(), entry_str.strip()
                entry_point = entrypoints.EntryPoint.from_string(entry_str, name)
                self._load_plugin_from_entrypoint(entry_point, local=True, namespace="", label=label)
            except:
                LOG.warning(f"Can't load local plugin {plugin_str}")
        return self

    def load_global(self, namespace, label=""):
        """Load plugins from entry point
        
        :param str namespace:
            Namespace of the plugins to manage, e.g., 'flake8.extension'.
        """
        LOG.info('Loading entry-points for "%s".', namespace)
        for entry_point in entrypoints.get_group_all(namespace):
            self._load_plugin_from_entrypoint(entry_point, local=False, namespace=namespace, label=label)
        return self

    def _load_plugin_from_entrypoint(self, entry_point, local=False, namespace="", label=""):
        """Load a plugin from a setuptools EntryPoint.

        :param EntryPoint entry_point:
            EntryPoint to load plugin from.
        :param bool local:
            Is this a repo-local plugin?
        """
        name = entry_point.name
        self.plugins[name] = Plugin(name, entry_point, local=local, namespace=namespace, label=label)
        self.names.append(name)
        LOG.debug('Loaded %r for plugin "%s".', self.plugins[name], name)

    def map(self, func, names=None, *args, **kwargs):
        r"""Call ``func`` with the plugin and \*args and \**kwargs after.

        This yields the return value from ``func`` for each plugin.

        :param collections.Callable func:
            Function to call with each plugin. Signature should at least be:

            .. code-block:: python
                def myfunc(plugin, *args, **kwargs):
                     pass

            or if func is string then
            .. code-block:: python
                plugin().myfunc(*args, **kwargs)


            Any extra positional or keyword arguments specified with map will
            be passed along to this function after the plugin.
        :param names:
            Names of plugins on which function should run.

        :param args:
            Positional arguments to pass to ``func`` after each plugin.
        :param kwargs:
            Keyword arguments to pass to ``func`` after each plugin.
        """
        if names is None:
            names = self.names

        for name in utils.to_list(names):
            if not name in self.plugins:
                continue
            if isinstance(func, str):
                func_run = getattr(self.plugins[name].plugin(), func, None)
                if func_run is None:
                    LOG.warning("Can't run for plugin %r function %s.", self.plugins[name], func)
                    continue
                yield func_run(*args, **kwargs)
            else:
                yield func(self.plugins[name], *args, **kwargs)

    def map_all(self, func, names=None, *args, **kwargs):
        """Execute generator created by map"""
        return list(self.map(func=func, names=names, *args, **kwargs))



    def versions(self):
        # () -> (str, str)
        """Generate the versions of plugins.

        :returns:
            Tuples of the plugin_name and version
        :rtype:
            tuple
        """
        plugins_seen = set()  # type: Set[str]
        for entry_point_name in self.names:
            plugin = self.plugins[entry_point_name]
            plugin_name = plugin.plugin_name
            if plugin.plugin_name in plugins_seen:
                continue
            plugins_seen.add(plugin_name)
            yield (plugin_name, plugin.version)

    def select_by(self, stype="all", **kwargs):
        """Filter plugins by Namespace and another methods
        stype == "any": if any is true of condition then select
        stype == "all": if all is true of condition then select

        kwargs["namespace"]: equal namespace
        kwargs["namespace_re"]: re.match namespace
        and etc.
        """
        if stype.lower().strip() in ["all", "and", "&", "&&"]:
            func_stype = all
        else:
            func_stype = any

        _selected = {}
        for name in self.plugins:
            # set values to compare
            _engines = {}
            _engines["name"] = name
            _engines["namespace"] = self.plugins[name].namespace
            _engines["label"] = self.plugins[name].label

            # compare conditions: parse all kwargs without optimization for "any" condition
            if kwargs:
                _cond = []
            else:
                _cond = [True]

            for k in kwargs:
                kL = k.lower()
                if kL in _engines:
                    if utils.check_equal(value = _engines[kL], search = kwargs[k]):
                        _cond.append(True)
                    else:
                        _cond.append(False)
                if kL.endswith("_re") and kL[:-len("_re")] in _engines:
                    if utils.check_re(value = _engines[kL[:-len("_re")]], search = kwargs[k]):
                        _cond.append(True)
                    else:
                        _cond.append(False)

            if func_stype(_cond):
                _selected[name] = self.plugins[name]

        return  _selected

    def add_external_path(self, path):
        """Extend sys.path to load modules in external locations"""
        for p in utils.to_list(path):
            sys.path.append(pathlib.Path(p).resolve())





