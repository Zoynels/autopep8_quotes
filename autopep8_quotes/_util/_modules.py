from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._colorama import col_green
from autopep8_quotes._util._colorama import col_magenta
from autopep8_quotes._util._colorama import col_red
from autopep8_quotes._util._io import open_with_encoding
from autopep8_quotes._util._io import print__stdout_err


class main_formatter(object):
    def __init__(self) -> None:
        self.open_with_encoding = open_with_encoding
        self.print__stdout_err = print__stdout_err
        self.color = SimpleNamespace()
        self.color.green = col_green
        self.color.red = col_red
        self.color.magenta = col_magenta

    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        """Add options like argparser.add_argument()"""
        pass

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        """Set default args for argparser"""
        pass

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        """Action on token"""
        return leaf

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        pass

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        pass
