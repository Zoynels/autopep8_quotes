from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

import tokenize

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("--fix-end-file-lines", action="store_true",
                            help="Set only one empty line in the end of file (remove several or add one line)")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["fix_end_file_lines"] = True

    def parse(self, token: tokenize.TokenInfo,
              line_tokens: List[tokenize.TokenInfo],
              args: SimpleNamespace,
              token_dict: Dict[str, Any],
              *_args: Any,
              **kwargs: Any
              ) -> tokenize.TokenInfo:
        if args.fix_end_file_lines:
            if token.type == tokenize.ENDMARKER:
                # remove all new lines in the end of file
                while True:
                    if args._modified_tokens[-1][1] not in ["\r\n", "\n", "\r"]:
                        break
                    args._modified_tokens.pop()

                if args._modified_tokens[-1] not in ["\r\n", "\n", "\r"]:
                    args._modified_tokens.append((tokenize.NEWLINE, "\r\n", token.start, token.end, token.line))
        return token

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.fix_end_file_lines
