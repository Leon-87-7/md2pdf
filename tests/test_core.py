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


class TestConvertBatch:
    """Integration tests for the convert_batch function."""

    @pytest.fixture
    def mock_modules(self, mocker):
        """Mock all module dependencies for core.convert_batch."""
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
                side_effect=lambda x: Path(f"/path/to/{x}"),
            ),
            "determine_output_path": mocker.patch(
                "md2pdf.core.file_operations.determine_output_path",
                side_effect=lambda p, _: Path(str(p).replace(".md", ".pdf")),
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

    def test_batch_conversion_success_multiple_files(self, mock_modules, capsys):
        """Test successful batch conversion of multiple files."""
        # Act
        core.convert_batch(["file1.md", "file2.md", "file3.md"])

        # Assert
        assert mock_modules["validate_input_file"].call_count == 3
        assert mock_modules["convert_html_to_pdf"].call_count == 3

        captured = capsys.readouterr()
        assert "Total files: 3" in captured.out
        assert "Successful: 3" in captured.out
        assert "Failed: 0" in captured.out

    def test_batch_conversion_with_output_dir(self, mock_modules, temp_dir):
        """Test batch conversion with custom output directory."""
        output_dir = temp_dir / "output"

        # Act
        core.convert_batch(["file1.md", "file2.md"], output_dir=str(output_dir))

        # Assert
        assert output_dir.exists()
        assert mock_modules["convert_html_to_pdf"].call_count == 2

    def test_batch_conversion_partial_failure(self, mock_modules, capsys):
        """Test batch conversion with partial failures."""
        # Arrange: Make second file fail
        def validate_side_effect(filename):
            if filename == "file2.md":
                raise InvalidInputError("File not found")
            return Path(f"/path/to/{filename}")

        mock_modules["validate_input_file"].side_effect = validate_side_effect

        # Act
        core.convert_batch(["file1.md", "file2.md", "file3.md"])

        # Assert
        captured = capsys.readouterr()
        assert "Total files: 3" in captured.out
        assert "Successful: 2" in captured.out
        assert "Failed: 1" in captured.out
        assert "file2.md" in captured.err

    def test_batch_conversion_empty_list(self, mock_modules, capsys):
        """Test batch conversion with empty file list."""
        # Act
        core.convert_batch([])

        # Assert
        captured = capsys.readouterr()
        assert "No input files specified" in captured.err
        mock_modules["convert_html_to_pdf"].assert_not_called()

    def test_batch_conversion_with_preview(self, mock_modules):
        """Test batch conversion with preview enabled."""
        # Act
        core.convert_batch(["file1.md", "file2.md"], preview=True)

        # Assert
        mock_modules["preview_file"].assert_called_once()

    def test_batch_conversion_output_dir_creation_failure(self, mock_modules, capsys):
        """Test batch conversion when output directory cannot be created."""
        # Act
        with patch("pathlib.Path.mkdir", side_effect=PermissionError("Access denied")):
            core.convert_batch(["file1.md"], output_dir="/invalid/path")

        # Assert
        captured = capsys.readouterr()
        assert "Cannot create output directory" in captured.err
        mock_modules["convert_html_to_pdf"].assert_not_called()

    def test_batch_conversion_handles_os_errors(self, mock_modules, capsys):
        """Test batch conversion handles OS-level errors gracefully."""
        # Arrange
        mock_modules["read_markdown_file"].side_effect = OSError("Disk read error")

        # Act
        core.convert_batch(["file1.md"])

        # Assert
        captured = capsys.readouterr()
        assert "System error" in captured.err
        assert "Failed: 1" in captured.out


class TestConvertMerge:
    """Integration tests for the convert_merge function."""

    @pytest.fixture
    def mock_modules(self, mocker):
        """Mock all module dependencies for core.convert_merge."""
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
                side_effect=lambda x: Path(f"/path/to/{x}"),
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

    def test_merge_conversion_success(self, mock_modules, capsys):
        """Test successful merge of multiple files."""
        # Act
        core.convert_merge(["file1.md", "file2.md", "file3.md"])

        # Assert
        assert mock_modules["validate_input_file"].call_count == 3
        mock_modules["convert_html_to_pdf"].assert_called_once()

        captured = capsys.readouterr()
        assert "Total files: 3" in captured.out
        assert "Successfully merged: 3" in captured.out

    def test_merge_conversion_with_auto_break_true(self, mock_modules):
        """Test merge conversion with auto_break=True."""
        # Act
        core.convert_merge(["file1.md", "file2.md"], auto_break=True)

        # Assert
        # Check that build_html_document was called
        mock_modules["build_html_document"].assert_called_once()
        call_args = mock_modules["build_html_document"].call_args
        body_html = call_args[1]["body_html"]

        # Should contain page breaks (checked via presence of page-break div)
        assert "page-break" in body_html

    def test_merge_conversion_with_auto_break_false(self, mock_modules):
        """Test merge conversion with auto_break=False."""
        # Act
        core.convert_merge(["file1.md", "file2.md"], auto_break=False)

        # Assert
        mock_modules["build_html_document"].assert_called_once()
        call_args = mock_modules["build_html_document"].call_args
        body_html = call_args[1]["body_html"]

        # Should NOT contain page breaks between documents
        # Count occurrences - with 2 files and auto_break=False, no page breaks
        assert body_html.count("page-break") == 0

    def test_merge_conversion_with_output_file(self, mock_modules):
        """Test merge conversion with custom output file."""
        # Act
        core.convert_merge(["file1.md", "file2.md"], output_file="custom.pdf")

        # Assert
        mock_modules["convert_html_to_pdf"].assert_called_once()
        call_args = mock_modules["convert_html_to_pdf"].call_args
        output_path = call_args[0][1]
        assert output_path == Path("custom.pdf")

    def test_merge_conversion_default_output(self, mock_modules):
        """Test merge conversion uses default output name."""
        # Act
        core.convert_merge(["file1.md", "file2.md"])

        # Assert
        call_args = mock_modules["convert_html_to_pdf"].call_args
        output_path = call_args[0][1]
        assert output_path == Path("merged_output.pdf")

    def test_merge_conversion_empty_list(self, mock_modules, capsys):
        """Test merge conversion with empty file list."""
        # Act
        core.convert_merge([])

        # Assert
        captured = capsys.readouterr()
        assert "No input files specified" in captured.err
        mock_modules["convert_html_to_pdf"].assert_not_called()

    def test_merge_conversion_single_file_warning(self, mock_modules, capsys):
        """Test merge conversion with single file shows warning."""
        # Act
        core.convert_merge(["file1.md"])

        # Assert
        captured = capsys.readouterr()
        assert "at least 2 files" in captured.err

    def test_merge_conversion_partial_failure(self, mock_modules, capsys):
        """Test merge conversion with partial failures."""
        # Arrange: Make second file fail
        def validate_side_effect(filename):
            if filename == "file2.md":
                raise FileOperationError("Read error")
            return Path(f"/path/to/{filename}")

        mock_modules["validate_input_file"].side_effect = validate_side_effect

        # Act
        core.convert_merge(["file1.md", "file2.md", "file3.md"])

        # Assert
        captured = capsys.readouterr()
        assert "Successfully merged: 2" in captured.out
        assert "Failed: 1" in captured.out
        assert "file2.md" in captured.err

    def test_merge_conversion_all_failures(self, mock_modules, capsys):
        """Test merge conversion when all files fail."""
        # Arrange
        mock_modules["validate_input_file"].side_effect = InvalidInputError("Not found")

        # Act
        core.convert_merge(["file1.md", "file2.md"])

        # Assert
        captured = capsys.readouterr()
        assert "No files were successfully processed" in captured.err
        mock_modules["convert_html_to_pdf"].assert_not_called()

    def test_merge_conversion_with_preview(self, mock_modules):
        """Test merge conversion with preview enabled."""
        # Act
        core.convert_merge(["file1.md", "file2.md"], preview=True)

        # Assert
        mock_modules["preview_file"].assert_called_once()


class TestMergeHtmlBodies:
    """Tests for the _merge_html_bodies helper function."""

    def test_merge_html_bodies_with_auto_break(self):
        """Test merging HTML bodies with auto page breaks."""
        html_bodies = [
            ("file1.md", "<p>Content 1</p>"),
            ("file2.md", "<p>Content 2</p>"),
            ("file3.md", "<p>Content 3</p>"),
        ]

        result = core._merge_html_bodies(html_bodies, auto_break=True)

        # Should contain all filenames as headers
        assert "file1.md" in result
        assert "file2.md" in result
        assert "file3.md" in result

        # Should contain all content
        assert "Content 1" in result
        assert "Content 2" in result
        assert "Content 3" in result

        # Should contain page breaks (2 breaks for 3 files)
        assert result.count("page-break") == 2

    def test_merge_html_bodies_without_auto_break(self):
        """Test merging HTML bodies without auto page breaks."""
        html_bodies = [
            ("file1.md", "<p>Content 1</p>"),
            ("file2.md", "<p>Content 2</p>"),
        ]

        result = core._merge_html_bodies(html_bodies, auto_break=False)

        # Should contain filenames and content
        assert "file1.md" in result
        assert "file2.md" in result

        # Should NOT contain page breaks
        assert "page-break" not in result

    def test_merge_html_bodies_escapes_filenames(self):
        """Test that filenames are HTML-escaped to prevent injection."""
        html_bodies = [
            ("<script>alert('xss')</script>.md", "<p>Content</p>"),
        ]

        result = core._merge_html_bodies(html_bodies, auto_break=False)

        # Should not contain raw script tags
        assert "<script>" not in result
        # Should contain escaped version
        assert "&lt;script&gt;" in result

    def test_merge_html_bodies_single_file(self):
        """Test merging with single file."""
        html_bodies = [("file1.md", "<p>Content 1</p>")]

        result = core._merge_html_bodies(html_bodies, auto_break=True)

        # Should contain content
        assert "Content 1" in result
        # Should NOT contain page breaks (no files after this one)
        assert "page-break" not in result

    def test_merge_html_bodies_contains_section_headers(self):
        """Test that section headers are properly formatted."""
        html_bodies = [("file1.md", "<p>Content</p>")]

        result = core._merge_html_bodies(html_bodies, auto_break=False)

        # Should contain section header with proper class
        assert "document-section-header" in result
        assert "file1.md" in result


class TestSetupConversionEnvironment:
    """Tests for the _setup_conversion_environment helper function."""

    def test_setup_with_default_theme(self, mocker):
        """Test setup with default theme."""
        mocker.patch("md2pdf.core.pdf_engine.find_wkhtmltopdf", return_value="/usr/bin/wkhtmltopdf")
        mocker.patch("md2pdf.core.pdf_engine.create_pdf_configuration", return_value=MagicMock())
        mock_validate = mocker.patch("md2pdf.core.theme_manager.validate_theme")
        mocker.patch("md2pdf.core.theme_manager.load_css", return_value="css")

        # Act
        pdf_config, css_content = core._setup_conversion_environment()

        # Assert
        mock_validate.assert_called_once_with("default")
        assert css_content == "css"

    def test_setup_with_custom_css(self, mocker):
        """Test setup with custom CSS (theme validation skipped)."""
        mocker.patch("md2pdf.core.pdf_engine.find_wkhtmltopdf", return_value="/usr/bin/wkhtmltopdf")
        mocker.patch("md2pdf.core.pdf_engine.create_pdf_configuration", return_value=MagicMock())
        mock_validate = mocker.patch("md2pdf.core.theme_manager.validate_theme")
        mocker.patch("md2pdf.core.theme_manager.load_css", return_value="custom css")

        # Act
        pdf_config, css_content = core._setup_conversion_environment(custom_css="custom.css")

        # Assert
        mock_validate.assert_not_called()
        assert css_content == "custom css"

    def test_setup_warns_on_both_css_and_theme(self, mocker, capsys):
        """Test setup warns when both CSS and theme are specified."""
        mocker.patch("md2pdf.core.pdf_engine.find_wkhtmltopdf", return_value="/usr/bin/wkhtmltopdf")
        mocker.patch("md2pdf.core.pdf_engine.create_pdf_configuration", return_value=MagicMock())
        mocker.patch("md2pdf.core.theme_manager.load_css", return_value="css")

        # Act
        core._setup_conversion_environment(custom_css="custom.css", theme="dark")

        # Assert
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "ignoring theme" in captured.err
