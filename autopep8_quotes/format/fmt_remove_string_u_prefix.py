﻿import re
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes.format._fmt_cls import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--remove-string-u-prefix", action="store_true",
                            help='Removes any u prefix from the string: u"sometext" to "sometext"')

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
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
