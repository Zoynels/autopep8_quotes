import io
from types import SimpleNamespace
from typing import Any
from typing import List

import tokenize
import untokenize  # type: ignore

from autopep8_quotes._util._format import get_token_dict
from autopep8_quotes._util._format import save_values_to_file
from autopep8_quotes._util._io import detect_encoding
from autopep8_quotes._util._io import open_with_encoding


def format_file(args: SimpleNamespace) -> Any:
    """Run format_code() on a file.

    Returns `True` if any changes are needed and they are not being done
    in-place.

    """
    args._read_encoding = detect_encoding(args._read_filename)
    with open_with_encoding(args._read_filename, encoding=args._read_encoding, mode="rb") as input_file:
        source = input_file.read()
        source = source.decode(args._read_encoding)
        formatted_source = format_code(
            source,
            args=args,
            filename=args._read_filename)

    if source != formatted_source:
        result: List[Any] = [False]
        for _dict_mod in args._start_save_order:
            func = _dict_mod["module"].formatter().show_or_save
            res = func(args, source, formatted_source, **_dict_mod["kwargs"])
            if res is None:
                pass
            elif isinstance(res, list):
                if res[0].lower() == "return":
                    if len(res[1:]) == 1:
                        result.append(res[1])
                    else:
                        result.append(res[1:])
                if res[0].lower() == "immediately return":
                    if len(res[1:]) == 1:
                        return res[1]
                    else:
                        return res[1:]
            elif isinstance(res, str):
                if res.lower() == "continue":
                    continue

        if all(result):
            return 1
    return 0


def format_code(source: str, args: SimpleNamespace, filename: str) -> Any:
    """Return source code with quotes unified."""
    try:
        return _format_code(source, args, filename)
    except (tokenize.TokenError, IndentationError):
        return source


def _format_code(source: str, args: SimpleNamespace, filename: str) -> Any:
    """Return source code with quotes unified."""
    if not source:
        return source

    modified_tokens = []

    sio = io.StringIO(source)
    save_list = []
    for (token_type,
         token_string,
         start,
         end,
         line) in tokenize.generate_tokens(sio.readline):
        if token_type == tokenize.STRING:
            token_dict = get_token_dict(token_type, token_string, start, end, line, filename)

            if args.save_values_to_file:
                save_list.append(token_dict)

            for _dict_mod in args._start_parse_order:
                func = _dict_mod["module"].formatter().parse
                token_string = func(token_string, args=args, token_dict=token_dict, **_dict_mod["kwargs"])

        modified_tokens.append((token_type, token_string, start, end, line))

    save_values_to_file(save_list, args, "found_values")

    return untokenize.untokenize(modified_tokens)
