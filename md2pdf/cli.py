"""Command-line interface for md2pdf."""

import argparse
import sys

from . import config
from .core import convert_batch, convert_md_to_pdf, convert_merge
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
  # Single file conversion
  md2pdf document.md                                   # Use default theme
  md2pdf input.md -o output.pdf                        # Specify output file name
  md2pdf report.md --css custom-style.css              # Use custom CSS file
  md2pdf report.md --theme dark -p                     # Use dark theme and preview

  # Batch conversion (multiple files)
  md2pdf file1.md file2.md file3.md                    # Convert multiple files
  md2pdf *.md --output-dir pdfs                        # Convert all .md files to pdfs/ directory

  # Merge mode (combine multiple files into one PDF)
  md2pdf file1.md file2.md --merge -o combined.pdf     # Merge files into one PDF
  md2pdf *.md --merge --no-auto-break                  # Merge without page breaks

  # Theme management
  md2pdf --theme-list                                  # List all available themes
  """,
    )
    parser.add_argument(
        "input",
        nargs="*",
        help="Path to input Markdown file(s). Multiple files triggers batch mode.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file name (single file mode only, default: same name as input)",
    )
    parser.add_argument(
        "--output-dir",
        "-od",
        help="Output directory for batch mode (default: same directory as each input file)",
    )
    parser.add_argument(
        "--theme",
        "-th",
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
        "-c",
        help="Path to a custom CSS file for styling the PDF. Takes precedence over --theme.",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Open the PDF with the default viewer after conversion",
    )
    parser.add_argument(
        "--merge",
        "-m",
        action="store_true",
        help="Merge multiple input files into a single PDF (requires 2+ files)",
    )
    parser.add_argument(
        "--no-auto-break",
        "-nab",
        action="store_true",
        help="Disable automatic page breaks between merged documents (merge mode only)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"md2pdf {config.__version__}"
    )

    args = parser.parse_args()

    # Handle --theme-list flag
    if args.theme_list:
        display_themes()
        return

    # Require input file(s) if not listing themes
    if not args.input:
        parser.error("the following arguments are required: input")

    try:
        # Determine conversion mode
        if args.merge:
            # Merge mode: combine multiple files into one PDF
            if len(args.input) < 2:
                print(
                    "Error: Merge mode requires at least 2 input files.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if args.output_dir:
                print(
                    "Warning: --output-dir flag is ignored in merge mode. Use --output instead.",
                    file=sys.stderr,
                )
            auto_break = not args.no_auto_break
            convert_merge(
                args.input, args.output, args.css, args.theme, auto_break, args.preview
            )
        elif len(args.input) > 1:
            # Batch mode: convert multiple files to separate PDFs
            if args.output:
                print(
                    "Warning: --output flag is ignored in batch mode. Use --output-dir instead.",
                    file=sys.stderr,
                )
            if args.no_auto_break:
                print(
                    "Warning: --no-auto-break flag is only valid in merge mode.",
                    file=sys.stderr,
                )
            convert_batch(
                args.input, args.output_dir, args.css, args.theme, args.preview
            )
        else:
            # Single file mode
            if args.output_dir:
                print(
                    "Warning: --output-dir flag is ignored in single file mode. Use --output instead.",
                    file=sys.stderr,
                )
            if args.no_auto_break:
                print(
                    "Warning: --no-auto-break flag is only valid in merge mode.",
                    file=sys.stderr,
                )
            convert_md_to_pdf(
                args.input[0], args.output, args.css, args.theme, args.preview
            )
    except Md2PdfError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
