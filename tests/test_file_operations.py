"""Tests for md2pdf.file_operations module."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from md2pdf import file_operations
from md2pdf.exceptions import InvalidInputError, FileOperationError


class TestValidateInputFile:
    """Test input file validation."""

    def test_validate_input_file_success(self, sample_markdown_file):
        """Test validating a valid markdown file."""
        result = file_operations.validate_input_file(str(sample_markdown_file))
        assert isinstance(result, Path)
        assert result == sample_markdown_file

    def test_validate_input_file_nonexistent(self):
        """Test validating a non-existent file raises InvalidInputError."""
        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.validate_input_file("nonexistent_file.md")
        assert "does not exist" in str(exc_info.value)

    def test_validate_input_file_directory(self, temp_dir):
        """Test validating a directory raises InvalidInputError."""
        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.validate_input_file(str(temp_dir))
        assert "is not a file" in str(exc_info.value)

    def test_validate_input_file_warns_on_invalid_extension(self, temp_dir, capsys):
        """Test warning on non-markdown extension."""
        test_file = temp_dir / "test.html"
        test_file.write_text("# Test", encoding="utf-8")

        result = file_operations.validate_input_file(str(test_file))
        captured = capsys.readouterr()

        assert isinstance(result, Path)
        assert "Warning" in captured.err
        assert "markdown extension" in captured.err

    def test_validate_input_file_markdown_extension(self, temp_dir):
        """Test file with .markdown extension."""
        test_file = temp_dir / "test.markdown"
        test_file.write_text("# Test", encoding="utf-8")

        result = file_operations.validate_input_file(str(test_file))
        assert isinstance(result, Path)

    def test_validate_input_file_txt_extension(self, temp_dir):
        """Test file with .txt extension."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("# Test", encoding="utf-8")

        result = file_operations.validate_input_file(str(test_file))
        assert isinstance(result, Path)


class TestReadMarkdownFile:
    """Test reading markdown files."""

    def test_read_markdown_file_success(self, sample_markdown_file, sample_markdown):
        """Test reading a valid markdown file."""
        content = file_operations.read_markdown_file(sample_markdown_file)
        assert content == sample_markdown

    def test_read_markdown_file_empty(self, temp_dir):
        """Test reading an empty file."""
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("", encoding="utf-8")

        content = file_operations.read_markdown_file(empty_file)
        assert content == ""

    def test_read_markdown_file_utf8_content(self, temp_dir):
        """Test reading file with UTF-8 content."""
        utf8_file = temp_dir / "utf8.md"
        utf8_content = "# Test 你好 🌟"
        utf8_file.write_text(utf8_content, encoding="utf-8")

        content = file_operations.read_markdown_file(utf8_file)
        assert content == utf8_content


class TestDetermineOutputPath:
    """Test output path determination."""

    def test_determine_output_path_no_arg(self, temp_dir):
        """Test output path when no argument is provided."""
        input_path = temp_dir / "test.md"
        output_path = file_operations.determine_output_path(input_path, None)

        assert isinstance(output_path, Path)
        assert output_path.suffix == ".pdf"
        assert output_path.stem == "test"

    def test_determine_output_path_with_arg(self, temp_dir):
        """Test output path when argument is provided."""
        input_path = temp_dir / "test.md"
        output_arg = str(temp_dir / "custom_output.pdf")
        output_path = file_operations.determine_output_path(input_path, output_arg)

        assert isinstance(output_path, Path)
        assert output_path.name == "custom_output.pdf"

    def test_determine_output_path_preserves_name(self, temp_dir):
        """Test that input filename is preserved in output."""
        input_path = temp_dir / "my_document.md"
        output_path = file_operations.determine_output_path(input_path, None)

        assert output_path.name == "my_document.pdf"

    def test_determine_output_path_different_directory(self, temp_dir):
        """Test output in different directory."""
        input_path = temp_dir / "input.md"
        output_arg = str(temp_dir / "subdir" / "output.pdf")
        output_path = file_operations.determine_output_path(input_path, output_arg)

        assert output_path.parent.name == "subdir"


class TestPreviewFile:
    """Test PDF preview functionality."""

    @patch("platform.system")
    @patch("os.startfile")
    def test_preview_file_windows(self, mock_startfile, mock_system, temp_dir):
        """Test preview on Windows platform."""
        mock_system.return_value = "Windows"
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        mock_startfile.assert_called_once_with(str(pdf_path))

    @patch("platform.system")
    @patch("subprocess.run")
    def test_preview_file_macos(self, mock_run, mock_system, temp_dir):
        """Test preview on macOS platform."""
        mock_system.return_value = "Darwin"
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        mock_run.assert_called_once_with(["open", str(pdf_path)], check=True)

    @patch("platform.system")
    @patch("subprocess.run")
    def test_preview_file_linux(self, mock_run, mock_system, temp_dir):
        """Test preview on Linux platform."""
        mock_system.return_value = "Linux"
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        mock_run.assert_called_once_with(["xdg-open", str(pdf_path)], check=True)

    @patch("platform.system")
    def test_preview_file_unknown_platform(self, mock_system, temp_dir, capsys):
        """Test preview on unknown platform."""
        mock_system.return_value = "UnknownOS"
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "Unable to open PDF" in captured.err

    @patch("platform.system")
    @patch("os.startfile")
    def test_preview_file_error_handling(self, mock_startfile, mock_system, temp_dir, capsys):
        """Test preview error handling."""
        mock_system.return_value = "Windows"
        mock_startfile.side_effect = OSError("File not found")
        pdf_path = temp_dir / "test.pdf"

        file_operations.preview_file(pdf_path)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "Could not open PDF" in captured.err