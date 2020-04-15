import io
import os
import pathlib
import re
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
            modulename = modulename.replace("/", ".").replace("\\", ".").replace("..", ".")
            _modules_dict[modulename] = __import__(modulename, globals(), level=1, fromlist=[""])
    return _modules_dict
