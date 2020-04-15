"""Unify strings to all use the same quote.
Unify all prefixex to lowercase.
Remove u"" prefixes.
Source: https://github.com/Zoynels/autopep8_quotes"""

import os
import re
import signal
import sys
from typing import IO
from typing import Any

from autopep8_quotes.format._main import format_file as __base_function__

__version__ = "0.6"
__title_name__ = "autopep8_quotes"


def _main(args: Any, standard_out: IO[Any], standard_error: IO[Any]) -> int:
    """Run function on files.

    Returns `1` if any changes are still needed, otherwise 0"""

    from . args import agrs_parse
    args = agrs_parse(args)

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
                    for pat in args.filename:
                        if re.match(pat, os.path.join(root, f), re.DOTALL):
                            filenames.append(os.path.join(root, f))

                directories[:] = [d for d in directories if not d.startswith(".")]
        else:
            try:
                if __base_function__(name, args=args, standard_out=standard_out):
                    changes_needed = True
            except IOError as exception:
                print(exception, file=standard_error)
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
                     standard_out=sys.stdout,
                     standard_error=sys.stderr)
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
