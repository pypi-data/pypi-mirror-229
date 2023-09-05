"""
UltraCOLOR is a Python library that provides functionality for working with
different color spaces. It supports RGBA, Hex and HSLA color spaces, allowing
for accurate color conversion. The library does not require any third-party
dependencies and only utilizes the Python standard library. With UltraCOLOR,
you can easily convert colors between different color spaces and perform various
operations on them.
"""

__all__ = ["DEFAULT_TERM_COLOR", "cprint", "convert", "ColorRGBA", "ColorHSLA",
           "ColorHSVA"]

from . import convert
from .color_rgba import ColorRGBA
from .color_hsla import ColorHSLA
from .color_hsva import ColorHSVA


DEFAULT_TERM_COLOR = "\033[0m"


def cprint(
        text: str,
        color: ColorRGBA | ColorHSLA,
        end: str = DEFAULT_TERM_COLOR + "\n") -> None:
    if isinstance(color, ColorRGBA):
        ansi = convert.rgba_to_ansi(color)
    else:
        ansi = convert.hsla_to_ansi(color)
    print(ansi + text, end=end)

