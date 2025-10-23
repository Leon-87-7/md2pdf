# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2025-10-23

### Added

- **Modular package architecture** - Refactored from single file to clean multi-module structure
  - `cli.py` - Command-line interface
  - `core.py` - Conversion orchestrator
  - `config.py` - Configuration and constants
  - `pdf_engine.py` - PDF generation engine
  - `markdown_processor.py` - Markdown to HTML conversion
  - `theme_manager.py` - Theme and CSS management
  - `file_operations.py` - File I/O operations
  - `exceptions.py` - Custom exception hierarchy
- **Custom exception hierarchy** for professional error handling
  - `Md2PdfError` - Base exception for all md2pdf errors
  - `WkhtmltopdfNotFoundError` - Raised when wkhtmltopdf is not found
  - `ConversionError` - Raised when PDF conversion fails
  - `FileOperationError` - Raised when file operations fail
  - `ThemeNotFoundError` - Raised when theme is not found (includes available themes list)
  - `CSSNotFoundError` - Raised when custom CSS file is not found
  - `InvalidInputError` - Raised when input validation fails
  - All exceptions exported in public API for programmatic use
  - Proper exception chaining with `from e` for debugging
- **Theme system** for flexible PDF styling (5 pre-built themes)
  - `default` - Gradient theme with modern styling
  - `dark` - Dark mode theme for reduced eye strain
  - `light` - Clean light theme
  - `minimal` - Ultra-minimal black and white styling
  - `professional` - Business-oriented corporate theme
  - `--theme` CLI argument for selecting themes
  - `--theme-list` / `-thl` flag to list all available themes
  - Support for external CSS theme files in `themes/` directory
  - **Early theme validation** - Validates theme exists before conversion starts
  - Helpful error messages with list of available themes when theme not found
- **Comprehensive test suite** with pytest
  - 116 tests across 7 test modules (including new test_core.py)
  - 94% code coverage (exceeds 85% target)
  - Unit tests for all modules
  - Integration tests for CLI and core orchestrator
  - Proper mocking of external dependencies
  - Test fixtures for markdown and CSS files
  - Comprehensive error path testing for all exception types
  - Tests verify exception handling throughout the stack
- **Testing documentation** (`docs/TESTING.md`)
  - How to run tests and generate coverage reports
  - Writing new tests and best practices
  - Mocking strategies and CI/CD integration
- **Architecture documentation** (`docs/ARCHITECTURE.md`)
  - Module responsibilities and data flow
  - Design principles and benefits
  - Testing strategy and future extensions
- **Educational documentation** (`docs/LEARNING_GUIDE.md`)
  - Module structure and modern Python patterns
  - Auto-detection algorithms and cross-platform compatibility
  - Theme system architecture
  - Regular expressions and validation patterns
  - CLI design with argparse
- Additional themes with improved CSS
  - Fixed margin handling for consistent layout
  - Page break spacing improvements
  - Better typography and readability
- Project metadata improvements
  - Python 3.9+ requirement
  - pytest configuration in pyproject.toml
  - Development dependencies (pytest, pytest-cov, pytest-mock)
- Comprehensive type hints throughout the codebase
- Claude Code agent configurations for AI-assisted development
- Project documentation image in README
- **MIT License** for open source distribution

### Changed

- **BREAKING**: Refactored from single-file to modular package structure
  - Import path remains the same: `from md2pdf import convert_md_to_pdf`
  - CLI usage remains the same: `md2pdf document.md`
- **BREAKING**: Minimum Python version raised from 3.6 to 3.9
- **BREAKING**: Removed hardcoded CSS from monolithic structure
  - CSS now loaded from external theme files in `themes/` directory
  - Custom CSS takes precedence over themes with warning message
- Refactored wkhtmltopdf detection to use lazy initialization
  - No longer initialized at module import time
  - Configured only when needed during conversion
- **BREAKING**: Improved error handling with custom exception hierarchy
  - Replaced all `sys.exit()` calls in library code with exceptions
  - Library functions now raise exceptions, CLI handles system exit
  - Better separation between library and CLI concerns
  - Exceptions include helpful troubleshooting tips and context
  - `IOError`, `PermissionError`, `UnicodeDecodeError` for file operations
  - `OSError`, `subprocess.CalledProcessError` wrapped in ConversionError
- Enhanced input validation
  - File existence and type checking
  - Permission verification with `os.access()`
  - Extension validation with warnings for non-markdown files
- Better code organization with clear separation of concerns
- Improved docstrings following consistent format with type information
- Updated CLI help text with theme examples and --theme-list flag
- CSS styling improvements for all themes
  - Fixed @page margins (set to 0, padding on body instead)
  - Improved page break margins (2cm spacing)
  - Better formatting and readability

### Fixed

- Version consistency throughout the codebase (synced to 0.2.1 in pyproject.toml)
- Error messages now include troubleshooting tips for common issues
- Input argument handling (now optional when using --theme-list)
- Theme CSS margin and padding for proper PDF layout
- Missing return type hint in `create_pdf_configuration()` function
- Inappropriate use of `sys.exit()` in library code (now uses exceptions)
- Missing test coverage for core orchestrator module
- Theme validation now happens early before conversion starts
- CLI error handling now properly catches and displays all Md2PdfError exceptions

### Removed

- Old `test_refactor.py` (replaced by comprehensive pytest suite)

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

[unreleased]: https://github.com/leon-87-7/md2pdf/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/leon-87-7/md2pdf/compare/v0.1.0...v0.2.1
[0.1.0]: https://github.com/leon-87-7/md2pdf/releases/tag/v0.1.0
