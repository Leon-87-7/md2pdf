"""PDF generation engine using wkhtmltopdf."""

import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

import pdfkit

from . import config


def find_wkhtmltopdf() -> Optional[str]:
    """Auto-detect wkhtmltopdf installation path across different platforms.

    Returns:
        Path to wkhtmltopdf executable if found, None otherwise.
    """
    # First, check if wkhtmltopdf is in PATH
    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if wkhtmltopdf_path:
        return wkhtmltopdf_path

    # Get platform-specific common paths
    system = platform.system()
    common_paths = config.WKHTMLTOPDF_PATHS.get(system, []).copy()

    # Add user-specific path for Windows
    if system == "Windows":
        user_path = Path.home() / "AppData/Local/Programs/wkhtmltopdf/bin/wkhtmltopdf.exe"
        common_paths.append(user_path)

    # Check each common path
    for path in common_paths:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_file():
            return str(path_obj)

    return None


def create_pdf_configuration(wkhtmltopdf_path: str):
    """Create pdfkit configuration object.

    Args:
        wkhtmltopdf_path: Path to wkhtmltopdf executable

    Returns:
        pdfkit.configuration object
    """
    return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


def print_installation_help() -> None:
    """Print platform-specific installation instructions for wkhtmltopdf."""
    print("Error: wkhtmltopdf not found.", file=sys.stderr)
    print(
        "\nwkhtmltopdf is required for PDF generation but was not found on your system.",
        file=sys.stderr,
    )
    print("\nInstallation instructions:", file=sys.stderr)

    system = platform.system()
    instructions = config.INSTALLATION_INSTRUCTIONS.get(system, config.INSTALLATION_INSTRUCTIONS["default"])

    for instruction in instructions:
        print(instruction, file=sys.stderr)


def convert_html_to_pdf(
    html_content: str,
    output_path: Path,
    pdf_config,
) -> None:
    """Convert HTML content to PDF file using wkhtmltopdf.

    Args:
        html_content: HTML content to convert
        output_path: Path where PDF should be saved
        pdf_config: pdfkit configuration object

    Raises:
        IOError: If PDF file cannot be written
        OSError: If system error occurs
        PermissionError: If insufficient permissions
        Exception: For other pdfkit/wkhtmltopdf errors
    """
    try:
        pdfkit.from_string(
            html_content,
            str(output_path),
            configuration=pdf_config,
            options=config.PDF_OPTIONS,
        )
    except (IOError, OSError, PermissionError) as e:
        print(f"Error writing PDF file: {e}", file=sys.stderr)
        print(
            "Check that you have write permissions for the output directory.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        print("\nTroubleshooting tips:", file=sys.stderr)
        print(
            "1. Try using a simpler output filename without special characters",
            file=sys.stderr,
        )
        print(
            "2. Ensure wkhtmltopdf is properly installed and accessible",
            file=sys.stderr,
        )
        print(
            "3. Try removing images or complex formatting from the markdown",
            file=sys.stderr,
        )
        sys.exit(1)