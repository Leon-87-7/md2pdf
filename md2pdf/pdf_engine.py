"""PDF generation engine using wkhtmltopdf."""

import platform
import shutil
from pathlib import Path
from typing import Optional

import pdfkit

from . import config
from .exceptions import ConversionError


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


def create_pdf_configuration(wkhtmltopdf_path: str) -> pdfkit.configuration:
    """Create pdfkit configuration object.

    Args:
        wkhtmltopdf_path: Path to wkhtmltopdf executable

    Returns:
        pdfkit.configuration object
    """
    return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


def get_installation_instructions() -> str:
    """Get platform-specific installation instructions for wkhtmltopdf.

    Returns:
        Formatted installation instructions as a string
    """
    system = platform.system()
    instructions = config.INSTALLATION_INSTRUCTIONS.get(
        system, config.INSTALLATION_INSTRUCTIONS["default"]
    )

    lines = [
        "wkhtmltopdf is required for PDF generation but was not found on your system.",
        "",
        "Installation instructions:",
    ]
    lines.extend(instructions)

    return "\n".join(lines)


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
        ConversionError: If PDF conversion fails for any reason
    """
    try:
        pdfkit.from_string(
            html_content,
            str(output_path),
            configuration=pdf_config,
            options=config.PDF_OPTIONS,
        )
    except (IOError, OSError, PermissionError) as e:
        error_msg = f"Error writing PDF file: {e}\n"
        error_msg += "Check that you have write permissions for the output directory."
        raise ConversionError(error_msg) from e
    except Exception as e:
        error_msg = f"Error generating PDF: {e}\n\n"
        error_msg += "Troubleshooting tips:\n"
        error_msg += "1. Try using a simpler output filename without special characters\n"
        error_msg += "2. Ensure wkhtmltopdf is properly installed and accessible\n"
        error_msg += "3. Try removing images or complex formatting from the markdown"
        raise ConversionError(error_msg) from e