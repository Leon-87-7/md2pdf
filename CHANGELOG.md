# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2025-10-24

### Added

- **Comprehensive test suite expansion** - 74 new tests added (154 → 228 total tests)
  - New `test_theme_builder.py` with 40 tests for theme validation and CSS generation
  - 26 new tests in `test_core.py` for batch and merge conversion modes
  - 11 new security tests in `test_file_operations.py` for path traversal protection
  - Test coverage improved from 15% to 76% (+61% improvement)
  - Individual module improvements:
    - `core.py`: 9% → 98% (+89%)
    - `file_operations.py`: 19% → 80% (+61%)
    - `theme_builder.py`: 0% → 33% (+33%)
    - `pdf_engine.py`: 27% → 100% (+73%)
    - `markdown_processor.py`: 54% → 100% (+46%)
    - `color_utils.py`: 12% → 95% (+83%)
    - `theme_manager.py`: 24% → 89% (+65%)
    - `cli.py`: 14% → 67% (+53%)
    - `exceptions.py`: 67% → 100% (+33%)
    - `config.py`: 100% → 100%
    - `__init__.py`: 100% → 100%

### Fixed

- **Enhanced path traversal protection** in `file_operations.py`
  - Added 4-step validation process with comprehensive security checks
  - Step 1: Check for explicit ".." components in path
  - Step 2: Resolve to absolute path with symlink resolution
  - Step 3: Validate relative paths stay within current working directory
  - Step 4: Detect symlinks and validate their targets
  - Prevents attacks: `../../etc/passwd`, symlink traversal, mixed attacks
  - Improved error messages with specific guidance and resolved paths
  - Builds on Phase 1 security fixes (commit d283be5)

### Changed

- **Improved error handling** in `core.py`
  - Split exception handling into `Md2PdfError` vs system errors (`OSError`, `IOError`)
  - Added specific error handling for directory creation failures
  - Better error messages distinguishing app errors from system errors
  - Added comment explaining `exist_ok=True` for race condition handling

### Improved

- **Enhanced wkhtmltopdf error messages** in `pdf_engine.py`
  - Added 6 comprehensive troubleshooting tips for common issues
  - Permission check instructions
  - Windows path/space handling guidance (critical for Windows users)
  - wkhtmltopdf version verification command
  - Update recommendations
  - Output directory validation
  - Complex content debugging tips
  - Added type hints for `PdfKitConfig` (pdfkit lacks type stubs)

- **Better path configuration** in `config.py`
  - Clarified `PACKAGE_DIR` comment (package dir, not project root)
  - Added `THEMES_DIR` constant for better path management
  - Improved code documentation

- **Code quality improvements** in `theme_manager.py`
  - Updated to use `config.THEMES_DIR` instead of manual path construction
  - Better separation of concerns

### Documentation

- Updated CLAUDE.md to reflect v0.3.1 and current state
  - Version references updated: 0.3.0 → 0.3.1
  - Test coverage updated to 76% (from initial 15%)
  - Added accurate test count: 228 tests across 9 test modules

### Security

- Phase 2 security enhancements with symlink detection and validation
- Comprehensive security test suite (11 dedicated tests)
- Path traversal protection hardened against edge cases
- No breaking changes - fully backward compatible

### Added

- **Interactive Theme Builder** (`--create-theme`) - Create custom themes through guided CLI wizard
  - **Color utilities module** (`color_utils.py`) with comprehensive color parsing and accessibility:
    - Supports hex (#fff, #ffffff), named colors (white, red), and HSL (hsl(210, 50%, 20%))
    - WCAG contrast ratio calculation following WebAIM standards
    - Automatic contrast checking against WCAG AA (4.5:1) and AAA (7.0:1) compliance
    - Smart color adjustment functions (darken/lighten by percentage)
    - Accessible color suggestions to meet target contrast ratios
    - 32 comprehensive tests with 94% code coverage
  - **Theme builder module** (`theme_builder.py`) with interactive wizard:
    - Guided prompts for 10 theme properties (name, colors, fonts, sizes)
    - Real-time contrast validation with warnings for low-contrast combinations
    - Smart defaults for all inputs - press Enter to accept defaults
    - Separate color controls for H1 vs H2-H6 headings
    - Automatic theme name validation and conflict detection
    - Generates complete CSS with all required selectors
    - Beautiful terminal UI with checkmarks (✓) and warnings (⚠)
  - **CLI integration**: `--create-theme` flag launches wizard, exits after creation
  - **Accessibility-first design**: All generated themes meet WCAG AA standards (4.5:1 minimum)
  - Works seamlessly with all conversion modes (single, batch, merge)

### Fixed

- CLI argument name corrected from `args.output` to `args.output_name` to match actual argument definition
  - Changed argument from `-o/--output` to `-on/--output-name` for consistency
  - Updated all code references in merge mode conversion
  - Fixed AttributeError that occurred when using merge mode
- Warning messages updated to reference correct `--output-name` flag instead of `--output`
  - Batch mode now suggests `--output-dir` instead of incorrect `--output`
  - Single file mode warnings now reference `--output-name` correctly
- Fixed 3 pre-existing CLI test failures that used old flag names (`-o`/`--output`)

### Changed

- CLI argument definitions reorganized with short flags listed before long flags for consistency
- Help text examples updated to use `-on` instead of `-o` for output file specification
- Test suite expanded from 116 to 148 tests (added 32 color utility tests)
- Package now includes 11 modules (added color_utils.py and theme_builder.py)

### Documentation

- Updated CLAUDE.md to reflect current modular architecture
  - Replaced outdated "single-file application" description with accurate modular package structure
  - Added package structure diagram showing 9 specialized modules
  - Documented all three conversion modes: single, batch, and merge
  - Added comprehensive development commands including testing (148 tests)
  - Updated CLI argument documentation with correct flags (`-on`, `-od`, `-m`, `--create-theme`)

## [0.3.0] - 2025-10-23

### Added

- **Batch processing mode** - Convert multiple Markdown files to separate PDFs in one command
  - Automatic detection when multiple input files are provided
  - `--output-dir` flag to specify output directory for batch conversions
  - Efficient processing with shared setup (PDF engine and CSS loaded once)
  - Progress tracking with [OK]/[FAILED] status for each file
  - Comprehensive summary showing total, successful, and failed conversions
  - Graceful error handling - continues processing remaining files if one fails
- **Merge mode** - Combine multiple Markdown files into a single PDF
  - `--merge` flag to enable merge mode
  - Automatic page breaks between merged sections (default behavior)
  - `--no-auto-break` flag to disable page breaks between sections
  - Section headers showing source filenames for each merged document
  - Validates minimum of 2 files required for merge mode
  - Support for custom output filename with `-o` flag
  - Processing summary showing successful and failed files
- **Shared helper functions** in core module for code reuse
  - `_setup_conversion_environment()` - Setup PDF engine and CSS once for efficiency
  - `_process_single_file()` - Read and process a single markdown file to HTML
  - `_merge_html_bodies()` - Merge multiple HTML bodies with optional page breaks
- Enhanced CLI mode detection logic
  - Single file mode: `md2pdf file.md`
  - Batch mode: `md2pdf file1.md file2.md` (multiple files, no --merge)
  - Merge mode: `md2pdf file1.md file2.md --merge`
- Helpful warnings when incompatible flags are used
  - Warns if `--output` is used in batch mode (suggests `--output-dir`)
  - Warns if `--output-dir` is used in single/merge mode (suggests `--output`)
  - Warns if `--no-auto-break` is used outside merge mode

### Changed

- CLI now accepts multiple input files via `nargs="*"` instead of single file
  - Allows --theme-list to work without requiring input files
  - Multiple files automatically trigger batch mode (unless --merge is specified)
- Updated help text and examples to document batch and merge modes
- Improved error messages for better user guidance
- Modified print output to use `[OK]` and `[FAILED]` prefixes (Windows console compatible)

### Documentation

- Updated README with batch processing and merge mode sections
- Added Examples 8 and 9 for batch and merge workflows
- Updated command-line options documentation
- Marked Priority 5 (Batch Processing) and Priority 6 (Merge Mode) as completed

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
  - 116 tests across 7 test modules (including test_core.py)
  - 69% code coverage with all existing functionality fully tested
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

[unreleased]: https://github.com/leon-87-7/md2pdf/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/leon-87-7/md2pdf/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/leon-87-7/md2pdf/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/leon-87-7/md2pdf/compare/v0.1.0...v0.2.1
[0.1.0]: https://github.com/leon-87-7/md2pdf/releases/tag/v0.1.0
