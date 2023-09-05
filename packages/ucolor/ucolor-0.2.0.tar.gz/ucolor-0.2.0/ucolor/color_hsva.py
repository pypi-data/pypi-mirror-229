"""
This module provides the ColorHSLA class for representing colors in HSLA format.

The ColorHSVA class includes methods for color manipulation such as linear
interpolation (lerp) and mixing.

It also includes properties for accessing and modifying individual color
components (hue, saturation, value, alpha).

Additionally, the module provides predefined colors as class properties
(white, black, red, etc.).
"""

__all__ = ["ColorHSVA"]

from typing import Self
from .utils import _in_range, _lerp


class ColorHSVA:
    """
    A class to represent HSLA color.

    Attributes:
    h: float
        Hue component of the color, in the range 0-360.
    s: float
        Saturation component of the color, in the range 0-100.
    v: float
        Value component of the color, in the range 0-100.
    a: float = 1
        Alpha (transparency) component of the color, in the range 0-1.

    Methods:
    __str__(self) -> str

    __repr__(self) -> str

    __eq__(self, other: ColorHSVA) -> bool

    lerp(cls, a: ColorHSLA, b: ColorHSVA, t: float) -> ColorHSVA

    mix(cls, a: ColorHSLA, b: ColorHSVA) -> ColorHSVA
    """

    def __init__(self, h: float, s: float, v: float, a: float = 1) -> None:
        self.__h = h
        self.__s = s
        self.__v = v
        self.__a = a
        if not self.__isValid():
            raise ValueError("Hue must be in 0..360, "
                             "Saturation and Volume must be in 0..100 and "
                             "Alpha in 0..1")

    # magic methods
    def __str__(self) -> str:
        """ Returns a string representation of the color """
        return f"h={self.__h}, s={self.__s}, v={self.__v}, a={self.__a}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the color, suitable for debugging
        """
        return (f"<ColorHSLA(h={self.__h}, s={self.__s}, v={self.__v}, "
                f"a={self.__a}) at {hex(id(self))}>")

    def __eq__(self, other: Self) -> bool:
        """ Checks if this color is equal to another color """
        return self.__h == other.__h and self.__s == other.s \
               and self.__v == other.v and self.__a == other.a

    # private methods
    def __isValid(self) -> bool:
        return _in_range(self.__h, 0, 360) \
               and _in_range(self.__s, 0, 100) \
               and _in_range(self.__v, 0, 100) \
               and _in_range(self.__a, 0, 1)

    # colors
    @classmethod
    @property
    def white(cls) -> Self:
        return ColorHSVA(0, 0, 100)

    @classmethod
    @property
    def black(cls) -> Self:
        return ColorHSVA(0, 0, 0)

    @classmethod
    @property
    def red(cls) -> Self:
        return ColorHSVA(0, 100, 100)

    @classmethod
    @property
    def orange(cls) -> Self:
        return ColorHSVA(31, 100, 100)

    @classmethod
    @property
    def yellow(cls) -> Self:
        return ColorHSVA(60, 100, 100)

    @classmethod
    @property
    def green(cls) -> Self:
        return ColorHSVA(120, 100, 100)

    @classmethod
    @property
    def blue(cls) -> Self:
        return ColorHSVA(198, 100, 100)

    @classmethod
    @property
    def darkBlue(cls) -> Self:
        return ColorHSVA(228, 100, 100)

    @classmethod
    @property
    def purple(cls) -> Self:
        return ColorHSVA(270, 100, 78)

    # hsla components
    @property
    def h(self) -> float:
        """ Hue HSLA component """
        return self.__h

    @h.setter
    def h(self, new_value: int) -> None:
        if not _in_range(new_value, 0, 360):
            raise ValueError("Hue must be in 0..360")
        self.__h = new_value

    @property
    def s(self) -> float:
        """ Saturation HSLA component """
        return self.__s

    @s.setter
    def s(self, new_value: int) -> None:
        if not _in_range(new_value, 0, 100):
            raise ValueError("Saturation must be in 0..100")
        self.__s = new_value

    @property
    def v(self) -> float:
        """ Lightness HSLA component """
        return self.__v

    @v.setter
    def v(self, new_value: int) -> None:
        if not _in_range(new_value, 0, 100):
            raise ValueError("Value must be in 0..100")
        self.__v = new_value

    @property
    def a(self) -> float:
        """ HSLA Alpha component """
        return self.__a

    @a.setter
    def a(self, new_value: int) -> None:
        if not _in_range(new_value, 0, 1):
            raise ValueError("Alpha must be in 0..1!")
        self.__a = new_value

    # lerp
    @classmethod
    def lerp(cls, a: Self, b: Self, t: float) -> Self:
        """ Mixes two colors with a certain factor and returns the result """
        return ColorHSVA(
            _lerp(a.h, b.h, t),
            _lerp(a.s, b.s, t),
            _lerp(a.v, b.v, t),
            _lerp(a.a, b.a, t)
        )

    @classmethod
    def mix(cls, a: Self, b: Self) -> Self:
        """ Mixes two colors with a factor of 0.5 and returns the result """
        return ColorHSVA.lerp(a, b, 0.5)

