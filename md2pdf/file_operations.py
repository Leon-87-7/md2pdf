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
    """Determine the output PDF path.

    Args:
        input_path: Path to input markdown file
        output_arg: Optional output path argument from CLI

    Returns:
        Path where PDF should be saved
    """
    if output_arg is None:
        return input_path.with_suffix(".pdf")
    else:
        return Path(output_arg)


def preview_file(pdf_path: Path) -> None:
    """Open a PDF file using the default system viewer.

    Args:
        pdf_path: Path to the PDF file to open
    """
    try:
        system = platform.system()

        if system == "Windows":
            os.startfile(str(pdf_path))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(pdf_path)], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(pdf_path)], check=True)
        else:
            print(
                f"Warning: Unable to open PDF on {system} platform", file=sys.stderr
            )
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Warning: Could not open PDF: {e}", file=sys.stderr)
