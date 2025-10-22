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
│   ├── config.py             # Configuration & constants
│   ├── core.py               # Conversion orchestrator
│   ├── file_operations.py    # File I/O operations
│   ├── markdown_processor.py # Markdown → HTML conversion
│   ├── pdf_engine.py         # PDF generation (wkhtmltopdf)
│   └── theme_manager.py      # Theme & CSS management
├── themes/                    # CSS theme files
│   ├── default.css
│   ├── dark.css
│   ├── light.css
│   ├── minimal.css
│   └── professional.css
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md       # This file
│   └── LEARNING_GUIDE.md     # Learning guide
├── setup.py                   # Package installation
├── requirements.txt           # Dependencies
├── README.md                  # Project README
└── md2pdf_old.py             # Legacy single-file version (backup)
```

---

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

---

## Benefits of This Architecture

### Before (Single File - 428 lines)
❌ Everything mixed together
❌ Hard to find specific functionality
❌ Difficult to test individual components
❌ Can't easily swap PDF engines
❌ Modification risk (change one thing, break another)

### After (Multi-File Package - 9 modules)
✅ **Clear organization** - Know exactly where to look
✅ **Easy testing** - Mock individual modules
✅ **Maintainable** - Change one module without affecting others
✅ **Extensible** - Add features without modifying core
✅ **Professional** - Follows Python best practices
✅ **Reusable** - Can import and use programmatically
✅ **Documented** - Clear module boundaries and responsibilities

---

## Module Metrics

| Module | Lines | Responsibility | Dependencies |
|--------|-------|----------------|--------------|
| `config.py` | ~65 | Configuration | None |
| `pdf_engine.py` | ~110 | PDF generation | config, pdfkit |
| `markdown_processor.py` | ~70 | MD processing | config, markdown |
| `theme_manager.py` | ~125 | Theme mgmt | config |
| `file_operations.py` | ~110 | File I/O | config |
| `core.py` | ~65 | Orchestration | All modules |
| `cli.py` | ~55 | CLI interface | config, core |
| `__init__.py` | ~15 | Public API | config, core, theme_manager |
| `__main__.py` | ~5 | Entry point | cli |

**Total**: ~620 lines (vs 428 in single file)
**Overhead**: ~45% more lines, but **much** better organized

---

## Testing Strategy

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
    assert "<h1>Hello</h1>" in html

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

---

## Conclusion

The refactored architecture provides:
- ✅ Clear separation of concerns
- ✅ Better testability
- ✅ Easier maintenance
- ✅ Extensibility for future features
- ✅ Professional Python package structure

Each module is focused, cohesive, and loosely coupled—making the codebase **easier to understand, modify, and extend**.