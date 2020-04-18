﻿import difflib
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._colorama import color_diff
from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-d", "--diff", action="store_true",
                            help="Print changes. "
                            "Real changes can be applied by other modules. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["diff"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.diff:
                diff = difflib.unified_diff(
                    source.splitlines(),
                    formatted_source.splitlines(),
                    "before/" + args._read_filename,
                    "after /" + args._read_filename,
                    lineterm="")
                self.stdout_print("\n".join(list(color_diff(diff)) + [""]), otype=args._standard_out)
                return "return", True
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.diff
