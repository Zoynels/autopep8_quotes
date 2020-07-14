"""Unify strings to all use the same quote and etc.
Source: https://github.com/Zoynels/autopep8_quotes"""

import os
import re
import signal
import sys
from typing import Any

from autopep8_quotes._util._colorama import col_green
from autopep8_quotes._util._colorama import col_red
from autopep8_quotes._util._io import stdout_print
from autopep8_quotes._util._main import format_file as __base_function__

__version__ = "0.6.3"
__title_name__ = "autopep8_quotes"


def _main(args: Any, standard_out: Any, standard_error: Any) -> int:
    """Run function on files.

    Returns `1` if any changes are still needed, otherwise 0"""

    from . args import agrs_parse

    kwargs = {}
    kwargs["_standard_out"] = standard_out
    kwargs["_standard_error"] = standard_error
    args = agrs_parse(args, **kwargs)

    filenames = list(set(args.files))
    changes_needed = False
    failure_files_count = 0
    read_files_count = 0
    args._diff_files_count = 0
    while filenames:
        name = filenames.pop(0)
        if os.path.isdir(name):
            if args.recursive:
                for root, directories, children in os.walk(name):
                    for f in children:
                        for pat in args.read_files_matching_pattern:
                            if re.match(pat, os.path.join(root, f), re.DOTALL):
                                filenames.append(os.path.join(root, f))

                    directories[:] = [d for d in directories if not d.startswith(".")]
            else:
                for f in os.listdir(name):
                    if os.path.isfile(os.path.join(name, f)):
                        for pat in args.read_files_matching_pattern:
                            if re.match(pat, os.path.join(name, f), re.DOTALL):
                                filenames.append(os.path.join(name, f))
        elif os.path.isfile(name):
            try:
                if args.print_files:
                    stdout_print(f"    read: {name}", otype="ok")
                read_files_count += 1
                args._read_filename = name
                if __base_function__(args=args):
                    changes_needed = True
            except IOError as exception:
                stdout_print(exception, otype="error")
                failure_files_count += 1
        else:
            from errno import ENOENT
            raise IOError(ENOENT, f"File is not exist: {name}", name)

    if failure_files_count != 0:
        stdout_print(col_red + f"Error: read {read_files_count} source files with failure {failure_files_count}", otype="ok")
        if args.exit_zero:
            return 0
        return 1

    if args._diff_files_count != 0:
        stdout_print(col_red + f"Failure: read {read_files_count} with changes in {args._diff_files_count} files", otype="ok")
        if args.exit_zero:
            return 0
        return 1

    stdout_print(col_green + f"Success: read {read_files_count} source files", otype="ok")
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
        return _main(sys.argv[1:],
                     standard_out="sys.stdout",
                     standard_error="sys.stderr")
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
