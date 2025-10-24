# md2pdf Architecture

## Overview

md2pdf has been refactored into a **modular, multi-file package** with clear separation of concerns. Each module has a single, well-defined responsibility.

## Package Structure

```
md2pdf/
├── md2pdf/                    # Main package directory
│   ├── __init__.py           # Package interface & exports
│   ├── __main__.py           # Module entry point (python -m md2pdf)
│   ├── cli.py                # Command-line interface
│   ├── color_utils.py        # Color parsing & accessibility (NEW)
│   ├── config.py             # Configuration & constants
│   ├── core.py               # Conversion orchestrator
│   ├── exceptions.py         # Custom exception hierarchy
│   ├── file_operations.py    # File I/O operations
│   ├── markdown_processor.py # Markdown → HTML conversion
│   ├── pdf_engine.py         # PDF generation (wkhtmltopdf)
│   ├── theme_builder.py      # Interactive theme wizard (NEW)
│   └── theme_manager.py      # Theme & CSS management
├── themes/                    # CSS theme files
│   ├── default.css
│   ├── dark.css
│   ├── light.css
│   ├── minimal.css
│   └── professional.css
├── tests/                     # Comprehensive test suite
│   ├── test_cli.py
│   ├── test_color_utils.py   # 32 tests for color utilities
│   ├── test_config.py
│   ├── test_core.py
│   ├── test_file_operations.py
│   ├── test_markdown_processor.py
│   ├── test_pdf_engine.py
│   ├── test_theme_builder.py # 40 tests for theme builder
│   └── test_theme_manager.py
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md       # This file
│   ├── LEARNING_GUIDE.md     # Learning guide
│   └── TESTING.md            # Testing documentation
├── setup.py                   # Package installation
├── requirements.txt           # Dependencies
├── README.md                  # Project README
└── md2pdf_old.py             # Legacy single-file version (backup)
```

---

<!-- pagebreak -->

## Module Responsibilities

### 1. `config.py` - Configuration & Constants

**Purpose**: Centralize all configuration and constants in one place.

**Contents**:
- Version number (`__version__`)
- Paths (package directory, themes directory)
- Markdown extensions list
- PDF generation options
- wkhtmltopdf installation paths by platform
- Installation instructions by platform

**Benefits**:
- ✅ Single source of truth for configuration
- ✅ Easy to modify settings
- ✅ No magic strings/numbers scattered throughout code

**Example**:
```python
from . import config

extensions = config.MARKDOWN_EXTENSIONS
options = config.PDF_OPTIONS
```

<!-- pagebreak -->

---

### 2. `pdf_engine.py` - PDF Generation Engine

**Purpose**: Abstract all wkhtmltopdf-specific logic.

**Functions**:
- `find_wkhtmltopdf()` - Auto-detect wkhtmltopdf installation
- `create_pdf_configuration()` - Create pdfkit config object
- `print_installation_help()` - Show platform-specific installation instructions
- `convert_html_to_pdf()` - Convert HTML string to PDF file

**Benefits**:
- ✅ All PDF engine logic isolated
- ✅ Easy to swap PDF engines (e.g., add WeasyPrint, Playwright PDF support)
- ✅ Platform-specific code centralized
- ✅ Clear error handling for PDF generation

**Example**:
```python
from . import pdf_engine

path = pdf_engine.find_wkhtmltopdf()
config = pdf_engine.create_pdf_configuration(path)
pdf_engine.convert_html_to_pdf(html, output_path, config)
```

<!-- pagebreak -->

---

### 3. `markdown_processor.py` - Markdown Processing

**Purpose**: Handle all Markdown → HTML conversion logic.

**Functions**:
- `markdown_to_html()` - Convert markdown content to HTML
- `process_page_breaks()` - Handle page break comments
- `build_html_document()` - Build complete HTML document with CSS

**Benefits**:
- ✅ Text processing logic separated from I/O
- ✅ Easy to test with string inputs/outputs
- ✅ Can extend with additional markdown features

**Example**:
```python
from . import markdown_processor

html_body = markdown_processor.markdown_to_html(md_content)
html_body = markdown_processor.process_page_breaks(html_body)
full_html = markdown_processor.build_html_document(title, html_body, css)
```

<!-- pagebreak -->

---

### 4. `theme_manager.py` - Theme Management

**Purpose**: Manage themes and CSS loading.

**Functions**:
- `get_themes_directory()` - Get path to themes folder
- `list_available_themes()` - List all available theme names
- `load_css()` - Load CSS from theme or custom file
- `_load_custom_css()` - Private: Load custom CSS file
- `_load_theme_css()` - Private: Load theme CSS file

**Benefits**:
- ✅ All theme logic centralized
- ✅ Easy to add theme metadata/validation
- ✅ Clear precedence handling (custom CSS > theme)

**Example**:
```python
from . import theme_manager

themes = theme_manager.list_available_themes()
css = theme_manager.load_css(custom_css=None, theme="dark")
```

<!-- pagebreak -->

---

### 5. `file_operations.py` - File I/O Operations

**Purpose**: Handle all file system operations.

**Functions**:
- `validate_input_file()` - Validate markdown file exists and is readable
- `read_markdown_file()` - Read file content
- `determine_output_path()` - Determine output PDF path
- `preview_file()` - Open PDF with system default viewer (cross-platform)

**Benefits**:
- ✅ All I/O in one place
- ✅ Easy to mock for testing
- ✅ Cross-platform file handling centralized

**Example**:
```python
from . import file_operations

input_path = file_operations.validate_input_file("document.md")
content = file_operations.read_markdown_file(input_path)
output_path = file_operations.determine_output_path(input_path, None)
file_operations.preview_file(output_path)
```

<!-- pagebreak -->

---

### 6. `core.py` - Conversion Orchestrator

**Purpose**: Coordinate all modules to perform conversion (the "conductor").

**Functions**:
- `convert_md_to_pdf()` - Main conversion function

**Workflow**:
1. Setup - Validate arguments, show warnings
2. PDF Engine - Find and configure wkhtmltopdf
3. File I/O - Validate input, determine output, read content
4. Processing - Convert MD→HTML, apply styling
5. PDF Generation - Generate PDF file
6. Finalization - Show success message, optionally preview

**Benefits**:
- ✅ Clear, linear workflow
- ✅ Each step is one function call
- ✅ Easy to understand the entire process
- ✅ Minimal business logic (delegates to modules)

**Example** (simplified orchestrator):
```python
def convert_md_to_pdf(input_file, output_file, custom_css, theme, preview):
    # 1. Setup
    if custom_css and theme != "default":
        _warn_css_precedence(theme)

    # 2. PDF Engine
    engine_path = pdf_engine.find_wkhtmltopdf()
    config = pdf_engine.create_pdf_configuration(engine_path)

    # 3. File I/O
    input_path = file_operations.validate_input_file(input_file)
    output_path = file_operations.determine_output_path(input_path, output_file)
    markdown_content = file_operations.read_markdown_file(input_path)

    # 4. Processing
    html_body = markdown_processor.markdown_to_html(markdown_content)
    html_body = markdown_processor.process_page_breaks(html_body)
    css = theme_manager.load_css(custom_css, theme)
    full_html = markdown_processor.build_html_document(input_path.stem, html_body, css)

    # 5. PDF Generation
    pdf_engine.convert_html_to_pdf(full_html, output_path, config)

    # 6. Finalization
    print(f"Success!")
    if preview:
        file_operations.preview_file(output_path)
```

<!-- pagebreak -->

---

### 7. `cli.py` - Command-Line Interface

**Purpose**: Handle argument parsing and user interaction.

**Functions**:
- `main()` - CLI entry point

**Responsibilities**:
- Create `ArgumentParser`
- Define CLI arguments
- Parse user input
- Call `convert_md_to_pdf()` from core module

**Benefits**:
- ✅ CLI logic separated from conversion logic
- ✅ Easy to add new CLI arguments
- ✅ Can create alternative interfaces (GUI, web API) easily

**Example**:
```python
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("input", ...)
    parser.add_argument("--theme", ...)
    # ... more arguments

    args = parser.parse_args()
    convert_md_to_pdf(args.input, args.output, args.css, args.theme, args.preview)
```

<!-- pagebreak -->

---

### 8. `__init__.py` - Package Interface

**Purpose**: Define public API and exports.

**Contents**:
```python
"""md2pdf - Convert Markdown to PDF with beautiful themes."""

from .config import __version__
from .core import convert_md_to_pdf
from .theme_manager import list_available_themes

__all__ = [
    "__version__",
    "convert_md_to_pdf",
    "list_available_themes",
]
```

**Benefits**:
- ✅ Clean public API
- ✅ Hide internal implementation details
- ✅ Users import from package root: `from md2pdf import convert_md_to_pdf`

<!-- pagebreak -->

---

### 9. `__main__.py` - Module Entry Point

**Purpose**: Allow running package as a module.

**Contents**:
```python
"""Entry point for running md2pdf as a module: python -m md2pdf"""

from .cli import main

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
python -m md2pdf document.md --theme dark
```

**Benefits**:
- ✅ Standard Python package pattern
- ✅ Works without installation (`python -m md2pdf`)

<!-- pagebreak -->

---

### 10. `color_utils.py` - Color Utilities & Accessibility

**Purpose**: Provide color parsing, conversion, and WCAG accessibility validation.

**Functions**:
- `parse_color()` - Parse hex, named colors, and HSL to RGB
- `rgb_to_hex()` - Convert RGB tuple to hex string
- `calculate_contrast_ratio()` - Calculate WCAG contrast ratio between colors
- `meets_wcag_aa()` / `meets_wcag_aaa()` - Check WCAG compliance
- `get_contrast_rating()` - Get human-readable contrast rating
- `suggest_darker()` / `suggest_lighter()` - Adjust color brightness
- `suggest_accessible_color()` - Auto-suggest accessible color alternatives

**Supported Color Formats**:
- Hex: `#fff`, `#ffffff`, `#1a2b3c`
- Named: `white`, `black`, `red`, `blue` (CSS standard colors)
- HSL: `hsl(210, 50%, 20%)`

**Benefits**:
- ✅ Comprehensive color format support
- ✅ Built-in accessibility validation (WCAG 2.1 standards)
- ✅ 32 comprehensive tests (94% coverage)
- ✅ Smart color suggestions for accessibility compliance

**Example**:
```python
from . import color_utils

# Parse colors
rgb = color_utils.parse_color("#1a2332")
rgb = color_utils.parse_color("white")
rgb = color_utils.parse_color("hsl(210, 50%, 20%)")

# Check contrast
ratio = color_utils.calculate_contrast_ratio("#1a2332", "#ffffff")
is_accessible = color_utils.meets_wcag_aa(ratio)  # True if ratio >= 4.5

# Get suggestions
darker = color_utils.suggest_darker("#667eea", 15)  # Darken by 15%
accessible = color_utils.suggest_accessible_color("#cccccc", "#ffffff")
```

<!-- pagebreak -->

---

### 11. `theme_builder.py` - Interactive Theme Builder

**Purpose**: Provide guided wizard for creating custom themes interactively.

**Functions**:
- `run_theme_wizard()` - Main entry point for interactive wizard
- `prompt_theme_properties()` - Collect theme properties from user
- `generate_css_from_properties()` - Generate complete CSS from properties
- `save_theme()` - Save generated CSS to themes directory
- `validate_theme_name()` - Validate theme name uniqueness
- `check_contrast_and_warn()` - Real-time contrast validation with warnings

**Theme Properties**:
1. Theme name (validated for uniqueness)
2. Background color
3. Text color (with contrast check)
4. Font family
5. Body text size
6. H1 heading color (with contrast check)
7. H2-H6 heading color (with contrast check)
8. Accent color for links/borders (with contrast check)
9. Code block background
10. Table header background

**Benefits**:
- ✅ Zero CSS knowledge required
- ✅ Real-time WCAG contrast validation
- ✅ Smart defaults for all inputs
- ✅ Generates complete, valid CSS automatically
- ✅ Beautiful terminal UI with visual feedback

**Example Workflow**:
```bash
$ md2pdf --create-theme

Theme name: corporate
✓ Name available

Background color [#ffffff]: white
✓ Using: #ffffff

Text color [#000000]: #2c3e50
✓ Using: #2c3e50
✓ Contrast ratio: 11.4:1 (Excellent - WCAG AAA)

... (more prompts) ...

✓ CSS file created: themes/corporate.css
✓ Theme ready to use!
```

<!-- pagebreak -->

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                    (cli.py, __main__.py)                    │
│  • Parse arguments                                          │
│  • Call convert_md_to_pdf()                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Orchestrator Layer                        │
│                        (core.py)                            │
│  • Coordinate workflow                                      │
│  • Delegate to specialized modules                          │
└─┬──────┬──────────┬─────────────┬────────────┬─────────────┘
  │      │          │             │            │
┌─▼──┐ ┌─▼──────┐ ┌▼──────────┐ ┌▼──────────┐┌▼────────────┐
│PDF │ │Markdown│ │   Theme   │ │   File    ││   Config    │
│Eng │ │Process │ │  Manager  │ │Operations ││             │
└────┘ └────────┘ └───────────┘ └───────────┘└─────────────┘
 wkhtml  MD→HTML    CSS Load    I/O & Valid   Constants
```

<!-- pagebreak -->

---

## Usage Examples

### 1. Command-Line Usage

```bash
# Use as module
python -m md2pdf document.md --theme dark

# After installation (pip install -e .)
md2pdf document.md --theme dark -p
```

### 2. Programmatic Usage

```python
import md2pdf

# Basic conversion
md2pdf.convert_md_to_pdf("input.md")

# With theme
md2pdf.convert_md_to_pdf("input.md", theme="dark", preview=True)

# With custom CSS
md2pdf.convert_md_to_pdf("input.md", custom_css="custom.css")

# List available themes
themes = md2pdf.list_available_themes()
print(f"Available themes: {', '.join(themes)}")
```

<!-- pagebreak -->

---

## Design Principles Applied

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- PDF engine ≠ Markdown processing
- File I/O ≠ Theme management
- CLI ≠ Conversion logic

### 2. **Dependency Injection**
Core module receives dependencies (paths, config) rather than creating them:
```python
# Good: Dependencies injected
pdf_engine.convert_html_to_pdf(html, output_path, config)

# Bad: Creating dependencies internally
# pdf_engine.convert_html_to_pdf(html)  # Where does output_path come from?
```

### 3. **Single Responsibility Principle (SRP)**
Each function/module does one thing:
- `find_wkhtmltopdf()` → Find executable
- `validate_input_file()` → Validate file
- `markdown_to_html()` → Convert markdown

### 4. **Open/Closed Principle**
Easy to extend without modifying existing code:
- Add new theme → Drop CSS file in `themes/`
- Add new PDF engine → Create new module implementing same interface

### 5. **DRY (Don't Repeat Yourself)**
Configuration centralized in `config.py`:
- Platform paths defined once
- Markdown extensions defined once
- PDF options defined once

<!-- pagebreak -->

---

## Benefits of This Architecture

### Before (Single File - 428 lines)
❌ Everything mixed together
❌ Hard to find specific functionality
❌ Difficult to test individual components
❌ Can't easily swap PDF engines
❌ Modification risk (change one thing, break another)

### After (Multi-File Package - 11 modules)
✅ **Clear organization** - Know exactly where to look
✅ **Easy testing** - Mock individual modules
✅ **Maintainable** - Change one module without affecting others
✅ **Extensible** - Add features without modifying core
✅ **Professional** - Follows Python best practices
✅ **Reusable** - Can import and use programmatically
✅ **Documented** - Clear module boundaries and responsibilities
✅ **Accessible** - Built-in WCAG compliance checking

<!-- pagebreak -->

---

## Module Metrics

| Module | Lines | Responsibility | Dependencies |
|--------|-------|----------------|--------------|
| `config.py` | ~65 | Configuration | None |
| `color_utils.py` | ~345 | Color parsing & accessibility | None |
| `theme_builder.py` | ~626 | Interactive theme wizard | color_utils, theme_manager, config |
| `pdf_engine.py` | ~110 | PDF generation | config, pdfkit |
| `markdown_processor.py` | ~70 | MD processing | config, markdown |
| `theme_manager.py` | ~135 | Theme mgmt | config |
| `file_operations.py` | ~110 | File I/O | config |
| `exceptions.py` | ~45 | Custom exceptions | None |
| `core.py` | ~350 | Orchestration | All modules |
| `cli.py` | ~190 | CLI interface | config, core, theme_builder |
| `__init__.py` | ~15 | Public API | config, core, theme_manager |
| `__main__.py` | ~5 | Entry point | cli |

**Total**: ~2,066 lines (vs 428 in original single file)
**Growth**: Significant expansion with powerful new features
**Organization**: 11 focused modules vs monolithic structure
**Test Coverage**: 228 tests across 9 test modules (76% coverage)

<!-- pagebreak -->

---

## Testing Strategy

md2pdf includes a **comprehensive pytest-based test suite** with **228 tests** covering all functionality.

### Test Suite Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_cli.py              # CLI interface tests (19 tests)
├── test_color_utils.py      # Color utilities tests (32 tests)
├── test_config.py           # Configuration module tests (9 tests)
├── test_core.py             # Core orchestrator tests (46 tests)
├── test_file_operations.py  # File I/O tests (28 tests)
├── test_markdown_processor.py # Markdown processing tests (20 tests)
├── test_pdf_engine.py       # PDF generation tests (15 tests)
├── test_theme_builder.py    # Theme builder tests (40 tests)
└── test_theme_manager.py    # Theme management tests (19 tests)
```

### Coverage by Module

| Module | Coverage | Tests |
|--------|----------|-------|
| `__init__.py` | 100% | ✓ |
| `config.py` | 100% | 9 |
| `markdown_processor.py` | 100% | 20 |
| `pdf_engine.py` | 100% | 15 |
| `color_utils.py` | 95% | 32 |
| `theme_manager.py` | 89% | 19 |
| `file_operations.py` | 80% | 28 |
| `core.py` | 98% | 46 |
| `cli.py` | 67% | 19 |
| `exceptions.py` | 100% | ✓ |
| `theme_builder.py` | 33% | 40 |
| **TOTAL** | **76%** | **228** |

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run without coverage
pytest --no-cov

# Run specific test file
pytest tests/test_cli.py
```

### Unit Testing
Each module can be tested independently:

```python
# Test theme_manager
def test_list_themes():
    themes = theme_manager.list_available_themes()
    assert "default" in themes
    assert "dark" in themes

# Test markdown_processor
def test_markdown_to_html():
    md = "# Hello"
    html = markdown_processor.markdown_to_html(md)
    assert "<h1" in html
    assert "Hello</h1>" in html

# Test file_operations (with mocking)
def test_validate_input_file(tmp_path):
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    result = file_operations.validate_input_file(str(test_file))
    assert result.exists()
```

### Integration Testing
Test module interactions:

```python
def test_full_conversion(tmp_path):
    input_file = tmp_path / "input.md"
    input_file.write_text("# Test Doc")

    output_file = tmp_path / "output.pdf"

    convert_md_to_pdf(
        str(input_file),
        str(output_file),
        theme="minimal"
    )

    assert output_file.exists()
```

### Mocking Strategy

Tests use `unittest.mock` and `pytest-mock` to isolate external dependencies:

```python
@patch("pdfkit.from_string")
def test_pdf_generation(mock_from_string):
    mock_from_string.return_value = None
    # Test without actually calling wkhtmltopdf

@patch("platform.system")
def test_platform_detection(mock_system):
    mock_system.return_value = "Linux"
    # Test platform-specific behavior
```

For more details, see the [Testing Documentation](TESTING.md).

<!-- pagebreak -->

---

## Future Extensions

### 1. Add New PDF Engine (e.g., WeasyPrint)

Create `pdf_engine_weasyprint.py`:
```python
def convert_html_to_pdf(html, output_path):
    from weasyprint import HTML
    HTML(string=html).write_pdf(output_path)
```

Update `core.py` to allow engine selection:
```python
if engine == "wkhtmltopdf":
    from . import pdf_engine
elif engine == "weasyprint":
    from . import pdf_engine_weasyprint as pdf_engine
```

### 2. Add Theme Metadata

Create `theme_metadata.json` for each theme:
```json
{
  "name": "Dark",
  "description": "A dark mode theme for reduced eye strain",
  "author": "Your Name",
  "tags": ["dark", "modern"],
  "preview_image": "dark_preview.png"
}
```

Update `theme_manager.py` to read metadata.

### 3. Add Plugin System

Create `plugins/` directory with plugin interface:
```python
# plugins/base.py
class Plugin:
    def pre_process(self, markdown: str) -> str:
        """Process markdown before conversion"""
        return markdown

    def post_process(self, html: str) -> str:
        """Process HTML after conversion"""
        return html
```

<!-- pagebreak -->

---

## Migration from Legacy

The old single-file version (`md2pdf_old.py`) is kept as a backup. To migrate:

1. **For CLI users**: No changes needed! Use `python -m md2pdf` as before
2. **For library users**: Update imports:
   ```python
   # Old
   from md2pdf import convert_md_to_pdf

   # New (same!)
   from md2pdf import convert_md_to_pdf
   ```

3. **Installation**: Run `pip install -e .` in project root

<!-- pagebreak -->

---

## Conclusion

The refactored architecture provides:
- ✅ Clear separation of concerns
- ✅ Better testability
- ✅ Easier maintenance
- ✅ Extensibility for future features
- ✅ Professional Python package structure

Each module is focused, cohesive, and loosely coupled—making the codebase **easier to understand, modify, and extend**.