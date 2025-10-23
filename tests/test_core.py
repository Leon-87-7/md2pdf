"""Comprehensive integration tests for md2pdf.core module."""

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from md2pdf import core
from md2pdf.exceptions import (
    ConversionError,
    CSSNotFoundError,
    FileOperationError,
    InvalidInputError,
    ThemeNotFoundError,
    WkhtmltopdfNotFoundError,
)


class TestConvertMdToPdf:
    """Integration tests for the convert_md_to_pdf function."""

    @pytest.fixture
    def mock_modules(self, mocker):
        """Mock all module dependencies for core.convert_md_to_pdf."""
        return {
            "find_wkhtmltopdf": mocker.patch(
                "md2pdf.core.pdf_engine.find_wkhtmltopdf",
                return_value="/usr/bin/wkhtmltopdf",
            ),
            "create_pdf_configuration": mocker.patch(
                "md2pdf.core.pdf_engine.create_pdf_configuration",
                return_value=MagicMock(),
            ),
            "validate_theme": mocker.patch(
                "md2pdf.core.theme_manager.validate_theme",
            ),
            "validate_input_file": mocker.patch(
                "md2pdf.core.file_operations.validate_input_file",
                return_value=Path("/path/to/input.md"),
            ),
            "determine_output_path": mocker.patch(
                "md2pdf.core.file_operations.determine_output_path",
                return_value=Path("/path/to/output.pdf"),
            ),
            "read_markdown_file": mocker.patch(
                "md2pdf.core.file_operations.read_markdown_file",
                return_value="# Test Markdown\n\nContent",
            ),
            "markdown_to_html": mocker.patch(
                "md2pdf.core.markdown_processor.markdown_to_html",
                return_value="<h1>Test Markdown</h1><p>Content</p>",
            ),
            "process_page_breaks": mocker.patch(
                "md2pdf.core.markdown_processor.process_page_breaks",
                return_value="<h1>Test Markdown</h1><p>Content</p>",
            ),
            "load_css": mocker.patch(
                "md2pdf.core.theme_manager.load_css",
                return_value="body { color: black; }",
            ),
            "build_html_document": mocker.patch(
                "md2pdf.core.markdown_processor.build_html_document",
                return_value="<html><body>Full HTML</body></html>",
            ),
            "convert_html_to_pdf": mocker.patch(
                "md2pdf.core.pdf_engine.convert_html_to_pdf",
            ),
            "preview_file": mocker.patch(
                "md2pdf.core.file_operations.preview_file",
            ),
        }

    def test_basic_conversion_with_defaults(self, mock_modules):
        """Test successful conversion with default parameters."""
        # Act
        core.convert_md_to_pdf("input.md")

        # Assert: Verify the full pipeline was executed
        mock_modules["validate_theme"].assert_called_once_with("default")
        mock_modules["find_wkhtmltopdf"].assert_called_once()
        mock_modules["create_pdf_configuration"].assert_called_once_with(
            "/usr/bin/wkhtmltopdf"
        )
        mock_modules["validate_input_file"].assert_called_once_with("input.md")
        mock_modules["determine_output_path"].assert_called_once_with(
            Path("/path/to/input.md"), None
        )
        mock_modules["read_markdown_file"].assert_called_once_with(
            Path("/path/to/input.md")
        )
        mock_modules["markdown_to_html"].assert_called_once_with(
            "# Test Markdown\n\nContent"
        )
        mock_modules["process_page_breaks"].assert_called_once()
        mock_modules["load_css"].assert_called_once_with(None, "default")
        mock_modules["build_html_document"].assert_called_once()
        mock_modules["convert_html_to_pdf"].assert_called_once()
        mock_modules["preview_file"].assert_not_called()

    def test_conversion_with_custom_output(self, mock_modules):
        """Test conversion with custom output path."""
        # Act
        core.convert_md_to_pdf("input.md", output_file="custom.pdf")

        # Assert
        mock_modules["determine_output_path"].assert_called_once_with(
            Path("/path/to/input.md"), "custom.pdf"
        )

    def test_conversion_with_custom_css(self, mock_modules):
        """Test conversion with custom CSS file."""
        # Act
        core.convert_md_to_pdf("input.md", custom_css="custom.css")

        # Assert: validate_theme should NOT be called when using custom CSS
        mock_modules["validate_theme"].assert_not_called()
        mock_modules["load_css"].assert_called_once_with("custom.css", "default")

    def test_conversion_with_theme(self, mock_modules):
        """Test conversion with specific theme."""
        # Act
        core.convert_md_to_pdf("input.md", theme="dark")

        # Assert
        mock_modules["validate_theme"].assert_called_once_with("dark")
        mock_modules["load_css"].assert_called_once_with(None, "dark")

    def test_conversion_with_preview(self, mock_modules):
        """Test conversion with preview enabled."""
        # Act
        core.convert_md_to_pdf("input.md", preview=True)

        # Assert
        mock_modules["preview_file"].assert_called_once_with(Path("/path/to/output.pdf"))

    def test_conversion_with_both_css_and_theme(self, mock_modules, capsys):
        """Test warning when both custom CSS and theme are specified."""
        # Act
        core.convert_md_to_pdf("input.md", custom_css="custom.css", theme="dark")

        # Assert
        captured = capsys.readouterr()
        assert "Warning: Both --css and --theme specified" in captured.err
        assert "ignoring theme 'dark'" in captured.err
        # validate_theme should NOT be called
        mock_modules["validate_theme"].assert_not_called()
        mock_modules["load_css"].assert_called_once_with("custom.css", "dark")

    def test_wkhtmltopdf_not_found(self, mock_modules):
        """Test error handling when wkhtmltopdf is not found."""
        # Arrange
        mock_modules["find_wkhtmltopdf"].return_value = None
        with patch(
            "md2pdf.core.pdf_engine.get_installation_instructions",
            return_value="Install wkhtmltopdf",
        ):
            # Act & Assert
            with pytest.raises(WkhtmltopdfNotFoundError) as exc_info:
                core.convert_md_to_pdf("input.md")

            assert "Install wkhtmltopdf" in str(exc_info.value)

    def test_theme_not_found(self, mock_modules):
        """Test error handling when theme is not found."""
        # Arrange
        mock_modules["validate_theme"].side_effect = ThemeNotFoundError(
            "nonexistent", ["default", "dark", "light"]
        )

        # Act & Assert
        with pytest.raises(ThemeNotFoundError) as exc_info:
            core.convert_md_to_pdf("input.md", theme="nonexistent")

        error_msg = str(exc_info.value)
        assert "Theme 'nonexistent' not found" in error_msg
        # Check all themes are mentioned (they may be sorted)
        assert "default" in error_msg
        assert "dark" in error_msg
        assert "light" in error_msg

    def test_css_file_not_found(self, mock_modules):
        """Test error handling when custom CSS file is not found."""
        # Arrange
        mock_modules["load_css"].side_effect = CSSNotFoundError(
            "CSS file 'custom.css' does not exist."
        )

        # Act & Assert
        with pytest.raises(CSSNotFoundError) as exc_info:
            core.convert_md_to_pdf("input.md", custom_css="custom.css")

        assert "custom.css" in str(exc_info.value)

    def test_input_file_not_found(self, mock_modules):
        """Test error handling when input file is not found."""
        # Arrange
        mock_modules["validate_input_file"].side_effect = InvalidInputError(
            "Input file 'missing.md' does not exist."
        )

        # Act & Assert
        with pytest.raises(InvalidInputError) as exc_info:
            core.convert_md_to_pdf("missing.md")

        assert "missing.md" in str(exc_info.value)

    def test_markdown_file_read_error(self, mock_modules):
        """Test error handling when reading markdown file fails."""
        # Arrange
        mock_modules["read_markdown_file"].side_effect = FileOperationError(
            "Error reading input file: Permission denied"
        )

        # Act & Assert
        with pytest.raises(FileOperationError) as exc_info:
            core.convert_md_to_pdf("input.md")

        assert "Permission denied" in str(exc_info.value)

    def test_pdf_conversion_error(self, mock_modules):
        """Test error handling when PDF conversion fails."""
        # Arrange
        mock_modules["convert_html_to_pdf"].side_effect = ConversionError(
            "Error generating PDF: wkhtmltopdf failed"
        )

        # Act & Assert
        with pytest.raises(ConversionError) as exc_info:
            core.convert_md_to_pdf("input.md")

        assert "wkhtmltopdf failed" in str(exc_info.value)

    def test_full_integration_with_all_parameters(self, mock_modules):
        """Test full conversion pipeline with all parameters specified."""
        # Act
        core.convert_md_to_pdf(
            input_file="report.md",
            output_file="output.pdf",
            custom_css="style.css",
            theme="dark",  # Will be ignored due to custom_css
            preview=True,
        )

        # Assert: Verify complete pipeline
        assert mock_modules["validate_theme"].call_count == 0  # Not called with custom CSS
        mock_modules["find_wkhtmltopdf"].assert_called_once()
        mock_modules["validate_input_file"].assert_called_once_with("report.md")
        mock_modules["determine_output_path"].assert_called_once_with(
            Path("/path/to/input.md"), "output.pdf"
        )
        mock_modules["load_css"].assert_called_once_with("style.css", "dark")
        mock_modules["convert_html_to_pdf"].assert_called_once()
        mock_modules["preview_file"].assert_called_once()

    def test_markdown_processing_pipeline(self, mock_modules):
        """Test that markdown processing happens in correct order."""
        # Arrange
        markdown_content = "# Heading\n\nParagraph"
        html_body = "<h1>Heading</h1><p>Paragraph</p>"
        processed_html = "<h1>Heading</h1><div class='page-break'></div><p>Paragraph</p>"

        mock_modules["read_markdown_file"].return_value = markdown_content
        mock_modules["markdown_to_html"].return_value = html_body
        mock_modules["process_page_breaks"].return_value = processed_html

        # Act
        core.convert_md_to_pdf("input.md")

        # Assert: Verify processing order
        mock_modules["markdown_to_html"].assert_called_once_with(markdown_content)
        mock_modules["process_page_breaks"].assert_called_once_with(html_body)
        mock_modules["build_html_document"].assert_called_once_with(
            title="input",  # stem of input.md
            body_html=processed_html,
            css_content="body { color: black; }",
        )

    def test_output_path_determination(self, mock_modules):
        """Test output path is correctly determined from input."""
        # Arrange
        input_path = Path("/docs/report.md")
        mock_modules["validate_input_file"].return_value = input_path

        # Act
        core.convert_md_to_pdf("report.md")

        # Assert
        mock_modules["determine_output_path"].assert_called_once_with(input_path, None)

    def test_pdf_configuration_creation(self, mock_modules):
        """Test PDF configuration is created with found wkhtmltopdf path."""
        # Arrange
        wkhtmltopdf_path = "/custom/path/wkhtmltopdf"
        mock_modules["find_wkhtmltopdf"].return_value = wkhtmltopdf_path

        # Act
        core.convert_md_to_pdf("input.md")

        # Assert
        mock_modules["create_pdf_configuration"].assert_called_once_with(
            wkhtmltopdf_path
        )

    def test_html_document_title_from_input_stem(self, mock_modules):
        """Test that HTML document title is derived from input file stem."""
        # Arrange
        input_path = Path("/docs/my-report.md")
        mock_modules["validate_input_file"].return_value = input_path

        # Act
        core.convert_md_to_pdf("my-report.md")

        # Assert
        # Check that build_html_document was called with title='my-report'
        call_args = mock_modules["build_html_document"].call_args
        assert call_args[1]["title"] == "my-report"

    def test_preview_not_called_when_disabled(self, mock_modules):
        """Test that preview is not called when preview=False."""
        # Act
        core.convert_md_to_pdf("input.md", preview=False)

        # Assert
        mock_modules["preview_file"].assert_not_called()

    def test_exception_propagation(self, mock_modules):
        """Test that exceptions from submodules are properly propagated."""
        # Test various exception types
        exceptions_to_test = [
            (
                "validate_theme",
                ThemeNotFoundError("test", []),
                ThemeNotFoundError,
            ),
            (
                "validate_input_file",
                InvalidInputError("test"),
                InvalidInputError,
            ),
            (
                "read_markdown_file",
                FileOperationError("test"),
                FileOperationError,
            ),
            (
                "load_css",
                CSSNotFoundError("test"),
                CSSNotFoundError,
            ),
            (
                "convert_html_to_pdf",
                ConversionError("test"),
                ConversionError,
            ),
        ]

        for mock_name, exception, expected_type in exceptions_to_test:
            # Reset mocks
            for mock in mock_modules.values():
                mock.reset_mock()
                mock.side_effect = None

            # Setup
            mock_modules["find_wkhtmltopdf"].return_value = "/usr/bin/wkhtmltopdf"
            mock_modules[mock_name].side_effect = exception

            # Act & Assert
            with pytest.raises(expected_type):
                core.convert_md_to_pdf("input.md")
