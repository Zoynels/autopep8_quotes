import io
from types import SimpleNamespace
from typing import Any
from typing import List

import tokenize
import untokenize  # type: ignore

from autopep8_quotes._util._format import get_token_dict
from autopep8_quotes._util._io import detect_encoding
from autopep8_quotes._util._io import open_with_encoding


def format_file(args: SimpleNamespace) -> Any:
    """Run format_code() on a file.

    Returns `True` if any changes are needed and they are not being done
    in-place.

    """
    args._read_encoding = detect_encoding(args._read_filename)
    args._read_file_need_load = True

    result: List[Any] = [False]

    for onfile_dict in args._plugin_order_onfile_order:
        onfile_plugin = args._plugins_manager.plugins[onfile_dict.name].plugin()
        if not onfile_plugin.check_is_enabled(args):
            continue

        if args._read_file_need_load:
            # On first launch read file
            # If file changed, e.i. --in-place, then need to reload file on next run (data is updated)
            with open_with_encoding(args._read_filename, encoding=args._read_encoding, mode="rb") as input_file:
                source = input_file.read()
                source = source.decode(args._read_encoding)

        formatted_source = format_code(
            source,
            args=args,
            filename=args._read_filename
        )

        result = [False]
        if source != formatted_source:
            func = onfile_plugin.show_or_save
            res = func(args, source, formatted_source, *onfile_dict.args, **onfile_dict.kwargs)
            if res is None:
                pass
            elif isinstance(res, (list, tuple)):
                if res[0].lower() == "return":
                    if len(res[1:]) == 1:
                        result.append(res[1])
                    else:
                        result.append(res[1:])
            elif isinstance(res, str):
                if res.lower() == "continue":
                    continue

    return any(result)


def format_code(source: str, args: SimpleNamespace, filename: str) -> Any:
    """Return source code with quotes unified."""
    if search_comment_code(source, search="flake8: noqa"):
        # no check/reformat entire file
        return source
    try:
        return _format_code(source, args, filename)
    except (tokenize.TokenError, IndentationError):  # pragma: no cover
        return source


def search_comment_code(line: str, search: str = "noqa") -> bool:
    sio = io.StringIO(line)
    try:
        for token in tokenize.generate_tokens(sio.readline):
            if token.type == tokenize.COMMENT:
                t = token.string.lower().strip().strip("#;, \t\n\r")
                if t == search:
                    return True
                elif t.endswith(search):
                    return True
                elif t.startswith(search):
                    return True
    except:
        return True
    return False


def _format_code(source: str, args: SimpleNamespace, filename: str) -> Any:
    """Return source code with quotes unified."""
    if not source:
        return source

    modified_tokens = []
    sio = io.StringIO(source)

    for (token_type, token_string, start, end, line) in tokenize.generate_tokens(sio.readline):
        if token_type == tokenize.STRING:
            if search_comment_code(line, search="noqa"):
                pass
                # no check/reformat line
            else:
                for ontoken_dict in args._plugin_order_ontoken_order:
                    ontoken_plugin = args._plugins_manager.plugins[ontoken_dict.name].plugin()

                    token_dict = get_token_dict(token_type, token_string, start, end, line, filename)

                    if not ontoken_plugin.check_is_enabled(args):
                        continue
                    token_string = ontoken_plugin.parse(token_string, args=args, token_dict=token_dict, *ontoken_dict.args, **ontoken_dict.kwargs)

        modified_tokens.append((token_type, token_string, start, end, line))

    return untokenize.untokenize(modified_tokens)
