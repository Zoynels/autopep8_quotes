import difflib
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._colorama import color_diff
from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        super().__init__()
        self.is_show_or_save = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("-d", "--diff", action="store_true",
                            help="Print changes. "
                            "Real changes can be applied by other modules. ")
        parser.add_argument("-d2", "--diff-count", action="store_true",
                            help="Count changes files. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["diff"] = False
        defaults["diff_count"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.diff:
                if args.diff_count:
                    args._diff_files_count += 1
                diff = difflib.unified_diff(
                    source.splitlines(),
                    formatted_source.splitlines(),
                    "before/" + args._read_filename,
                    "after /" + args._read_filename,
                    lineterm="")
                self.stdout_print(args, "\n".join(list(color_diff(diff)) + [""]), otype=args._standard_out)
                return "return", True
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.diff
