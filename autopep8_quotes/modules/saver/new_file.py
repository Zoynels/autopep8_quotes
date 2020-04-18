﻿
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-n", "--new-file", action="store_true",
                            help="Make changes to files and create new file in "
                            "same location with .autopep8_quotesing extention. "
                            "If --new-file and --check-only then will be used only --check-only. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["new_file"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.new_file:
                with self.open_with_encoding(args._read_filename + ".autopep8_quotes",
                                             mode="w",
                                             encoding=args._read_encoding) as output_file:
                    output_file.write(formatted_source)
                return "return", True
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.new_file
