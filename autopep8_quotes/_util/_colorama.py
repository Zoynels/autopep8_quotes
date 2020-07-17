from types import SimpleNamespace
from typing import Generator
from typing import Iterator

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
except ImportError:  # fallback so that the imported classes always exist
    pass
    # disable now, because don't know how to enable/disable print message
    # print("Can't import 'colorama' module to colorize output. "
    #       "Will use uncolored output!")

    class ColorFallback():
        def __getattr__(self, name: str) -> str:
            try:
                colorama.init(autoreset=True)
            except BaseException:
                pass
            return ""

    colorama = SimpleNamespace()
    colorama.Fore = ColorFallback()
    colorama.Back = ColorFallback()
    colorama.Style = ColorFallback()

col_red = colorama.Style.BRIGHT + colorama.Back.RED
col_green = colorama.Style.BRIGHT + colorama.Back.GREEN
col_magenta = colorama.Style.BRIGHT + colorama.Back.MAGENTA
col_reset = colorama.Style.RESET_ALL


def color_diff(diff: Iterator[str]) -> Generator[str, None, None]:
    """Colorize diff lines"""
    for line in diff:
        if line.startswith("+"):
            yield colorama.Fore.LIGHTGREEN_EX + line + colorama.Style.RESET_ALL
        elif line.startswith("-"):
            yield colorama.Fore.LIGHTRED_EX + line + colorama.Style.RESET_ALL
        elif line.startswith("^"):
            yield colorama.Fore.LIGHTBLUE_EX + line + colorama.Style.RESET_ALL
        else:
            yield colorama.Fore.LIGHTWHITE_EX + line + colorama.Style.RESET_ALL
