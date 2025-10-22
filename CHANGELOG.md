# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Theme system for flexible PDF styling
  - `--theme` CLI argument for selecting predefined themes
  - `_get_themes_directory()` function to locate theme files
  - `_list_available_themes()` function to discover available themes
  - Support for external CSS theme files in `themes/` directory
- Comprehensive test suite (`test_refactor.py`) with coverage for:
  - wkhtmltopdf detection across platforms
  - Page break processing with multiple comment formats
  - CSS loading from themes and custom files
  - Input validation and error handling
  - Basic markdown to PDF conversion
- Educational documentation (`docs/LEARNING_GUIDE.md`) covering:
  - Module structure and modern Python patterns
  - Auto-detection algorithms and cross-platform compatibility
  - Theme system architecture
  - Regular expressions and validation patterns
  - CLI design with argparse
  - Practical exercises and best practices
- Comprehensive type hints throughout the codebase
- Dynamic version extraction in `setup.py` for single source of truth
- Claude Code agent configurations and artifacts for AI-assisted development
- Smart commit slash command from claude-code-templates
- Project documentation image in README

### Changed

- **BREAKING**: Removed hardcoded CSS from `get_default_css()` function
  - CSS now loaded from external theme files via `_load_css()`
  - Custom CSS takes precedence over themes with warning message
- Refactored wkhtmltopdf detection to use lazy initialization
  - No longer initialized at module import time
  - Configured only when needed during conversion
- Improved error handling with specific exception types:
  - `IOError`, `PermissionError`, `UnicodeDecodeError` for file operations
  - `OSError`, `subprocess.CalledProcessError` for system operations
- Enhanced input validation with dedicated `_validate_input_file()` function
  - File existence and type checking
  - Permission verification with `os.access()`
  - Extension validation with warnings for non-markdown files
- Better code organization with private helper functions (prefixed with `_`)
- Improved docstrings following consistent format with type information
- Updated CLI help text with theme examples
- CSS styling improvements for better PDF rendering

### Fixed

- Version consistency between `setup.py` and source code
- Error messages now include troubleshooting tips for common issues

## [0.1.0] - 2025-10-20

### Added

- Initial release of md2pdf CLI tool
- Markdown to PDF conversion with professional styling
- Cross-platform wkhtmltopdf auto-detection for Windows, macOS, and Linux
- Custom CSS support for personalized PDF styling
- Preview mode (`-p`/`--preview`) to automatically open generated PDFs
- Explicit page break support via HTML comments:
  - `<!-- pagebreak -->`
  - `<!-- page-break -->`
  - Case-insensitive variants supported
- Default gradient-based CSS theme with:
  - Purple/blue gradient backgrounds
  - Semi-transparent white content boxes
  - Professional typography using Segoe UI font family
  - Syntax highlighting for code blocks
  - A4 page size with 2cm margins
- Markdown extension support:
  - Tables
  - Code highlighting
  - Table of contents
  - Extra features (footnotes, definition lists, etc.)

### Fixed

- Text size rendering issues in generated PDFs
- Error handling improvements for missing wkhtmltopdf installations
- Better error messages with platform-specific installation instructions

### Documentation

- Comprehensive README with usage examples
- Installation instructions for all platforms
- Custom CSS styling guide
- Future features roadmap
- CLAUDE.md for AI development assistance

[unreleased]: https://github.com/yourusername/md2pdf/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/md2pdf/releases/tag/v0.1.0
