import os
from typing import Any

import pytest  # type: ignore

from autopep8_quotes import _main


def write_changeable_string(fname: str) -> None:
    test_str = b"""
        a = ""\"A""\"
        b = '''B'''
        c = "C"
        d = 'D'
        e = ""
        f = ''
        g= ""\"""\"
        h = ''''''
        Z = ""
        z = Z
    """
    with open(fname, "wb") as file:
        file.write(test_str)


def remove_file(fname: str) -> None:
    if os.path.isfile(fname):
        os.remove(fname)
    if os.path.isfile(fname + ".autopep8_quotes"):
        os.remove(fname + ".autopep8_quotes")


def pytest_generate_tests(metafunc: Any) -> None:
    fix = {}
    fix["standard_out"] = ["sys.stdout"]
    fix["standard_error"] = ["sys.stderr"]

    fname = "tests/good/tests_002_raw.py"
    argv_1 = ["--save-values-to-file", "--debug", "--diff", "--diff-to-txt", "--new-file", "--in-place", "--check", "--recursive", f"--files={fname}"]
    fix["args"] = []
    fix["args"].append(argv_1)  # type: ignore

    for key in fix:
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, fix[key])


@pytest.mark.basic  # type: ignore
def test__main(args: Any, standard_out: Any, standard_error: Any) -> None:
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)


@pytest.mark.basic  # type: ignore
def test__main_base(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/tests_changeable_string_BASE.py"
    write_changeable_string(fname)

    # Hard check: need changes Exit
    args = ["--check-hard", f"--files={fname}"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    assert pytest_wrapped_e.type == SystemExit
    errcode = f"Error: --check-hard: need changes in file: {fname}"
    assert pytest_wrapped_e.value.code == errcode

    # Soft check: need changes
    args = ["--diff", "--diff-to-txt", "--new-file", "--in-place", "--check-soft", f"--files={fname}"]
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)

    # Hard check: no need changes
    args = ["--check-hard", f"--files={fname}"]
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    remove_file(fname)


@pytest.mark.basic  # type: ignore
def test__main_exit_v1(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/tests_changeable_string_EXIT.py"
    write_changeable_string(fname)

    args = ["--check-hard", f"--files={fname}"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    assert pytest_wrapped_e.type == SystemExit
    errcode = f"Error: --check-hard: need changes in file: {fname}"
    assert pytest_wrapped_e.value.code == errcode
    remove_file(fname)


@pytest.mark.basic  # type: ignore
def test__main_exit_not_recursive(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/"

    args = ["--check-soft", f"--files={fname}"]
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    remove_file(fname)


@pytest.mark.basic  # type: ignore
def test__main_exit_recursive(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/"

    args = ["--check-soft", "--recursive", f"--files={fname}"]
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    remove_file(fname)


@pytest.mark.basic  # type: ignore
def test__main_no_file(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/tests_changeable_string_EXIT.py"
    remove_file(fname)

    args = ["--check-hard", f"--files={fname}"]
    with pytest.raises(ValueError) as pytest_wrapped_e:
        res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    errcode = f"File is not exist: {fname}"
    assert pytest_wrapped_e.value.args[0] == errcode


@pytest.mark.basic  # type: ignore
def test__main_show_args(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/tests_changeable_string_EXIT.py"
    write_changeable_string(fname)

    args = ["--show-args", f"--files={fname}"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    assert pytest_wrapped_e.type == SystemExit
    errcode = 0
    assert pytest_wrapped_e.value.code == 0
    remove_file(fname)


@pytest.mark.basic  # type: ignore
def test__main_remaining_argv(standard_out: Any, standard_error: Any) -> None:
    fname = "tests/good/tests_changeable_string_EXIT.py"
    write_changeable_string(fname)

    args = []
    args.append("--HAHAHAH_remaining_argv_AHAHAHA")
    args.append(f"--files={fname}")
    res = _main(args=args, standard_out=standard_out, standard_error=standard_error)
    remove_file(fname)
