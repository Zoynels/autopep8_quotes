from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import ast


def str2bool(v: Any) -> bool:
    """Transforms string values into boolean"""
    if isinstance(v, bool):
        return v
    elif str(v).lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif str(v).lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return False


def str2bool_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
    try:
        for key in dict1:
            try:
                if isinstance(dict1[key], (bool)):
                    if key in dict2:
                        dict2[key] = str2bool(dict2[key])
            except Exception:  # pragma: no cover
                pass
    except Exception:  # pragma: no cover
        pass


def get_list_of_order(_dict: Union[SimpleNamespace, Dict[str, Any]], search: Union[str, List[str]]) -> Set[str]:
    if isinstance(_dict, SimpleNamespace):
        _dict = _dict.__dict__
    if not isinstance(search, list):
        search = list(search)

    n = []
    for key in _dict:
        if key in search:
            n.append(_dict[key])

    # Get entire line
    st = ";".join(n).replace("-", "_").lower().split(";")

    # Remove options from name
    m = []
    for x in st:
        pos = x.find("[")
        if pos == -1:
            m.append(x)
        else:
            m.append(x[:pos])
    return set(m)


def parse_startup(args: SimpleNamespace, n: str, groups: Union[str, List[str]], search: Union[str, List[str]]) -> None:
    """Transform string values into list of order startup
    First/Last modules could run several times like check-only in example
        that will run several times with different arguments
    Undefined function will run between First/Last modules in os.listdir() order
"""
    # Get all modules with order
    m_exist = get_list_of_order(args, search)

    if not isinstance(groups, list):
        groups = list(groups)

    for val in [f"{n}_first", f"{n}_last"]:
        args.__dict__[f"_{val}"] = []
        st = args.__dict__.get(val, "").replace("-", "_").lower()
        for x in st.split(";"):
            pos = x.find("[")
            if pos == -1:
                name, kwargs = x, {}
            else:
                name, kwargs = x[:pos], ast.literal_eval(x[pos:][1:-1])

            for group in groups:
                if group not in args._plugins:
                    continue
                # If write one module several times, then add several times
                # even in it has same args
                for mod in list(args._plugins[group].keys()):
                    if mod.lower().replace("-", "_").endswith(name.lower()):
                        d = SimpleNamespace()
                        d.mod_path = mod
                        d.loaded = args._plugins[group][mod].loaded
                        d.apply = args._plugins[group][mod].apply
                        d.name = name
                        d.kwargs = kwargs
                        d.start = f"_{val}"
                        args.__dict__[f"_{val}"].append(d)

    # Get medium modules
    args.__dict__[f"_{n}_med"] = []
    all_modules = []
    for group in groups:
        if group not in args._plugins:
            continue
        for mod in list(args._plugins[group].keys()):
            if mod in all_modules:
                # Add module only once
                # Because it is not written in order
                continue
            found = False
            for m in m_exist:
                if mod.endswith(f":{m}"):
                    found = True
                    break

            if not found:
                d = SimpleNamespace()
                d.mod_path = mod
                d.loaded = args._plugins[group][mod].loaded
                d.apply = args._plugins[group][mod].apply
                d.name = mod
                d.kwargs = {}
                d.start = f"_{n}_med"
                args.__dict__[f"_{n}_med"].append(d)
                all_modules.append(mod)

    # Get real order
    args.__dict__[f"_{n}_order"] = []
    for val in [f"_{n}_first", f"_{n}_med", f"_{n}_last"]:
        for k in args.__dict__[val]:
            args.__dict__[f"_{n}_order"].append(k)


def get_order_plugins_list(args: SimpleNamespace, L: List[str], all_plugins: List[str]) -> List[str]:
    used_plugins = []
    for order in L:
        for plugin_desc in args.__dict__[order]:
            try:
                name = plugin_desc.get("name", "")
                name = name.replace("-", "_").lower()
                if name in all_plugins:
                    used_plugins.append(name)
            except BaseException:
                pass
    return list(set(used_plugins))


def get_order_unused(used_plugins: List[str], all_plugins: List[str]) -> List[Dict[str, str]]:
    med = []
    for x in all_plugins:
        if x not in used_plugins:
            med.append({"name": str(x)})
    return med


def get_order_123(args: SimpleNamespace, L: List[str], func_default: Optional[str] = None, func_set: Optional[str] = None) -> List[SimpleNamespace]:
    order = []
    for i in L:
        for plugin_desc in args.__dict__[i]:
            if "name" not in plugin_desc:
                continue

            d = SimpleNamespace()
            d.__dict__.update(plugin_desc)
            d.name = d.name.replace("-", "_").lower()

            if "args" not in d.__dict__:
                d.args = ()

            if "kwargs" not in d.__dict__:
                d.kwargs = {}

            if "func" not in d.__dict__:
                if func_default is not None:
                    d.func = func_default
            if func_set is not None:
                d.func = func_default

            order.append(d)
    return order
