"""Tests for md2pdf.cli module."""

from unittest.mock import patch, MagicMock

import pytest

from md2pdf import cli


class TestDisplayThemes:
    """Test theme listing functionality."""

    @patch("md2pdf.cli.list_available_themes")
    def test_display_themes_with_themes(self, mock_list_themes, capsys):
        """Test displaying themes when themes exist."""
        mock_list_themes.return_value = ["default", "dark", "light", "minimal"]

        cli.display_themes()
        captured = capsys.readouterr()

        assert "Available themes:" in captured.out
        assert "  - dark" in captured.out
        assert "  - default" in captured.out
        assert "  - light" in captured.out
        assert "  - minimal" in captured.out
        assert "Usage: md2pdf document.md --theme <theme-name>" in captured.out

    @patch("md2pdf.cli.list_available_themes")
    def test_display_themes_no_themes(self, mock_list_themes, capsys):
        """Test displaying themes when no themes are found."""
        mock_list_themes.return_value = []

        cli.display_themes()
        captured = capsys.readouterr()

        assert "No themes found" in captured.out

    @patch("md2pdf.cli.list_available_themes")
    def test_display_themes_sorted(self, mock_list_themes, capsys):
        """Test that themes are displayed in sorted order."""
        mock_list_themes.return_value = ["zebra", "apple", "mango"]

        cli.display_themes()
        captured = capsys.readouterr()

        # Check that sorted order appears
        output = captured.out
        apple_pos = output.find("apple")
        mango_pos = output.find("mango")
        zebra_pos = output.find("zebra")

        assert apple_pos < mango_pos < zebra_pos


class TestMain:
    """Test main CLI function."""

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md"])
    def test_main_basic_usage(self, mock_convert):
        """Test basic CLI usage with just input file."""
        cli.main()
        mock_convert.assert_called_once_with("test.md", None, None, "default", False)

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "-on", "output.pdf"])
    def test_main_with_output(self, mock_convert):
        """Test CLI with output file specified."""
        cli.main()
        mock_convert.assert_called_once_with(
            "test.md", "output.pdf", None, "default", False
        )

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "--theme", "dark"])
    def test_main_with_theme(self, mock_convert):
        """Test CLI with theme specified."""
        cli.main()
        mock_convert.assert_called_once_with("test.md", None, None, "dark", False)

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "--css", "custom.css"])
    def test_main_with_custom_css(self, mock_convert):
        """Test CLI with custom CSS specified."""
        cli.main()
        mock_convert.assert_called_once_with(
            "test.md", None, "custom.css", "default", False
        )

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "-p"])
    def test_main_with_preview(self, mock_convert):
        """Test CLI with preview flag."""
        cli.main()
        mock_convert.assert_called_once_with("test.md", None, None, "default", True)

    @patch("md2pdf.cli.display_themes")
    @patch("sys.argv", ["md2pdf", "--theme-list"])
    def test_main_theme_list_flag(self, mock_display_themes):
        """Test CLI with --theme-list flag."""
        cli.main()
        mock_display_themes.assert_called_once()

    @patch("md2pdf.cli.display_themes")
    @patch("sys.argv", ["md2pdf", "-thl"])
    def test_main_theme_list_short_flag(self, mock_display_themes):
        """Test CLI with -thl short flag."""
        cli.main()
        mock_display_themes.assert_called_once()

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("md2pdf.cli.display_themes")
    @patch("sys.argv", ["md2pdf", "--theme-list"])
    def test_main_theme_list_does_not_convert(
        self, mock_display_themes, mock_convert
    ):
        """Test that --theme-list doesn't trigger conversion."""
        cli.main()
        mock_display_themes.assert_called_once()
        mock_convert.assert_not_called()

    @patch("sys.argv", ["md2pdf"])
    def test_main_no_input_file(self):
        """Test CLI without input file raises error."""
        with pytest.raises(SystemExit):
            cli.main()

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "--theme", "dark", "-on", "out.pdf", "-p"])
    def test_main_all_options(self, mock_convert):
        """Test CLI with all options combined."""
        cli.main()
        mock_convert.assert_called_once_with("test.md", "out.pdf", None, "dark", True)


class TestMainArgumentParsing:
    """Test argument parsing edge cases."""

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "--output-name", "output.pdf"])
    def test_long_output_flag(self, mock_convert):
        """Test --output-name long form."""
        cli.main()
        mock_convert.assert_called_once()
        args = mock_convert.call_args[0]
        assert args[1] == "output.pdf"

    @patch("md2pdf.cli.convert_md_to_pdf")
    @patch("sys.argv", ["md2pdf", "test.md", "--preview"])
    def test_long_preview_flag(self, mock_convert):
        """Test --preview long form."""
        cli.main()
        mock_convert.assert_called_once()
        args = mock_convert.call_args[0]
        assert args[4] is True  # preview argument

    @patch("sys.argv", ["md2pdf", "--version"])
    def test_version_flag(self):
        """Test --version flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        # Version flag causes SystemExit with code 0
        assert exc_info.value.code == 0

    @patch("sys.argv", ["md2pdf", "-v"])
    def test_version_short_flag(self):
        """Test -v short version flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 0

    @patch("sys.argv", ["md2pdf", "-h"])
    def test_help_flag(self):
        """Test -h help flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 0

    @patch("sys.argv", ["md2pdf", "--help"])
    def test_help_long_flag(self):
        """Test --help long flag."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 0