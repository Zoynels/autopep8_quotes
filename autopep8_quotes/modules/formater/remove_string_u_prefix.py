import re
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("--remove-string-u-prefix", action="store_true",
                            help='Removes any u prefix from the string: u"sometext" to "sometext"')

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["remove_string_u_prefix"] = True

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

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.remove_string_u_prefix
