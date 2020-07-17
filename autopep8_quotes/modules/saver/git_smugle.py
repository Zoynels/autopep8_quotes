import io
import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        super().__init__()
        self.is_show_or_save = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("-gs", "--git-smugle", action="store_true",
                            help="Git smugle filter. "
                            "Please use right order in --start-save-first/--start-save-last options. ")
        parser.add_argument("-gs2", "--git-smugle-count", action="store_true",
                            help="Count changes files. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["git_smugle"] = False
        defaults["git_smugle_count"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""

        # write always even if not changed
        if args.git_smugle:
            if args.git_smugle_count:
                args._diff_files_count += 1
            output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
            output_stream.write(formatted_source)
            output_stream.flush()

            args._read_file_need_load = False
            return "return", False
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.git_smugle
