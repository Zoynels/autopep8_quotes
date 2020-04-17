import io
import os
import sys
from typing import Any
from typing import Pattern
from typing import Union

import pytest  # type: ignore

from autopep8_quotes._util._io import detect_encoding
from autopep8_quotes._util._io import load_modules
from autopep8_quotes._util._io import open_with_encoding
from autopep8_quotes._util._io import stdout_get
from autopep8_quotes._util._io import stdout_print


def pytest_generate_tests(metafunc):
    fix = {}
    fix["value"] = [""]
    fix["otype"] = [None, io.BytesIO, io.BytesIO(), "sys.stdout", "out", "", "sys.stderr", "err", "else", 1, float("inf"), {}, []]
    fix["search_path"] = ["modules/formater", "modules/saver"]
    fix["pat"] = [r".*\.py$"]

    fix["filename"] = []
    for d in ["tests/good/"]:
        for f in os.listdir(d):
            fname = os.path.join(d, f)
            if os.path.isfile(fname) and fname.lower().endswith(".py"):
                fix["filename"].append(fname)
    fix["encoding"] = ["", "utf-8", "latin-1", None]

    # r: Opens the file in read-only mode. Starts reading from the beginning of the file and is the default mode for the open() function.
    # rb: Opens the file as read-only in binary format and starts reading from the beginning of the file.
    # While binary format can be used for different purposes, it is usually used when dealing with things like images, videos, etc.
    # r+: Opens a file for reading and writing, placing the pointer at the beginning of the file.
    # w: Opens in write-only mode. The pointer is placed at the beginning of the file and this will overwrite
    # any existing file with the same name. It will create a new file if one with the same name doesn't exist.
    # wb: Opens a write-only file in binary mode.
    # w+: Opens a file for writing and reading.
    # wb+: Opens a file for writing and reading in binary mode.
    # a: Opens a file for appending new information to it. The pointer is placed at the end of the file.
    # A new file is created if one with the same name doesn't exist.
    # ab: Opens a file for appending in binary mode.
    # a+: Opens a file for both appending and reading.
    # ab+: Opens a file for both appending and reading in binary mode.
    fix["mode"] = ["r", "rb", "r+", "w", "wb", "w+", "wb+", "a", "ab", "a+", "ab+"]

    for key in fix:
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, fix[key])


@pytest.mark.basic
def test_open_with_encoding(filename: str, encoding: str, mode: str) -> None:
    # TODO: Add assert
    if os.path.isfile(filename):
        a = open_with_encoding(filename=filename, encoding=encoding, mode=mode)


@pytest.mark.basic
def test_detect_encoding(filename: str, mode: str) -> None:
    # TODO: Add assert
    if os.path.isfile(filename):
        a = detect_encoding(filename=filename)


@pytest.mark.basic
def test_load_modules(search_path: str, pat: Union[str, Pattern[Any]]) -> None:
    # Load all modules from location
    _modules_dict = {}
    _modules_dict.update(load_modules(search_path, pat=pat))
    assert len(_modules_dict) != 0


@pytest.mark.basic
def test_stdout_print(value: Any, otype: str) -> None:
    stdout_print(value, otype=otype)


@pytest.mark.basic
def test_stdout_get(otype: str) -> None:
    res = stdout_get(otype)
    if otype is None:
        assert isinstance(res, type(sys.stdout))
    elif hasattr(otype, "write"):
        assert isinstance(res, type(res))
    else:
        if str(otype).lower() in ["sys.stderr", "err"]:
            assert isinstance(res, type(sys.stderr))
        else:
            assert isinstance(res, type(sys.stdout))
