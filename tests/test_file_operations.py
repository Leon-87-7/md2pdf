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

    def test_determine_output_path_rejects_path_traversal(self, temp_dir):
        """Test that path traversal attempts are rejected."""
        input_path = temp_dir / "input.md"
        # Try to write outside current directory using ..
        output_arg = "../../../etc/passwd.pdf"

        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.determine_output_path(input_path, output_arg)
        assert "path traversal" in str(exc_info.value).lower()

    def test_determine_output_path_allows_absolute_path(self, temp_dir):
        """Test that absolute paths are allowed."""
        input_path = temp_dir / "input.md"
        output_arg = str(temp_dir / "output.pdf")
        output_path = file_operations.determine_output_path(input_path, output_arg)

        assert output_path.is_absolute()
        assert output_path.name == "output.pdf"

    def test_determine_output_path_normalizes_path(self, temp_dir):
        """Test that output paths are normalized."""
        input_path = temp_dir / "input.md"
        output_arg = "output.pdf"
        output_path = file_operations.determine_output_path(input_path, output_arg)

        # Should be resolved to absolute path
        assert output_path.is_absolute()


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
        mock_run.assert_called_once_with(["open", str(pdf_path)], check=True, timeout=10)

    @patch("platform.system")
    @patch("subprocess.run")
    def test_preview_file_linux(self, mock_run, mock_system, temp_dir):
        """Test preview on Linux platform."""
        mock_system.return_value = "Linux"
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        mock_run.assert_called_once_with(["xdg-open", str(pdf_path)], check=True, timeout=10)

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
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "Could not open PDF" in captured.err

    def test_preview_file_nonexistent(self, temp_dir, capsys):
        """Test preview with non-existent file."""
        pdf_path = temp_dir / "nonexistent.pdf"

        file_operations.preview_file(pdf_path)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "does not exist" in captured.err

    def test_preview_file_not_a_file(self, temp_dir, capsys):
        """Test preview with directory instead of file."""
        file_operations.preview_file(temp_dir)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "not a file" in captured.err

    @patch("platform.system")
    @patch("subprocess.run")
    def test_preview_file_timeout(self, mock_run, mock_system, temp_dir, capsys):
        """Test preview handles timeout gracefully."""
        import subprocess
        mock_system.return_value = "Linux"
        mock_run.side_effect = subprocess.TimeoutExpired("xdg-open", 10)
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("fake pdf", encoding="utf-8")

        file_operations.preview_file(pdf_path)
        captured = capsys.readouterr()

        assert "Warning" in captured.err
        assert "Timeout" in captured.err


class TestDetermineOutputPathSecurity:
    """Security tests for output path validation."""

    def test_path_traversal_attack_simple(self, temp_dir):
        """Test that simple path traversal attacks are blocked."""
        input_path = temp_dir / "input.md"

        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.determine_output_path(input_path, "../../etc/passwd.pdf")

        assert "path traversal" in str(exc_info.value).lower()

    def test_path_traversal_attack_complex(self, temp_dir):
        """Test that complex path traversal attacks are blocked."""
        input_path = temp_dir / "input.md"

        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.determine_output_path(input_path, "../../../secret.pdf")

        assert "path traversal" in str(exc_info.value).lower()

    def test_path_traversal_mixed_with_safe_path(self, temp_dir):
        """Test that traversal mixed with safe paths is blocked."""
        input_path = temp_dir / "input.md"

        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.determine_output_path(input_path, "safe/../../../etc/passwd.pdf")

        assert "path traversal" in str(exc_info.value).lower()

    def test_relative_path_escaping_cwd(self, temp_dir):
        """Test that relative paths escaping CWD are blocked."""
        import os
        input_path = temp_dir / "input.md"

        # Create a relative path that would escape CWD after resolution
        # This test ensures the function checks the resolved path against CWD
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Try to write to parent of temp_dir using a relative path
            parent_path = "../outside.pdf"

            with pytest.raises(InvalidInputError) as exc_info:
                file_operations.determine_output_path(input_path, parent_path)

            # Should be caught as path traversal or outside current directory
            error_msg = str(exc_info.value).lower()
            assert "path traversal" in error_msg or "outside current directory" in error_msg
        finally:
            os.chdir(original_cwd)

    def test_absolute_path_allowed(self, temp_dir):
        """Test that absolute paths are allowed and work correctly."""
        input_path = temp_dir / "input.md"
        output_arg = str(temp_dir / "output.pdf")

        result = file_operations.determine_output_path(input_path, output_arg)

        assert result.is_absolute()
        assert result.name == "output.pdf"

    def test_safe_relative_path_within_cwd(self, temp_dir):
        """Test that safe relative paths within CWD are allowed."""
        input_path = temp_dir / "input.md"

        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Create subdirectory
            subdir = temp_dir / "subdir"
            subdir.mkdir()

            # This should be allowed
            result = file_operations.determine_output_path(input_path, "subdir/output.pdf")

            assert result.is_absolute()
            assert "subdir" in str(result)
            assert result.name == "output.pdf"
        finally:
            os.chdir(original_cwd)

    def test_symlink_detection_and_validation(self, temp_dir):
        """Test that symlinks are detected and validated."""
        import os

        if not hasattr(os, 'symlink'):
            pytest.skip("Symlinks not supported on this platform")

        input_path = temp_dir / "input.md"

        # Create a safe symlink within temp_dir
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        symlink_dir = temp_dir / "link"

        try:
            symlink_dir.symlink_to(target_dir)

            # This should work - symlink points within CWD
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = file_operations.determine_output_path(
                    input_path, "link/output.pdf"
                )
                assert result.is_absolute()
            finally:
                os.chdir(original_cwd)
        except OSError:
            pytest.skip("Cannot create symlinks (may need elevated permissions on Windows)")

    def test_normalized_path_returned(self, temp_dir):
        """Test that returned paths are properly normalized."""
        input_path = temp_dir / "input.md"
        output_arg = str(temp_dir / "dir1" / "." / "output.pdf")

        result = file_operations.determine_output_path(input_path, output_arg)

        # Should be normalized (no . components)
        assert "." not in result.parts[-2:]  # Check last two parts
        assert result.name == "output.pdf"

    def test_invalid_path_characters_handled(self, temp_dir):
        """Test handling of paths with invalid characters."""
        input_path = temp_dir / "input.md"

        # On Windows, certain characters are invalid
        # On Unix, most characters are valid
        # Just ensure no crash occurs
        import platform
        if platform.system() == "Windows":
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            for char in invalid_chars:
                try:
                    result = file_operations.determine_output_path(
                        input_path, f"test{char}file.pdf"
                    )
                    # If it doesn't raise, that's fine too (path validation may occur later)
                except (InvalidInputError, OSError, ValueError):
                    # Expected - invalid character caught
                    pass

    def test_error_messages_are_informative(self, temp_dir):
        """Test that error messages provide helpful information."""
        input_path = temp_dir / "input.md"

        with pytest.raises(InvalidInputError) as exc_info:
            file_operations.determine_output_path(input_path, "../../attack.pdf")

        error_msg = str(exc_info.value)
        # Should mention what's wrong
        assert "path traversal" in error_msg.lower()
        # Should mention what was attempted
        assert "attack.pdf" in error_msg or ".." in error_msg