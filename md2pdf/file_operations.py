"""File I/O operations and validation."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

from . import config
from .exceptions import FileOperationError, InvalidInputError


def validate_input_file(input_file: str) -> Path:
    """Validate the input markdown file.

    Args:
        input_file: Path to the input markdown file

    Returns:
        Validated Path object

    Raises:
        InvalidInputError: If validation fails
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise InvalidInputError(f"Input file '{input_file}' does not exist.")

    if not input_path.is_file():
        raise InvalidInputError(f"'{input_file}' is not a file.")

    # Optional: Validate extension (warn, don't error)
    if input_path.suffix.lower() not in config.SUPPORTED_MARKDOWN_EXTENSIONS:
        print(
            f"Warning: '{input_file}' does not have a markdown extension (.md, .markdown, .txt)",
            file=sys.stderr,
        )

    # Check readability
    if not os.access(input_path, os.R_OK):
        raise InvalidInputError(f"No read permission for '{input_file}'.")

    return input_path


def read_markdown_file(path: Path) -> str:
    """Read markdown file and return its content.

    Args:
        path: Path to markdown file

    Returns:
        File content as string

    Raises:
        FileOperationError: If file cannot be read
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (IOError, PermissionError, UnicodeDecodeError) as e:
        raise FileOperationError(f"Error reading input file: {e}") from e


def determine_output_path(input_path: Path, output_arg: Optional[str]) -> Path:
    """Determine the output PDF path with enhanced security validation.

    This function validates output paths to prevent security issues including:
    - Path traversal attacks (../ sequences)
    - Symlink attacks
    - Writing outside the current working directory (for relative paths)

    Args:
        input_path: Path to input markdown file
        output_arg: Optional output path argument from CLI

    Returns:
        Path where PDF should be saved (always resolved to absolute path)

    Raises:
        InvalidInputError: If output path is invalid or attempts path traversal
    """
    if output_arg is None:
        return input_path.with_suffix(".pdf")

    output_path = Path(output_arg)

    # Step 1: Check for explicit path traversal components before resolution
    if ".." in output_path.parts:
        raise InvalidInputError(
            f"Invalid output path '{output_arg}': path traversal (..) is not allowed"
        )

    # Step 2: Resolve to absolute path (resolves symlinks and normalizes)
    try:
        resolved_path = output_path.resolve(strict=False)
    except (ValueError, OSError, RuntimeError) as e:
        raise InvalidInputError(
            f"Invalid output path '{output_arg}': cannot resolve path - {e}"
        ) from e

    # Step 3: If a relative path was provided, ensure it resolves within current directory
    if not output_path.is_absolute():
        cwd = Path.cwd().resolve()

        # Check if the resolved path is within or equal to current working directory
        try:
            resolved_path.relative_to(cwd)
        except ValueError:
            raise InvalidInputError(
                f"Invalid output path '{output_arg}': resolved path '{resolved_path}' "
                f"is outside current directory '{cwd}'. Use an absolute path if you "
                f"need to write outside the current directory."
            )

    # Step 4: Detect symlink traversal (if path doesn't exist yet, check parent)
    check_path = resolved_path if resolved_path.exists() else resolved_path.parent
    if check_path.exists() and check_path.is_symlink():
        # For symlinks, verify the target stays within bounds
        if not output_path.is_absolute():
            symlink_target = check_path.resolve()
            cwd = Path.cwd().resolve()
            try:
                symlink_target.relative_to(cwd)
            except ValueError:
                raise InvalidInputError(
                    f"Invalid output path '{output_arg}': symlink target points "
                    f"outside current directory"
                )

    return resolved_path


def preview_file(pdf_path: Path) -> None:
    """Open a PDF file using the default system viewer.

    Args:
        pdf_path: Path to the PDF file to open

    Note:
        This function validates the PDF path exists and is a file before
        attempting to open it. Subprocess calls include timeout protection.
    """
    # Validate the PDF path before attempting to open
    if not pdf_path.exists():
        print(f"Warning: PDF file does not exist: {pdf_path}", file=sys.stderr)
        return

    if not pdf_path.is_file():
        print(f"Warning: Path is not a file: {pdf_path}", file=sys.stderr)
        return

    try:
        system = platform.system()

        if system == "Windows":
            # os.startfile is Windows-specific and relatively safe
            # It validates the path and uses the default file association
            os.startfile(str(pdf_path))
        elif system == "Darwin":  # macOS
            # Use timeout to prevent hanging
            subprocess.run(
                ["open", str(pdf_path)],
                check=True,
                timeout=config.SUBPROCESS_TIMEOUT,
            )
        elif system == "Linux":
            # Use timeout to prevent hanging
            subprocess.run(
                ["xdg-open", str(pdf_path)],
                check=True,
                timeout=config.SUBPROCESS_TIMEOUT,
            )
        else:
            print(
                f"Warning: Unable to open PDF on {system} platform", file=sys.stderr
            )
    except subprocess.TimeoutExpired:
        print(f"Warning: Timeout opening PDF: {pdf_path}", file=sys.stderr)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Warning: Could not open PDF: {e}", file=sys.stderr)
