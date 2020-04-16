"""Unify strings to all use the same quote and etc.
Source: https://github.com/Zoynels/autopep8_quotes"""

import os
import re
import signal
import sys
from typing import Any

from autopep8_quotes._util._colorama import col_green
from autopep8_quotes._util._colorama import col_red
from autopep8_quotes._util._io import stdout_return
from autopep8_quotes._util._main import format_file as __base_function__

__version__ = "0.6"
__title_name__ = "autopep8_quotes"


def _main(args: Any, standard_out: Any, standard_error: Any) -> int:
    """Run function on files.

    Returns `1` if any changes are still needed, otherwise 0"""

    from . args import agrs_parse
    args = agrs_parse(args)

    args._standard_out = standard_out
    args._standard_error = standard_error

    filenames = list(set(args.files))
    changes_needed = False
    failure = False
    read_files_count = 0
    while filenames:
        name = filenames.pop(0)
        if os.path.isdir(name):
            if args.recursive:
                for root, directories, children in os.walk(name):
                    for f in children:
                        if f.startswith("."):
                            continue
                        for pat in args.read_files_matching_pattern:
                            if re.match(pat, os.path.join(root, f), re.DOTALL):
                                filenames.append(os.path.join(root, f))

                    directories[:] = [d for d in directories if not d.startswith(".")]
            else:
                for f in os.listdir(name):
                    if os.path.isfile(os.path.join(name, f)):
                        filenames.append(os.path.join(name, f))
        elif os.path.isfile(name):
            try:
                if args.print_files:
                    print(f"    read: {name}", file=stdout_return(args._standard_out))
                read_files_count += 1
                args._read_filename = name
                if __base_function__(args=args):
                    changes_needed = True
            except IOError as exception:
                print(exception, file=stdout_return(args._standard_error))
                failure = True
        else:
            raise RuntimeError(f"Unknown type of file/dir: {name}")

    if failure or (args.check_only and changes_needed):
        print(col_red + f"Error: read {read_files_count} source files", file=stdout_return(args._standard_out))
        return 1

    print(col_green + f"Success: read {read_files_count} source files", file=stdout_return(args._standard_out))
    return 0


def main() -> int:  # pragma: no cover
    """Return exit status."""
    try:
        # Exit on broken pipe.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:
        # SIGPIPE is not available on Windows.
        pass

    try:
        return _main(sys.argv,
                     standard_out="sys.stdout",
                     standard_error="sys.stderr")
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
