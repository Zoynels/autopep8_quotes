from types import SimpleNamespace
from typing import Any
from typing import Dict

__version__ = '2.0.0'


class formatter(object):
    name = 'TestPlugin2'
    version = '2.0.0'

    def __init__(self) -> None:
        pass

    def CLI__add_argument(self, parser: Any, **kwargs: Any) -> None:
        """Add options like argparser.add_argument()"""
        print(self.name, "CLI__add_argument")

    def CLI__default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        """Set default args for argparser"""
        print(self.name, "CLI__default_arguments")

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        """Action on token"""
        print(self.name, "parse")
        return leaf
