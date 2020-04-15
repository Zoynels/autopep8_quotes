﻿from types import SimpleNamespace
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import ast

from autopep8_quotes._util import open_with_encoding


def get_token_dict(token_type: int, token_string: str, start: Tuple[int, int],
                   end: Tuple[int, int], line: str,
                   filename: str) -> Dict[str, Union[str, int, Tuple[int, int]]]:
    _dict: Dict[str, Union[str, int, Tuple[int, int]]] = {}
    _dict["token_type"] = token_type
    _dict["token_string"] = token_string
    _dict["start"] = start
    _dict["end"] = end
    _dict["line"] = line
    _dict["filename"] = filename
    _dict["text"] = f"Line {start[0]}, pos {start[1]} - line {end[0]}, pos {end[1]}: {token_string}"
    _dict["pos"] = f"Line:pos ({start[0]}:{start[1]} - {end[0]}:{end[1]})"
    _dict["pos1"] = f"({start[0]}:{start[1]} - {end[0]}:{end[1]})"
    _dict["pos2"] = f"Line {start[0]}, pos {start[1]} - line {end[0]}, pos {end[1]}"

    return _dict


def save_values_to_file(input_list: List[Dict[str, Any]], args: SimpleNamespace, name: str) -> None:
    if args.save_values_to_file:
        os.makedirs("log", exist_ok=True)
        fname = f"log/autopep8_quotes.{name}.{args.datetime_start.strftime('%Y%d%m %H%M%S')}.txt"
        if input_list:
            print(f"Write strings to {fname} from file " + input_list[0]["filename"])
        with open_with_encoding(fname, mode="a", encoding="utf-8") as output_file:
            for i, token_dict in enumerate(input_list):
                try:
                    output_file.write("\n")
                    output_file.write("# " + token_dict["filename"] + ":" + token_dict["pos1"])
                    output_file.write("\n")
                    output_file.write(f"a_{i+1} = " + token_dict["token_string"])
                    output_file.write("\n")
                except BaseException:
                    pass


def isevaluatable(s: str, prefix: str = "") -> Tuple[bool, Any]:
    """Check string is calculatable and get it's value"""
    try:
        v = ast.literal_eval(s)
        return True, v
    except BaseException:
        try:
            # ast.literal_eval not work with f-strings
            # try to calculate without prefix
            v = ast.literal_eval(s[len(prefix):])
            return True, v
        except BaseException:
            return False, None
