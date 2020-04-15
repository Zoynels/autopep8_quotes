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
from autopep8_quotes.format._colorama import col_green
from autopep8_quotes.format._colorama import col_red


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
        if isinstance(dict1[key], (bool)):
            dict2[key] = str2bool(dict2[key])
        else:
            pass


def agrs_parse(argv: List[Any]) -> Any:  # type Namespace
    import argparse
    import configparser

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-f", "--config-file",
                             help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect-conf",
                             action="store_true", default=True,
                             help="Try to detect config file: *.ini, *.cfg")

    args, remaining_argv = conf_parser.parse_known_args()

    defaults: Dict[str, Any] = {}
    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["check_only"] = False
    defaults["diff"] = False
    defaults["in_place"] = False
    defaults["new_file"] = False
    defaults["save_values_to_file"] = False
    defaults["recursive"] = False
    defaults["normalize_string_quotes"] = True
    defaults["inline_quotes"] = '"'
    defaults["multiline_quotes"] = '"""'
    defaults["lowercase_string_prefix"] = True
    defaults["remove_string_u_prefix"] = True
    defaults["filename"] = [r".*\.py$"]

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
            for sec in ["pep8", "flake8", "autopep8", "autopep8_quotes"]:
                try:
                    _dict = dict(config.items(sec))
                    _dict = {key.replace("-", "_"): value for (key, value) in _dict.items()}
                    str2bool_dict(defaults, _dict)
                    defaults.update(_dict)
                except BaseException:
                    pass
        except BaseException:
            pass

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser],
        description=__doc__,
        prog=__title_name__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True)
    parser.set_defaults(**defaults)

    parser.add_argument("-i", "--in-place", action="store_true",
                        help="Make changes to files. "
                        "Could be combined with --diff and can't combined with --in-place"
                        "If --inplace --new-file then will be used only --new-file")
    parser.add_argument("-n", "--new-file", action="store_true",
                        help="Make changes to files and create new file with "
                        ".autopep8_quotesing extention. "
                        "Could be combined with --diff and can't combined with --in-place"
                        "If --inplace --new-file then will be used only --new-file")
    parser.add_argument("-d", "--diff", action="store_true",
                        help="Print changes without make changes. "
                        "Could be combined with --in-place")
    parser.add_argument("-s", "--save-values-to-file", action="store_true",
                        help="Save all strings into file.")
    parser.add_argument("-c", "--check-only", action="store_true",
                        help="Exit with a status code of 1 if any changes are still needed")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
    parser.add_argument("--filename",
                        type=str, nargs="+",
                        help="Check only for filenames matching the patterns.")
    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__,
                        help="Show program's version number and exit")
    parser.add_argument("--show-args", action="store_true",
                        help="Show readed args for script and exit")
    parser.add_argument("--debug", action="store_true",
                        help="Show debug messages")
    parser.add_argument("files", nargs="+",
                        help="Files to format")

    # Load all modules from location
    _modules_dict = load_modules("format", pat=r"($|/|\\)fmt_.*\.py$", ext=".py")
    for key in _modules_dict:
        _modules_dict[key].formatter().add_arguments(parser)

    args = parser.parse_args(remaining_argv)

    # Add loaded modules
    args._modules_dict = _modules_dict

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    args._datetime_start = datetime.datetime.now()

    if args.in_place and args.new_file:
        args.in_place = False
        print(col_red + "Option --in-place and --new-file shouldn't pass togeather.")
        print(col_green + "Disable --in-place, run only --new-file")

    if isinstance(args.filename, (str)):
        args.filename = [args.filename]

    if args.show_args:
        print(args)
        sys.exit(0)

    return args
