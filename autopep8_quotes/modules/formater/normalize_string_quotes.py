import re
from enum import Enum
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import tokenize

from autopep8_quotes._util._format import isevaluatable
from autopep8_quotes._util._format import save_values_to_file
from autopep8_quotes._util._format import sub_twice
from autopep8_quotes._util._modules import main_formatter


class quotes_codes(Enum):
    changed__quote_bruteforce = -3
    changed__old_quote = -2
    changed__new_quote = -1
    original__equal = 1
    original__bad_value = 2
    original__cant_transform = 3
    original__cant_detect_quote_type = 11
    original__cant_find_first_quote = 12
    original__unescaped_quote_in_r_prefix = 13
    original__backslashes_in_expressions = 14
    original__do_not_introduce_more_escaping = 15
    original__prefer_double_quotes = 16
    original__empty = 17


class formatter(main_formatter):
    def __init__(self) -> None:
        super().__init__()
        self.is_parse = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("--normalize-string-quotes", "--nsq",
                            action="store_true",
                            help="Normalize all quotes to standart "
                                 "by options --multiline-quotes and --inline-quotes")
        parser.add_argument("--inline-quotes", "--nsq-inline-quotes",
                            choices=["'", '"'],
                            help="Preferred inline-quotes. "
                            "Works only when --normalize-string-quotes is True")
        parser.add_argument("--multiline-quotes", "--nsq-multiline-quotes",
                            choices=["'''", '"""'],
                            help="Preferred multiline-quotes. "
                            "Works only when --normalize-string-quotes is True")
        parser.add_argument("--nsq-log-transform",
                            action="store_true",
                            help="Log transform strings from normalize-string-quotes plugin. "
                            "Works only when --normalize-string-quotes is True. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["normalize_string_quotes"] = True
        defaults["inline_quotes"] = '"'
        defaults["multiline_quotes"] = '"""'
        defaults["nsq_log_transform"] = False

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.normalize_string_quotes

    def parse(self, token: tokenize.TokenInfo,
              line_tokens: List[tokenize.TokenInfo],
              args: SimpleNamespace,
              token_dict: Dict[str, Any],
              *_args: Any,
              **kwargs: Any
              ) -> tokenize.TokenInfo:
        """Prefer quotes but only if it doesn't cause more escaping.

        Adds or removes backslashes as appropriate.
        Doesn't parse and fix strings nested in f-strings (yet).

        Original from https://github.com/psf/black
        Second return value:
            if result > 0 then error else no error but may be warning
        """
        if token.type != tokenize.STRING:
            return token

        def parse(leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any], change_quote: bool = False) -> Tuple[str, quotes_codes]:
            body_quoted = leaf.lstrip("furbFURB")

            quotes = {}
            quotes["'''"] = '"""'
            quotes['"""'] = "'''"
            quotes["'"] = '"'
            quotes['"'] = "'"

            if (body_quoted[:3] == body_quoted[-3:]) and len(body_quoted) >= 6:
                if body_quoted[:3] == args.multiline_quotes:
                    orig_quote = args.multiline_quotes
                    if change_quote:
                        new_quote = quotes[args.multiline_quotes]
                    else:
                        new_quote = args.multiline_quotes
                else:
                    orig_quote = quotes[args.multiline_quotes]
                    new_quote = args.multiline_quotes
            elif body_quoted[:1] == body_quoted[-1:]:
                if body_quoted[0] == args.inline_quotes:
                    orig_quote = args.inline_quotes
                    new_quote = quotes[args.inline_quotes]
                else:
                    orig_quote = quotes[args.inline_quotes]
                    new_quote = args.inline_quotes
            else:
                if args.nsq_log_transform:
                    save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__cant_detect_quote_type")
                return leaf, quotes_codes.original__cant_detect_quote_type

            first_quote_pos = leaf.find(orig_quote)
            if first_quote_pos == -1:
                if args.nsq_log_transform:
                    save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__cant_find_first_quote")
                return leaf, quotes_codes.original__cant_find_first_quote

            prefix = leaf[:first_quote_pos]
            unescaped_new_quote = re.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
            escaped_new_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
            escaped_orig_quote = re.compile(rf"([^\\]|^)\\((?:\\\\)*){orig_quote}")

            escaped_quote_single_el_v1 = re.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote[0]}")
            escaped_quote_single_el_v2 = re.compile(rf"([^\\]|^)\\((?:\\\\)*){quotes[new_quote[0]][0]}")

            body = leaf[first_quote_pos + len(orig_quote): -len(orig_quote)]
            # Save body for future checks
            old_body = body

            if "r" in prefix.casefold():
                if unescaped_new_quote.search(body):
                    # There's at least one unescaped new_quote in this raw string
                    # so converting is impossible
                    if args.nsq_log_transform:
                        save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__unescaped_quote_in_r_prefix")
                    return leaf, quotes_codes.original__unescaped_quote_in_r_prefix

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
                    return self.check_string(leaf, prefix, old_body, new_body, orig_quote, new_quote, args=args, token_dict=token_dict)
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
                        if args.nsq_log_transform:
                            save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__backslashes_in_expressions")
                        return leaf, quotes_codes.original__backslashes_in_expressions

            if len(new_quote) == 3 and new_body[-1:] == new_quote[0]:
                # edge case:
                new_body = new_body[:-1] + "\\" + new_quote[0]
            orig_escape_count = body.count("\\")
            new_escape_count = new_body.count("\\")
            if new_escape_count > orig_escape_count:
                if args.nsq_log_transform:
                    save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__do_not_introduce_more_escaping")
                return leaf, quotes_codes.original__do_not_introduce_more_escaping

            if new_escape_count == orig_escape_count and orig_quote == args.inline_quotes:
                if args.nsq_log_transform:
                    save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__prefer_double_quotes")
                return leaf, quotes_codes.original__prefer_double_quotes

            return self.check_string(leaf, prefix, old_body, new_body, orig_quote, new_quote, args=args, token_dict=token_dict)

        if args.normalize_string_quotes:
            result_string, code = parse(token.string, args=args, token_dict=token_dict, change_quote=False)
            if code == quotes_codes.changed__quote_bruteforce:
                # Try to change quote """ => ''' and vice versa
                result_string_v2, code_v2 = parse(token.string, args=args, token_dict=token_dict, change_quote=True)
                if code_v2 in [quotes_codes.changed__old_quote, quotes_codes.changed__new_quote]:
                    result_string, code = result_string_v2, code_v2

            if args.debug:
                self.stdout_print(args, "normalize_string_quotes: ")
                self.stdout_print(args, "    code:           {code}")
                self.stdout_print(args, "    input_sting:    {token.string}")
                self.stdout_print(args, "    result_string:  {result_string}")

            if result_string is not None:
                token = tokenize.TokenInfo(type=token.type, string=result_string, start=token.start, end=token.end, line=token.line)
                return token

        if args.nsq_log_transform:
            save_values_to_file(args=args, input_list=[token_dict], name="nsq-leaf_None")
        return token

    def bruteforce_body(self, body: str, prefix: str, quote: str) -> str:
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
                    continue

            if not last_line:
                # All symbols instead of last symbol which should be escaped
                # ast.literal_eval: if last symbol is quote[0] then it should be escaped
                # but that it it not last sybmol of body then check if it not a last
                v11 = f"{prefix}{quote}{new_body + body[i] + space}{quote}"
                v11_res = isevaluatable(v11)
                if v11_res[0]:
                    new_body = new_body + body[i]
                    continue

            # Escaped symbol
            v20 = f"{prefix}{quote}{new_body+delim+body[i]}{quote}"
            v20_res = isevaluatable(v20)
            if v20_res[0]:
                new_body = new_body + delim + body[i]
                continue

        # Result line. It could be not normal
        return f"{prefix}{quote}{new_body}{quote}"

    def check_string(self,
                     original: str,
                     prefix: str,
                     old_body: str,
                     new_body: str,
                     orig_quote: str,
                     new_quote: str,
                     args: SimpleNamespace,
                     token_dict: Dict[str, Any]
                     ) -> Tuple[str, quotes_codes]:

        v1 = f"{prefix}{new_quote}{new_body}{new_quote}"
        v2 = f"{prefix}{orig_quote}{new_body}{orig_quote}"
        if original == v1:
            if args.nsq_log_transform:
                save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__equal")
            return original, quotes_codes.original__equal

        v0_res = isevaluatable(original, prefix)
        if not v0_res[0]:
            self.stdout_print(args, "")
            self.stdout_print(args, self.color.red + "Can't check original! Please test string manually!" + self.color.reset)
            self.stdout_print(args, "    " + self.color.red + f"Filename:   {token_dict['filename']}" + self.color.reset)
            self.stdout_print(args, "    " + self.color.red + f"Position:   {token_dict['pos']}" + self.color.reset)
            self.stdout_print(args, "    " + self.color.red + f"String:     {token_dict['token_string']}" + self.color.reset)
            self.stdout_print(args, "")
            if args.nsq_log_transforn:
                save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__bad_value")
            return original, quotes_codes.original__bad_value

        v1_res = isevaluatable(v1, prefix)
        # Good string and value is not changed!
        if v1_res[0] and (v1_res[1] == v0_res[1]):
            if args.debug:
                self.stdout_print(args, self.color.red + f"Return v1: {v1}" + self.color.reset)
            if args.nsq_log_transform:
                save_values_to_file(args=args, input_list=[token_dict], name="nsq-changed__new_quote")
            return v1, quotes_codes.changed__new_quote

        v2_res = isevaluatable(v2, prefix)
        # Good string and value is not changed!
        if v2_res[0] and (v2_res[1] == v0_res[1]):
            if args.debug:
                self.stdout_print(args, self.color.red + f"Return v2: {v2}" + self.color.reset)
            if args.nsq_log_transform:
                save_values_to_file(args=args, input_list=[token_dict], name="nsq-changed__old_quote")
            return v2, quotes_codes.changed__old_quote

        v3 = self.bruteforce_body(new_body, prefix, new_quote)
        v3_res = isevaluatable(v3, prefix)
        if v3_res[0] and (v3_res[1] == v0_res[1]):
            if args.debug:
                self.stdout_print(args, self.color.red + f"Return v3: {v3}" + self.color.reset)
            if args.nsq_log_transform:
                save_values_to_file(args=args, input_list=[token_dict], name="nsq-changed__quote_bruteforce")
            return v3, quotes_codes.changed__quote_bruteforce

        return self.check_string__cant_transform(original, v1, v2, args, token_dict)

    def check_string__cant_transform(self,
                                     original: str,
                                     v1: str,
                                     v2: str,
                                     args: SimpleNamespace,
                                     token_dict: Dict[str, Any]
                                     ) -> Tuple[str, quotes_codes]:
        self.stdout_print(args, "")
        self.stdout_print(args, self.color.red + "Can't transform, return original! Please simpify string manually!" + self.color.reset)
        self.stdout_print(args, "    " + self.color.red + f"Filename:   {token_dict['filename']}" + self.color.reset)
        self.stdout_print(args, "    " + self.color.red + f"Position:   {token_dict['pos']}" + self.color.reset)
        self.stdout_print(args, "    " + self.color.red + f"String:     {token_dict['token_string']}" + self.color.reset)
        self.stdout_print(args, "        " + self.color.red + f"Original:   {original}" + self.color.reset)
        self.stdout_print(args, "        " + self.color.red + f"Try v1:     {v1}" + self.color.reset)
        self.stdout_print(args, "        " + self.color.red + f"Try v2:     {v2}" + self.color.reset)
        self.stdout_print(args, "")
        if args.nsq_log_transform:
            save_values_to_file(args=args, input_list=[token_dict], name="nsq-original__cant_transform")
        return original, quotes_codes.original__cant_transform
