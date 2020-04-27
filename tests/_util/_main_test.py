import io
import os
import sys
from typing import Any
from typing import Pattern
from typing import Union
from types import SimpleNamespace

import pytest  # type: ignore

from autopep8_quotes._util import _main
from autopep8_quotes._util._io import open_with_encoding


def test_format_code__noqa_entire_file():
    source = """
# flake8: noqa
abc = "xyz"
"""
    args = SimpleNamespace()
    filename = "no_file"
    assert source == _main.format_code(source=source, args=args, filename=filename)

def test_format_code__None():
    source = None
    args = SimpleNamespace()
    filename = "no_file"
    assert source == _main.format_code(source=source, args=args, filename=filename)

def test_format_code__tokenizer_error():
    filename = "tests/good/tokenize_error.py"
    encoding = None
    mode = "r"
    args = SimpleNamespace()

    with open_with_encoding(filename=filename, encoding=encoding, mode=mode) as f:
        source = f.read()
    assert source == _main.format_code(source=source, args=args, filename=filename)