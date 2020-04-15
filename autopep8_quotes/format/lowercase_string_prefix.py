import re
from types import SimpleNamespace
from typing import Any
from typing import Dict


def lowercase_string_prefix(leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
    """Make furbFURB prefixes lowercase.

    Original from https://github.com/psf/black
    """
    if args.lowercase_string_prefix:
        match = re.match(r"^([furbFURB]*)(.*)$", leaf, re.DOTALL)
        assert match is not None, f"failed to match string {leaf!r}"
        orig_prefix = match.group(1)
        new_prefix = orig_prefix
        new_prefix = new_prefix.replace("F", "f")
        new_prefix = new_prefix.replace("U", "u")
        new_prefix = new_prefix.replace("R", "r")
        new_prefix = new_prefix.replace("B", "b")
        leaf = f"{new_prefix}{match.group(2)}"
    return leaf
