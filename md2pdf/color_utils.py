"""Color utilities for theme building and accessibility validation."""

import re
from typing import Tuple

from . import config


# CSS named colors (subset of most common colors)
CSS_NAMED_COLORS = {
    "white": "#ffffff",
    "black": "#000000",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "silver": "#c0c0c0",
    "maroon": "#800000",
    "olive": "#808000",
    "lime": "#00ff00",
    "aqua": "#00ffff",
    "teal": "#008080",
    "navy": "#000080",
    "fuchsia": "#ff00ff",
    "purple": "#800080",
    "orange": "#ffa500",
}


def parse_color(color_string: str) -> Tuple[int, int, int]:
    """Parse a color string into RGB tuple.

    Supports:
    - Hex: #fff, #ffffff, #1a2b3c
    - Named: white, black, red, etc.
    - HSL: hsl(210, 50%, 20%)

    Args:
        color_string: Color in hex, named, or HSL format

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Raises:
        ValueError: If color format is invalid
    """
    color_string = color_string.strip().lower()

    # Try hex format
    if color_string.startswith("#"):
        return _parse_hex(color_string)

    # Try HSL format
    if color_string.startswith("hsl"):
        return _parse_hsl(color_string)

    # Try named color
    if color_string in CSS_NAMED_COLORS:
        return _parse_hex(CSS_NAMED_COLORS[color_string])

    raise ValueError(
        f"Invalid color format: '{color_string}'. "
        f"Supported formats: hex (#fff, #ffffff), named colors (white, black), "
        f"or HSL (hsl(210, 50%, 20%))"
    )


def _parse_hex(hex_string: str) -> Tuple[int, int, int]:
    """Parse hex color string to RGB.

    Args:
        hex_string: Hex color like #fff or #ffffff

    Returns:
        RGB tuple (r, g, b)

    Raises:
        ValueError: If hex format is invalid
    """
    hex_string = hex_string.lstrip("#")

    # Expand shorthand (#fff -> #ffffff)
    if len(hex_string) == 3:
        hex_string = "".join([c * 2 for c in hex_string])

    if len(hex_string) != 6:
        raise ValueError(f"Invalid hex color: #{hex_string}")

    try:
        r = int(hex_string[0:2], 16)
        g = int(hex_string[2:4], 16)
        b = int(hex_string[4:6], 16)
        return (r, g, b)
    except ValueError:
        raise ValueError(f"Invalid hex color: #{hex_string}")


def _parse_hsl(hsl_string: str) -> Tuple[int, int, int]:
    """Parse HSL color string to RGB.

    Args:
        hsl_string: HSL color like hsl(210, 50%, 20%)

    Returns:
        RGB tuple (r, g, b)

    Raises:
        ValueError: If HSL format is invalid
    """
    # Extract numbers from hsl(h, s%, l%)
    match = re.match(r"hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)", hsl_string)

    if not match:
        raise ValueError(f"Invalid HSL format: '{hsl_string}'")

    h = int(match.group(1))
    s = int(match.group(2)) / 100.0
    l = int(match.group(3)) / 100.0

    # Validate ranges
    if not (0 <= h <= 360):
        raise ValueError(f"HSL hue must be 0-360, got {h}")
    if not (0 <= s <= 1):
        raise ValueError(f"HSL saturation must be 0-100%, got {s * 100}%")
    if not (0 <= l <= 1):
        raise ValueError(f"HSL lightness must be 0-100%, got {l * 100}%")

    # Convert HSL to RGB
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r_prime, g_prime, b_prime = c, x, 0
    elif 60 <= h < 120:
        r_prime, g_prime, b_prime = x, c, 0
    elif 120 <= h < 180:
        r_prime, g_prime, b_prime = 0, c, x
    elif 180 <= h < 240:
        r_prime, g_prime, b_prime = 0, x, c
    elif 240 <= h < 300:
        r_prime, g_prime, b_prime = x, 0, c
    else:  # 300 <= h < 360
        r_prime, g_prime, b_prime = c, 0, x

    r = int((r_prime + m) * 255)
    g = int((g_prime + m) * 255)
    b = int((b_prime + m) * 255)

    return (r, g, b)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex string.

    Args:
        rgb: RGB tuple (r, g, b) with values 0-255

    Returns:
        Hex color string like #1a2b3c
    """
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance of a color per WCAG formula.

    Args:
        rgb: RGB tuple (r, g, b) with values 0-255

    Returns:
        Relative luminance (0.0 to 1.0)
    """
    r, g, b = rgb

    # Convert to sRGB
    r_srgb = r / 255.0
    g_srgb = g / 255.0
    b_srgb = b / 255.0

    # Apply gamma correction
    def gamma_correct(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    r_linear = gamma_correct(r_srgb)
    g_linear = gamma_correct(g_srgb)
    b_linear = gamma_correct(b_srgb)

    # Calculate luminance
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two colors per WCAG formula.

    Args:
        color1: First color (any supported format)
        color2: Second color (any supported format)

    Returns:
        Contrast ratio (1.0 to 21.0)

    Raises:
        ValueError: If color format is invalid
    """
    rgb1 = parse_color(color1)
    rgb2 = parse_color(color2)

    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)

    # Ensure l1 is the lighter color
    if l1 < l2:
        l1, l2 = l2, l1

    return (l1 + 0.05) / (l2 + 0.05)


def meets_wcag_aa(ratio: float) -> bool:
    """Check if contrast ratio meets WCAG AA standard (4.5:1 minimum).

    Args:
        ratio: Contrast ratio

    Returns:
        True if ratio >= 4.5, False otherwise
    """
    return ratio >= 4.5


def meets_wcag_aaa(ratio: float) -> bool:
    """Check if contrast ratio meets WCAG AAA standard (7.0:1 minimum).

    Args:
        ratio: Contrast ratio

    Returns:
        True if ratio >= 7.0, False otherwise
    """
    return ratio >= 7.0


def get_contrast_rating(ratio: float) -> str:
    """Get human-readable rating for contrast ratio.

    Args:
        ratio: Contrast ratio

    Returns:
        Rating string: "Excellent - WCAG AAA", "Good - WCAG AA", or "Poor - Below WCAG AA"
    """
    if meets_wcag_aaa(ratio):
        return "Excellent - WCAG AAA"
    elif meets_wcag_aa(ratio):
        return "Good - WCAG AA"
    else:
        return "Poor - Below WCAG AA"


def suggest_darker(color: str, percentage: float = 15.0) -> str:
    """Darken a color by a percentage.

    Args:
        color: Color in any supported format
        percentage: Percentage to darken (0-100)

    Returns:
        Darkened color as hex string
    """
    rgb = parse_color(color)
    factor = 1.0 - (percentage / 100.0)

    r = int(rgb[0] * factor)
    g = int(rgb[1] * factor)
    b = int(rgb[2] * factor)

    return rgb_to_hex((r, g, b))


def suggest_lighter(color: str, percentage: float = 15.0) -> str:
    """Lighten a color by a percentage.

    Args:
        color: Color in any supported format
        percentage: Percentage to lighten (0-100)

    Returns:
        Lightened color as hex string
    """
    rgb = parse_color(color)
    factor = percentage / 100.0

    r = int(rgb[0] + (255 - rgb[0]) * factor)
    g = int(rgb[1] + (255 - rgb[1]) * factor)
    b = int(rgb[2] + (255 - rgb[2]) * factor)

    return rgb_to_hex((r, g, b))


def suggest_accessible_color(
    foreground: str, background: str, target_ratio: float = 4.5
) -> str:
    """Suggest an adjusted foreground color to meet target contrast ratio.

    Args:
        foreground: Foreground color (any supported format)
        background: Background color (any supported format)
        target_ratio: Target contrast ratio (default: 4.5 for WCAG AA)

    Returns:
        Adjusted foreground color as hex string
    """
    current_ratio = calculate_contrast_ratio(foreground, background)

    if current_ratio >= target_ratio:
        return rgb_to_hex(parse_color(foreground))

    # Determine if we need to darken or lighten
    bg_luminance = get_relative_luminance(parse_color(background))

    # If background is light, darken foreground; if dark, lighten foreground
    if bg_luminance > 0.5:
        # Light background, darken foreground
        for percentage in range(
            config.COLOR_ADJUSTMENT_START,
            config.COLOR_ADJUSTMENT_END,
            config.COLOR_ADJUSTMENT_STEP,
        ):
            adjusted = suggest_darker(foreground, percentage)
            if calculate_contrast_ratio(adjusted, background) >= target_ratio:
                return adjusted
    else:
        # Dark background, lighten foreground
        for percentage in range(
            config.COLOR_ADJUSTMENT_START,
            config.COLOR_ADJUSTMENT_END,
            config.COLOR_ADJUSTMENT_STEP,
        ):
            adjusted = suggest_lighter(foreground, percentage)
            if calculate_contrast_ratio(adjusted, background) >= target_ratio:
                return adjusted

    # If we can't adjust the foreground enough, return pure black or white
    if bg_luminance > 0.5:
        return "#000000"
    else:
        return "#ffffff"
