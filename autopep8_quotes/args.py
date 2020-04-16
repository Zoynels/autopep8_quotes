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
from autopep8_quotes._util._io import parse_startup

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


def agrs_parse(argv: List[Any]) -> SimpleNamespace:
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

    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["save_values_to_file"] = False
    defaults["recursive"] = False
    defaults["read_files_matching_pattern"] = [r".*\.py$"]
    defaults["start_save_first"] = "check-only;diff-to-txt;diff;new-file"
    defaults["start_save_last"] = "in-place;check"
    defaults["start_parse_first"] = "remove-string-u-prefix;lowercase-string-prefix"
    defaults["start_parse_last"] = "normalize-string-quotes"

    # Prepare config file parser
    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.set_defaults(**defaults)

    conf_parser.add_argument("-f", "--config-file",
                             help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect-conf",
                             action="store_true", default=True,
                             help="Try to detect config file: *.ini, *.cfg")
    conf_parser.add_argument("--debug", action="store_true",
                             help="Show debug messages")
    conf_parser.add_argument("--show-args", action="store_true",
                             help="Show readed args for script and exit")
    conf_parser.add_argument("-v", "--version", action="version",
                             version="%(prog)s " + __version__,
                             help="Show program's version number and exit")
    conf_parser.add_argument("--start-parse-first", type=str, 
                             help="Define order when run parse function (before undefined functions).")
    conf_parser.add_argument("--start-parse-last", type=str, 
                             help="Define order when run parse function (after undefined functions).")
    conf_parser.add_argument("--start-save-first", type=str, 
                             help="Define order when run save function (before undefined functions).")
    conf_parser.add_argument("--start-save-last", type=str, 
                             help="Define order when run save function (after undefined functions).")

    args_parsed, remaining_argv = conf_parser.parse_known_args()

    # Read config files
    cfg_files = []
    if args_parsed.autodetect_conf:
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

    parser.add_argument("-s", "--save-values-to-file", action="store_true",
                        help="Save all strings into file.")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
    parser.add_argument("--read-files-matching-pattern",
                        type=str, nargs="+",
                        help="Check only for filenames matching the patterns.")
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
