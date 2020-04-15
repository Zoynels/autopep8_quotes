from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes.format._fmt_cls import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-c", "--check-only", action="store_true",
                            help="Check if any changes are still needed (Exit with a status code of 1).")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["check_only"] = False

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        return leaf

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if args.check_only:
            return ["return", True]
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        pass
