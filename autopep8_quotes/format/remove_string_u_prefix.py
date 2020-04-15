import re
from types import SimpleNamespace
from typing import Any
from typing import Dict


def remove_string_u_prefix(leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
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
