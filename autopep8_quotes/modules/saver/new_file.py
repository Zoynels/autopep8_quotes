
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def __init__(self):
        super().__init__()
        self.is_show_or_save = True

    def add_arguments(self, parser: Any, *_args: Any, **kwargs: Any) -> None:
        parser.add_argument("-n", "--new-file", action="store_true",
                            help="Make changes to files and create new file in "
                            "same location with .autopep8_quotesing extention. "
                            "If --new-file and --check-only then will be used only --check-only. ")
        parser.add_argument("-n2", "--new-file-count", action="store_true",
                            help="Count changes files. ")

    def default_arguments(self, defaults: Dict[str, Any], *_args: Any, **kwargs: Any) -> None:
        defaults["new_file"] = False
        defaults["new_file_count"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.new_file:
                if args.new_file_count:
                    args._diff_files_count += 1
                with self.open_with_encoding(args._read_filename + ".autopep8_quotes",
                                             mode="w",
                                             encoding=args._read_encoding) as output_file:
                    output_file.write(formatted_source)
                return "return", True
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, *_args: Any, **kwargs: Any) -> Any:
        """Check: Can be this function be enabled"""
        return args.new_file
