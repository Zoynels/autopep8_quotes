
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-i", "--in-place", action="store_true",
                            help="Make changes to files. "
                            "If --in-place and --check-only then will be used only --check-only. "
                            "Be carefull when use --in-place and --new-file togeather. "
                            "Please use right order in --start-save-first/--start-save-last options. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["in_place"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> None:
        """Actions with result"""
        if args.in_place:
            with self.open_with_encoding(args._read_filename, mode="w",
                                         encoding=args._read_encoding) as output_file:
                output_file.write(formatted_source)

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        if args.in_place and args.check_only:
            args.in_place = False
            self.stdout_print("\n" + self.color.red + "Option --in-place and --check_only shouldn't pass togeather.", otype=args._standard_out)
            self.stdout_print("\n", otype=args._standard_out)
            self.stdout_print("\n" + self.color.green + "Disable --in-place, run only --check_only", otype=args._standard_out)
            self.stdout_print("\n", otype=args._standard_out)
