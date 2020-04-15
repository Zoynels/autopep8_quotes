import datetime
import os
import sys
from typing import Any
from typing import Dict
from typing import List

from autopep8_quotes import __doc__
from autopep8_quotes import __title_name__
from autopep8_quotes import __version__
from autopep8_quotes._util import load_modules
from autopep8_quotes._util import parse_startup

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


def agrs_parse(argv: List[Any]) -> Any:  # type Namespace
    import argparse
    import configparser

    # Load all modules from location
    _modules_dict = {}
    _modules_dict.update(load_modules("format", pat=r"(^|\/|\\)fmt_.*\.py$", ext=".py"))
    _modules_dict.update(load_modules("format", pat=r"(^|\/|\\)save_.*\.py$", ext=".py"))

    # Set default arguments for function
    defaults: Dict[str, Any] = {}
    for key in _modules_dict:
        _modules_dict[key].formatter().default_arguments(defaults)

    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["save_values_to_file"] = False
    defaults["recursive"] = False
    defaults["filename"] = [r".*\.py$"]

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

    args, remaining_argv = conf_parser.parse_known_args()

    # Read config files
    cfg_files = []
    if args.autodetect_conf:
        for f in os.listdir():
            if f.endswith(".ini") or f.endswith(".cfg"):
                cfg_files.append(f)
    cfg_files = sorted(cfg_files)
    if args.config_file:
        cfg_files.append(args.config_file)

    for f in cfg_files:
        try:
            config = configparser.SafeConfigParser()
            config.read([f])
            for sec in __read_sections__:
                try:
                    _dict = dict(config.items(sec))
                    _dict = {str(key).replace("-", "_"): value for (key, value) in _dict.items()}
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
    parser.add_argument("--filename",
                        type=str, nargs="+",
                        help="Check only for filenames matching the patterns.")
    parser.add_argument("files", nargs="+",
                        help="Files to format")

    # Add options like argparser.add_argument() from loaded modules
    for key in _modules_dict:
        _modules_dict[key].formatter().add_arguments(parser)

    args = parser.parse_args(remaining_argv)

    ###########################################################
    # After prepare args we add some calculateble variables and modules
    ###########################################################

    # Add loaded modules to args
    args._modules_dict = _modules_dict

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    # Transform string into list
    if isinstance(args.filename, (str)):
        args.filename = [args.filename]

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
