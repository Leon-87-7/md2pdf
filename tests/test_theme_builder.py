"""Tests for md2pdf.theme_builder module validators."""

import pytest

from md2pdf import theme_builder


class TestValidateThemeName:
    """Tests for validate_theme_name function."""

    def test_valid_theme_name_simple(self):
        """Test valid simple theme name."""
        # Should not raise
        theme_builder.validate_theme_name("mytheme")

    def test_valid_theme_name_with_hyphens(self):
        """Test valid theme name with hyphens."""
        theme_builder.validate_theme_name("my-custom-theme")

    def test_valid_theme_name_with_underscores(self):
        """Test valid theme name with underscores."""
        theme_builder.validate_theme_name("my_custom_theme")

    def test_valid_theme_name_with_numbers(self):
        """Test valid theme name with numbers."""
        theme_builder.validate_theme_name("theme123")
        theme_builder.validate_theme_name("theme-v2")

    def test_valid_theme_name_mixed(self):
        """Test valid theme name with mixed valid characters."""
        theme_builder.validate_theme_name("my-theme_v2")

    def test_invalid_theme_name_empty(self):
        """Test that empty theme name is rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_theme_name("")

        assert "cannot be empty" in str(exc_info.value).lower()

    def test_invalid_theme_name_spaces(self):
        """Test that theme names with spaces are rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_theme_name("my theme")

        assert "letters, numbers, hyphens, and underscores" in str(exc_info.value)

    def test_invalid_theme_name_special_characters(self):
        """Test that theme names with special characters are rejected."""
        invalid_names = [
            "theme@home",
            "theme#1",
            "theme$",
            "theme!",
            "theme.css",
            "theme/path",
            "theme\\path",
        ]

        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                theme_builder.validate_theme_name(name)

            assert "letters, numbers, hyphens, and underscores" in str(exc_info.value)

    def test_invalid_theme_name_existing(self, mocker):
        """Test that existing theme names are rejected."""
        # Mock list_available_themes to return some themes
        mocker.patch(
            "md2pdf.theme_builder.list_available_themes",
            return_value=["default", "dark", "light"]
        )

        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_theme_name("default")

        assert "already exists" in str(exc_info.value)

    def test_case_sensitive_theme_names(self, mocker):
        """Test that theme name validation is case-sensitive."""
        mocker.patch(
            "md2pdf.theme_builder.list_available_themes",
            return_value=["default"]
        )

        # Should be allowed - different case
        theme_builder.validate_theme_name("Default")
        theme_builder.validate_theme_name("DEFAULT")


class TestValidateColorInput:
    """Tests for validate_color_input function."""

    def test_valid_hex_color_6_digits(self):
        """Test valid 6-digit hex color."""
        theme_builder.validate_color_input("#ff0000")
        theme_builder.validate_color_input("#ABCDEF")

    def test_valid_hex_color_3_digits(self):
        """Test valid 3-digit hex color."""
        theme_builder.validate_color_input("#f00")
        theme_builder.validate_color_input("#ABC")

    def test_valid_hsl_color(self):
        """Test valid HSL color."""
        theme_builder.validate_color_input("hsl(0, 100%, 50%)")
        theme_builder.validate_color_input("hsl(210, 50%, 20%)")

    def test_valid_color_names(self):
        """Test valid color names."""
        theme_builder.validate_color_input("red")
        theme_builder.validate_color_input("blue")
        theme_builder.validate_color_input("white")
        theme_builder.validate_color_input("black")

    def test_invalid_hex_color_format(self):
        """Test invalid hex color formats."""
        invalid_colors = [
            "#gg0000",  # Invalid hex digits
            "#12345",   # Wrong length
            "#1234567", # Too long
            "ff0000",   # Missing #
            "#",        # Just hash
        ]

        for color in invalid_colors:
            with pytest.raises(ValueError):
                theme_builder.validate_color_input(color)

    def test_invalid_hsl_format(self):
        """Test invalid HSL formats."""
        invalid_colors = [
            "hsl(361, 100%, 50%)",  # Hue out of range
            "hsl(-1, 50%, 50%)",    # Negative hue
            "hsl(210, 101%, 50%)",  # Saturation out of range
            "hsl(210, 50%)",        # Missing component
            "hsl(a, b%, c%)",       # Non-numeric
        ]

        for color in invalid_colors:
            with pytest.raises(ValueError):
                theme_builder.validate_color_input(color)

    def test_invalid_color_name(self):
        """Test invalid color name."""
        with pytest.raises(ValueError):
            theme_builder.validate_color_input("notacolor")

    def test_empty_color_input(self):
        """Test empty color input."""
        with pytest.raises(ValueError):
            theme_builder.validate_color_input("")


class TestValidateFontSize:
    """Tests for validate_font_size function."""

    def test_valid_font_size_numeric(self):
        """Test valid numeric font sizes."""
        theme_builder.validate_font_size("11")
        theme_builder.validate_font_size("12")
        theme_builder.validate_font_size("16.5")

    def test_valid_font_size_with_pt(self):
        """Test valid font sizes with 'pt' suffix."""
        theme_builder.validate_font_size("11pt")
        theme_builder.validate_font_size("12pt")
        theme_builder.validate_font_size("16.5pt")

    def test_valid_font_size_with_spaces(self):
        """Test font size with surrounding spaces."""
        theme_builder.validate_font_size("  11  ")
        theme_builder.validate_font_size("  12pt  ")

    def test_invalid_font_size_zero(self):
        """Test that zero font size is rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_font_size("0")

        # The function re-raises with a generic message
        assert "Invalid font size" in str(exc_info.value) or "must be positive" in str(exc_info.value)

    def test_invalid_font_size_negative(self):
        """Test that negative font size is rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_font_size("-5")

        # The function re-raises with a generic message
        assert "Invalid font size" in str(exc_info.value) or "must be positive" in str(exc_info.value)

    def test_invalid_font_size_too_large(self):
        """Test that very large font sizes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_font_size("150")

        # The function re-raises with a generic message
        assert "Invalid font size" in str(exc_info.value) or "too large" in str(exc_info.value).lower()

    def test_invalid_font_size_non_numeric(self):
        """Test that non-numeric font sizes are rejected."""
        with pytest.raises(ValueError) as exc_info:
            theme_builder.validate_font_size("abc")

        assert "Invalid font size" in str(exc_info.value)

    def test_invalid_font_size_empty(self):
        """Test that empty font size is rejected."""
        with pytest.raises(ValueError):
            theme_builder.validate_font_size("")

    def test_invalid_font_size_wrong_unit(self):
        """Test that font sizes with wrong units are rejected."""
        # Only 'pt' or no unit should be accepted
        with pytest.raises(ValueError):
            theme_builder.validate_font_size("12px")


class TestGenerateCssFromProperties:
    """Tests for generate_css_from_properties function."""

    def test_generate_css_basic(self):
        """Test basic CSS generation."""
        props = {
            "name": "test-theme",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_family": "Arial, sans-serif",
            "body_text_size": "11pt",
            "h1_color": "#2c3e50",
            "h2_h6_color": "#34495e",
            "accent_color": "#3498db",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#3498db",
        }

        result = theme_builder.generate_css_from_properties(props)

        # Should contain theme name in comment
        assert "Theme: test-theme" in result

        # Should contain all colors
        assert "#ffffff" in result
        assert "#000000" in result
        assert "#2c3e50" in result

        # Should contain font settings
        assert "Arial, sans-serif" in result
        assert "11pt" in result

        # Should contain essential CSS rules
        assert "body {" in result
        assert "h1 {" in result
        assert "table {" in result
        assert "code {" in result

    def test_generate_css_contains_page_settings(self):
        """Test that generated CSS contains page settings."""
        props = {
            "name": "test",
            "background_color": "#fff",
            "text_color": "#000",
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#333",
            "h2_h6_color": "#333",
            "accent_color": "#00f",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#00f",
        }

        result = theme_builder.generate_css_from_properties(props)

        # Should contain @page rule
        assert "@page" in result
        assert "size: A4" in result

    def test_generate_css_contains_section_header_style(self):
        """Test that generated CSS includes document-section-header style."""
        props = {
            "name": "test",
            "background_color": "#fff",
            "text_color": "#000",
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#333",
            "h2_h6_color": "#333",
            "accent_color": "#00f",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#00f",
        }

        result = theme_builder.generate_css_from_properties(props)

        # Should contain document-section-header class for merge mode
        assert "document-section-header" in result

    def test_generate_css_contains_page_break_style(self):
        """Test that generated CSS includes page-break style."""
        props = {
            "name": "test",
            "background_color": "#fff",
            "text_color": "#000",
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#333",
            "h2_h6_color": "#333",
            "accent_color": "#00f",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#00f",
        }

        result = theme_builder.generate_css_from_properties(props)

        # Should contain page-break class
        assert "page-break" in result
        assert "page-break-after: always" in result or "break-after: page" in result

    def test_generate_css_uses_all_properties(self):
        """Test that all provided properties are used in the CSS."""
        props = {
            "name": "custom",
            "background_color": "#f0f0f0",
            "text_color": "#111111",
            "font_family": "Georgia, serif",
            "body_text_size": "12pt",
            "h1_color": "#800000",
            "h2_h6_color": "#600000",
            "accent_color": "#ff6600",
            "code_bg_color": "#e0e0e0",
            "table_header_bg": "#ff6600",
        }

        result = theme_builder.generate_css_from_properties(props)

        # Check that all unique colors appear
        assert "#f0f0f0" in result
        assert "#111111" in result
        assert "#800000" in result
        assert "#600000" in result
        assert "#ff6600" in result
        assert "#e0e0e0" in result

        # Check font family and size
        assert "Georgia, serif" in result
        assert "12pt" in result


class TestCheckContrastAndWarn:
    """Tests for check_contrast_and_warn function."""

    def test_high_contrast_no_warning(self, capsys):
        """Test high contrast colors don't trigger warning."""
        result = theme_builder.check_contrast_and_warn(
            "#000000", "#ffffff", "text"
        )

        captured = capsys.readouterr()
        assert result is True
        assert "Warning" not in captured.out
        assert "ratio" in captured.out.lower()

    def test_low_contrast_shows_warning(self, capsys, mocker):
        """Test low contrast colors show warning and suggestion."""
        # Mock user input to continue with current color
        mocker.patch("builtins.input", return_value="y")

        result = theme_builder.check_contrast_and_warn(
            "#cccccc", "#ffffff", "text"
        )

        captured = capsys.readouterr()
        assert "Warning" in captured.out or "⚠" in captured.out
        assert "WCAG AA" in captured.out
        assert "Suggestion" in captured.out

    def test_user_accepts_low_contrast(self, mocker):
        """Test user can accept low contrast color."""
        mocker.patch("builtins.input", return_value="y")

        result = theme_builder.check_contrast_and_warn(
            "#cccccc", "#ffffff", "text"
        )

        assert result is True

    def test_user_rejects_low_contrast(self, mocker):
        """Test user can reject low contrast color."""
        mocker.patch("builtins.input", return_value="n")

        result = theme_builder.check_contrast_and_warn(
            "#cccccc", "#ffffff", "text"
        )

        assert result is False


class TestSaveTheme:
    """Tests for save_theme function."""

    def test_save_theme_success(self, temp_dir, mocker):
        """Test successful theme saving."""
        # Mock get_themes_directory to return our temp_dir
        mocker.patch(
            "md2pdf.theme_builder.get_themes_directory",
            return_value=temp_dir
        )

        css_content = "body { color: black; }"
        result = theme_builder.save_theme("test-theme", css_content)

        assert result.exists()
        assert result.name == "test-theme.css"
        assert result.read_text() == css_content

    def test_save_theme_overwrites_existing(self, temp_dir, mocker):
        """Test that saving overwrites existing theme file."""
        mocker.patch(
            "md2pdf.theme_builder.get_themes_directory",
            return_value=temp_dir
        )

        # Create existing file
        existing = temp_dir / "test-theme.css"
        existing.write_text("old content")

        # Save new content
        new_content = "new content"
        theme_builder.save_theme("test-theme", new_content)

        assert existing.read_text() == new_content

    def test_save_theme_permission_error(self, temp_dir, mocker):
        """Test handling of permission errors when saving theme."""
        mocker.patch(
            "md2pdf.theme_builder.get_themes_directory",
            return_value=temp_dir
        )

        # Mock open to raise PermissionError
        mocker.patch(
            "builtins.open",
            side_effect=PermissionError("Access denied")
        )

        with pytest.raises(IOError) as exc_info:
            theme_builder.save_theme("test-theme", "content")

        assert "Failed to save theme" in str(exc_info.value)
