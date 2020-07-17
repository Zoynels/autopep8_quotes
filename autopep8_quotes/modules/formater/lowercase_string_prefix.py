import re
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

import tokenize

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("--lowercase-string-prefix", action="store_true",
                            help='Make FURB prefixes lowercase: B"sometext" to b"sometext"')

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["lowercase_string_prefix"] = True

    def parse(self, token: tokenize.TokenInfo,
              line_tokens: List[tokenize.TokenInfo],
              args: SimpleNamespace,
              token_dict: Dict[str, Any],
              *_args: Any,
              **kwargs: Any
              ) -> tokenize.TokenInfo:
        """Make furbFURB prefixes lowercase.

        Original from https://github.com/psf/black
        """
        if args.lowercase_string_prefix:
            if token.type != tokenize.STRING:
                return token

            leaf = token.string
            match = re.match(r"^([furbFURB]*)(.*)$", leaf, re.DOTALL)
            assert match is not None, f"failed to match string {leaf!r}"
            orig_prefix = match.group(1)
            new_prefix = orig_prefix
            new_prefix = new_prefix.replace("F", "f")
            new_prefix = new_prefix.replace("U", "u")
            new_prefix = new_prefix.replace("R", "r")
            new_prefix = new_prefix.replace("B", "b")
            leaf = f"{new_prefix}{match.group(2)}"

            token = tokenize.TokenInfo(type=token.type, string=leaf, start=token.start, end=token.end, line=token.line)
        return token

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.lowercase_string_prefix
