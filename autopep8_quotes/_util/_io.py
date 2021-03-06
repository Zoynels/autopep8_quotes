﻿import argparse
import io
import os
import pathlib
import re
import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import Pattern
from typing import Union

from pkg_resources import iter_entry_points


def open_with_encoding(filename: str, encoding: str = "", mode: str = "rb") -> Any	:
    """Return opened file with a specific encoding."""
    if mode is None:
        raise ValueError("open_with_encoding mode is None")
    else:
        mode = str(mode).lower()

    if "b" in str(mode).lower():
        return io.open(filename, mode=mode)
    else:
        try:
            # Preserve line endings
            return io.open(filename, mode=mode, encoding=encoding, newline="")
        except BaseException:
            encoding = detect_encoding(filename)
            # Preserve line endings
            return io.open(filename, mode=mode, encoding=encoding, newline="")


def detect_encoding(filename: str) -> str:
    """Return file encoding."""
    from lib2to3.pgen2 import tokenize as lib2to3_tokenize
    mode = "rb"
    try:
        with open(filename, mode=mode) as input_file:
            encoding: str = lib2to3_tokenize.detect_encoding(input_file.readline)[0]  # type: ignore
            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding, mode=mode) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return "latin-1"


def load_modules(search_path: str, pat: Union[str, Pattern[Any]]) -> Dict[str, Any]:
    """Load reformat modules"""
    _modules_dict: Dict[str, Any] = {}
    from autopep8_quotes import __file__ as pkg__file__
    modules_location = os.path.join(pathlib.Path(pkg__file__).parent, search_path)

    for f in os.listdir(modules_location):
        if f.lower().startswith("__init__"):
            continue
        if re.match(pat, f, re.DOTALL):
            ext = pathlib.Path(f).suffix
            loc = os.path.abspath(pathlib.Path(pkg__file__).parent.parent)
            modulename: str = os.path.abspath(os.path.join(modules_location, f))
            modulename = modulename[len(loc):-len(ext)].lstrip(os.path.sep)

            while True:
                st = modulename
                modulename = modulename.replace("/", ".")
                modulename = modulename.replace("\\", ".")
                modulename = modulename.replace("-", "_")
                modulename = modulename.replace("..", ".")
                if st == modulename:
                    break

            _modules_dict[modulename] = __import__(modulename, fromlist=[""])
    return _modules_dict


def load_modules_ep(group: str) -> Dict[str, Any]:
    available_methods = {}
    for entry_point in iter_entry_points(group=group):
        name = f"{entry_point.module_name}:{entry_point.name}"
        available_methods[name] = SimpleNamespace()
        available_methods[name].ep = entry_point
        available_methods[name].loaded = entry_point.load()
        available_methods[name].apply = available_methods[name].loaded()
    return available_methods


def stdout_print(args: Union[SimpleNamespace, argparse.Namespace], value: Any, otype: str = "", sep: str = " ", end: str = "\n") -> int:
    if hasattr(args, "print_disable") and args.print_disable:
        return 0
    try:
        stdout_get(otype).write(value)
        stdout_get(otype).write(end)
    except BaseException:
        try:
            stdout_get(otype).write(str(value).encode("utf-8"))
            stdout_get(otype).write(str(end).encode("utf-8"))
        except BaseException:
            pass
    return 0


def stdout_get(otype: Any) -> Any:
    if otype is None:
        return sys.stdout
    elif hasattr(otype, "write"):
        if isinstance(otype, type):
            return otype()
        return otype
    else:
        if str(otype).lower() in ["sys.stderr", "err", "error"]:
            return sys.stderr
        else:
            return sys.stdout
