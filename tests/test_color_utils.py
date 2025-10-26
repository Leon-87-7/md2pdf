"""Tests for color_utils module."""

import pytest

from md2pdf import color_utils


class TestColorParsing:
    """Test color parsing functionality."""

    def test_parse_hex_6_digit(self):
        """Test parsing 6-digit hex colors."""
        assert color_utils.parse_color("#ffffff") == (255, 255, 255)
        assert color_utils.parse_color("#000000") == (0, 0, 0)
        assert color_utils.parse_color("#1a2b3c") == (26, 43, 60)
        assert color_utils.parse_color("#FF5733") == (255, 87, 51)

    def test_parse_hex_3_digit(self):
        """Test parsing 3-digit hex colors (shorthand)."""
        assert color_utils.parse_color("#fff") == (255, 255, 255)
        assert color_utils.parse_color("#000") == (0, 0, 0)
        assert color_utils.parse_color("#f0f") == (255, 0, 255)
        assert color_utils.parse_color("#abc") == (170, 187, 204)

    def test_parse_hex_without_hash(self):
        """Test parsing hex colors without # prefix is handled."""
        # The parse_color expects # prefix, but _parse_hex handles it
        with pytest.raises(ValueError):
            color_utils.parse_color("ffffff")

    def test_parse_named_colors(self):
        """Test parsing named CSS colors."""
        assert color_utils.parse_color("white") == (255, 255, 255)
        assert color_utils.parse_color("black") == (0, 0, 0)
        assert color_utils.parse_color("red") == (255, 0, 0)
        assert color_utils.parse_color("blue") == (0, 0, 255)
        assert color_utils.parse_color("green") == (0, 128, 0)

    def test_parse_hsl_colors(self):
        """Test parsing HSL colors."""
        # Pure white
        assert color_utils.parse_color("hsl(0, 0%, 100%)") == (255, 255, 255)
        # Pure black
        assert color_utils.parse_color("hsl(0, 0%, 0%)") == (0, 0, 0)
        # Pure red
        assert color_utils.parse_color("hsl(0, 100%, 50%)") == (255, 0, 0)
        # Pure blue
        assert color_utils.parse_color("hsl(240, 100%, 50%)") == (0, 0, 255)

    def test_parse_hsl_with_spaces(self):
        """Test parsing HSL colors with different spacing."""
        result1 = color_utils.parse_color("hsl(210, 50%, 20%)")
        result2 = color_utils.parse_color("hsl(210,50%,20%)")
        result3 = color_utils.parse_color("hsl( 210 , 50% , 20% )")
        assert result1 == result2 == result3

    def test_parse_invalid_hex(self):
        """Test parsing invalid hex colors raises ValueError."""
        with pytest.raises(ValueError):
            color_utils.parse_color("#gggggg")
        with pytest.raises(ValueError):
            color_utils.parse_color("#12345")
        with pytest.raises(ValueError):
            color_utils.parse_color("#1234567")

    def test_parse_invalid_hsl(self):
        """Test parsing invalid HSL colors raises ValueError."""
        with pytest.raises(ValueError):
            color_utils.parse_color("hsl(400, 50%, 50%)")  # Hue > 360
        with pytest.raises(ValueError):
            color_utils.parse_color("hsl(0, 150%, 50%)")  # Saturation > 100%
        with pytest.raises(ValueError):
            color_utils.parse_color("hsl(0, 50%, 150%)")  # Lightness > 100%

    def test_parse_invalid_format(self):
        """Test parsing unsupported color format raises ValueError."""
        with pytest.raises(ValueError):
            color_utils.parse_color("invalid")
        with pytest.raises(ValueError):
            color_utils.parse_color("rgb(255, 255, 255)")
        with pytest.raises(ValueError):
            color_utils.parse_color("")


class TestRGBToHex:
    """Test RGB to hex conversion."""

    def test_rgb_to_hex_white(self):
        """Test converting white to hex."""
        assert color_utils.rgb_to_hex((255, 255, 255)) == "#ffffff"

    def test_rgb_to_hex_black(self):
        """Test converting black to hex."""
        assert color_utils.rgb_to_hex((0, 0, 0)) == "#000000"

    def test_rgb_to_hex_custom(self):
        """Test converting custom RGB to hex."""
        assert color_utils.rgb_to_hex((26, 43, 60)) == "#1a2b3c"
        assert color_utils.rgb_to_hex((255, 87, 51)) == "#ff5733"


class TestLuminanceAndContrast:
    """Test luminance calculation and contrast ratios."""

    def test_luminance_black(self):
        """Test luminance of pure black is 0."""
        assert color_utils.get_relative_luminance((0, 0, 0)) == pytest.approx(0.0)

    def test_luminance_white(self):
        """Test luminance of pure white is 1."""
        assert color_utils.get_relative_luminance((255, 255, 255)) == pytest.approx(1.0)

    def test_contrast_black_white(self):
        """Test contrast between black and white is maximum (21:1)."""
        ratio = color_utils.calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_contrast_same_color(self):
        """Test contrast of same color is minimum (1:1)."""
        ratio = color_utils.calculate_contrast_ratio("#ffffff", "#ffffff")
        assert ratio == pytest.approx(1.0, rel=0.01)

    def test_contrast_order_independence(self):
        """Test contrast ratio is same regardless of order."""
        ratio1 = color_utils.calculate_contrast_ratio("#000000", "#ffffff")
        ratio2 = color_utils.calculate_contrast_ratio("#ffffff", "#000000")
        assert ratio1 == pytest.approx(ratio2)

    def test_contrast_typical_colors(self):
        """Test contrast with typical web colors."""
        # Dark blue on white (should pass WCAG AA)
        ratio = color_utils.calculate_contrast_ratio("#1a2332", "#ffffff")
        assert ratio > 4.5

        # Light gray on white (should fail WCAG AA)
        ratio = color_utils.calculate_contrast_ratio("#cccccc", "#ffffff")
        assert ratio < 4.5


class TestWCAGCompliance:
    """Test WCAG compliance checking."""

    def test_meets_wcag_aa_pass(self):
        """Test colors that meet WCAG AA standard."""
        assert color_utils.meets_wcag_aa(4.5) is True
        assert color_utils.meets_wcag_aa(7.0) is True
        assert color_utils.meets_wcag_aa(21.0) is True

    def test_meets_wcag_aa_fail(self):
        """Test colors that don't meet WCAG AA standard."""
        assert color_utils.meets_wcag_aa(4.4) is False
        assert color_utils.meets_wcag_aa(3.0) is False
        assert color_utils.meets_wcag_aa(1.0) is False

    def test_meets_wcag_aaa_pass(self):
        """Test colors that meet WCAG AAA standard."""
        assert color_utils.meets_wcag_aaa(7.0) is True
        assert color_utils.meets_wcag_aaa(10.0) is True
        assert color_utils.meets_wcag_aaa(21.0) is True

    def test_meets_wcag_aaa_fail(self):
        """Test colors that don't meet WCAG AAA standard."""
        assert color_utils.meets_wcag_aaa(6.9) is False
        assert color_utils.meets_wcag_aaa(4.5) is False
        assert color_utils.meets_wcag_aaa(1.0) is False

    def test_contrast_rating(self):
        """Test human-readable contrast rating."""
        assert color_utils.get_contrast_rating(21.0) == "Excellent - WCAG AAA"
        assert color_utils.get_contrast_rating(7.0) == "Excellent - WCAG AAA"
        assert color_utils.get_contrast_rating(5.0) == "Good - WCAG AA"
        assert color_utils.get_contrast_rating(4.5) == "Good - WCAG AA"
        assert color_utils.get_contrast_rating(3.0) == "Poor - Below WCAG AA"
        assert color_utils.get_contrast_rating(1.0) == "Poor - Below WCAG AA"


class TestColorAdjustment:
    """Test color darkening and lightening."""

    def test_suggest_darker(self):
        """Test darkening colors."""
        # Darken white by 50%
        result = color_utils.suggest_darker("#ffffff", 50)
        rgb = color_utils.parse_color(result)
        assert rgb == (127, 127, 127)

        # Darken red
        result = color_utils.suggest_darker("#ff0000", 20)
        rgb = color_utils.parse_color(result)
        assert rgb[0] < 255
        assert rgb[1] == 0
        assert rgb[2] == 0

    def test_suggest_lighter(self):
        """Test lightening colors."""
        # Lighten black by 50%
        result = color_utils.suggest_lighter("#000000", 50)
        rgb = color_utils.parse_color(result)
        assert rgb == (127, 127, 127)

        # Lighten blue
        result = color_utils.suggest_lighter("#0000ff", 20)
        rgb = color_utils.parse_color(result)
        assert rgb[0] > 0
        assert rgb[1] > 0
        assert rgb[2] == 255

    def test_suggest_darker_boundary(self):
        """Test darkening doesn't go below 0."""
        result = color_utils.suggest_darker("#101010", 90)
        rgb = color_utils.parse_color(result)
        assert all(c >= 0 for c in rgb)

    def test_suggest_lighter_boundary(self):
        """Test lightening doesn't exceed 255."""
        result = color_utils.suggest_lighter("#f0f0f0", 90)
        rgb = color_utils.parse_color(result)
        assert all(c <= 255 for c in rgb)


class TestAccessibleColorSuggestion:
    """Test automatic accessible color suggestion."""

    def test_suggest_accessible_color_already_accessible(self):
        """Test suggesting color that's already accessible."""
        # Black on white is already highly accessible
        result = color_utils.suggest_accessible_color("#000000", "#ffffff")
        assert result == "#000000"

    def test_suggest_accessible_color_light_background(self):
        """Test suggesting accessible color for light background."""
        # Light gray on white (fails) -> should darken
        result = color_utils.suggest_accessible_color("#cccccc", "#ffffff")
        ratio = color_utils.calculate_contrast_ratio(result, "#ffffff")
        assert ratio >= 4.5

    def test_suggest_accessible_color_dark_background(self):
        """Test suggesting accessible color for dark background."""
        # Dark gray on black (fails) -> should lighten
        result = color_utils.suggest_accessible_color("#333333", "#000000")
        ratio = color_utils.calculate_contrast_ratio(result, "#000000")
        assert ratio >= 4.5

    def test_suggest_accessible_color_target_ratio(self):
        """Test suggesting color with custom target ratio."""
        # Request AAA compliance (7:1)
        result = color_utils.suggest_accessible_color(
            "#666666", "#ffffff", target_ratio=7.0
        )
        ratio = color_utils.calculate_contrast_ratio(result, "#ffffff")
        assert ratio >= 7.0

    def test_suggest_accessible_color_impossible_case(self):
        """Test fallback to black/white when adjustment isn't enough."""
        # Very similar colors that can't be adjusted within range
        result = color_utils.suggest_accessible_color("#fefefe", "#ffffff")
        # Should darken significantly or fallback to black
        ratio = color_utils.calculate_contrast_ratio(result, "#ffffff")
        assert ratio >= 4.5  # Should meet WCAG AA at minimum
