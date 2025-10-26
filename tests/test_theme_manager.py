"""Tests for md2pdf.theme_manager module."""

from pathlib import Path

import pytest

from md2pdf import theme_manager
from md2pdf.exceptions import ThemeNotFoundError, CSSNotFoundError, FileOperationError


class TestThemeManager:
    """Test theme management functionality."""

    def test_get_themes_directory(self):
        """Test getting themes directory path."""
        themes_dir = theme_manager.get_themes_directory()
        assert isinstance(themes_dir, Path)
        assert themes_dir.name == "themes"

    def test_themes_directory_exists(self):
        """Test that themes directory actually exists."""
        themes_dir = theme_manager.get_themes_directory()
        assert themes_dir.exists()
        assert themes_dir.is_dir()

    def test_list_available_themes(self):
        """Test listing available themes."""
        themes = theme_manager.list_available_themes()
        assert isinstance(themes, list)
        assert len(themes) > 0

        # Should have at least the default theme
        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes
        assert "minimal" in themes
        assert "professional" in themes

    def test_list_available_themes_no_duplicates(self):
        """Test that theme list has no duplicates."""
        themes = theme_manager.list_available_themes()
        assert len(themes) == len(set(themes))

    def test_load_css_with_default_theme(self):
        """Test loading default theme CSS."""
        css = theme_manager.load_css()
        assert isinstance(css, str)
        assert len(css) > 0
        assert "body" in css.lower()

    def test_load_css_with_dark_theme(self):
        """Test loading dark theme CSS."""
        css = theme_manager.load_css(theme="dark")
        assert isinstance(css, str)
        assert len(css) > 0

    def test_load_css_with_custom_file(self, sample_css_file):
        """Test loading custom CSS file."""
        css = theme_manager.load_css(custom_css=str(sample_css_file))
        assert isinstance(css, str)
        assert len(css) > 0
        assert "Arial" in css

    def test_load_css_custom_takes_precedence(self, sample_css_file):
        """Test that custom CSS takes precedence over theme."""
        css = theme_manager.load_css(custom_css=str(sample_css_file), theme="dark")
        # Should load custom CSS, not dark theme
        assert "Arial" in css

    def test_load_css_nonexistent_theme(self):
        """Test loading non-existent theme raises ThemeNotFoundError."""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            theme_manager.load_css(theme="nonexistent_theme_xyz")
        assert "nonexistent_theme_xyz" in str(exc_info.value)

    def test_load_css_nonexistent_file(self):
        """Test loading non-existent custom CSS file raises CSSNotFoundError."""
        with pytest.raises(CSSNotFoundError) as exc_info:
            theme_manager.load_css(custom_css="/path/to/nonexistent.css")
        assert "nonexistent.css" in str(exc_info.value)

    def test_load_css_directory_as_file(self, temp_dir):
        """Test that passing a directory as CSS file raises CSSNotFoundError."""
        with pytest.raises(CSSNotFoundError) as exc_info:
            theme_manager.load_css(custom_css=str(temp_dir))
        assert "is not a file" in str(exc_info.value)

    def test_load_css_warns_on_non_css_extension(self, temp_dir, capsys):
        """Test warning when loading file without .css extension."""
        txt_file = temp_dir / "style.txt"
        txt_file.write_text("body { color: red; }", encoding="utf-8")

        css = theme_manager.load_css(custom_css=str(txt_file))
        captured = capsys.readouterr()

        # Should load the file but warn
        assert isinstance(css, str)
        assert "Warning" in captured.err
        assert ".css extension" in captured.err

    def test_validate_theme_success(self):
        """Test validate_theme with valid theme."""
        # Should not raise any exception
        theme_manager.validate_theme("default")
        theme_manager.validate_theme("dark")
        theme_manager.validate_theme("light")

    def test_validate_theme_nonexistent(self):
        """Test validate_theme with non-existent theme."""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            theme_manager.validate_theme("nonexistent_theme")
        assert "nonexistent_theme" in str(exc_info.value)


class TestPrivateFunctions:
    """Test private helper functions."""

    def test_load_custom_css_success(self, sample_css_file):
        """Test _load_custom_css with valid file."""
        css = theme_manager._load_custom_css(str(sample_css_file))
        assert isinstance(css, str)
        assert len(css) > 0

    def test_load_theme_css_success(self):
        """Test _load_theme_css with valid theme."""
        css = theme_manager._load_theme_css("default")
        assert isinstance(css, str)
        assert len(css) > 0

    def test_load_theme_css_invalid_theme(self):
        """Test _load_theme_css with invalid theme."""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            theme_manager._load_theme_css("invalid_theme")
        assert "invalid_theme" in str(exc_info.value)


class TestThemeManagerErrors:
    """Test error handling in theme_manager."""

    def test_list_available_themes_nonexistent_directory(self, mocker):
        """Test listing themes when themes directory doesn't exist."""
        # Mock get_themes_directory to return a non-existent path
        fake_path = Path("/nonexistent/themes")
        mocker.patch("md2pdf.theme_manager.get_themes_directory", return_value=fake_path)

        themes = theme_manager.list_available_themes()
        assert themes == []

    def test_load_theme_css_permission_error(self, mocker):
        """Test handling of permission errors when loading theme."""
        # Mock open to raise PermissionError
        mocker.patch("builtins.open", side_effect=PermissionError("Access denied"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_theme_css("default")

        assert "Error reading theme file" in str(exc_info.value)

    def test_load_theme_css_io_error(self, mocker):
        """Test handling of IO errors when loading theme."""
        # Mock open to raise IOError
        mocker.patch("builtins.open", side_effect=IOError("Disk error"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_theme_css("default")

        assert "Error reading theme file" in str(exc_info.value)

    def test_load_theme_css_unicode_decode_error(self, mocker):
        """Test handling of unicode decode errors when loading theme."""
        # Mock open to raise UnicodeDecodeError
        mocker.patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_theme_css("default")

        assert "Error reading theme file" in str(exc_info.value)

    def test_load_custom_css_permission_error(self, sample_css_file, mocker):
        """Test handling of permission errors when loading custom CSS."""
        # Mock open to raise PermissionError
        mocker.patch("builtins.open", side_effect=PermissionError("Access denied"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_custom_css(str(sample_css_file))

        assert "Error reading CSS file" in str(exc_info.value)

    def test_load_custom_css_io_error(self, sample_css_file, mocker):
        """Test handling of IO errors when loading custom CSS."""
        # Mock open to raise IOError
        mocker.patch("builtins.open", side_effect=IOError("Disk error"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_custom_css(str(sample_css_file))

        assert "Error reading CSS file" in str(exc_info.value)

    def test_load_custom_css_unicode_decode_error(self, sample_css_file, mocker):
        """Test handling of unicode decode errors when loading custom CSS."""
        # Mock open to raise UnicodeDecodeError
        mocker.patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"))

        with pytest.raises(FileOperationError) as exc_info:
            theme_manager._load_custom_css(str(sample_css_file))

        assert "Error reading CSS file" in str(exc_info.value)
