from typing import Iterator, Generator
from types import SimpleNamespace

try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        def __getattr__(self, name: str) -> str:
            return ""

    colorama = SimpleNamespace()
    colorama.Fore = ColorFallback()
    colorama.Back = ColorFallback()
    colorama.Style = ColorFallback()


col_red = colorama.Style.BRIGHT + colorama.Back.RED
col_green = colorama.Style.BRIGHT + colorama.Back.GREEN


def color_diff(diff: Iterator[str]) -> Generator[str, None, None]:
    """Colorize diff lines"""
    for line in diff:
        if line.startswith("+"):
            yield colorama.Fore.GREEN + line + colorama.Fore.RESET
        elif line.startswith("-"):
            yield colorama.Fore.RED + line + colorama.Fore.RESET
        elif line.startswith("^"):
            yield colorama.Fore.BLUE + line + colorama.Fore.RESET
        else:
            yield line
