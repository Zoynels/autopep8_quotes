import sys
from types import SimpleNamespace
from typing import Any
from typing import Dict

from autopep8_quotes._util._modules import main_formatter


class formatter(main_formatter):
    def add_arguments(self, parser: Any, **kwargs: Any) -> None:
        parser.add_argument("-c", "--check", action="store_true",
                            help="Check if any changes are still needed (Exit with a status code of 1).")
        parser.add_argument("-ch", "--check-only", action="store_true",
                            help="Check if any changes are still needed (Exit with a status code of 1). "
                            "Aggressive function that should not work with other 'saver' functions "
                            "which edit files like --in-place/--new-file (prevent its work). ")

    def default_arguments(self, defaults: Dict[str, Any], **kwargs: Any) -> None:
        defaults["check"] = False
        defaults["check_only"] = False

    def show_or_save(self,
                     args: SimpleNamespace,
                     source: Any,
                     formatted_source: Any,
                     **kwargs: Any
                     ) -> Any:
        """Actions with result"""
        if source != formatted_source:
            if args.check_only:
                sys.exit("Error: need changes in file: {args._read_filename}")
            if args.check:
                self.stdout_print("\n" + self.color.red + f"    need changes in file: {args._read_filename}", otype=args._standard_out)
                self.stdout_print("\n", otype=args._standard_out)
        return "continue"

    def check_is_enabled(self, args: SimpleNamespace, **kwargs: Any) -> None:
        """Check: Can be this function be enabled"""
        pass
