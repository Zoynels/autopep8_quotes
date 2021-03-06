﻿
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        super().__init__()
        self.is_show_or_save = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("-i", "--in-place", "--inplace", action="store_true",
                            help="Make changes to files. "
                            "If --in-place and --check-only then will be used only --check-only. "
                            "Be carefull when use --in-place and --new-file togeather. "
                            "Please use right order in --start-save-first/--start-save-last options. ")
        parser.add_argument("-i2", "--in-place-count", action="store_true",
                            help="Count changes files. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["in_place"] = False
        defaults["in_place_count"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.in_place:
                if args.in_place_count:
                    args._diff_files_count += 1
                with self.open_with_encoding(args._read_filename, mode="w",
                                             encoding=args._read_encoding) as output_file:
                    output_file.write(formatted_source)
                args._read_file_need_load = True
                return "return", False
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.in_place
