from typing import Iterator
from types import SimpleNamespace
from typing import Generator

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
except ImportError:  # fallback so that the imported classes always exist
    print("Can't import 'colorama' module to colorize output. "
          "Will use uncolored output!")

    class ColorFallback():
        def __getattr__(self, name: str) -> str:
            return ""

    colorama = SimpleNamespace()
    colorama.Fore = ColorFallback()
    colorama.Back = ColorFallback()
    colorama.Style = ColorFallback()


col_red = colorama.Style.BRIGHT + colorama.Back.RED
col_green = colorama.Style.BRIGHT + colorama.Back.GREEN
col_magenta = colorama.Style.BRIGHT + colorama.Back.MAGENTA


def color_diff(diff: Iterator[str]) -> Generator[str, None, None]:
    """Colorize diff lines"""
    for line in diff:
        if line.startswith("+"):
            yield colorama.Fore.LIGHTGREEN_EX + line + colorama.Fore.RESET
        elif line.startswith("-"):
            yield colorama.Fore.LIGHTRED_EX + line + colorama.Fore.RESET
        elif line.startswith("^"):
            yield colorama.Fore.LIGHTBLUE_EX + line + colorama.Fore.RESET
        else:
            yield colorama.Fore.LIGHTWHITE_EX + line + colorama.Fore.RESET
