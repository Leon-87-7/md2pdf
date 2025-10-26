#! /usr/bin/env python3

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import markdown
import pdfkit

__version__ = "0.1.0"


def find_wkhtmltopdf() -> Optional[str]:
    """Auto-detect wkhtmltopdf installation path across different platforms.

    Returns:
        Path to wkhtmltopdf executable if found, None otherwise.
    """
    # First, check if wkhtmltopdf is in PATH
    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if wkhtmltopdf_path:
        return wkhtmltopdf_path

    # Define common installation paths by platform
    system = platform.system()
    common_paths = []

    if system == "Windows":
        common_paths = [
            "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
            "C:/Program Files (x86)/wkhtmltopdf/bin/wkhtmltopdf.exe",
            Path.home() / "AppData/Local/Programs/wkhtmltopdf/bin/wkhtmltopdf.exe",
        ]
    elif system == "Darwin":  # macOS
        common_paths = [
            "/usr/local/bin/wkhtmltopdf",
            "/opt/homebrew/bin/wkhtmltopdf",
            "/usr/bin/wkhtmltopdf",
        ]
    elif system == "Linux":
        common_paths = [
            "/usr/bin/wkhtmltopdf",
            "/usr/local/bin/wkhtmltopdf",
            "/bin/wkhtmltopdf",
        ]

    # Check each common path
    for path in common_paths:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_file():
            return str(path_obj)

    return None


def _get_themes_directory() -> Path:
    """Get the path to the themes directory.

    Returns:
        Path to the themes directory (same location as this script).
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    return script_dir / "themes"


def _list_available_themes() -> list[str]:
    """List all available theme names.

    Returns:
        List of theme names (without .css extension).
    """
    themes_dir = _get_themes_directory()
    if not themes_dir.exists():
        return []

    # Get all .css files and remove extension
    return [f.stem for f in themes_dir.glob("*.css")]


def process_page_breaks(html_content: str) -> str:
    """Process HTML comments for page breaks and convert them to CSS page breaks.

    Supports the following markdown comment syntaxes:
    - <!-- pagebreak -->
    - <!-- page-break -->
    - <!-- PAGEBREAK -->
    - <!-- PAGE-BREAK -->

    Args:
        html_content: HTML content to process

    Returns:
        HTML content with page break comments replaced by div elements
    """
    # Pattern matches HTML comments with various page break formats (case-insensitive)
    pattern = r"<!--\s*page[-_\s]*break\s*-->"
    replacement = '<div class="page-break"></div>'
    return re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)


def open_pdf(pdf_path: Path) -> None:
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
            print(f"Warning: Unable to open PDF on {system} platform", file=sys.stderr)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Warning: Could not open PDF: {e}", file=sys.stderr)


def _print_wkhtmltopdf_installation_instructions() -> None:
    """Print platform-specific installation instructions for wkhtmltopdf."""
    print("Error: wkhtmltopdf not found.", file=sys.stderr)
    print(
        "\nwkhtmltopdf is required for PDF generation but was not found on your system.",
        file=sys.stderr,
    )
    print("\nInstallation instructions:", file=sys.stderr)

    system = platform.system()
    if system == "Windows":
        print(
            "  - Download from: https://wkhtmltopdf.org/downloads.html", file=sys.stderr
        )
        print(
            "  - Install to default location (C:/Program Files/wkhtmltopdf/)",
            file=sys.stderr,
        )
        print("  - Or add wkhtmltopdf to your system PATH", file=sys.stderr)
    elif system == "Darwin":
        print("  - Install via Homebrew: brew install wkhtmltopdf", file=sys.stderr)
        print(
            "  - Or download from: https://wkhtmltopdf.org/downloads.html",
            file=sys.stderr,
        )
    elif system == "Linux":
        print("  - Ubuntu/Debian: sudo apt-get install wkhtmltopdf", file=sys.stderr)
        print("  - Fedora: sudo dnf install wkhtmltopdf", file=sys.stderr)
        print(
            "  - Or download from: https://wkhtmltopdf.org/downloads.html",
            file=sys.stderr,
        )
    else:
        print(
            "  - Download from: https://wkhtmltopdf.org/downloads.html", file=sys.stderr
        )


def _validate_input_file(input_file: str) -> Path:
    """Validate the input markdown file.

    Args:
        input_file: Path to the input markdown file

    Returns:
        Validated Path object

    Raises:
        SystemExit: If validation fails
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # Optional: Validate extension (warn, don't error)
    if input_path.suffix.lower() not in [".md", ".markdown", ".txt"]:
        print(
            f"Warning: '{input_file}' does not have a markdown extension (.md, .markdown)",
            file=sys.stderr,
        )

    # Check readability
    if not os.access(input_path, os.R_OK):
        print(f"Error: No read permission for '{input_file}'.", file=sys.stderr)
        sys.exit(1)

    return input_path


def _load_css(custom_css: Optional[str] = None, theme: str = "default") -> str:
    """Load CSS content from custom file, theme, or default.

    Args:
        custom_css: Path to custom CSS file, or None to use theme
        theme: Theme name to use (default: "default")

    Returns:
        CSS content as string

    Raises:
        SystemExit: If CSS file is invalid or unreadable
    """
    # --css flag takes precedence over --theme
    if custom_css:
        css_path = Path(custom_css).resolve()

        # Validate it's a file and exists
        if not css_path.exists():
            print(f"Error: CSS file '{custom_css}' does not exist.", file=sys.stderr)
            sys.exit(1)

        if not css_path.is_file():
            print(f"Error: CSS file '{custom_css}' is not a file.", file=sys.stderr)
            sys.exit(1)

        # Warn if extension is not .css
        if css_path.suffix.lower() != ".css":
            print(
                f"Warning: '{custom_css}' does not have .css extension", file=sys.stderr
            )

        try:
            with open(css_path, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, PermissionError, UnicodeDecodeError) as e:
            print(f"Error reading CSS file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Load from themes directory
        themes_dir = _get_themes_directory()
        theme_path = themes_dir / f"{theme}.css"

        if not theme_path.exists():
            available_themes = _list_available_themes()
            print(f"Error: Theme '{theme}' not found.", file=sys.stderr)
            if available_themes:
                print(f"Available themes: {', '.join(available_themes)}", file=sys.stderr)
            else:
                print("No themes found in themes directory.", file=sys.stderr)
            sys.exit(1)

        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, PermissionError, UnicodeDecodeError) as e:
            print(f"Error reading theme file: {e}", file=sys.stderr)
            sys.exit(1)


def convert_md_to_pdf(
    input_file: str,
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:
    """Convert a Markdown file to PDF.

    Args:
        input_file: Path to the input Markdown file
        output_file: Path to the output PDF file (optional, defaults to input name with .pdf)
        custom_css: Path to a custom CSS file (optional, takes precedence over theme)
        theme: Theme name to use (default: "default", ignored if custom_css is provided)
        preview: Whether to open the PDF after generation (default: False)

    Raises:
        SystemExit: If conversion fails or dependencies are missing
    """
    # Warn if both custom_css and theme are specified
    if custom_css and theme != "default":
        print(
            f"Warning: Both --css and --theme specified. Using custom CSS file, ignoring theme '{theme}'.",
            file=sys.stderr,
        )
    # Find and configure wkhtmltopdf when needed (lazy initialization)
    wkhtmltopdf_path = find_wkhtmltopdf()

    if wkhtmltopdf_path is None:
        _print_wkhtmltopdf_installation_instructions()
        sys.exit(1)

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Validate input file
    input_path = _validate_input_file(input_file)

    # Determine output file path
    if output_file is None:
        output_path = input_path.with_suffix(".pdf")
    else:
        output_path = Path(output_file)

    # Read markdown content
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except (IOError, PermissionError, UnicodeDecodeError) as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content, extensions=["extra", "codehilite", "tables", "toc"]
    )

    # Process page breaks
    html_content = process_page_breaks(html_content)

    # Load CSS (custom, theme, or default)
    css_content = _load_css(custom_css, theme)

    # Wrap in basic HTML content with embedded CSS
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{input_path.stem}</title>
        <style>
            {css_content}
        </style>
    </head>
    <body>
       {html_content}
    </body>
    </html>
    """

    # Convert HTML to PDF with configuration
    try:
        # Configure pdfkit options for better compatibility
        options = {"enable-local-file-access": None, "encoding": "UTF-8", "quiet": ""}
        pdfkit.from_string(
            full_html, str(output_path), configuration=config, options=options
        )
        print(f"Successfully converted '{input_file}' to '{output_path}'")

        # Open PDF in preview mode if requested
        if preview:
            open_pdf(output_path)

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


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF with custom styles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  md2pdf document.md                                    # Use default theme
  md2pdf input.md -o output.pdf                        # Specify output file
  md2pdf notes.md --theme dark                         # Use dark theme
  md2pdf notes.md --theme minimal                      # Use minimal theme
  md2pdf notes.md --css custom-style.css               # Use custom CSS file
  md2pdf report.md --theme dark -p                     # Use dark theme and preview
  md2pdf report.md --theme minimal --css custom.css    # CSS takes precedence (with warning)
  """,
    )
    parser.add_argument("input", help="Path to the input Markdown file.")
    parser.add_argument(
        "-o", "--output", help="Output PDF file (default: same name as input)"
    )
    parser.add_argument(
        "--theme",
        default="default",
        help="Theme to use for styling (default: default). Ignored if --css is specified.",
    )
    parser.add_argument(
        "--css",
        help="Path to a custom CSS file for styling the PDF. Takes precedence over --theme.",
    )
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        help="Open the PDF with the default viewer after conversion",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"md2pdf {__version__}"
    )

    args = parser.parse_args()

    convert_md_to_pdf(args.input, args.output, args.css, args.theme, args.preview)


if __name__ == "__main__":
    main()
