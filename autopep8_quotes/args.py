import ast
import datetime
import os
import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

from autopep8_quotes import __doc__
from autopep8_quotes import __title_name__
from autopep8_quotes import __version__
from autopep8_quotes._util._io import load_modules

__read_sections__ = ["pep8", "flake8", "autopep8", "autopep8_quotes"]


def str2bool(v: Any) -> bool:
    """Transforms string values into boolean"""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return False


def str2bool_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
    for key in dict1:
        try:
            if isinstance(dict1[key], (bool)):
                if key in dict2:
                    dict2[key] = str2bool(dict2[key])
        except BaseException:
            pass


def parse_startup(args: SimpleNamespace, n: str) -> None:
    """Transform string values into list of order startup
    First/Last modules could run several times like check-only in example
        that will run several times with different arguments
    Undefined function will run between First/Last modules in os.listdir() order

    args = SimpleNamespace()
    args.__dict__["start_save_first"] = "check-only[{'sometext':'aha'}];diff-to-txt;diff;new-file;check-only"
    args.__dict__["start_save_last"] = "in-place;check"
    args.__dict__["_modules_dict"] = {
        "mod/check_only": "somemodule",
        "mod/diff_to_txt": "somemodule",
        "mod/diff": "somemodule",
        "mod/new_file": "somemodule",
        "mod/in_place": "somemodule",
        "mod/check": "somemodule",
        "mod/somethingelse": "somemodule",
    }
    parse_startup(args, "start_save")
    
    # Have result of function
    args._start_save_order == [
        {'mod_path': 'mod/check_only', 'module': 'somemodule', 'name': 'check_only', 'kwargs': {'sometext': 'aha'}, 'start': '_start_save_first'},
        {'mod_path': 'mod/diff_to_txt', 'module': 'somemodule', 'name': 'diff_to_txt', 'kwargs': {}, 'start': '_start_save_first'},
        {'mod_path': 'mod/diff', 'module': 'somemodule', 'name': 'diff', 'kwargs': {}, 'start': '_start_save_first'},
        {'mod_path': 'mod/new_file', 'module': 'somemodule', 'name': 'new_file', 'kwargs': {}, 'start': '_start_save_first'},
        {'mod_path': 'mod/check_only', 'module': 'somemodule', 'name': 'check_only', 'kwargs': {}, 'start': '_start_save_first'},
        {'mod_path': 'mod/somethingelse', 'module': 'somemodule', 'name': 'check', 'kwargs': {}, 'start': '_start_save_med'},
        {'mod_path': 'mod/in_place', 'module': 'somemodule', 'name': 'in_place', 'kwargs': {}, 'start': '_start_save_last'},
        {'mod_path': 'mod/check', 'module': 'somemodule', 'name': 'check', 'kwargs': {}, 'start': '_start_save_last'}
    ]

"""
    all_used_modules = []
    for val in [f"{n}_first", f"{n}_last"]:
        args.__dict__[f"_{val}"] = []
        st = args.__dict__.get(val, "").replace("-", "_").lower()
        for x in st.split(";"):
            pos = x.find("[")
            if pos == -1:
                name, kwargs = x, {}
            else:
                name, kwargs = x[:pos], ast.literal_eval(x[pos:][1:-1])
            for mod in list(args._modules_dict.keys()):
                if mod.lower().replace("-", "_").endswith(name.lower()):
                    d = {}
                    d["mod_path"] = mod
                    d["module"] = args._modules_dict[mod]
                    d["name"] = name
                    d["kwargs"] = kwargs
                    d["start"] = f"_{val}"
                    args.__dict__[f"_{val}"].append(d)
                    all_used_modules.append(mod)

    # Get medium modules
    args.__dict__[f"_{n}_med"] = []
    for mod in list(args._modules_dict.keys()):
        if mod not in all_used_modules:
            d = {}
            d["mod_path"] = mod
            d["module"] = args._modules_dict[mod]
            d["name"] = name
            d["kwargs"] = {}
            d["start"] = f"_{n}_med"
            args.__dict__[f"_{n}_med"].append(d)

    # Get real order
    args.__dict__[f"_{n}_order"] = []
    for val in [f"_{n}_first", f"_{n}_med", f"_{n}_last"]:
        for k in args.__dict__[val]:
            args.__dict__[f"_{n}_order"].append(k)


def agrs_parse(argv: List[Any]) -> SimpleNamespace:
    """Main function to parse basic args of cli"""
    import argparse
    import configparser

    # Load all modules from location
    _modules_dict = {}
    _modules_dict.update(load_modules("modules/formater", pat=r".*\.py$", ext=".py"))
    _modules_dict.update(load_modules("modules/saver", pat=r".*\.py$", ext=".py"))

    # Set default arguments for function
    defaults: Dict[str, Any] = {}
    for key in _modules_dict:
        _modules_dict[key].formatter().default_arguments(defaults)

    defaults["print_files"] = False
    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["save_values_to_file"] = False
    defaults["recursive"] = False
    defaults["read_files_matching_pattern"] = [r".*\.py$"]
    defaults["start_parse_first"] = "remove-string-u-prefix;lowercase-string-prefix"
    defaults["start_parse_last"] = "normalize-string-quotes"
    defaults["start_save_first"] = "check-only;diff-to-txt;diff;new-file"
    defaults["start_save_last"] = "in-place;check"

    # Prepare config file parser
    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.set_defaults(**defaults)

    # Do not add args which could be rewritten by config-file
    # Use here only args which influence on config-file
    conf_parser.add_argument("-f", "--config-file",
                             help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect-config-file",
                             action="store_true", default=True,
                             help="Try to detect config file: *.ini, *.cfg")

    args_parsed, remaining_argv = conf_parser.parse_known_args()

    # Read config files
    cfg_files = []
    if args_parsed.autodetect_config_file:
        for f in os.listdir():
            if f.endswith(".ini") or f.endswith(".cfg"):
                cfg_files.append(f)
    cfg_files = sorted(cfg_files)
    if args_parsed.config_file:
        cfg_files.append(args_parsed.config_file)

    for f in cfg_files:
        try:
            config = configparser.SafeConfigParser()
            config.read([f])
            for sec in __read_sections__:
                try:
                    _dict = dict(config.items(sec))
                    _dict = {str(k).replace("-", "_").lower(): v for (k, v) in _dict.items()}
                    str2bool_dict(defaults, _dict)
                    defaults.update(_dict)
                except Exception as e:
                    pass
        except Exception as e:
            pass

    # Prepare argv parser which inherit data from config parser
    parser = argparse.ArgumentParser(
        parents=[conf_parser],
        description=__doc__,
        prog=__title_name__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True)
    parser.set_defaults(**defaults)

    # Define basic options
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s " + __version__,
                        help="Show program's version number and exit")

    parser.add_argument("--debug", action="store_true",
                        help="Show debug messages")

    parser.add_argument("--show-args", action="store_true",
                        help="Show readed args for script and exit")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
    parser.add_argument("--print-files", action="store_true",
                        help="Print parsed files")

    parser.add_argument("--read-files-matching-pattern",
                        type=str, nargs="+",
                        help="Check only for filenames matching the pattern.")

    # Define order when run functions
    parser.add_argument("--start-parse-first", type=str,
                        help="Define order when run parse function (before undefined functions).")
    parser.add_argument("--start-parse-last", type=str,
                        help="Define order when run parse function (after undefined functions).")
    parser.add_argument("--start-save-first", type=str,
                        help="Define order when run save function (before undefined functions).")
    parser.add_argument("--start-save-last", type=str,
                        help="Define order when run save function (after undefined functions).")

    # Define some addiotional functions: TODO: move to module
    parser.add_argument("--save-values-to-file", action="store_true",
                        help="Save all strings into file. "
                        "All founded values before any reformatting, "
                        "bad original values and error values when reformat them.")

    # Define files which should be parsed
    parser.add_argument("files", nargs="+",
                        help="Files to format")

    # Add options like argparser.add_argument() from loaded modules
    for key in _modules_dict:
        _modules_dict[key].formatter().add_arguments(parser)

    args_parsed = parser.parse_args(remaining_argv)

    ###################################################################
    # After prepare args we add some calculateble variables and modules
    ###################################################################

    # Convert into SimpleNamespace to add new attrs in future
    args = SimpleNamespace()
    args.__dict__.update(args_parsed.__dict__)

    # Add loaded modules to args
    args._modules_dict = _modules_dict

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    # Transform string into list
    if isinstance(args.read_files_matching_pattern, (str)):
        args.read_files_matching_pattern = [args.read_files_matching_pattern]

    # Transform string values into list of order startup
    parse_startup(args, "start_parse")
    parse_startup(args, "start_save")

    # Check: Can function be enabled to run in script or not (if conflict)
    for key in _modules_dict:
        _modules_dict[key].formatter().check_is_enabled(args)

    # Add some basic values
    args._datetime_start = datetime.datetime.now()

    if args.show_args:
        print(args)
        sys.exit(0)

    return args
