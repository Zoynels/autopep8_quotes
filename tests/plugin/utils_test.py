import argparse
from types import SimpleNamespace
from typing import Any
from typing import Dict

import pytest

from autopep8_quotes.plugin import utils
from autopep8_quotes.plugin.manager import PluginManager
from autopep8_quotes.plugin.plugin import FailedToLoadPlugin
from autopep8_quotes.plugin.plugin import __prog__name__


def test_check_re():
    assert utils.check_re(value="abc", search="a", none_is_true=True)
    assert utils.check_re(value="abc", search=["a"], none_is_true=True)
    assert utils.check_re(value="abc", search=["z", "a"], none_is_true=True)
    assert not utils.check_re(value="abc", search=["z", "x"], none_is_true=True)

    assert utils.check_re(value="abc", search="a", none_is_true=True)
    assert utils.check_re(value="abc", search="a", none_is_true=False)
    assert utils.check_re(value="abc", search=None, none_is_true=True)
    assert not utils.check_re(value="abc", search=None, none_is_true=False)
    assert not utils.check_re(value=None, search="a", none_is_true=True)
    assert not utils.check_re(value=None, search="a", none_is_true=False)
    assert utils.check_re(value=None, search=None, none_is_true=True)
    assert utils.check_re(value=None, search=None, none_is_true=False)


def test_check_equal():
    assert utils.check_equal(value="abc", search="abc", none_is_true=True)
    assert utils.check_equal(value="abc", search=["abc"], none_is_true=True)
    assert utils.check_equal(value="abc", search=["z", "abc"], none_is_true=True)
    assert not utils.check_equal(value="abc", search=["z", "x"], none_is_true=True)

    assert utils.check_equal(value="abc", search="abc", none_is_true=True)
    assert utils.check_equal(value="abc", search="abc", none_is_true=False)
    assert utils.check_equal(value="abc", search=None, none_is_true=True)
    assert not utils.check_equal(value="abc", search=None, none_is_true=False)
    assert not utils.check_equal(value=None, search="abc", none_is_true=True)
    assert not utils.check_equal(value=None, search="abc", none_is_true=False)
    assert utils.check_equal(value=None, search=None, none_is_true=True)
    assert utils.check_equal(value=None, search=None, none_is_true=False)


def test_to_list():
    a = SimpleNamespace()
    a.tester = "123"
    assert utils.to_list(value=None) == [None]
    assert utils.to_list(value=[None]) == [None]
    assert utils.to_list(value="abc") == ["abc"]
    assert utils.to_list(value=["a", "b", "c"]) == ["a", "b", "c"]

    assert utils.to_list(dict_to_keys=True, value=a) == list(a.__dict__.keys())
    assert utils.to_list(dict_to_keys=False, value=a) == list(a.__dict__)
    assert utils.to_list(dict_to_keys=True, value=a.__dict__) == list(a.__dict__.keys())
    assert utils.to_list(dict_to_keys=False, value=a.__dict__) == list(a.__dict__)


def test_get_module():
    a = PluginManager()
    a.load_local(["Local:MyTestPlugin1 = plugin._plugin1:formatter"], path="..")
    a.load_local(["Local:MyTestPlugin2 = plugin._plugin2:formatter"], path="..")
    assert utils.get_module(a.plugins["Local:MyTestPlugin1"].plugin).__version__ == "1.0.0"

    s = "some text"
    assert utils.get_module(s) is None


def test_():
    pass
