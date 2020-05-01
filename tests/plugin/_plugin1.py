from types import SimpleNamespace
from typing import Any
from typing import Dict

__version__ = "1.0.0"


class formatter(object):
    name = "TestPlugin1"
    version = "1.0.0"

    def __init__(self) -> None:
        pass

    def CLI__add_argument(self, parser: Any, **kwargs: Any) -> None:
        """Add options like argparser.add_argument()"""
        print(self.name, "CLI__add_argument")
        parser.add_argument("--test_plugin_num1_ha",
                            action="store_true", default=True,
                            help="Test description. ")

    def CLI__set_defaults(self, parser: Any, **kwargs: Any) -> None:
        """Set default args for argparser"""
        defaults = {}
        defaults["test_plugin_num1_ha"] = False

        parser.set_defaults(**defaults)
        print(self.name, "CLI__set_defaults")

    def CONFIG__add_argument(self, parser: Any, **kwargs: Any) -> None:
        """Add options like argparser.add_argument()"""
        print(self.name, "CONFIG__add_argument")

    def CONFIG__set_defaults(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        """Set default args for argparser"""
        print(self.name, "CONFIG__set_defaults")

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        """Action on token"""
        print(self.name, "parse")
        return leaf
