from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

import tokenize

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("--remove-empty-lines-spaces", action="store_true",
                            help="Removes any spaces in empty lines")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["remove_empty_lines_spaces"] = True

    def parse(self, token: tokenize.TokenInfo,
              line_tokens: List[tokenize.TokenInfo],
              args: SimpleNamespace,
              token_dict: Dict[str, Any],
              *_args: Any,
              **kwargs: Any
              ) -> tokenize.TokenInfo:
        if args.remove_empty_lines_spaces:
            if (len(line_tokens) != 1) or (token.type != tokenize.NL):
                return token
            if ((token.string != "\n") and (token.string != "\r\n") and (token.string != "\r")):
                return token
            token = tokenize.TokenInfo(type=tokenize.NL, string=token.string, start=(token.start[0], 0), end=(token.end[0], 1), line=token.string)
        return token

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.remove_empty_lines_spaces
