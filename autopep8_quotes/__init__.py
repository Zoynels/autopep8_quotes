"""Unify strings to all use the same quote and etc.
Source: https://github.com/Zoynels/autopep8_quotes"""

import os
import re
import signal
import sys
from typing import Any

from autopep8_quotes._util._io import return__stdout_err
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
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk(name):
                for f in children:
                    if f.startswith("."):
                        continue
                    for pat in args.read_files_matching_pattern:
                        if re.match(pat, os.path.join(root, f), re.DOTALL):
                            filenames.append(os.path.join(root, f))

                directories[:] = [d for d in directories if not d.startswith(".")]
        else:
            try:
                args._read_filename = name
                if __base_function__(args=args):
                    changes_needed = True
            except IOError as exception:
                print(exception, file=return__stdout_err(args._standard_error))
                failure = True

    if failure or (args.check_only and changes_needed):
        return 1
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
