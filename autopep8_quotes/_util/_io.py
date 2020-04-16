import io
import os
import pathlib
import re
import sys
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
        if f.lower().startswith("__init__"):
            continue
        if re.match(pat, f, re.DOTALL):
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


def stdout_print(inp: Any, otype: str) -> None:
    if otype is None:
        sys.stdout.write(inp)
    elif isinstance(otype, str):
        otype = otype.lower().strip()
        if otype in ["sys.stdout", "out", ""]:
            sys.stdout.write(inp)
        elif otype in ["sys.stderr", "err"]:
            sys.stderr.write(inp)
        else:
            sys.stdout.write(inp)
    else:
        otype.write(inp)


def stdout_return(otype: str) -> Any:
    if otype is None:
        pass
    elif isinstance(otype, str):
        if otype.lower() == "sys.stdout":
            return sys.stdout
        elif otype.lower() == "sys.stderr":
            return sys.stderr
        else:
            pass
    else:
        return otype
