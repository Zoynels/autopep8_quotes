import io
from types import SimpleNamespace
from typing import IO
from typing import Any

import tokenize
import untokenize  # type: ignore

from autopep8_quotes._util import detect_encoding
from autopep8_quotes._util import open_with_encoding
from autopep8_quotes.format._colorama import color_diff
from autopep8_quotes.format._format_util import get_token_dict
from autopep8_quotes.format._format_util import save_values_to_file
from autopep8_quotes.format.lowercase_string_prefix import lowercase_string_prefix
from autopep8_quotes.format.normalize_string_quotes import normalize_string_quotes
from autopep8_quotes.format.remove_string_u_prefix import remove_string_u_prefix


def format_file(filename: str, args: SimpleNamespace, standard_out: IO[Any]) -> bool:
    """Run format_code() on a file.

    Returns `True` if any changes are needed and they are not being done
    in-place.

    """
    encoding = detect_encoding(filename)
    with open_with_encoding(filename, encoding=encoding, mode="rb") as input_file:
        source = input_file.read()
        source = source.decode(encoding)
        formatted_source = format_code(
            source,
            args=args,
            filename=filename)

    if source != formatted_source:
        if args.in_place:
            with open_with_encoding(filename, mode="w",
                                    encoding=encoding) as output_file:
                output_file.write(formatted_source)
        elif args.new_file:
            with open_with_encoding(filename + ".autopep8_quotes",
                                    mode="w",
                                    encoding=encoding) as output_file:
                output_file.write(formatted_source)

        if args.diff:
            import difflib
            diff = difflib.unified_diff(
                source.splitlines(),
                formatted_source.splitlines(),
                "before/" + filename,
                "after/" + filename,
                lineterm="")

            standard_out.write("\n".join(list(color_diff(diff)) + [""]))

        if args.in_place or args.new_file or args.diff:
            return True

    return False


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

            token_string = normalize_string_quotes(token_string, args=args, token_dict=token_dict)
            token_string = lowercase_string_prefix(token_string, args=args, token_dict=token_dict)
            token_string = remove_string_u_prefix(token_string, args=args, token_dict=token_dict)

        modified_tokens.append(
            (token_type, token_string, start, end, line))

    save_values_to_file(save_list, args, "saved_values")

    return untokenize.untokenize(modified_tokens)
