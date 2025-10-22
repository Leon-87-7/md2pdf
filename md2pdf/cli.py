"""Command-line interface for md2pdf."""

import argparse

from . import config
from .core import convert_md_to_pdf


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
        "-v", "--version", action="version", version=f"md2pdf {config.__version__}"
    )

    args = parser.parse_args()

    convert_md_to_pdf(args.input, args.output, args.css, args.theme, args.preview)


if __name__ == "__main__":
    main()
