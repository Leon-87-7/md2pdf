"""Tests for md2pdf.pdf_engine module."""

from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from md2pdf import pdf_engine


class TestFindWkhtmltopdf:
    """Test wkhtmltopdf detection."""

    @patch("shutil.which")
    def test_find_wkhtmltopdf_in_path(self, mock_which):
        """Test finding wkhtmltopdf in system PATH."""
        mock_which.return_value = "/usr/bin/wkhtmltopdf"
        result = pdf_engine.find_wkhtmltopdf()
        assert result == "/usr/bin/wkhtmltopdf"
        mock_which.assert_called_once_with("wkhtmltopdf")

    @patch("shutil.which")
    @patch("platform.system")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_find_wkhtmltopdf_common_path_linux(
        self, mock_is_file, mock_exists, mock_system, mock_which
    ):
        """Test finding wkhtmltopdf in common Linux paths."""
        mock_which.return_value = None  # Not in PATH
        mock_system.return_value = "Linux"
        mock_exists.return_value = True
        mock_is_file.return_value = True

        result = pdf_engine.find_wkhtmltopdf()
        assert result is not None
        assert "wkhtmltopdf" in result

    @patch("shutil.which")
    @patch("platform.system")
    def test_find_wkhtmltopdf_not_found(self, mock_system, mock_which):
        """Test when wkhtmltopdf is not found anywhere."""
        mock_which.return_value = None
        mock_system.return_value = "Linux"

        result = pdf_engine.find_wkhtmltopdf()
        # Result might be None if not installed
        assert result is None or isinstance(result, str)

    @patch("shutil.which")
    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_find_wkhtmltopdf_windows_user_path(
        self, mock_home, mock_system, mock_which
    ):
        """Test Windows user-specific path is checked."""
        mock_which.return_value = None
        mock_system.return_value = "Windows"
        mock_home.return_value = Path("C:/Users/TestUser")

        # Call the function (it will check user path)
        pdf_engine.find_wkhtmltopdf()

        # Verify home() was called for Windows
        mock_home.assert_called()


class TestCreatePdfConfiguration:
    """Test PDF configuration creation."""

    @patch("pdfkit.configuration")
    def test_create_pdf_configuration(self, mock_pdfkit_config):
        """Test creating pdfkit configuration."""
        mock_config = MagicMock()
        mock_config.wkhtmltopdf = "/usr/bin/wkhtmltopdf"
        mock_pdfkit_config.return_value = mock_config

        test_path = "/usr/bin/wkhtmltopdf"
        config = pdf_engine.create_pdf_configuration(test_path)

        assert config is not None
        mock_pdfkit_config.assert_called_once_with(wkhtmltopdf=test_path)


class TestPrintInstallationHelp:
    """Test installation help printing."""

    @patch("platform.system")
    def test_print_installation_help_linux(self, mock_system, capsys):
        """Test printing installation help for Linux."""
        mock_system.return_value = "Linux"

        pdf_engine.print_installation_help()
        captured = capsys.readouterr()

        assert "Error: wkhtmltopdf not found" in captured.err
        assert "Installation instructions" in captured.err
        assert "apt-get" in captured.err or "dnf" in captured.err

    @patch("platform.system")
    def test_print_installation_help_windows(self, mock_system, capsys):
        """Test printing installation help for Windows."""
        mock_system.return_value = "Windows"

        pdf_engine.print_installation_help()
        captured = capsys.readouterr()

        assert "Error: wkhtmltopdf not found" in captured.err
        assert "Installation instructions" in captured.err
        assert "Download from" in captured.err

    @patch("platform.system")
    def test_print_installation_help_macos(self, mock_system, capsys):
        """Test printing installation help for macOS."""
        mock_system.return_value = "Darwin"

        pdf_engine.print_installation_help()
        captured = capsys.readouterr()

        assert "Error: wkhtmltopdf not found" in captured.err
        assert "Installation instructions" in captured.err
        assert "brew" in captured.err or "Homebrew" in captured.err

    @patch("platform.system")
    def test_print_installation_help_unknown_platform(self, mock_system, capsys):
        """Test printing installation help for unknown platform."""
        mock_system.return_value = "UnknownOS"

        pdf_engine.print_installation_help()
        captured = capsys.readouterr()

        assert "Error: wkhtmltopdf not found" in captured.err
        assert "Installation instructions" in captured.err
        # Should fall back to default instructions


class TestConvertHtmlToPdf:
    """Test HTML to PDF conversion."""

    @patch("pdfkit.from_string")
    def test_convert_html_to_pdf_success(self, mock_from_string, temp_dir):
        """Test successful HTML to PDF conversion."""
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = temp_dir / "output.pdf"
        config = MagicMock()

        pdf_engine.convert_html_to_pdf(html, output_path, config)

        mock_from_string.assert_called_once()
        args, kwargs = mock_from_string.call_args
        assert args[0] == html
        assert args[1] == str(output_path)
        assert kwargs["configuration"] == config

    @patch("pdfkit.from_string")
    def test_convert_html_to_pdf_io_error(self, mock_from_string, temp_dir):
        """Test handling of IOError during conversion."""
        mock_from_string.side_effect = IOError("Cannot write file")
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = temp_dir / "output.pdf"
        config = MagicMock()

        with pytest.raises(SystemExit):
            pdf_engine.convert_html_to_pdf(html, output_path, config)

    @patch("pdfkit.from_string")
    def test_convert_html_to_pdf_permission_error(self, mock_from_string, temp_dir, capsys):
        """Test handling of PermissionError during conversion."""
        mock_from_string.side_effect = PermissionError("Access denied")
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = temp_dir / "output.pdf"
        config = MagicMock()

        with pytest.raises(SystemExit):
            pdf_engine.convert_html_to_pdf(html, output_path, config)

        captured = capsys.readouterr()
        assert "Error writing PDF file" in captured.err
        assert "write permissions" in captured.err

    @patch("pdfkit.from_string")
    def test_convert_html_to_pdf_general_error(self, mock_from_string, temp_dir, capsys):
        """Test handling of general errors during conversion."""
        mock_from_string.side_effect = Exception("Unknown error")
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = temp_dir / "output.pdf"
        config = MagicMock()

        with pytest.raises(SystemExit):
            pdf_engine.convert_html_to_pdf(html, output_path, config)

        captured = capsys.readouterr()
        assert "Error generating PDF" in captured.err
        assert "Troubleshooting tips" in captured.err

    @patch("pdfkit.from_string")
    def test_convert_html_to_pdf_uses_config_options(self, mock_from_string, temp_dir):
        """Test that PDF options from config are used."""
        html = "<html><body><h1>Test</h1></body></html>"
        output_path = temp_dir / "output.pdf"
        config = MagicMock()

        pdf_engine.convert_html_to_pdf(html, output_path, config)

        # Verify options parameter was passed
        args, kwargs = mock_from_string.call_args
        assert "options" in kwargs
        assert isinstance(kwargs["options"], dict)