import json
from types import SimpleNamespace
from typing import Any
from typing import Dict

import pytest  # type: ignore

from autopep8_quotes.args import agrs_parse
from autopep8_quotes.args import parse_startup
from autopep8_quotes.args import str2bool
from autopep8_quotes.args import str2bool_dict

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
    args = SimpleNamespace()
    args.__dict__["start_save_first"] = "check-only[{'sometext':'aha'}];new-file;check-only"
    args.__dict__["start_save_last"] = "in-place;check"
    args.__dict__["_modules_dict"] = {
        "mod/check_only": "somemodule",
        "mod/new_file": "somemodule",
        "mod/in_place": "somemodule",
        "mod/check": "somemodule",
        "mod/somethingelse": "somemodule",
    }

    parse_startup(args, "start_save")

    # Have result of function
    res = [
        {"mod_path": "mod/check_only", "module": "somemodule", "name": "check_only", "kwargs": {"sometext": "aha"}, "start": "_start_save_first"},
        {"mod_path": "mod/new_file", "module": "somemodule", "name": "new_file", "kwargs": {}, "start": "_start_save_first"},
        {"mod_path": "mod/check_only", "module": "somemodule", "name": "check_only", "kwargs": {}, "start": "_start_save_first"},
        {"mod_path": "mod/somethingelse", "module": "somemodule", "name": "check", "kwargs": {}, "start": "_start_save_med"},
        {"mod_path": "mod/in_place", "module": "somemodule", "name": "in_place", "kwargs": {}, "start": "_start_save_last"},
        {"mod_path": "mod/check", "module": "somemodule", "name": "check", "kwargs": {}, "start": "_start_save_last"}
    ]

    dictA_str = json.dumps(res, sort_keys=True)
    dictB_str = json.dumps(args._start_save_order, sort_keys=True)
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
