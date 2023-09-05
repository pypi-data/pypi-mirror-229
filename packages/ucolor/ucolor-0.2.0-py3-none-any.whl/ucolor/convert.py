"""
This module provides various color conversion utilities.
It includes functions to convert:
- HSLA to RGBA
- Hex to RGBA
- RGBA to HSLA
- Hex to HSLA
- RGBA to Hex
- HSLA to Hex
- RGBA to ANSI
- HSLA to ANSI
- Hex to ANSI

Each function takes in a color in one format and returns it in another.
The color formats supported are HSLA, RGBA and HEX.
"""

__all__ = ["hsla_to_rgba", "hex_to_rgba", "rgba_to_hsla", "hex_to_hsla",
           "rgba_to_hex", "hsla_to_hex", "rgba_to_ansi", "hsla_to_ansi",
           "hex_to_ansi"]

import re
from math import fabs
from .color_rgba import ColorRGBA
from .color_hsla import ColorHSLA
from .color_hsva import ColorHSVA
from .utils import _to_decimal


long_hex_expr = re.compile("^#" + "([0-9A-F]{2})" * 3 + "$")
short_hex_expr = re.compile("^#" + "([0-9A-F])" * 3 + "$")


# toRgba
def hsla_to_rgba(hsla: ColorHSLA) -> ColorRGBA:
    h, s, l = (_to_decimal(hsla.h), _to_decimal(hsla.s) / 100,
               _to_decimal(hsla.l) / 100)
    c = (1 - abs(l * 2 - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    r = g = b = 0
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x
    return ColorRGBA(
        float((m + r) * 255),
        float((m + g) * 255),
        float((m + b) * 255),
        hsla.a
    )


def hsva_to_rgba(hsva: ColorHSVA) -> ColorRGBA:
    h, s, v = _to_decimal(hsva.h), _to_decimal(hsva.s) / 100, _to_decimal(hsva.v) / 100
    c = s * v
    x = c * (1 - abs(h / 60 % 2 - 1))
    m = v - c
    r = g = b = 0

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    return ColorRGBA(
        float((m + r) * 255),
        float((m + g) * 255),
        float((m + b) * 255),
        hsva.a
    )


def hex_to_rgba(hex_value: str) -> ColorRGBA:
    result = short_hex_expr.search(hex_value)
    if result is not None:
        r = int(result.group(1) * 2, 16)
        g = int(result.group(2) * 2, 16)
        b = int(result.group(3) * 2, 16)
        return ColorRGBA(r, g, b)

    result = long_hex_expr.search(hex_value)
    if result is None:
        raise ValueError(f"Invalid hex number: {hex_value}")
    r = int(result.group(1), 16)
    g = int(result.group(2), 16)
    b = int(result.group(3), 16)

    return ColorRGBA(r, g, b)


# toHsla
def rgba_to_hsla(rgba: ColorRGBA) -> ColorHSLA:
    r = _to_decimal(rgba.r) / 255
    g = _to_decimal(rgba.g) / 255
    b = _to_decimal(rgba.b) / 255

    max_value = max(r, g, b)
    min_value = min(r, g, b)
    delta = max_value - min_value

    # Calculate hue
    if delta == 0:
        h = 0
    elif max_value == r:
        h = ((g - b) / delta) % 6
    elif max_value == g:
        h = (b - r) / delta + 2
    else:
        h = (r - g) / delta + 4
    h *= 60

    # Calculate lightness
    l = (max_value + min_value) / 2

    # Calculate saturation
    if delta == 0:
        s = 0
    else:
        s = delta / (1 - abs(l * 2 - 1))

    return ColorHSLA(float(h), float(s * 100), float(l * 100), rgba.a)


def hex_to_hsla(hex_value: str) -> ColorHSLA:
    return rgba_to_hsla(hex_to_rgba(hex_value))


def hsva_to_hsla(hsva: ColorHSVA) -> ColorHSLA:
    s, v = _to_decimal(hsva.s) / 100, _to_decimal(hsva.v) / 100

    l = v * (1 - s / 2)
    if l == 0 or l == 1:
        s_hsl = 0
    else:
        s_hsl = (v - l) / min(l, 1 - l)

    return ColorHSLA(hsva.h, float(s_hsl * 100), float(l * 100))


# toHsva
def rgba_to_hsva(rgba: ColorRGBA) -> ColorHSVA:
    r, g, b = _to_decimal(rgba.r) / 255, _to_decimal(rgba.g) / 255, \
              _to_decimal(rgba.b) / 255
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    # hue calculation
    if delta == 0:
        h = 0
    elif cmax == r:
        h = ((g - b) / delta % 6) * 60
    elif cmax == g:
        h = ((b - r) / delta + 2) * 60
    else:
        h = ((r - g) / delta + 4) * 60

    # saturation calculation
    if cmax == 0:
        s = 0
    else:
        s = delta / cmax

    return ColorHSVA(float(h), float(s * 100), float(cmax * 100), rgba.a)


def hsla_to_hsva(hsla: ColorHSLA) -> ColorHSVA:
    s, l = _to_decimal(hsla.s) / 100, _to_decimal(hsla.l) / 100
    v = (l + s * _to_decimal(min(float(l), float(1 - l))))
    if v == 0:
        s_hsv = 0
    else:
        s_hsv = (1 - l / v) * 2
    return ColorHSVA(hsla.h, float(s_hsv * 100), float(v * 100))


def hex_to_hsva(hex_value: str) -> ColorHSVA:
    return rgba_to_hsva(hex_to_rgba(hex_value))


# toHex
def rgba_to_hex(rgba: ColorRGBA, *, force_long: bool = False) -> str:
    result = f"{int(rgba.r):02X}{int(rgba.g):02X}{int(rgba.b):02X}"

    if not force_long and result[0::2] == result[1::2]:
        result = "".join(result[0::2])

    return "#" + result


def hsla_to_hex(hsla: ColorHSLA, *, force_long: bool = False) -> str:
    return rgba_to_hex(hsla_to_rgba(hsla), force_long=force_long)


def hsva_to_hex(hsva: ColorHSVA, *, force_long: bool = False) -> str:
    return rgba_to_hex(hsva_to_rgba(hsva), force_long=force_long)


# toAnsi
def rgba_to_ansi(color: ColorRGBA) -> str:
    r = int(color.r)
    g = int(color.g)
    b = int(color.b)
    return f"\033[38;2;{r};{g};{b}m"


def hsla_to_ansi(hsla: ColorHSLA) -> str:
    return rgba_to_ansi(hsla_to_rgba(hsla))


def hsva_to_ansi(hsva: ColorHSVA) -> str:
    return rgba_to_ansi(hsva_to_rgba(hsva))


def hex_to_ansi(hex_value: str) -> str:
    return rgba_to_ansi(hex_to_rgba(hex_value))

