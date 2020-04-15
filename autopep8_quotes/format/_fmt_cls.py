from types import SimpleNamespace
from typing import Any
from typing import Dict


class main_formatter(object):
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: Any) -> None:
        pass

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        return leaf
