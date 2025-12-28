"""
Utility functions for creative coding with Kanvas.

Provides common mathematical and color utilities inspired by Processing/p5.js.
"""

from __future__ import annotations


def map_range(
    value: float,
    start1: float,
    stop1: float,
    start2: float,
    stop2: float,
) -> float:
    """
    Re-map a number from one range to another.
    
    Args:
        value: The value to re-map
        start1: Lower bound of the value's current range
        stop1: Upper bound of the value's current range
        start2: Lower bound of the value's target range
        stop2: Upper bound of the value's target range
    
    Returns:
        The re-mapped value
    
    Example:
        >>> map_range(5, 0, 10, 0, 100)
        50.0
    """
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))


def constrain(value: float, low: float, high: float) -> float:
    """
    Constrain a value to a range.
    
    Args:
        value: The value to constrain
        low: Minimum limit
        high: Maximum limit
    
    Returns:
        The constrained value
    
    Example:
        >>> constrain(150, 0, 100)
        100
    """
    return max(low, min(high, value))


def lerp(start: float, stop: float, amt: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        start: First value
        stop: Second value
        amt: Amount to interpolate (0.0 to 1.0)
    
    Returns:
        The interpolated value
    
    Example:
        >>> lerp(0, 100, 0.5)
        50.0
    """
    return start + (stop - start) * amt


def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate the distance between two points.
    
    Args:
        x1: X coordinate of first point
        y1: Y coordinate of first point
        x2: X coordinate of second point
        y2: Y coordinate of second point
    
    Returns:
        The distance between the points
    """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """
    Convert RGB color to HSV.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
    
    Returns:
        Tuple of (hue, saturation, value) where hue is 0-360 and s/v are 0-1
    """
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    
    if diff == 0:
        h = 0.0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    s = 0.0 if max_c == 0 else diff / max_c
    v = max_c
    
    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """
    Convert HSV color to RGB.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value (0-1)
    
    Returns:
        Tuple of (r, g, b) where each component is 0-255
    """
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0.0
    elif h < 120:
        r, g, b = x, c, 0.0
    elif h < 180:
        r, g, b = 0.0, c, x
    elif h < 240:
        r, g, b = 0.0, x, c
    elif h < 300:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


__all__ = [
    "map_range",
    "constrain",
    "lerp",
    "dist",
    "rgb_to_hsv",
    "hsv_to_rgb",
]