import builtins
import sys
from types import SimpleNamespace

import pytest  # type: ignore

try:
    import colorama  # noqa
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# https://stackoverflow.com/questions/51044068/test-for-import-of-optional-dependencies-in-init-py-with-pytest-python-3-5
@pytest.fixture
def no_module(monkeypatch):
    import_orig = builtins.__import__

    def mocked_import(name, globals, locals, fromlist, level):
        if name == "colorama":
            raise ImportError()
        return import_orig(name, locals, fromlist, level)
    monkeypatch.setattr(builtins, "__import__", mocked_import)


@pytest.fixture(autouse=True)
def cleanup_imports():
    yield
    sys.modules.pop("autopep8_quotes", None)
    sys.modules.pop("autopep8_quotes._util._colorama", None)
    sys.modules.pop("util_colorama", None)

# Error when uncomment and commend skipif
# @pytest.mark.usefixtures('no_module')
@pytest.mark.skipif("HAS_COLORAMA")  # type: ignore
@pytest.mark.skipif("not HAS_COLORAMA")  # type: ignore
def test_module_missing() -> None:
    import autopep8_quotes._util._colorama as util_colorama
    assert isinstance(util_colorama.colorama, SimpleNamespace)


@pytest.mark.skipif("HAS_COLORAMA")  # type: ignore
@pytest.mark.skipif("not HAS_COLORAMA")  # type: ignore
def test_module_missing_v2(monkeypatch) -> None:
    import autopep8_quotes._util._colorama
    import copy
    fakesysmodules = copy.copy(sys.modules)
    fakesysmodules["colorama"] = None
    monkeypatch.delitem(sys.modules, "colorama")
    monkeypatch.setattr("sys.modules", fakesysmodules)
    from importlib import reload
    reload(autopep8_quotes._util._colorama)
    assert isinstance(autopep8_quotes._util._colorama.colorama, SimpleNamespace)


@pytest.mark.skipif("HAS_COLORAMA")  # type: ignore
@pytest.mark.skipif("not HAS_COLORAMA")  # type: ignore
def test_module_available() -> None:
    import autopep8_quotes._util._colorama as util_colorama
    assert not isinstance(util_colorama.colorama, SimpleNamespace)

@pytest.mark.skipif("HAS_COLORAMA")  # type: ignore
@pytest.mark.skipif("not HAS_COLORAMA")  # type: ignore
def test_color_diff() -> None:
    import autopep8_quotes._util._colorama as util_colorama
    lines = []
    lines.append("-  Was string")
    lines.append("+  New string")
    lines.append("^  ^^^")
    assert len(list(util_colorama.color_diff(lines))) == len(lines)
