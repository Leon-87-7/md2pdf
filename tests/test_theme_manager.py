"""Tests for md2pdf.theme_manager module."""

from pathlib import Path

import pytest

from md2pdf import theme_manager


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
        """Test loading non-existent theme raises SystemExit."""
        with pytest.raises(SystemExit):
            theme_manager.load_css(theme="nonexistent_theme_xyz")

    def test_load_css_nonexistent_file(self):
        """Test loading non-existent custom CSS file raises SystemExit."""
        with pytest.raises(SystemExit):
            theme_manager.load_css(custom_css="/path/to/nonexistent.css")

    def test_load_css_directory_as_file(self, temp_dir):
        """Test that passing a directory as CSS file raises SystemExit."""
        with pytest.raises(SystemExit):
            theme_manager.load_css(custom_css=str(temp_dir))

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
        with pytest.raises(SystemExit):
            theme_manager._load_theme_css("invalid_theme")
