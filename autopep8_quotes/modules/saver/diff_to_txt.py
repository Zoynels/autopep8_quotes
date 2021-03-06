﻿import difflib
import os
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        super().__init__()
        self.is_show_or_save = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("-t", "--diff-to-txt", action="store_true",
                            help="Save changes into txt file. "
                            "Real changes can be applied by other modules. ")
        parser.add_argument("-t2", "--diff-to-txt-count", action="store_true",
                            help="Count changes files. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["diff_to_txt"] = False
        defaults["diff_to_txt_count"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.diff_to_txt:
                if args.diff_to_txt_count:
                    args._diff_files_count += 1
                diff = difflib.unified_diff(
                    source.splitlines(),
                    formatted_source.splitlines(),
                    "before/" + args._read_filename,
                    "after /" + args._read_filename,
                    lineterm="")

                os.makedirs("log", exist_ok=True)
                fname = os.path.abspath(f"log/autopep8_quotes.diff.{args._datetime_start.strftime('%Y%m%d %H%M%S')}.txt")
                self.stdout_print(args, "\n    " + self.color.magenta + f"diff-to-txt: save file: {fname}" + self.color.reset, otype=args._standard_out)

                with self.open_with_encoding(fname, mode="a", encoding="utf-8") as output_file:
                    self.stdout_print(args, "\n".join(list(diff) + [""]), otype=output_file)
                return "return", True
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.diff_to_txt
