﻿import re
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._format import save_values_to_file
from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("--save-values-to-file", action="store_true",
                            help="Save strings into file. "
                            "All founded values before any reformatting, "
                            "bad original values and error values when reformat them. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["save_values_to_file"] = True

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any], **kwargs: Any) -> str:
        if args.save_values_to_file:
            name = kwargs.get("name", "undefined")
            save_values_to_file(args=args, input_list=[token_dict], name=name)
        return leaf

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.save_values_to_file