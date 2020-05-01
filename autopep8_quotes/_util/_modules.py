from abc import ABCMeta
from abc import abstractmethod
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

import tokenize

from autopep8_quotes._util._colorama import col_green
from autopep8_quotes._util._colorama import col_magenta
from autopep8_quotes._util._colorama import col_red
from autopep8_quotes._util._io import open_with_encoding
from autopep8_quotes._util._io import stdout_print


class main_formatter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self) -> None:
        self.open_with_encoding = open_with_encoding
        self.stdout_print = stdout_print
        self.color = SimpleNamespace()
        self.color.green = col_green
        self.color.red = col_red
        self.color.magenta = col_magenta

    @abstractmethod
    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        """Add options like argparser.add_argument()"""
        pass  # pragma: no cover

    @abstractmethod
    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        """Set default args for argparser"""
        pass  # pragma: no cover

    @abstractmethod
    def parse(self, token: tokenize.TokenInfo,
              line_tokens: List[tokenize.TokenInfo],
              args: SimpleNamespace,
              token_dict: Dict[str, Any],
              *_args: Any,
              **kwargs: Any
              ) -> tokenize.TokenInfo:
        """Action on token"""
        return token  # pragma: no cover

    @abstractmethod
    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        pass  # pragma: no cover

    @abstractmethod
    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return False  # pragma: no cover

    @abstractmethod
    def run_pass(self, *_args: Any, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        pass  # pragma: no cover

    @abstractmethod
    def return_self(self, *_args: Any, **kwargs: Any) -> "main_formatter":
        """Check: Can be this function be enabled"""
        return self  # pragma: no cover
