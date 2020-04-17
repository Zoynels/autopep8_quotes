import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-cs", "--check-soft", "--check", action="store_true",
                            help="Check if any changes are still needed. "
                            "Compare source on start and formatted code when finish run all modules. "
                            "Even if all changes were made before check == changes is needed. "
                            "Check all files and print list of files that need changes. ")

        parser.add_argument("-ch", "--check-hard", action="store_true",
                            help="Check if any changes are still needed. "
                            "Even if all changes were made before check == changes is needed. "
                            "Compare source on start and formatted code when finish run all modules. "
                            "Exit with a error code when find first file that need changes. ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["check_soft"] = False
        defaults["check_hard"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.check_hard:
                sys.exit(f"Error: --check-hard: need changes in file: {args._read_filename}")
            if args.check_soft:
                self.stdout_print("\n" + self.color.red + f"    need changes in file: {args._read_filename}", otype=args._standard_out)
            return "return", True
        return "continue"
