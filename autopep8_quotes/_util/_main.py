import io
from types import SimpleNamespace
from typing import Any
from typing import List
from typing import Union

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
        onfile_plugin = args._plugins_manager.filter(name=onfile_dict.name).index(0).plugin()
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
    if search_comment_code(source, search="flake8: noqa", filename=filename):
        # no check/reformat entire file
        return source
    try:
        return _format_code(source, args, filename)
    except (tokenize.TokenError, IndentationError):  # pragma: no cover
        return source


def prepare_tokens(line: str) -> Any:
    sio = io.StringIO(line)

    all_tokens = list(tokenize.generate_tokens(sio.readline))

    L = {}
    for x in all_tokens:
        endsline = x.end[0]
        if endsline not in L:
            L[endsline] = []
        L[endsline].append(x)
    for endsline in L:
        for x in L[endsline]:
            yield x, L[endsline]


def search_comment_code(line: Union[str, List[Any]], filename: str, search: str = "noqa") -> bool:
    if line is None:
        return True
    if isinstance(line, str):
        sio = io.StringIO(line)
        try:
            all_tokens = list(tokenize.generate_tokens(sio.readline))
        except BaseException as e:
            return True
    else:
        all_tokens = line

    for token in all_tokens:
        if token.type == tokenize.COMMENT:
            t = token.string.lower().strip().strip("#;, \t\n\r")
            if t == search:
                return True
            elif t.endswith(search):
                return True
            elif t.startswith(search):
                return True
    return False


def _format_code(source: str, args: SimpleNamespace, filename: str) -> Any:
    """Return source code with quotes unified."""
    if not source:
        return source

    modified_tokens = []

    for token, line_tokens in prepare_tokens(source):
        if token.type == tokenize.STRING:
            if search_comment_code(line_tokens, search="noqa", filename=filename):
                pass
                # no check/reformat line
            else:
                for ontoken_dict in args._plugin_order_ontoken_order:
                    ontoken_plugin = args._plugins_manager.filter(name=ontoken_dict.name).index(0).plugin()
                    if not ontoken_plugin.check_is_enabled(args):
                        continue

                    token_dict = get_token_dict(token.type, token.string, token.start, token.end, token.line, filename)
                    token = ontoken_plugin.parse(token=token, line_tokens=line_tokens, args=args, token_dict=token_dict,
                                                 _args=ontoken_dict.args, kwargs=ontoken_dict.kwargs)

        modified_tokens.append((token.type, token.string, token.start, token.end, token.line))

    return untokenize.untokenize(modified_tokens)
