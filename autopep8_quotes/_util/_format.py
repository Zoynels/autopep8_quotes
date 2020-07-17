from types import SimpleNamespace
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Pattern
from typing import Tuple
from typing import Union

import ast

from autopep8_quotes._util._io import open_with_encoding
from autopep8_quotes._util._io import stdout_print


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


def save_values_to_file(args: SimpleNamespace, name: str, input_list: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
    os.makedirs("log", exist_ok=True)
    fname = f"log/autopep8_quotes.{name}.{args._datetime_start.strftime('%Y%m%d %H%M%S')}.txt"
    if isinstance(input_list, (dict)):
        input_list = [input_list]
    elif not isinstance(input_list, (list)):
        input_list = [{"filename": args._read_filename, "pos1": "Unknown (error)", "token_string": str(input_list)}]

    if input_list:
        stdout_print(args, f"Write strings to {fname} from file " + input_list[0]["filename"])
    with open_with_encoding(fname, mode="a", encoding="utf-8") as output_file:
        for i, token_dict in enumerate(input_list):
            try:
                for key in token_dict:
                    if isinstance(token_dict[key], (bytes)):
                        token_dict[key] = token_dict[key].decode()

                output_file.write("\n")
                output_file.write("# " + token_dict["filename"] + ":" + token_dict["pos1"])
                output_file.write("\n")
                output_file.write(f"a_{i+1} = " + token_dict["token_string"])
                output_file.write("\n")
            except BaseException as e:
                stdout_print(args, e)
                stdout_print(args, f"    for token_dict: {token_dict}")


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


def sub_twice(regex: Pattern[Any], replacement: str, original: str) -> Any:
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))
