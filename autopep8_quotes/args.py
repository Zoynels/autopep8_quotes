import datetime
import json
import logging
import os
import pathlib
import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List

from zs_pluginmanager.manager import PluginManager

from autopep8_quotes import __doc__
from autopep8_quotes import __title_name__
from autopep8_quotes import __version__
from autopep8_quotes._util import _args as _util_args
from autopep8_quotes._util._args import str2bool_dict
from autopep8_quotes._util._io import stdout_print

LOG = logging.getLogger(__name__)


__read_sections__ = ["pep8", "flake8", "autopep8", "autopep8_quotes"]


def agrs_parse(argv: List[Any], *_args: Any, **kwargs: Any) -> SimpleNamespace:
    """Main function to parse basic args of cli"""
    import argparse
    import configparser

    plugins = PluginManager()
    plugins.load_global("autopep8_quotes.formatter", label="formatter")
    plugins.load_global("autopep8_quotes.saver", label="saver")

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
    plugins.map_all(func="default_arguments", defaults=defaults)

    defaults["exit_zero"] = False
    defaults["print_files"] = False
    defaults["print_disable"] = False
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
    defaults["plugin_order_onfile_first"] = """[{"name": "check-soft"}, {"name": "diff-to-txt"}, {"name": "diff"}]"""
    defaults["plugin_order_onfile_last"] = """[{"name": "new-file"}, {"name": "in-place"}, {"name": "check-hard"}, {"name": "git-smugle"}]"""

    # Apply on each token
    defaults["plugin_order_ontoken_first"] = "["
    defaults["plugin_order_ontoken_first"] += '{"name": "save-values-to-file", "kwargs": {"name": "before_change"}}, '
    defaults["plugin_order_ontoken_first"] += '{"name": "remove-string-u-prefix"}, '
    defaults["plugin_order_ontoken_first"] += '{"name": "lowercase-string-prefix"} '
    defaults["plugin_order_ontoken_first"] += "]"

    defaults["plugin_order_ontoken_last"] = """[{"name": "normalize-string-quotes"}, {"name": "fix-end-file-lines"}, """ + \
        """{"name": "save-values-to-file", "kwargs": {"name": "after_change"}}]"""

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
                except BaseException as e:
                    LOG.warning(f"Pass exception when read section '{sec}' in config_file: '{f}', {e}")
        except BaseException as e:
            LOG.critical(f"Pass exception when read config_file: '{f}', {e}")

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
    parser.add_argument("--print-disable", action="store_true",
                        help="Disable print msg")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Drill down directories recursively")
    parser.add_argument("--print-files", action="store_true",
                        help="Print parsed files")
    parser.add_argument("--exit-zero", action="store_true",
                        help='Exit with status code "0" even if there are errors.')

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
    plugins.map_all(func="add_arguments", parser=parser)

    args_parsed, remaining_argv = parser.parse_known_args(remaining_argv)
    if remaining_argv:
        stdout_print(args_parsed, f"Warning: Unrecognized arguments transform to --files: {remaining_argv}", otype="ok")
        if args_parsed.files is None:
            args_parsed.files = []
        args_parsed.files = args_parsed.files + remaining_argv

    ###################################################################
    # After prepare args we add some calculateble variables and modules
    ###################################################################

    # Convert into SimpleNamespace to add new attrs in future
    args = SimpleNamespace()
    args.__dict__.update(args_parsed.__dict__)
    args.__dict__.update(kwargs)

    # Transform string values into boolean
    str2bool_dict(defaults, args.__dict__)

    # Transform string values into list of order startup
    all_plugins = [x.name for x in plugins]

    _F = "_plugin_order_onfile_first"
    _M = "_plugin_order_onfile_med"
    _L = "_plugin_order_onfile_last"
    _O = "_plugin_order_onfile_order"
    args.__dict__[_F] = json.loads(args.__dict__[_F[1:]])
    args.__dict__[_L] = json.loads(args.__dict__[_L[1:]])
    used_plugins = _util_args.get_order_plugins_list(args=args, L=[_F, _L], all_plugins=all_plugins)
    args.__dict__[_M] = _util_args.get_order_unused(used_plugins=used_plugins, all_plugins=all_plugins)
    args.__dict__[_O] = _util_args.get_order_123(args=args, L=[_F, _M, _L], func_set="return_self")

    _F = "_plugin_order_ontoken_first"
    _M = "_plugin_order_ontoken_med"
    _L = "_plugin_order_ontoken_last"
    _O = "_plugin_order_ontoken_order"
    args.__dict__[_F] = json.loads(args.__dict__[_F[1:]])
    args.__dict__[_L] = json.loads(args.__dict__[_L[1:]])
    used_plugins = _util_args.get_order_plugins_list(args=args, L=[_F, _L], all_plugins=all_plugins)
    args.__dict__[_M] = _util_args.get_order_unused(used_plugins=used_plugins, all_plugins=all_plugins)
    args.__dict__[_O] = _util_args.get_order_123(args=args, L=[_F, _M, _L], func_set="return_self")

    # Add loaded modules to args
    args._plugins_manager = plugins

    # Check: Can function be enabled to run in script or not (if conflict)
    plugins.map_all(func="check_is_enabled", args=args)

    # Add some basic values
    args._datetime_start = datetime.datetime.now()

    if args.show_args:
        stdout_print(args, str(args), otype="ok")
        sys.exit(0)

    args._dev_debug_level = 0
    return args
