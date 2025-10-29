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
        ]

        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                theme_builder.validate_theme_name(name)

            assert "letters, numbers, hyphens, and underscores" in str(exc_info.value)

    def test_invalid_theme_name_path_traversal(self):
        """Test that theme names with path traversal attempts are rejected."""
        invalid_names = [
            "theme/path",
            "theme\\path",
            "../theme",
            "..\\theme",
            "theme/../other",
        ]

        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                theme_builder.validate_theme_name(name)

            assert "path separators" in str(exc_info.value) or "path traversal" in str(exc_info.value)

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


class TestPrintHeader:
    """Tests for print_header function."""

    def test_print_header_outputs_title(self, capsys):
        """Test that print_header outputs the wizard title."""
        theme_builder.print_header()

        captured = capsys.readouterr()
        assert "md2pdf Interactive Theme Builder" in captured.out
        assert "Let's create a custom theme" in captured.out


class TestPromptWithValidation:
    """Tests for prompt_with_validation function."""

    def test_prompt_with_validation_accepts_default(self, mocker):
        """Test that empty input returns default value."""
        mocker.patch("builtins.input", return_value="")

        result = theme_builder.prompt_with_validation(
            "Test prompt",
            "default_value",
            allow_empty=True
        )

        assert result == "default_value"

    def test_prompt_with_validation_accepts_user_input(self, mocker):
        """Test that user input is returned."""
        mocker.patch("builtins.input", return_value="user_value")

        result = theme_builder.prompt_with_validation(
            "Test prompt",
            "default_value"
        )

        assert result == "user_value"

    def test_prompt_with_validation_requires_input_when_not_empty(self, mocker):
        """Test that empty input is rejected when allow_empty is False."""
        # First call returns empty, second returns valid input
        mocker.patch("builtins.input", side_effect=["", "valid_input"])

        result = theme_builder.prompt_with_validation(
            "Test prompt",
            "default",
            allow_empty=False
        )

        assert result == "valid_input"

    def test_prompt_with_validation_runs_validator(self, mocker):
        """Test that validator is called on user input."""
        mocker.patch("builtins.input", return_value="#ff0000")

        validator_called = []
        def mock_validator(value):
            validator_called.append(value)

        result = theme_builder.prompt_with_validation(
            "Test prompt",
            "#000000",
            validator=mock_validator
        )

        assert "#ff0000" in validator_called
        assert result == "#ff0000"

    def test_prompt_with_validation_retries_on_validation_error(self, mocker):
        """Test that prompt retries when validator raises ValueError."""
        # First input is invalid, second is valid
        mocker.patch("builtins.input", side_effect=["invalid", "valid"])

        def mock_validator(value):
            if value == "invalid":
                raise ValueError("Invalid value")

        result = theme_builder.prompt_with_validation(
            "Test prompt",
            "default",
            validator=mock_validator
        )

        assert result == "valid"


class TestPromptThemeProperties:
    """Tests for prompt_theme_properties function."""

    def test_prompt_theme_properties_collects_all_properties(self, mocker):
        """Test that prompt_theme_properties collects all required properties."""
        # Mock all input prompts to return valid values
        inputs = [
            "my-theme",           # name
            "#ffffff",            # background_color
            "#000000",            # text_color
            "Arial, sans-serif",  # font_family
            "11pt",               # body_text_size
            "#2c3e50",           # h1_color
            "#34495e",           # h2_h6_color
            "#3030ff",           # accent_color (high contrast version)
            "#f5f5f5",           # code_bg_color
            "#3030ff",           # table_header_bg
        ]
        mocker.patch("builtins.input", side_effect=inputs)
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])

        props = theme_builder.prompt_theme_properties()

        assert props["name"] == "my-theme"
        assert props["background_color"] == "#ffffff"
        assert props["text_color"] == "#000000"
        assert props["font_family"] == "Arial, sans-serif"
        assert props["body_text_size"] == "11pt"
        assert props["h1_color"] == "#2c3e50"
        assert props["h2_h6_color"] == "#34495e"
        assert props["accent_color"] == "#3030ff"
        assert props["code_bg_color"] == "#f5f5f5"
        assert props["table_header_bg"] == "#3030ff"

    def test_prompt_theme_properties_retries_on_low_contrast(self, mocker):
        """Test that low contrast colors trigger retry."""
        # First contrast check fails (returns False), second passes
        inputs = [
            "my-theme",
            "#ffffff",      # background
            "#fafafa",      # text (low contrast) - will fail
            "#000000",      # text (retry)
            "Arial",
            "11",
            "#000000",      # h1
            "#000000",      # h2-h6
            "#0000ff",      # accent
            "#f5f5f5",
            "#0000ff",
        ]
        mocker.patch("builtins.input", side_effect=inputs)
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])
        # Mock check_contrast_and_warn to return False first time, True after
        mocker.patch(
            "md2pdf.theme_builder.check_contrast_and_warn",
            side_effect=[False, True, True, True, True]
        )

        props = theme_builder.prompt_theme_properties()

        # Should have retried and gotten black text
        assert props["text_color"] == "#000000"


class TestDisplaySummary:
    """Tests for display_summary function."""

    def test_display_summary_shows_all_properties(self, capsys):
        """Test that summary displays all theme properties."""
        props = {
            "name": "test-theme",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#2c3e50",
            "h2_h6_color": "#34495e",
            "accent_color": "#667eea",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#667eea",
        }

        theme_builder.display_summary(props)

        captured = capsys.readouterr()
        assert "test-theme" in captured.out
        assert "#ffffff" in captured.out
        assert "#000000" in captured.out
        assert "Arial" in captured.out

    def test_display_summary_shows_accessibility_check(self, capsys):
        """Test that summary shows WCAG AA compliance status."""
        props = {
            "name": "accessible-theme",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#000000",
            "h2_h6_color": "#000000",
            "accent_color": "#0000ff",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#0000ff",
        }

        theme_builder.display_summary(props)

        captured = capsys.readouterr()
        assert "WCAG AA" in captured.out

    def test_display_summary_warns_on_inaccessible_colors(self, capsys):
        """Test that summary warns when colors don't meet WCAG AA."""
        props = {
            "name": "low-contrast-theme",
            "background_color": "#ffffff",
            "text_color": "#cccccc",  # Low contrast
            "font_family": "Arial",
            "body_text_size": "11pt",
            "h1_color": "#cccccc",
            "h2_h6_color": "#cccccc",
            "accent_color": "#cccccc",
            "code_bg_color": "#f5f5f5",
            "table_header_bg": "#cccccc",
        }

        theme_builder.display_summary(props)

        captured = capsys.readouterr()
        assert "⚠" in captured.out or "below WCAG AA" in captured.out


class TestRunThemeWizard:
    """Tests for run_theme_wizard function."""

    def test_run_theme_wizard_creates_theme(self, temp_dir, mocker, capsys):
        """Test that wizard creates a theme successfully."""
        mocker.patch("md2pdf.theme_builder.get_themes_directory", return_value=temp_dir)
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])
        # Mock Path.cwd() to return temp_dir for relative_to() call
        mocker.patch("pathlib.Path.cwd", return_value=temp_dir)

        # Mock all user inputs
        inputs = [
            "wizard-theme",
            "#ffffff",
            "#000000",
            "Arial",
            "11",
            "#000000",
            "#000000",
            "#0000ff",
            "#f5f5f5",
            "#0000ff",
            "y",  # Confirm creation
        ]
        mocker.patch("builtins.input", side_effect=inputs)

        theme_builder.run_theme_wizard()

        # Check that theme file was created
        theme_file = temp_dir / "wizard-theme.css"
        assert theme_file.exists()
        content = theme_file.read_text()
        assert "Theme: wizard-theme" in content

    def test_run_theme_wizard_cancels_on_no(self, capsys, mocker):
        """Test that wizard can be cancelled."""
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])

        inputs = [
            "cancel-theme",
            "#ffffff",
            "#000000",
            "Arial",
            "11",
            "#000000",
            "#000000",
            "#0000ff",
            "#f5f5f5",
            "#0000ff",
            "n",  # Cancel
        ]
        mocker.patch("builtins.input", side_effect=inputs)

        theme_builder.run_theme_wizard()

        captured = capsys.readouterr()
        assert "cancelled" in captured.out.lower()

    def test_run_theme_wizard_handles_keyboard_interrupt(self, capsys, mocker):
        """Test that wizard handles Ctrl+C gracefully."""
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])
        mocker.patch("builtins.input", side_effect=KeyboardInterrupt())

        with pytest.raises(SystemExit) as exc_info:
            theme_builder.run_theme_wizard()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "cancelled" in captured.out.lower()

    def test_run_theme_wizard_handles_general_exception(self, capsys, mocker):
        """Test that wizard handles general exceptions."""
        mocker.patch("md2pdf.theme_builder.list_available_themes", return_value=[])
        mocker.patch("builtins.input", side_effect=RuntimeError("Unexpected error"))

        with pytest.raises(SystemExit) as exc_info:
            theme_builder.run_theme_wizard()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        # Error is printed to stderr
        assert "Error" in captured.err or "X" in captured.err
