import json
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

import pytest  # type: ignore

from autopep8_quotes.args import agrs_parse
from autopep8_quotes._util._args import parse_startup
from autopep8_quotes._util._args import str2bool
from autopep8_quotes._util._args import str2bool_dict

testdata_str2bool = []
testdata_str2bool.append(("YES", True))
testdata_str2bool.append(("TrUe", True))
testdata_str2bool.append(("t", True))
testdata_str2bool.append(("y", True))
testdata_str2bool.append(("1", True))
testdata_str2bool.append(("NO", False))
testdata_str2bool.append(("FaLsE", False))
testdata_str2bool.append(("f", False))
testdata_str2bool.append(("n", False))
testdata_str2bool.append(("0", False))
testdata_str2bool.append(("anythigs", False))


@pytest.mark.basic  # type: ignore
@pytest.mark.parametrize("bool_value,expect", testdata_str2bool)  # type: ignore
def test_str2bool(bool_value: Any, expect: bool) -> None:
    assert str2bool(bool_value) == expect


@pytest.mark.basic  # type: ignore
def test_str2bool_dict() -> None:
    _dict1: Dict[str, Any] = {}
    _dict2: Dict[str, Any] = {}
    _dict3: Dict[str, Any] = {}

    _dict1["text_01"] = "False"
    _dict2["text_01"] = "1"
    _dict3["text_01"] = "1"

    _dict1["text_02"] = True
    _dict2["text_02"] = "false"
    _dict3["text_02"] = False

    _dict1["text_03"] = True
    _dict2["text_03"] = "no"
    _dict3["text_03"] = False

    _dict1["text_04"] = False
    _dict2["text_04"] = "1"
    _dict3["text_04"] = True

    _dict1["text_05"] = True
    _dict2["text_05"] = None
    _dict3["text_05"] = False

    str2bool_dict(_dict1, _dict2)
    assert _dict2["text_01"] == _dict3["text_01"]
    assert _dict2["text_02"] == _dict3["text_02"]
    assert _dict2["text_03"] == _dict3["text_03"]
    assert _dict2["text_04"] == _dict3["text_04"]
    assert _dict2["text_05"] == _dict3["text_05"]


@pytest.mark.basic  # type: ignore
def test_parse_startup() -> None:
    # For check/save changes there should be such scenario:
    # 1. Check all files: is there any need of changes (print files that need changes)
    # 2. Save diff into file
    # 3. Print diff into terminal
    # 4. Make changes into independent file
    # 5. Make changes into source file (rewrite it)
    # 6. Check all files: is there any need of changes (Exit code 1)

    class SimpleFallback():
        def __getattr__(self, name: str) -> Any:
            return SimpleFallback
        @property
        def loaded(self) -> Any:
            return SimpleFallback
        @property
        def apply(self) -> Any:
            return SimpleFallback()
    
    args = SimpleNamespace()
    args.__dict__["plugin_order_onfile_first"] = '''check-soft[{"a":"1"}];check-soft[{"z":"0"}];check-soft;diff-to-txt;diff'''
    args.__dict__["plugin_order_onfile_last"] = "new-file;in-place;check-hard"
    args.__dict__["plugin_order_ontoken_first"] = "check;remove-string-u-prefix;lowercase-string-prefix"
    args.__dict__["plugin_order_ontoken_last"] = "normalize-string-quotes"
    
    args.__dict__["_plugins"] = {}
    args.__dict__["_plugins"]["formatter"] = {
        "mod.path:remove_string_u_prefix": SimpleFallback().remove_string_u_prefix,
        "mod.path:lowercase_string_prefix": SimpleFallback().lowercase_string_prefix,
        "mod.path:normalize_string_quotes": SimpleFallback().normalize_string_quotes,
        "mod.path:something_else_formatter": SimpleFallback().something_else_formatter,
        "mod.path:something_same": SimpleFallback().something_same,
    }
    args.__dict__["_plugins"]["saver"] = {
        "mod.path:check_soft": SimpleFallback().check_soft,
        "mod.path:check_hard": SimpleFallback().check_soft,
        "mod.path:diff_to_txt": SimpleFallback().diff_to_txt,
        "mod.path:diff": SimpleFallback().diff,
        "mod.path:new_file": SimpleFallback().new_file,
        "mod.path:in_place": SimpleFallback().in_place,
        "mod.path:check": SimpleFallback().check,
        "mod.path:something_else_saver": SimpleFallback().something_else_saver,
        "mod.path:something_same": SimpleFallback().something_same,
    }
    
    m_search = []
    m_search.append("plugin_order_onfile_first")
    m_search.append("plugin_order_onfile_last")
    m_search.append("plugin_order_ontoken_first")
    m_search.append("plugin_order_ontoken_last")
    
    parse_startup(args, "plugin_order_onfile", ["formatter", "saver"], m_search)
    parse_startup(args, "plugin_order_ontoken", ["formatter", "saver"], m_search)

    #for x in args._plugin_order_onfile_order:
    #    print(x["name"], x["kwargs"])

    # Have result of function
    dictA_str = """[
    {
        "mod_path": "mod.path:check_soft",
        "kwargs": {
            "a": "1"
        },
        "name": "check_soft",
        "start": "_plugin_order_onfile_first"
    },
    {
        "mod_path": "mod.path:check_soft",
        "kwargs": {
            "z": "0"
        },
        "name": "check_soft",
        "start": "_plugin_order_onfile_first"
    },
    {
        "mod_path": "mod.path:check_soft",
        "kwargs": {},
        "name": "check_soft",
        "start": "_plugin_order_onfile_first"
    },
    {
        "mod_path": "mod.path:diff_to_txt",
        "kwargs": {},
        "name": "diff_to_txt",
        "start": "_plugin_order_onfile_first"
    },
    {
        "mod_path": "mod.path:diff",
        "kwargs": {},
        "name": "diff",
        "start": "_plugin_order_onfile_first"
    },
    {
        "mod_path": "mod.path:something_else_formatter",
        "kwargs": {},
        "name": "mod.path:something_else_formatter",
        "start": "_plugin_order_onfile_med"
    },
    {
        "mod_path": "mod.path:something_same",
        "kwargs": {},
        "name": "mod.path:something_same",
        "start": "_plugin_order_onfile_med"
    },
    {
        "mod_path": "mod.path:something_else_saver",
        "kwargs": {},
        "name": "mod.path:something_else_saver",
        "start": "_plugin_order_onfile_med"
    },
    {
        "mod_path": "mod.path:new_file",
        "kwargs": {},
        "name": "new_file",
        "start": "_plugin_order_onfile_last"
    },
    {
        "mod_path": "mod.path:in_place",
        "kwargs": {},
        "name": "in_place",
        "start": "_plugin_order_onfile_last"
    },
    {
        "mod_path": "mod.path:check_hard",
        "kwargs": {},
        "name": "check_hard",
        "start": "_plugin_order_onfile_last"
    }
]"""
    res: List[Any] = []

    for x in args._plugin_order_onfile_order:
        x.loaded = "<property object at 0x0000000000000000>"
        x.apply = "<property object at 0x0000000000000000>"
        t = {}
        t["mod_path"] = x.mod_path
        t["kwargs"] = x.kwargs
        t["name"] = x.name
        t["start"] = x.start
        res.append(t)
    dictB_str = json.dumps(res, indent=4, sort_keys=False)
    assert dictA_str == dictB_str


@pytest.mark.basic  # type: ignore
def test_agrs_parse_v1() -> None:
    argv = []
    argv.append("--HAHAHAH_remaining_argv_AHAHAHA")
    args = agrs_parse(argv=argv)


@pytest.mark.basic  # type: ignore
def test_agrs_parse_v2() -> None:
    argv = []
    argv.append("--show-args")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        args = agrs_parse(argv=argv)
    assert pytest_wrapped_e.type == SystemExit
    errcode = 0
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.basic  # type: ignore
def test_agrs_parse_v3() -> None:
    argv = []
    argv.append("--config-file=tests/config_test.ini")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        args = agrs_parse(argv=argv)
    assert pytest_wrapped_e.type == SystemExit
    errcode = 0
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.basic  # type: ignore
def test_agrs_parse_v4() -> None:
    argv = []
    argv.append("--autodetect-config-file=tests/")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        args = agrs_parse(argv=argv)
    assert pytest_wrapped_e.type == SystemExit
    errcode = 0
    assert pytest_wrapped_e.value.code == 0
