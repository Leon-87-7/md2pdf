"""Configuration and constants for md2pdf package."""

from pathlib import Path

# Version
__version__ = "0.2.1"

# Paths
THEMES_DIR_NAME = "themes"
PACKAGE_DIR = Path(__file__).parent.parent  # Go up to project root

# Markdown extensions for python-markdown library
MARKDOWN_EXTENSIONS = ["extra", "codehilite", "tables", "toc"]

# PDF generation options for pdfkit/wkhtmltopdf
PDF_OPTIONS = {
    "enable-local-file-access": None,
    "encoding": "UTF-8",
    "quiet": "",
    "page-size": "A4",
    "margin-top": "0mm",
    "margin-right": "0mm",
    "margin-bottom": "0mm",
    "margin-left": "0mm",
    # "disable-smart-shrinking": "",
    "background": "",
}

# Supported markdown file extensions
SUPPORTED_MARKDOWN_EXTENSIONS = [".md", ".markdown", ".txt"]

# wkhtmltopdf common installation paths by platform
WKHTMLTOPDF_PATHS = {
    "Windows": [
        "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
        "C:/Program Files (x86)/wkhtmltopdf/bin/wkhtmltopdf.exe",
        # User-specific path added dynamically in pdf_engine.py
    ],
    "Darwin": [  # macOS
        "/usr/local/bin/wkhtmltopdf",
        "/opt/homebrew/bin/wkhtmltopdf",
        "/usr/bin/wkhtmltopdf",
    ],
    "Linux": [
        "/usr/bin/wkhtmltopdf",
        "/usr/local/bin/wkhtmltopdf",
        "/bin/wkhtmltopdf",
    ],
}

# Installation instructions by platform
INSTALLATION_INSTRUCTIONS = {
    "Windows": [
        "  - Download from: https://wkhtmltopdf.org/downloads.html",
        "  - Install to default location (C:/Program Files/wkhtmltopdf/)",
        "  - Or add wkhtmltopdf to your system PATH",
    ],
    "Darwin": [  # macOS
        "  - Install via Homebrew: brew install wkhtmltopdf",
        "  - Or download from: https://wkhtmltopdf.org/downloads.html",
    ],
    "Linux": [
        "  - Ubuntu/Debian: sudo apt-get install wkhtmltopdf",
        "  - Fedora: sudo dnf install wkhtmltopdf",
        "  - Or download from: https://wkhtmltopdf.org/downloads.html",
    ],
    "default": [
        "  - Download from: https://wkhtmltopdf.org/downloads.html",
    ],
}
