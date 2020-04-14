#!/usr/bin/env python

# Copyright (C) 2013-2018 Steven Myint
# Copyright (C) 2019-2000 Dmitrii
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unify strings to all use the same quote.
Unify all prefixex to lowercase.
Remove u"" prefixes.
Source: https://github.com/Zoynels/autopep8_quotes"""

from __future__ import print_function, unicode_literals

import io
import os
import re
import signal
import sys

import tokenize
import untokenize  # type: ignore
import ast
from enum import Enum

__version__ = "0.6"


try:
    unicode
except NameError:
    unicode = str

try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        def __getattr__(self, name):
            return ""

    from types import SimpleNamespace
    colorama = SimpleNamespace()
    colorama.Fore = ColorFallback()
    colorama.Back = ColorFallback()
    colorama.Style = ColorFallback()


col_red = colorama.Style.BRIGHT + colorama.Back.RED
col_green = colorama.Style.BRIGHT + colorama.Back.GREEN


def color_diff(diff):
    """Colorize diff lines"""
    for line in diff:
        if line.startswith("+"):
            yield colorama.Fore.GREEN + line + colorama.Fore.RESET
        elif line.startswith("-"):
            yield colorama.Fore.RED + line + colorama.Fore.RESET
        elif line.startswith("^"):
            yield colorama.Fore.BLUE + line + colorama.Fore.RESET
        else:
            yield line


def isevaluatable(s, prefix=""):
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


def format_code(source, args, filename):
    """Return source code with quotes unified."""
    try:
        return _format_code(source, args, filename)
    except (tokenize.TokenError, IndentationError):
        return source


def _format_code(source, args, filename):
    """Return source code with quotes unified."""
    if not source:
        return source

    modified_tokens = []

    sio = io.StringIO(source)
    for (token_type,
         token_string,
         start,
         end,
         line) in tokenize.generate_tokens(sio.readline):
        if token_type == tokenize.STRING:
            token_dict = get_token_dict(token_type, token_string, start, end, line, filename)
            token_string = normalize_string_quotes(token_string, args=args, token_dict=token_dict)
            token_string = lowercase_string_prefix(token_string, args=args, token_dict=token_dict)
            token_string = remove_string_u_prefix(token_string, args=args, token_dict=token_dict)

        modified_tokens.append(
            (token_type, token_string, start, end, line))

    return untokenize.untokenize(modified_tokens)


def get_token_dict(token_type, token_string, start, end, line, filename):
    _dict = {}
    _dict["token_type"] = token_type
    _dict["token_string"] = token_string
    _dict["start"] = start
    _dict["end"] = end
    _dict["line"] = line
    _dict["filename"] = filename
    _dict["text"] = f"Line {start[0]}, pos {start[1]} - line {end[0]}, pos {end[1]}: {token_string}"
    _dict["pos"] = f"Line:pos ({start[0]}:{start[1]} - {end[0]}:{end[1]})"
    _dict["pos2"] = f"Line {start[0]}, pos {start[1]} - line {end[0]}, pos {end[1]}"

    return _dict


def lowercase_string_prefix(leaf, args, token_dict):
    """Make furbFURB prefixes lowercase.

    Original from https://github.com/psf/black
    """
    if args.lowercase_string_prefix:
        match = re.match(r"^([furbFURB]*)(.*)$", leaf, re.DOTALL)
        assert match is not None, f"failed to match string {leaf!r}"
        orig_prefix = match.group(1)
        new_prefix = orig_prefix
        new_prefix = new_prefix.replace("F", "f")
        new_prefix = new_prefix.replace("U", "u")
        new_prefix = new_prefix.replace("R", "r")
        new_prefix = new_prefix.replace("B", "b")
        leaf = f"{new_prefix}{match.group(2)}"
    return leaf


def remove_string_u_prefix(leaf, args, token_dict):
    """Removes any u prefix from the string.

    Original from https://github.com/psf/black
    """
    if args.remove_string_u_prefix:
        match = re.match(r"^([uU]*)(.*)$", leaf, re.DOTALL)
        assert match is not None, f"failed to match string {leaf!r}"
        orig_prefix = match.group(1)
        new_prefix = orig_prefix.replace("u", "")
        leaf = f"{new_prefix}{match.group(2)}"
    return leaf


class quotes_codes(Enum):
    quote_bruteforce_good = -3
    old_quote_good = -2
    new_quote_good = -1
    original_equal = 0
    original_bad = 1
    cant_transform = 2
    quote_start_is_not_equal_end_v1 = 11
    quote_start_is_not_equal_end_v2 = 12
    unescaped_quote_in_r = 13
    backslashes_in_expressions = 14
    do_not_introduce_more_escaping = 15
    prefer_double_quotes = 16


def normalize_string_quotes(leaf, args, token_dict):
    """Prefer quotes but only if it doesn't cause more escaping.

    Adds or removes backslashes as appropriate.
    Doesn't parse and fix strings nested in f-strings (yet).

    Original from https://github.com/psf/black
    Second return value:
        if result > 0 then error else no error but may be warning
    """
    def parse(leaf, args, change_quote=False):
        value = leaf.lstrip("furbFURB")

        quotes = {}
        quotes["'''"] = '"""'
        quotes['"""'] = "'''"
        quotes["'"] = '"'
        quotes['"'] = "'"

        if value[:3] == value[-3:]:
            if value[:3] == args.multiline_quotes:
                orig_quote = args.multiline_quotes
                if change_quote:
                    new_quote = quotes[args.multiline_quotes]
                else:
                    new_quote = args.multiline_quotes
            else:
                orig_quote = quotes[args.multiline_quotes]
                new_quote = args.multiline_quotes
        elif value[:1] == value[-1:]:
            if value[0] == args.inline_quotes:
                orig_quote = args.inline_quotes
                new_quote = quotes[args.inline_quotes]
            else:
                orig_quote = quotes[args.inline_quotes]
                new_quote = args.inline_quotes
        else:
            return leaf, quotes_codes.quote_start_is_not_equal_end_v1

        first_quote_pos = leaf.find(orig_quote)
        if first_quote_pos == -1:
            return leaf, quotes_codes.quote_start_is_not_equal_end_v2

        prefix = leaf[:first_quote_pos]
        unescaped_new_quote = re.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
        escaped_new_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
        escaped_orig_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){orig_quote}")

        escaped_quote_single_el_v1 = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote[0]}")
        escaped_quote_single_el_v2 = re.compile(rf"([^\\]|^)\\((?:\\\\)*){quotes[new_quote[0]][0]}")

        body = leaf[first_quote_pos + len(orig_quote): -len(orig_quote)]
        old_body = body
        if "r" in prefix.casefold():
            if unescaped_new_quote.search(body):
                # There's at least one unescaped new_quote in this raw string
                # so converting is impossible
                return leaf, quotes_codes.unescaped_quote_in_r

            # Do not introduce or remove backslashes in raw strings
            new_body = body
        else:
            # remove unnecessary escapes
            new_body = sub_twice(escaped_new_quote, rf"\1\2{new_quote}", body)
            if len(new_quote) == 3:
                new_body = sub_twice(escaped_quote_single_el_v1, rf"\1\2{new_quote[0]}", new_body)
                new_body = sub_twice(escaped_quote_single_el_v2, rf"\1\2{quotes[new_quote[0]][0]}", new_body)

            if body != new_body:
                # Consider the string without unnecessary escapes as the original
                return check_string(leaf, prefix, old_body, new_body, orig_quote, new_quote, args=args, token_dict=token_dict)
            new_body = sub_twice(escaped_orig_quote, rf"\1\2{orig_quote}", new_body)
            new_body = sub_twice(unescaped_new_quote, rf"\1\\{new_quote}", new_body)
        if "f" in prefix.casefold():
            matches = re.findall(
                r"""
                (?:[^{]|^)\{  # start of the string or a non-{ followed by a single {
                    ([^{].*?)  # contents of the brackets except if begins with {{
                \}(?:[^}]|$)  # A } followed by end of the string or a non-}
                """,
                new_body,
                re.VERBOSE,
            )
            for m in matches:
                if "\\" in str(m):
                    # Do not introduce backslashes in interpolated expressions
                    return leaf, quotes_codes.backslashes_in_expressions

        if len(new_quote) == 3 and new_body[-1:] == new_quote[0]:
            # edge case:
            new_body = new_body[:-1] + "\\" + new_quote[0]
        orig_escape_count = body.count("\\")
        new_escape_count = new_body.count("\\")
        if new_escape_count > orig_escape_count:
            return leaf, quotes_codes.do_not_introduce_more_escaping

        if new_escape_count == orig_escape_count and orig_quote == args.inline_quotes:
            return leaf, quotes_codes.prefer_double_quotes

        return check_string(leaf, prefix, old_body, new_body, orig_quote, new_quote, args=args, token_dict=token_dict)

    if args.normalize_string_quotes:
        result_string, code = parse(leaf, args=args)
        if code == quotes_codes.quote_bruteforce_good:
            # Try to change quote """ => ''' and vice versa
            result_string_v2, code_v2 = parse(leaf, args=args, change_quote=True)
            if (code_v2 != quotes_codes.cant_transform) and (code_v2 != quotes_codes.quote_bruteforce_good):
                # If
                result_string, code = result_string_v2, code_v2

        if args.debug:
            print("normalize_string_quotes: ")
            print("    code:          ", code)
            print("    input_sting:   ", leaf)
            print("    result_string: ", result_string)

        if result_string is not None:
            return result_string
    return leaf


def sub_twice(regex, replacement, original, prefix=None, new_quote=None):
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    TODO: If bad replacement, then need to replace by one occurence and then check is it bad or not.
        If not bad then replacement is good and need to save
        If bad then skip this change and go to next.
        https://docs.python.org/3/library/re.html#re.sub
            count -- all replacements before bad could be fixed. But what to do with next? Split text?
    """
    return regex.sub(replacement, regex.sub(replacement, original))


def get_rep_body(body, prefix, quote):
    """Escape symbol by symbol to get new_body"""
    new_body = ""
    delim = "\\"
    space = " "
    L = len(body)
    for i, char in enumerate(body):
        last_line = (i == L - 1)
        # Standart line
        # ast.literal_eval: if last symbol is quote[0] then it should be escaped
        if (body[i] != quote[0]) or (not last_line):
            v10 = f"{prefix}{quote}{new_body + body[i]}{quote}"
            v10_res = isevaluatable(v10)
            if v10_res[0]:
                new_body = new_body + body[i]
                # print(i , L - 1, "V10", new_body)
                continue

        if not last_line:
            # All symbols instead of last symbol which should be escaped
            # ast.literal_eval: if last symbol is quote[0] then it should be escaped
            # but that it it not last sybmol of body then check if it not a last
            v11 = f"{prefix}{quote}{new_body + body[i] + space}{quote}"
            v11_res = isevaluatable(v11)
            if v11_res[0]:
                new_body = new_body + body[i]
                # print(i , L - 1, "	V11", new_body)
                continue

        # Escaped symbol
        v20 = f"{prefix}{quote}{new_body+delim+body[i]}{quote}"
        v20_res = isevaluatable(v20)
        if v20_res[0]:
            new_body = new_body + delim + body[i]
            # print(i , L - 1, "		V20", new_body)
            continue

    # Result line. It could be not normal
    return f"{prefix}{quote}{new_body}{quote}"


def check_string(original, prefix, old_body, new_body, orig_quote, new_quote, args, token_dict):
    v1 = f"{prefix}{new_quote}{new_body}{new_quote}"
    v2 = f"{prefix}{orig_quote}{new_body}{orig_quote}"
    if original == v1:
        return original, quotes_codes.original_equal

    v0_res = isevaluatable(original, prefix)
    if not v0_res[0]:
        print("")
        print(col_red + f"Can't check original! Please test string manually!")
        print("    " + col_red + f"Filename:   {token_dict['filename']}")
        print("    " + col_red + f"Position:   {token_dict['pos']}")
        print("    " + col_red + f"String:     {token_dict['token_string']}")
        print("")
        return original, quotes_codes.original_bad

    v1_res = isevaluatable(v1, prefix)
    # Good string and value is not changed!
    if v1_res[0] and (v1_res[1] == v0_res[1]):
        if args.debug:
            print("#" * 100)
            print(args.debug)
            print(col_red + f"Return v1: {v1}")
        return v1, quotes_codes.new_quote_good

    v2_res = isevaluatable(v2, prefix)
    # Good string and value is not changed!
    if v2_res[0] and (v2_res[1] == v0_res[1]):
        if args.debug:
            print(col_red + f"Return v2: {v2}")
        return v2, quotes_codes.old_quote_good

    v3 = get_rep_body(new_body, prefix, new_quote)
    v3_res = isevaluatable(v3, prefix)
    if v3_res[0] and (v3_res[1] == v0_res[1]):
        if args.debug:
            print(col_red + f"Return v3: {v3}")
        return v3, quotes_codes.quote_bruteforce_good

    print("")
    print(col_red + f"Can't transform, return original! Please simpify string manually!")
    print("    " + col_red + f"Filename:   {token_dict['filename']}")
    print("    " + col_red + f"Position:   {token_dict['pos']}")
    print("    " + col_red + f"String:     {token_dict['token_string']}")
    print("        " + col_red + f"Original:   {original}")
    print("        " + col_red + f"Try v1:     {v1}")
    print("        " + col_red + f"Try v2:     {v2}")
    print("")
    return original, quotes_codes.cant_transform


def open_with_encoding(filename, encoding, mode="rb"):
    """Return opened file with a specific encoding."""
    if mode.lower() == "rb":
        return io.open(filename, mode=mode)
    else:
        return io.open(filename, mode=mode, encoding=encoding,
                       newline="")  # Preserve line endings


def detect_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, "rb") as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding = lib2to3_tokenize.detect_encoding(input_file.readline)[0]

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return "latin-1"


def format_file(filename, args, standard_out):
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


def _main(args, standard_out, standard_error):
    """Run quotes autopep8_quotesing on files.

    Returns `1` if any quoting changes are still needed, otherwise
    `None`.

    """
    import argparse
    import configparser

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            return False
            # raise argparse.ArgumentTypeError('Boolean value expected.')

    def str2bool_dict(dict1, dict2):
        for key in dict1:
            if isinstance(dict1[key], (bool)):
                dict2[key] = str2bool(dict2[key])

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-f", "--conf_file",
                             help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect_conf",
                             action="store_true", default=True,
                             help="Try to detect config file: *.ini, *.cfg")

    argv, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["check_only"] = False
    defaults["diff"] = False
    defaults["in_place"] = False
    defaults["new_file"] = False
    defaults["recursive"] = False
    defaults["normalize_string_quotes"] = True
    defaults["inline_quotes"] = '"'
    defaults["multiline_quotes"] = '"""'
    defaults["lowercase_string_prefix"] = True
    defaults["remove_string_u_prefix"] = True
    defaults["filename"] = [r".*\.py$"]

    cfg_files = []
    if argv.autodetect_conf:
        for f in os.listdir():
            if f.endswith(".ini") or f.endswith(".cfg"):
                cfg_files.append(f)
    cfg_files = sorted(cfg_files)
    if argv.conf_file:
        cfg_files.append(argv.conf_file)

    for f in cfg_files:
        try:
            config = configparser.SafeConfigParser()
            config.read([f])
            for sec in ["pep8", "flake8", "autopep8", "autopep8_quotes"]:
                try:
                    _dict = dict(config.items(sec))
                    _dict = {key.replace("-", "_"): value for (key, value) in _dict.items()}
                    str2bool_dict(defaults, _dict)
                    defaults.update(_dict)
                except BaseException:
                    pass
        except BaseException:
            pass

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser],
        description=__doc__,
        prog="autopep8_quotes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True)
    parser.set_defaults(**defaults)

    parser.add_argument("-i", "--in-place", action="store_true",
                        help="Make changes to files. "
                        "Could be combined with --diff and can't combined with --in-place"
                        "If --inplace --new-file then will be used only --new-file")
    parser.add_argument("-n", "--new-file", action="store_true",
                        help="Make changes to files and create new file with "
                        ".autopep8_quotesing extention. "
                        "Could be combined with --diff and can't combined with --in-place"
                        "If --inplace --new-file then will be used only --new-file")
    parser.add_argument("-d", "--diff", action="store_true",
                        help="Print changes without make changes. "
                        "Could be combined with --in-place")
    parser.add_argument("-c", "--check-only", action="store_true",
                        help="Exit with a status code of 1 if any changes are still needed")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
    parser.add_argument("--filename",
                        type=str,
                        nargs="+",
                        help="Check only for filenames matching the patterns.")
    parser.add_argument("--normalize_string_quotes", action="store_true",
                        help="Normalize all quotes to standart "
                             "by options --multiline_quotes and --inline_quotes")
    parser.add_argument("--inline_quotes",
                        help="Preferred inline_quotes. "
                        "Works only when --normalize_string_quotes is True",
                        choices=["'", '"'])
    parser.add_argument("--multiline_quotes",
                        help="Preferred multiline_quotes. "
                        "Works only when --normalize_string_quotes is True",
                        choices=["'''", '"""'])
    parser.add_argument("--lowercase_string_prefix", action="store_true",
                        help='Make FURB prefixes lowercase: B"sometext" to b"sometext"')
    parser.add_argument("--remove_string_u_prefix", action="store_true",
                        help='Removes any u prefix from the string: u"sometext" to "sometext"')
    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__,
                        help="Show program's version number and exit")
    parser.add_argument("--show_args", action="store_true",
                        help="Show readed args for script and exit")
    parser.add_argument("--debug", action="store_true",
                        help="Show debug messages")
    parser.add_argument("files", nargs="+",
                        help="Files to format")

    args = parser.parse_args(remaining_argv)

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    if args.in_place and args.new_file:
        print(col_red + "Option --in-place and --new-file shouldn't pass togeather.")
        print(col_green + "Disable --in-place, run only --new-file")

    if isinstance(args.filename, (str)):
        args.filename = [args.filename]

    if args.show_args:
        print(args)
        sys.exit(0)

    filenames = list(set(args.files))
    changes_needed = False
    failure = False
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk(unicode(name)):
                for f in children:
                    if f.startswith("."):
                        continue
                    for pat in args.filename:
                        if re.match(pat, os.path.join(root, f), re.DOTALL):
                            filenames.append(os.path.join(root, f))

                directories[:] = [d for d in directories
                                  if not d.startswith(".")]
        else:
            try:
                if format_file(name, args=args, standard_out=standard_out):
                    changes_needed = True
            except IOError as exception:
                print(unicode(exception), file=standard_error)
                failure = True

    if failure or (args.check_only and changes_needed):
        return 1


def main():  # pragma: no cover
    """Return exit status."""
    try:
        # Exit on broken pipe.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:
        # SIGPIPE is not available on Windows.
        pass

    try:
        return _main(sys.argv,
                     standard_out=sys.stdout,
                     standard_error=sys.stderr)
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
