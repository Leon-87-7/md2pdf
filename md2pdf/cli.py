"""Command-line interface for md2pdf."""

import argparse
import sys

from . import config
from .core import convert_md_to_pdf
from .exceptions import Md2PdfError
from .theme_manager import list_available_themes


def display_themes() -> None:
    """Display all available themes and exit."""
    themes = list_available_themes()

    if not themes:
        print(
            "No themes found. \nPlease make sure the themes are installed correctly.\nLook in the 'themes' directory."
        )
        return

    print("Available themes:")
    for theme in sorted(themes):
        print(f"  - {theme}")
    print("\nUsage: md2pdf document.md --theme <theme-name>")


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF with custom styles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  md2pdf document.md                                   # Use default theme
  md2pdf input.md -o output.pdf                        # Specify output file
  md2pdf --theme-list                                  # List all available themes
  md2pdf report.md --theme dark                        # Use dark theme
  md2pdf report.md --theme minimal                     # Use minimal theme
  md2pdf report.md --css custom-style.css              # Use custom CSS file
  md2pdf report.md --theme dark -p                     # Use dark theme and preview
  md2pdf report.md --theme minimal --css custom.css    # CSS takes precedence (with warning)
  """,
    )
    parser.add_argument("input", nargs="?", help="Path to the input Markdown file.")
    parser.add_argument(
        "-o", "--output", help="Output PDF file (default: same name as input)"
    )
    parser.add_argument(
        "--theme",
        default="default",
        help="Theme to use for styling (default: default). Ignored if --css is specified.",
    )
    parser.add_argument(
        "--theme-list",
        "-thl",
        action="store_true",
        help="List all available themes and exit",
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
        "-v", "--version", action="version", version=f"md2pdf {config.__version__}"
    )

    args = parser.parse_args()

    # Handle --theme-list flag
    if args.theme_list:
        display_themes()
        return

    # Require input file if not listing themes
    if not args.input:
        parser.error("the following arguments are required: input")

    try:
        convert_md_to_pdf(args.input, args.output, args.css, args.theme, args.preview)
    except Md2PdfError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
