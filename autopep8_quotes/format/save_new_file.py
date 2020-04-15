
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util import open_with_encoding
from autopep8_quotes.format._colorama import col_green
from autopep8_quotes.format._colorama import col_red
from autopep8_quotes.format._fmt_cls import main_formatter


class formatter(main_formatter):
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-n", "--new-file", action="store_true",
                            help="Make changes to files and create new file in "
                            "same location with .autopep8_quotesing extention. "
                            "If --new-file and --check-only then will be used only --check-only. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["new_file"] = False

    def parse(self, leaf: str, args: SimpleNamespace, token_dict: Dict[str, Any]) -> str:
        return leaf

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if args.new_file:
            with open_with_encoding(args._read_filename + ".autopep8_quotes",
                                    mode="w",
                                    encoding=args._read_encoding) as output_file:
                output_file.write(formatted_source)

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        if args.new_file and args.check_only:
            args.new_file = False
            print(col_red + "Option --new-file and --check_only shouldn't pass togeather.")
            print(col_green + "Disable --new-file, run only --check_only")
