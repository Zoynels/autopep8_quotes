from types import SimpleNamespace
from typing import Any
from typing import Dict
import argparse
from types import SimpleNamespace


from autopep8_quotes.plugin.manager import PluginManager
from autopep8_quotes.plugin.plugin import FailedToLoadPlugin, __prog__name__
from autopep8_quotes.plugin import utils

import pytest

def test_global():
    # Load by adding new plugins
    a = PluginManager()
    a.load_global(namespace="setuptools.installation")
    # Check
    L = []
    assert list(a.select_by(stype="all", namespace="").keys()) == L
    assert list(a.select_by().keys()) != L


def test_global_map():
    # Load by adding new plugins
    a = PluginManager()
    a.load_global(namespace="autopep8_quotes.formatter")
    a.load_global(namespace="autopep8_quotes.saver")

    a.map_all(func="show_or_save", args=SimpleNamespace(), source="", formatted_source="")
    


def test_load_onestep():
    # Load by one step
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter", "Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    # Check ALL
    L = ['Local:MyTestPlugin1', 'Local:MyTestPlugin2']
    assert list(a.select_by(stype="all", namespace="").keys()) == L


def test_load_twostep():
    # Load by adding new plugins
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    # Check
    L = ['Local:MyTestPlugin1', 'Local:MyTestPlugin2']
    assert list(a.select_by(stype="all", namespace="").keys()) == L

def test_load_not_callable(capsys, caplog):
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin3 = plugin._plugin3_not_callable:formatter"], path="..")

    with pytest.raises(FailedToLoadPlugin) as pytest_wrapped_e:
        a.plugins["Local:MyTestPlugin3"].load_plugin()
    errcode = f"Plugin 'some string' is not a callable. It might be written for an older version of {__prog__name__} and might not work with this version"
    assert str(pytest_wrapped_e.value.args[1]) == errcode

    __prog__name__
    L = []
    L.append(["CRITICAL", f"""Plugin 'some string' is not a callable. It might be written for an older version of {__prog__name__} and might not work with this version"""])
    L.append(["ERROR", f"""Plugin 'some string' is not a callable. It might be written for an older version of {__prog__name__} and might not work with this version"""])
    L.append(["CRITICAL", f"""{__prog__name__} failed to load plugin "Local:MyTestPlugin3" due to Plugin 'some string' is not a callable. It might be written for an older version of {__prog__name__} and might not work with this version."""])
    L.append(["ERROR", f"""{__prog__name__} failed to load plugin "Local:MyTestPlugin3" due to Plugin 'some string' is not a callable. It might be written for an older version of {__prog__name__} and might not work with this version."""])
    for i, record in enumerate(caplog.records):
        assert record.levelname == L[i][0]
        assert str(record.message) == L[i][1]



def test_load_not_exist():
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")
    a.load_local(["Unexistent string for entry_point"], path="..")

    # Check
    L = ['Local:MyTestPlugin1', 'Local:MyTestPlugin2']
    assert list(a.select_by().keys()) == L



def test_select_by():
    # Load by one step
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    # Check ALL
    L = ['Local:MyTestPlugin1', 'Local:MyTestPlugin2']
    assert list(a.select_by(stype="all", namespace="").keys()) == L

    # Check ANY
    L = ['Local:MyTestPlugin1', 'Local:MyTestPlugin2']
    assert list(a.select_by(stype="any", name_re="Local:MyTestPlugin", name="Local:MyTestPlugin2").keys()) == L

    # Select without conditions
    L = ["Local:MyTestPlugin1", "Local:MyTestPlugin2"]
    assert L == list(a.select_by(stype="all").keys())
    assert L == list(a.select_by(stype="any").keys())
    assert L == list(a.select_by().keys())


def test_group():
    a = PluginManager()
    a.load_local(["Local:MyTest.Plugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTest.Plugin2 = plugin._plugin2:formatter"], path="..")
    assert a.plugins["Local:MyTest.Plugin1"].is_in_a_group()
    assert a.plugins["Local:MyTest.Plugin2"].is_in_a_group()
    assert a.plugins["Local:MyTest.Plugin1"].group == "Local:MyTest"
    assert a.plugins["Local:MyTest.Plugin2"].group == "Local:MyTest"

def test_to_dictionary():
    a = PluginManager()
    a.load_local(["Local:MyTest.Plugin1 = plugin._plugin1:formatter"], path="..", label="123")

    assert list(a.plugins["Local:MyTest.Plugin1"].to_dictionary().keys()) == ['namespace', 'name', 'label', 'parameters', 'parameter_names', 'plugin', 'plugin_name', 'group']

    _dict = a.plugins["Local:MyTest.Plugin1"].to_dictionary()
    assert _dict["name"] == "Local:MyTest.Plugin1"
    assert _dict["namespace"] == ""
    assert _dict["label"] == "123"
    assert _dict["parameter_names"] == []
    assert _dict["plugin_name"] == "Local:MyTest"
    assert _dict["group"] == "Local:MyTest"


def test_argparse(capsys):
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    parser = argparse.ArgumentParser(
        description="some description",
        prog="some prog",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True)

    # Add args and default args
    a.plugins["Local:MyTestPlugin1"].load_plugin()
    b = a.plugins["Local:MyTestPlugin1"]
    b.register_CLI_args(parser)
    assert "--test_plugin_num1_ha" in parser._option_string_actions
    assert parser.get_default("test_plugin_num1_ha")

    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 CLI__add_argument\n"
    assert captured.err == ""

    b.register_CLI_default_args(parser)
    assert not parser.get_default("test_plugin_num1_ha")

    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 CLI__set_defaults\n"
    assert captured.err == ""


    captured = capsys.readouterr()

    # CONFIG parser
    b.register_CONFIG_args(parser)
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 CONFIG__add_argument\n"
    assert captured.err == ""

    b.register_CONFIG_default_args(parser)
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 CONFIG__set_defaults\n"
    assert captured.err == ""


def test_map_all(capsys, caplog):
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    captured = capsys.readouterr()

    # map function of plugin class
    captured = capsys.readouterr()
    for x in a.map(func="parse", leaf="somestr", args=SimpleNamespace(), token_dict={}):
        assert x == "somestr"
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 parse\nTestPlugin2 parse\n"
    assert captured.err == ""

    # map_all function of plugin class which is exist
    captured = capsys.readouterr()
    a.map_all(func="parse", leaf="somestr", args=SimpleNamespace(), token_dict={})
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin1 parse\nTestPlugin2 parse\n"
    assert captured.err == ""


    # map_all function of plugin class which is not exist
    captured = capsys.readouterr()
    a.map_all(func="parse_not_exist", leaf="somestr", args=SimpleNamespace(), token_dict={})
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    L = []
    L.append(["WARNING", """Can't run for plugin Plugin(name=Local:MyTestPlugin1, entry_point=EntryPoint('Local:MyTestPlugin1', 'plugin._plugin1', 'formatter', None)) function parse_not_exist."""])
    L.append(["WARNING", """Can't run for plugin Plugin(name=Local:MyTestPlugin2, entry_point=EntryPoint('Local:MyTestPlugin2', 'plugin._plugin2', 'formatter', None)) function parse_not_exist."""])
    for i, record in enumerate(caplog.records):
        assert record.levelname == L[i][0]
        assert record.message == L[i][1]
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


    # map external function with plugin as argument
    captured = capsys.readouterr()
    def mapfunc(plugin, *args, **kwargs):
        print("Run mapfunc", plugin.name)
        return kwargs["a"] + kwargs["b"]
    for x in a.map(func=mapfunc, a=1, b=2):
        assert x == 3
    captured = capsys.readouterr()
    assert captured.out == "Run mapfunc Local:MyTestPlugin1\n" + "Run mapfunc Local:MyTestPlugin2\n"
    assert captured.err == ""

    # map_all external function with plugin as argument
    captured = capsys.readouterr()
    def mapfunc(plugin, *args, **kwargs):
        print("Run mapfunc", plugin.name)
        return kwargs["a"] + kwargs["b"]
    res = a.map_all(func=mapfunc, a=1, b=2)
    assert res == [3, 3]
    captured = capsys.readouterr()
    assert captured.out == "Run mapfunc Local:MyTestPlugin1\n" + "Run mapfunc Local:MyTestPlugin2\n"
    assert captured.err == ""


    # map_all with partial selection
    captured = capsys.readouterr()
    names = a.select_by(stype="all", name="Local:MyTestPlugin2")
    a.map_all(func="parse", names=names, leaf="somestr", args=SimpleNamespace(), token_dict={})
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin2 parse\n"
    assert captured.err == ""

    # map_all with partial selection with regex search
    captured = capsys.readouterr()
    names = a.select_by(stype="all", name="Local:MyTestPlugin2", name_re="MyTestPlugin2")
    a.map_all(func="parse", names=names, leaf="somestr", args=SimpleNamespace(), token_dict={})
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin2 parse\n"
    assert captured.err == ""

    # with unknown plugin name
    captured = capsys.readouterr()
    names = ["Local:MyTestPlugin2", "undefined name"]
    a.map_all(func="parse", names=names, leaf="somestr", args=SimpleNamespace(), token_dict={})
    captured = capsys.readouterr()
    assert captured.out == "TestPlugin2 parse\n"
    assert captured.err == ""



def test_version():
    a = PluginManager()
    a.load_local(["Local:MyTest.Plugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTest.Plugin2 = plugin._plugin2:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")

    assert list(a.versions()) == [('Local:MyTest', '1.0.0'), ('TestPlugin2', '2.0.0')]

    assert a.plugins["Local:MyTest.Plugin1"].version_for(a.plugins["Local:MyTest.Plugin1"]) == "1.0.0"
    assert a.plugins["Local:MyTest.Plugin2"].version_for(a.plugins["Local:MyTest.Plugin2"]) == "2.0.0"
    assert a.plugins["Local:MyTestPlugin2"].version_for(a.plugins["Local:MyTestPlugin2"]) == "2.0.0"


def test_repr():
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")
    assert repr(a.plugins["Local:MyTestPlugin1"]) == """Plugin(name=Local:MyTestPlugin1, entry_point=EntryPoint('Local:MyTestPlugin1', 'plugin._plugin1', 'formatter', None))"""

