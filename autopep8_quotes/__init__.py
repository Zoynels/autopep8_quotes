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
Remove u"" prefixes."""

from __future__ import print_function, unicode_literals

import io
import os
import re
import signal
import sys

import tokenize
import untokenize  # type: ignore

__version__ = "0.6"


try:
    unicode
except NameError:
    unicode = str


def format_code(source, args):
    """Return source code with quotes unified."""
    try:
        return _format_code(source, args)
    except (tokenize.TokenError, IndentationError):
        return source


def _format_code(source, args):
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
            token_string = normalize_string_quotes(token_string, args=args)
            token_string = lowercase_string_prefix(token_string, args=args)
            token_string = remove_string_u_prefix(token_string, args=args)

        modified_tokens.append(
            (token_type, token_string, start, end, line))

    return untokenize.untokenize(modified_tokens)


def get_starts_symbol(token_string):
    token_string[0]


def lowercase_string_prefix(leaf, args):
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


def remove_string_u_prefix(leaf, args):
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


def normalize_string_quotes(leaf, args):
    """Prefer quotes but only if it doesn't cause more escaping.

    Adds or removes backslashes as appropriate.
    Doesn't parse and fix strings nested in f-strings (yet).

    Original from https://github.com/psf/black
    """
    def parse(leaf, args):
        value = leaf.lstrip("furbFURB")

        quotes = {}
        quotes["'''"] = '"""'
        quotes['"""'] = "'''"
        quotes["'"] = '"'
        quotes['"'] = "'"

        if value[:3] == args.multiline_quotes:
            return leaf, 1
        elif value[:3] == quotes[args.multiline_quotes]:
            orig_quote = quotes[args.multiline_quotes]
            new_quote = args.multiline_quotes
        elif value[0] == args.inline_quotes:
            orig_quote = args.inline_quotes
            new_quote = quotes[args.inline_quotes]
        else:
            orig_quote = quotes[args.inline_quotes]
            new_quote = args.inline_quotes

        first_quote_pos = leaf.find(orig_quote)
        if first_quote_pos == -1:
            return leaf, 2  # There's an internal error

        prefix = leaf[:first_quote_pos]
        unescaped_new_quote = re.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
        escaped_new_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
        escaped_orig_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){orig_quote}")
        body = leaf[first_quote_pos + len(orig_quote): -len(orig_quote)]
        if "r" in prefix.casefold():
            if unescaped_new_quote.search(body):
                # There's at least one unescaped new_quote in this raw string
                # so converting is impossible
                return leaf, 3

            # Do not introduce or remove backslashes in raw strings
            new_body = body
        else:
            # remove unnecessary escapes
            new_body = sub_twice(escaped_new_quote, rf"\1\2{new_quote}", body)
            if body != new_body:
                # Consider the string without unnecessary escapes as the original
                body = new_body
                leaf = f"{prefix}{orig_quote}{body}{orig_quote}"
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
                    return leaf, 4

        if len(new_quote) == 3 and new_body[-1:] == new_quote[0]:
            # edge case:
            new_body = new_body[:-1] + "\\" + new_quote[0]
        orig_escape_count = body.count("\\")
        new_escape_count = new_body.count("\\")
        if new_escape_count > orig_escape_count:
            return leaf, 5  # Do not introduce more escaping

        if new_escape_count == orig_escape_count and orig_quote == args.inline_quotes:
            return leaf, 6  # Prefer double quotes

        return f"{prefix}{new_quote}{new_body}{new_quote}", 0

    if args.normalize_string_quotes:
        result_string, code = parse(leaf, args=args)
        if result_string is not None:
            return result_string
    return leaf


def sub_twice(regex, replacement, original):
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))


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
            args=args)

    if source != formatted_source:
        if args.in_place:
            with open_with_encoding(filename, mode="w",
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
            standard_out.write("\n".join(list(diff) + [""]))

        if args.in_place or args.diff:
            return True

    return False


def _main(args, standard_out, standard_error):
    """Run quotes autopep8_quotesing on files.

    Returns `1` if any quoting changes are still needed, otherwise
    `None`.

    """
    import argparse
    import configparser
    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-f", "--conf_file",
                        help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect_conf",
                        action="store_true", default=True,
                        help="Try to detect config file: *.ini, *.cfg")

    argv, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    defaults["show_args"] = False
    defaults["check-only"] = False
    defaults["diff"] = False
    defaults["in-place"] = False
    defaults["recursive"] = False
    defaults["normalize_string_quotes"] = True
    defaults["inline_quotes"] = '"'
    defaults["multiline_quotes"] = '"""'
    defaults["lowercase_string_prefix"] = True
    defaults["remove_string_u_prefix"] = True

    cfg_files = []
    if argv.autodetect_conf:
        for f in os.listdir():
            if f.endswith('.ini') or f.endswith('.cfg'):
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
                    _dict = {key.replace("-", "_"):value for (key,value) in _dict.items()}
                    defaults.update(_dict)
                except:
                    pass
        except:
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
                        "Could be combined with --diff")
    parser.add_argument("-d", "--diff", action="store_true",
                        help="Print changes without make changes. "
                        "Could be combined with --in-place")
    parser.add_argument("-c", "--check-only", action="store_true",
                        help="Exit with a status code of 1 if any changes are still needed")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
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
    parser.add_argument("files", nargs="+",
                        help="Files to format")

    args = parser.parse_args(remaining_argv)

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
                filenames += [os.path.join(root, f) for f in children
                              if f.endswith(".py") and not f.startswith(".")]
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
