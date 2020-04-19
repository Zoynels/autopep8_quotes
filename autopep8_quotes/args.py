import datetime
import os
import pathlib
import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

from autopep8_quotes import __doc__
from autopep8_quotes import __title_name__
from autopep8_quotes import __version__
from autopep8_quotes._util._args import parse_startup
from autopep8_quotes._util._args import str2bool_dict
from autopep8_quotes._util._io import load_modules_ep

__read_sections__ = ["pep8", "flake8", "autopep8", "autopep8_quotes"]


def agrs_parse(argv: List[Any], **kwargs: Any) -> SimpleNamespace:
    """Main function to parse basic args of cli"""
    import argparse
    import configparser

    # Load all plugins from entry_point
    _plugins = {}
    _plugins["formatter"] = load_modules_ep("autopep8_quotes.formatter")
    _plugins["saver"] = load_modules_ep("autopep8_quotes.saver")

    # Prepare config file parser
    conf_parser = argparse.ArgumentParser(add_help=False)

    # Do not add args which could be rewritten by config-file
    # Use here only args which influence on config-file
    conf_parser.add_argument("-f", "--config-file",
                             help="Specify config file", metavar="FILE")
    conf_parser.add_argument("-a", "--autodetect-config-file",
                             metavar="FILEPATH", default="",
                             help="Try to detect config file: *.ini, *.cfg in location. ")

    args_parsed, remaining_argv = conf_parser.parse_known_args(argv)

    # Set default arguments for function after parse
    defaults: Dict[str, Any] = {}
    for plugin_group in _plugins:
        for plugin in _plugins[plugin_group]:
            _plugins[plugin_group][plugin].apply.default_arguments(defaults)

    defaults["print_files"] = False
    defaults["debug"] = False
    defaults["show_args"] = False
    defaults["save_values_to_file"] = False
    defaults["recursive"] = False
    defaults["read_files_matching_pattern"] = [r".*\.py$"]

    # Apply on complete file, then next module
    # 1. Check all file: is there any need of changes
    # 2. Save diff into file
    # 3. Print diff into terminal
    # 4. Make changes into independent file
    # 5. Make changes into source file (rewrite it)
    # 6. Check files: is there any need of changes (Exit code 1)

    # Algo work
    # -> plugin_order_onfile(func1)
    #  -> read file1 and apply
    #    -> read token(1)
    #      -> plugin_order_ontoken(func1)
    #      -> plugin_order_ontoken(func2)
    #    -> read token(2)
    #      -> plugin_order_ontoken(func1)
    #      -> plugin_order_ontoken(func2)
    # -> apply saver function: plugin_order_onfile(func1)
    # If there are some function that not defined either in order_onfile or order_ontoken
    # then it run and onfile and ontoken, but between first and last list
    defaults["plugin_order_onfile_first"] = "check-soft;diff-to-txt;diff"
    defaults["plugin_order_onfile_last"] = "new-file;in-place;check-hard"

    # Apply on each token
    defaults["plugin_order_ontoken_first"] = """save-values-to-file[{"name": "before_change"}];remove-string-u-prefix;lowercase-string-prefix"""
    defaults["plugin_order_ontoken_last"] = """normalize-string-quotes;save-values-to-file[{"name": "after_change"}]"""

    # Read config files
    cfg_files = []
    if args_parsed.autodetect_config_file:
        look_dir = pathlib.Path(args_parsed.autodetect_config_file)
        if not look_dir.is_dir():
            look_dir = look_dir.parent
        for f in os.listdir(look_dir):
            if f.lower().endswith(".ini") or f.lower().endswith(".cfg"):
                cfg_files.append(str(look_dir.joinpath(f)))
    cfg_files = sorted(cfg_files)
    if args_parsed.config_file:
        cfg_files.append(args_parsed.config_file)

    for f in cfg_files:
        try:
            config = configparser.ConfigParser()
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
    parser.add_argument("--plugin-order-onfile-first", type=str,
                        help="Define order of run functions on entire file (before undefined functions).")
    parser.add_argument("--plugin-order-onfile-lase", type=str,
                        help="Define order of run functions on entire file (after undefined functions).")
    parser.add_argument("--plugin-order-ontoken-first", type=str,
                        help="Define order of run functions on each string token (before undefined functions).")
    parser.add_argument("--plugin-order-ontoken-lase", type=str,
                        help="Define order of run functions on each string token (after undefined functions).")

    # Define files which should be parsed
    parser.add_argument("--files", nargs="+",
                        help="Files to format")

    # Add options like argparser.add_argument() from loaded modules
    for plugin_group in _plugins:
        for plugin in _plugins[plugin_group]:
            _plugins[plugin_group][plugin].apply.add_arguments(parser)

    args_parsed, remaining_argv = parser.parse_known_args(remaining_argv)
    if remaining_argv:
        print(f"Warning: Unrecognized arguments transform to --files: {remaining_argv}")
        args.files = args.files + remaining_argv

    ###################################################################
    # After prepare args we add some calculateble variables and modules
    ###################################################################

    # Convert into SimpleNamespace to add new attrs in future
    args = SimpleNamespace()
    args.__dict__.update(args_parsed.__dict__)
    args.__dict__.update(kwargs)

    # Add loaded modules to args
    args._plugins = _plugins

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    # Transform string values into list of order startup
    m_search = []
    m_search.append("plugin_order_onfile_first")
    m_search.append("plugin_order_onfile_last")
    m_search.append("plugin_order_ontoken_first")
    m_search.append("plugin_order_ontoken_last")
    parse_startup(args, "plugin_order_onfile", ["formatter", "saver"], m_search)
    parse_startup(args, "plugin_order_ontoken", ["formatter", "saver"], m_search)

    # Check: Can function be enabled to run in script or not (if conflict)
    for plugin_group in args._plugins:
        for plugin in args._plugins[plugin_group]:
            args._plugins[plugin_group][plugin].apply.check_is_enabled(args)

    # Add some basic values
    args._datetime_start = datetime.datetime.now()

    if args.show_args:
        print(args)
        sys.exit(0)

    return args
