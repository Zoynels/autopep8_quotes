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


def open_with_encoding(filename: str, encoding: str, mode: str = "rb") -> Any	:
    """Return opened file with a specific encoding."""
    if mode.lower() == "rb":
        return io.open(filename, mode=mode)
    else:
        return io.open(filename, mode=mode, encoding=encoding,
                       newline="")  # Preserve line endings


def detect_encoding(filename: str) -> str:
    """Return file encoding."""
    try:
        with open(filename, "rb") as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding: str = lib2to3_tokenize.detect_encoding(input_file.readline)[0]  # type: ignore

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return "latin-1"


def load_modules(search_path: str, pat: Union[str, Pattern[Any]], ext: str) -> Dict[str, Any]:
    """Load reformat modules"""
    _modules_dict: Dict[str, Any] = {}
    from autopep8_quotes import __file__ as pkg__file__
    modules_location = os.path.join(pathlib.Path(pkg__file__).parent, search_path)

    for f in os.listdir(modules_location):
        if re.match(pat, f, re.DOTALL):
            modulename: str = str(os.path.join(search_path, f)[:-len(ext)])
            while True:
                st = modulename
                modulename = modulename.replace("/", ".")
                modulename = modulename.replace("\\", ".")
                modulename = modulename.replace("-", "_")
                modulename = modulename.replace("..", ".")
                if st == modulename:
                    break
            _modules_dict[modulename] = __import__(modulename, globals(), level=1, fromlist=[""])
    return _modules_dict


def print__stdout_err(inp: Any, out_type: str) -> None:
    if out_type is None:
        print(inp)
    elif isinstance(out_type, str):
        if out_type.lower() == "sys.stdout":
            sys.stdout.write(inp)
        elif out_type.lower() == "sys.stderr":
            sys.stderr.write(inp)
        else:
            print(inp)
    else:
        out_type.write(inp)


def return__stdout_err(out_type: str) -> Any:
    if out_type is None:
        pass
    elif isinstance(out_type, str):
        if out_type.lower() == "sys.stdout":
            return sys.stdout
        elif out_type.lower() == "sys.stderr":
            return sys.stderr
        else:
            pass
    else:
        return out_type


def parse_startup(args: SimpleNamespace, n: str) -> None:
    """Transform string values into list of order startup

    Get values from args:
        start_save_first = "diff;new-file;in-place"
        start_save_last = "check-only"
    Get modules which could be run, which also stored in args, but get real files from pkg
       _modules_dict = ["format.fmt_diff", "format.fmt_new_file", "format.fmt_in_place", "format.fmt_check_only", "format.fmt_something_else"]

    Calculate new values:
        _start_save_first = ["format.fmt_diff", "format.fmt_new_file", "format.fmt_in_place"]
        _start_save_last = ["format.fmt_check_only"]
        _start_save_med = ["format.fmt_something_else"]
        _start_save_order = ["format.fmt_diff", "format.fmt_new_file", "format.fmt_in_place", "format.fmt_something_else", "format.fmt_check_only"]
    Where the _start_save_order determines the order in which the modules start

    First/Last modules could run several times
"""
    for val in [f"{n}_first", f"{n}_last"]:
        args.__dict__[f"_{val}"] = []
        for x in args.__dict__.get(val, "").replace("-", "_").lower().split(";"):
            for y in list(args._modules_dict.keys()):
                if y.lower().endswith(x):
                    args.__dict__[f"_{val}"].append(y)
    ts = set(args.__dict__[f"_{n}_first"] + args.__dict__[f"_{n}_last"])
    args.__dict__[f"_{n}_med"] = list(set(list(args._modules_dict.keys())) - ts)
    args.__dict__[f"_{n}_order"] = []
    args.__dict__[f"_{n}_order"] += args.__dict__[f"_{n}_first"]
    args.__dict__[f"_{n}_order"] += args.__dict__[f"_{n}_med"]
    args.__dict__[f"_{n}_order"] += args.__dict__[f"_{n}_last"]
