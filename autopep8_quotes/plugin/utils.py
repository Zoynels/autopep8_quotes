import re, sys
from types import SimpleNamespace
import logging, sys
import collections
LOG = logging.getLogger(__name__)
import inspect
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Union

def get_module(cls):
    def get_submodule(mod, path, level=0):
        if isinstance(path, str):
            path = path.split(".")
        if len(path) == level+1:
            return mod
        return get_submodule(mod.__dict__[path[level+1]], path, level=level+1)

    try:
        module_name = cls.__module__
        module = __import__(module_name)
    except:
        return None

    return get_submodule(module, module_name)


def check_equal(value, search, none_is_true=True):
    found = False
    for sel in to_list(search):
        if sel is None:
            if none_is_true:
                found = True
                break
            if value is None:
                found = True
                break
        elif str(value) == str(sel):
            found = True
            break
    return found

def check_re(value, search, none_is_true=True):
    for sel in to_list(search):
        if sel is None:
            if none_is_true:
                return True
            if value is None:
                return True
        elif (re.search(sel, str(value)) is not None):
                return True
    return False

def to_list(value, dict_to_keys=True):
    if value is None:
        value = [None]
    elif isinstance(value, SimpleNamespace):
        if dict_to_keys:
            value = list(value.__dict__.keys())
        else:
            value = list(value.__dict__)
    elif isinstance(value, dict):
        if dict_to_keys:
            value = list(value.keys())
        else:
            value = list(value)
    elif not isinstance(value, (list)):
        value = [value]
    return value


