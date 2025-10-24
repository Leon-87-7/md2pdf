# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**md2pdf** is a Python CLI tool that converts Markdown files to professionally-styled PDF documents. Version 0.3.0 features a modular architecture with clean separation of concerns, supporting single-file conversion, batch processing, and merge mode with 5 pre-built themes.

## Architecture

### Package Structure

The project uses a modular architecture with specialized modules:

```
md2pdf/
├── md2pdf/                    # Main package
│   ├── cli.py                # CLI interface (argparse)
│   ├── core.py               # Conversion orchestrator (3 modes: single, batch, merge)
│   ├── config.py             # Configuration & constants (version: 0.3.0)
│   ├── markdown_processor.py # Markdown → HTML conversion
│   ├── pdf_engine.py         # PDF generation (wkhtmltopdf wrapper)
│   ├── theme_manager.py      # Theme & CSS loading
│   ├── theme_builder.py      # Theme customization utilities
│   ├── color_utils.py        # Color manipulation for themes
│   ├── file_operations.py    # File I/O operations
│   └── exceptions.py         # Custom exception classes
├── themes/                    # CSS theme files (5 themes)
├── tests/                     # Pytest test suite (8 test modules, 54% coverage)
└── docs/                      # Architecture and testing documentation
```

### Core Modules

**[cli.py](md2pdf/cli.py)**: Argument parsing with support for:
- Single file: `-on/--output-name` for output file
- Batch mode: `-od/--output-dir` for output directory
- Merge mode: `-m/--merge` to combine files, `-nab/--no-auto-break` to disable page breaks
- Themes: `-th/--theme` to select theme, `-thl/--theme-list` to list themes
- Preview: `-p/--preview` to auto-open PDF

**[core.py](md2pdf/core.py)**: Main orchestrator with three conversion functions:
- `convert_md_to_pdf()`: Single file conversion
- `convert_batch()`: Multiple files → separate PDFs
- `convert_merge()`: Multiple files → single merged PDF

**[pdf_engine.py](md2pdf/pdf_engine.py)**: wkhtmltopdf wrapper
- `find_wkhtmltopdf()`: Auto-detect installation across platforms
- Checks system PATH and common installation paths for Windows, macOS, Linux

**[theme_manager.py](md2pdf/theme_manager.py)**: Theme system
- Themes stored in `themes/` directory as CSS files
- `list_available_themes()`: Returns list of theme names
- Custom CSS takes precedence over themes

**[theme_builder.py](md2pdf/theme_builder.py)**: Theme customization utilities
- Programmatic theme generation and customization
- Color scheme manipulation

**[color_utils.py](md2pdf/color_utils.py)**: Color manipulation utilities
- Color format conversion and manipulation
- Support for theme color schemes

### Dependencies

- **wkhtmltopdf**: External system dependency (auto-detected at runtime)
- **Python packages**: `markdown>=3.4`, `pdfkit>=1.0.0`

## Development Commands

### Installation

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install dependencies manually
pip install -r requirements.txt
```

### Running the Tool

```bash
# Single file conversion
md2pdf input.md
md2pdf input.md -on output.pdf
md2pdf input.md --theme dark -p

# Batch processing
md2pdf file1.md file2.md file3.md
md2pdf *.md --output-dir pdfs/

# Merge mode
md2pdf ch1.md ch2.md ch3.md --merge -on book.pdf
md2pdf *.md --merge --no-auto-break -on combined.pdf

# Theme management
md2pdf --theme-list
```

### Testing

The project has a comprehensive test suite across 8 test modules:

```bash
# Run full test suite
pytest

# Run with coverage report (currently 54% coverage)
pytest --cov=md2pdf --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py

# Run verbose
pytest -v
```

**Test modules:**
- `test_cli.py`: CLI argument parsing and command execution
- `test_color_utils.py`: Color manipulation utilities
- `test_config.py`: Configuration and constants
- `test_core.py`: Core conversion logic (single, batch, merge modes)
- `test_file_operations.py`: File I/O operations
- `test_markdown_processor.py`: Markdown to HTML conversion
- `test_pdf_engine.py`: PDF generation and wkhtmltopdf integration
- `test_theme_manager.py`: Theme loading and management

## wkhtmltopdf Installation

The tool automatically detects wkhtmltopdf installations across platforms. If not found, it provides platform-specific installation instructions:

- **Windows**: Download from https://wkhtmltopdf.org/downloads.html and install to default location
- **macOS**: `brew install wkhtmltopdf` or download from the official site
- **Linux**:
  - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
  - Fedora: `sudo dnf install wkhtmltopdf`

The detection checks both the system PATH and common installation locations.

## Styling System

### Available Themes (5 pre-built themes)

The project includes 5 professionally-designed themes in the `themes/` directory:
- **default.css**: Gradient backgrounds (purple/blue), semi-transparent content boxes
- **dark.css**: Dark mode with high contrast
- **light.css**: Clean light theme
- **minimal.css**: Minimalist design
- **professional.css**: Professional business style

### Theme Features

All themes support:
- Professional typography with Segoe UI font family
- Syntax highlighting via `codehilite` markdown extension
- A4 page size with configurable margins
- Responsive styling for all Markdown elements (headings, paragraphs, tables, code blocks, lists, etc.)
- Document section headers in merge mode

### Custom CSS

Custom CSS files should include styles for all HTML elements generated by the markdown parser. Custom CSS takes precedence over pre-built themes when specified.

## Key Features

### Conversion Modes
- **Single file**: Convert one Markdown file to PDF
- **Batch mode**: Convert multiple Markdown files to separate PDFs
- **Merge mode**: Combine multiple Markdown files into a single PDF with optional auto page breaks

### CLI Capabilities
- Auto-detection of wkhtmltopdf across Windows, macOS, and Linux
- Preview mode to auto-open generated PDFs
- Theme selection from 5 pre-built themes
- Custom CSS support for advanced styling
- Flexible output naming and directory options

### Recent Enhancements (v0.3.0)
- Added `theme_builder.py` and `color_utils.py` modules for programmatic theme customization
- Added document section headers in merge mode
- Improved modular architecture with clearer separation of concerns
- Enhanced test coverage across 8 test modules

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md): Detailed architecture documentation
- [TESTING.md](docs/TESTING.md): Testing strategy and guidelines
- Version learning guides available in `docs/` directory

## Git Commit Guidelines

- Never write this in a git commit:
  ```
  🤖 Generated with [Claude Code](https://claude.ai/code)              │
  │
  │   Co-Authored-By: Claude <noreply@anthropic.com>"
  ```
