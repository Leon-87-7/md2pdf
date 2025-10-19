#! /usr/bin/env python3

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
import markdown
import pdfkit

config = pdfkit.configuration(
    wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
)


def get_default_css():
    """return default css for pdf rendering"""
    return """
    @page {
        size: A4;
        margin: 2cm;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 18pt;
        line-height: 1.8;
        color: #2c3e50;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        page-break-after: avoid;
    }
    
    h1 {
        font-size: 42pt;
        color: #fff;
        background: linear-gradient(90deg, #667eea, #764ba2);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
    }
    
    h2 {
        font-size: 32pt;
        color: #fff;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        padding: 15px;
        border-radius: 8px;
    }
    
    h3 {
        font-size: 24pt;
        color: #2c3e50;
        background: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 5px;
        font-weight: 600;
    }
    
    h4 {
        font-size: 20pt;
        color: #2c3e50;
        background: rgba(255, 255, 255, 0.85);
        padding: 8px;
        border-radius: 5px;
        font-weight: 600;
    }
    
    p {
        background: rgba(255, 255, 255, 0.95);
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 18pt;
    }
    
    ul, ol {
        background: rgba(255, 255, 255, 0.95);
        padding: 15px 15px 15px 40px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 18pt;
        line-height: 1.7;
    }
    
    li {
        margin: 10px 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        font-size: 16pt;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        overflow: hidden;
    }
    
    th {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 14px;
        text-align: left;
        font-weight: 600;
    }
    
    td {
        padding: 12px;
        border: 1px solid #ddd;
        background: rgba(255, 255, 255, 0.95);
    }
    
    tr:nth-child(even) td {
        background-color: rgba(248, 249, 250, 0.95);
    }
    
    code {
        background: rgba(255, 255, 255, 0.9);
        padding: 4px 8px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 16pt;
        color: #c7254e;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    pre {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ddd;
        border-left: 5px solid #667eea;
        border-radius: 5px;
        padding: 18px;
        overflow-x: auto;
        margin: 15px 0;
        font-size: 15pt;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: #333;
        border: none;
    }
    
    blockquote {
        border-left: 5px solid #667eea;
        padding-left: 2em;
        margin: 15px 0;
        color: #555;
        font-style: italic;
        background: rgba(255, 255, 255, 0.9);
        padding: 18px 18px 18px 2em;
        border-radius: 5px;
    }
    
    a {
        color: #4facfe;
        text-decoration: none;
        font-weight: 500;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe);
        margin: 25px 0;
    }
    
    img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        border: 3px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    """


def open_pdf(pdf_path):
    """Open a PDF file using the default system viewer

    Args:
        pdf_path (Path): path to the PDF file to open
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
    except Exception as e:
        print(f"Warning: Could not open PDF: {e}", file=sys.stderr)


def convert_md_to_pdf(input_file, output_file=None, custom_css=None, preview=False):
    """Convert a md file to pdf

    Args:
        input_file (str): path to the input md file
        output_file (str, optional): path to the output pdf file.
            If None, will use the same name as input file with .pdf extension.
        custom_css (str, optional): path to a custom css file. If None, default css will be used.
        preview (bool, optional): if True, open the PDF after generation. Defaults to False.

    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Determine output file path
    if output_file is None:
        output_path = input_path.with_suffix(".pdf")
    else:
        output_path = Path(output_file)

    # Read markdown content
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content, extensions=["extra", "codehilite", "tables", "toc"]
    )

    # Load custom CSS if provided
    if custom_css and Path(custom_css).exists():
        with open(custom_css, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        css_content = get_default_css()

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
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        print("\nTroubleshooting tips:", file=sys.stderr)
        print(
            "1. Try using a simpler output filename without special characters like emojis",
            file=sys.stderr,
        )
        print("2. Ensure wkhtmltopdf is properly installed", file=sys.stderr)
        print(
            "3. Try removing images or complex formatting from the markdown",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF with custom styles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  md2pdf document.md
  md2pdf input.md -o output.pdf
  md2pdf notes.md --css custom-style.css
  md2pdf report.md -p
  """,
    )
    parser.add_argument("input", help="Path to the input Markdown file.")
    parser.add_argument(
        "-o", "--output", help="Output PDF file (default: same name as input)"
    )
    parser.add_argument("--css", help="Path to a custom CSS file for styling the PDF.")
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        help="Open the PDF with the default viewer after conversion",
    )
    parser.add_argument("-v", "--version", action="version", version="md2pdf 1.0.0")

    args = parser.parse_args()

    convert_md_to_pdf(args.input, args.output, args.css, args.preview)


if __name__ == "__main__":
    main()
