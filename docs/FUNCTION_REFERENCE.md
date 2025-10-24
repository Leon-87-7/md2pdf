# md2pdf Function Reference

This document provides a comprehensive reference for all public functions available in the md2pdf package. Use this as an API reference for programmatic usage or integration with other tools.

**Version:** 0.3.1
**Last Updated:** 2025-10-24

---

## Table of Contents

1. [Core Conversion Functions](#core-conversion-functions)
2. [PDF Engine Functions](#pdf-engine-functions)
3. [Markdown Processing Functions](#markdown-processing-functions)
4. [Theme Management Functions](#theme-management-functions)
5. [Theme Builder Functions](#theme-builder-functions)
6. [Color Utility Functions](#color-utility-functions)
7. [File Operations Functions](#file-operations-functions)

---

## Core Conversion Functions

Module: `md2pdf.core`

### `convert_md_to_pdf()`

Convert a single Markdown file to PDF.

**Signature:**
```python
def convert_md_to_pdf(
    input_file: str,
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None
```

**Parameters:**
- `input_file` (str): Path to the input Markdown file
- `output_file` (str, optional): Path to the output PDF file (defaults to input name with .pdf extension)
- `custom_css` (str, optional): Path to a custom CSS file (takes precedence over theme)
- `theme` (str): Theme name to use (default: "default", ignored if custom_css is provided)
- `preview` (bool): Whether to open the PDF after generation (default: False)

**Raises:**
- `WkhtmltopdfNotFoundError`: If wkhtmltopdf is not found on the system
- `ConversionError`: If PDF conversion fails
- `ThemeNotFoundError`: If the requested theme is not found
- `CSSNotFoundError`: If the custom CSS file is not found
- `InvalidInputError`: If input file validation fails
- `FileOperationError`: If file read/write operations fail

**Example:**
```python
from md2pdf.core import convert_md_to_pdf

# Simple conversion
convert_md_to_pdf("document.md")

# With custom output and theme
convert_md_to_pdf("document.md", output_file="output.pdf", theme="dark")

# With preview
convert_md_to_pdf("document.md", preview=True)
```

**Location:** `md2pdf/core.py:117`

---

### `convert_batch()`

Convert multiple Markdown files to separate PDFs in batch mode.

**Signature:**
```python
def convert_batch(
    input_files: list[str],
    output_dir: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None
```

**Parameters:**
- `input_files` (list[str]): List of paths to input Markdown files
- `output_dir` (str, optional): Directory for output PDFs (defaults to each input's directory)
- `custom_css` (str, optional): Path to a custom CSS file (takes precedence over theme)
- `theme` (str): Theme name to use (default: "default", ignored if custom_css is provided)
- `preview` (bool): Whether to open the first PDF after generation (default: False)

**Raises:**
- Same exceptions as `convert_md_to_pdf()`

**Example:**
```python
from md2pdf.core import convert_batch

# Convert multiple files
convert_batch(["doc1.md", "doc2.md", "doc3.md"], output_dir="pdfs/")

# With custom theme
convert_batch(["*.md"], theme="professional")
```

**Location:** `md2pdf/core.py:168`

---

### `convert_merge()`

Merge multiple Markdown files into a single PDF.

**Signature:**
```python
def convert_merge(
    input_files: list[str],
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    auto_break: bool = True,
    preview: bool = False,
) -> None
```

**Parameters:**
- `input_files` (list[str]): List of paths to input Markdown files
- `output_file` (str, optional): Path to the output merged PDF (default: "merged_output.pdf")
- `custom_css` (str, optional): Path to a custom CSS file (takes precedence over theme)
- `theme` (str): Theme name to use (default: "default", ignored if custom_css is provided)
- `auto_break` (bool): Whether to add page breaks between documents (default: True)
- `preview` (bool): Whether to open the PDF after generation (default: False)

**Raises:**
- Same exceptions as `convert_md_to_pdf()`

**Example:**
```python
from md2pdf.core import convert_merge

# Merge multiple files
convert_merge(["ch1.md", "ch2.md", "ch3.md"], output_file="book.pdf")

# Merge without auto page breaks
convert_merge(["*.md"], output_file="combined.pdf", auto_break=False)
```

**Location:** `md2pdf/core.py:270`

---

## PDF Engine Functions

Module: `md2pdf.pdf_engine`

### `find_wkhtmltopdf()`

Auto-detect wkhtmltopdf installation path across different platforms.

**Signature:**
```python
def find_wkhtmltopdf() -> Optional[str]
```

**Returns:**
- `str | None`: Path to wkhtmltopdf executable if found, None otherwise

**Example:**
```python
from md2pdf.pdf_engine import find_wkhtmltopdf

wkhtmltopdf_path = find_wkhtmltopdf()
if wkhtmltopdf_path:
    print(f"Found wkhtmltopdf at: {wkhtmltopdf_path}")
else:
    print("wkhtmltopdf not found")
```

**Location:** `md2pdf/pdf_engine.py:17`

---

### `create_pdf_configuration()`

Create pdfkit configuration object.

**Signature:**
```python
def create_pdf_configuration(wkhtmltopdf_path: str) -> PdfKitConfig
```

**Parameters:**
- `wkhtmltopdf_path` (str): Path to wkhtmltopdf executable

**Returns:**
- `PdfKitConfig`: pdfkit.configuration object

**Example:**
```python
from md2pdf.pdf_engine import find_wkhtmltopdf, create_pdf_configuration

path = find_wkhtmltopdf()
config = create_pdf_configuration(path)
```

**Location:** `md2pdf/pdf_engine.py:46`

---

### `get_installation_instructions()`

Get platform-specific installation instructions for wkhtmltopdf.

**Signature:**
```python
def get_installation_instructions() -> str
```

**Returns:**
- `str`: Formatted installation instructions as a string

**Example:**
```python
from md2pdf.pdf_engine import get_installation_instructions

instructions = get_installation_instructions()
print(instructions)
```

**Location:** `md2pdf/pdf_engine.py:61`

---

### `convert_html_to_pdf()`

Convert HTML content to PDF file using wkhtmltopdf.

**Signature:**
```python
def convert_html_to_pdf(
    html_content: str,
    output_path: Path,
    pdf_config: PdfKitConfig,
) -> None
```

**Parameters:**
- `html_content` (str): HTML content to convert
- `output_path` (Path): Path where PDF should be saved
- `pdf_config` (PdfKitConfig): pdfkit configuration object

**Raises:**
- `ConversionError`: If PDF conversion fails for any reason

**Location:** `md2pdf/pdf_engine.py:82`

---

## Markdown Processing Functions

Module: `md2pdf.markdown_processor`

### `markdown_to_html()`

Convert markdown content to HTML.

**Signature:**
```python
def markdown_to_html(content: str) -> str
```

**Parameters:**
- `content` (str): Markdown content as string

**Returns:**
- `str`: HTML content as string

**Example:**
```python
from md2pdf.markdown_processor import markdown_to_html

markdown = "# Hello World\n\nThis is **bold** text."
html = markdown_to_html(markdown)
print(html)
```

**Location:** `md2pdf/markdown_processor.py:11`

---

### `process_page_breaks()`

Process HTML comments for page breaks and convert them to CSS page breaks.

**Signature:**
```python
def process_page_breaks(html_content: str) -> str
```

**Parameters:**
- `html_content` (str): HTML content to process

**Returns:**
- `str`: HTML content with page break comments replaced by div elements

**Supported Syntax:**
- `<!-- pagebreak -->`
- `<!-- page-break -->`
- `<!-- PAGEBREAK -->`
- `<!-- PAGE-BREAK -->`

**Example:**
```python
from md2pdf.markdown_processor import process_page_breaks

html = "<p>Page 1</p><!-- pagebreak --><p>Page 2</p>"
processed = process_page_breaks(html)
```

**Location:** `md2pdf/markdown_processor.py:23`

---

### `build_html_document()`

Build complete HTML document with embedded CSS.

**Signature:**
```python
def build_html_document(title: str, body_html: str, css_content: str) -> str
```

**Parameters:**
- `title` (str): Document title (for `<title>` tag) - will be HTML-escaped
- `body_html` (str): HTML content for body (should already be safe HTML from markdown)
- `css_content` (str): CSS content to embed in `<style>` tag

**Returns:**
- `str`: Complete HTML document as string

**Note:**
The title is escaped to prevent HTML injection. The body_html is expected to be safe HTML generated by the markdown library.

**Example:**
```python
from md2pdf.markdown_processor import build_html_document

html_doc = build_html_document(
    title="My Document",
    body_html="<h1>Hello</h1><p>World</p>",
    css_content="body { font-family: Arial; }"
)
```

**Location:** `md2pdf/markdown_processor.py:44`

---

## Theme Management Functions

Module: `md2pdf.theme_manager`

### `get_themes_directory()`

Get the path to the themes directory.

**Signature:**
```python
def get_themes_directory() -> Path
```

**Returns:**
- `Path`: Path to the themes directory (in project root)

**Example:**
```python
from md2pdf.theme_manager import get_themes_directory

themes_dir = get_themes_directory()
print(f"Themes directory: {themes_dir}")
```

**Location:** `md2pdf/theme_manager.py:11`

---

### `list_available_themes()`

List all available theme names.

**Signature:**
```python
def list_available_themes() -> list[str]
```

**Returns:**
- `list[str]`: List of theme names (without .css extension)

**Example:**
```python
from md2pdf.theme_manager import list_available_themes

themes = list_available_themes()
print("Available themes:", ", ".join(themes))
```

**Location:** `md2pdf/theme_manager.py:20`

---

### `validate_theme()`

Validate that a theme exists before conversion starts.

**Signature:**
```python
def validate_theme(theme: str) -> None
```

**Parameters:**
- `theme` (str): Theme name (without .css extension)

**Raises:**
- `ThemeNotFoundError`: If theme is not found

**Example:**
```python
from md2pdf.theme_manager import validate_theme

try:
    validate_theme("dark")
    print("Theme is valid")
except ThemeNotFoundError as e:
    print(f"Error: {e}")
```

**Location:** `md2pdf/theme_manager.py:34`

---

### `load_css()`

Load CSS content from custom file, theme, or default.

**Signature:**
```python
def load_css(custom_css: Optional[str] = None, theme: str = "default") -> str
```

**Parameters:**
- `custom_css` (str, optional): Path to custom CSS file, or None to use theme
- `theme` (str): Theme name to use (default: "default")

**Returns:**
- `str`: CSS content as string

**Raises:**
- `CSSNotFoundError`: If custom CSS file is not found
- `ThemeNotFoundError`: If theme is not found
- `FileOperationError`: If CSS file cannot be read

**Note:**
The `--css` flag takes precedence over `--theme`.

**Example:**
```python
from md2pdf.theme_manager import load_css

# Load default theme
css = load_css()

# Load specific theme
css = load_css(theme="dark")

# Load custom CSS
css = load_css(custom_css="my-theme.css")
```

**Location:** `md2pdf/theme_manager.py:51`

---

## Theme Builder Functions

Module: `md2pdf.theme_builder`

### `run_theme_wizard()`

Run the interactive theme builder wizard.

**Signature:**
```python
def run_theme_wizard() -> None
```

**Description:**
Launches an interactive CLI wizard that guides users through creating a custom theme. The wizard:
- Prompts for theme name, colors, fonts, and other properties
- Validates color formats and accessibility (WCAG contrast ratios)
- Suggests accessible color alternatives when needed
- Generates a complete CSS file
- Saves the theme to the themes directory

**Example:**
```python
from md2pdf.theme_builder import run_theme_wizard

# Launch interactive wizard
run_theme_wizard()
```

**Location:** `md2pdf/theme_builder.py:589`

---

### `generate_css_from_properties()`

Generate complete CSS file from theme properties.

**Signature:**
```python
def generate_css_from_properties(props: Dict[str, str]) -> str
```

**Parameters:**
- `props` (Dict[str, str]): Dictionary of theme properties

**Returns:**
- `str`: Complete CSS content as string

**Required Properties:**
- `name`: Theme name
- `background_color`: Background color (hex)
- `text_color`: Text color (hex)
- `font_family`: Font family string
- `body_text_size`: Body text size (e.g., "11pt")
- `h1_color`: H1 heading color (hex)
- `h2_h6_color`: H2-H6 heading color (hex)
- `accent_color`: Accent color for links and borders (hex)
- `code_bg_color`: Code block background (hex)
- `table_header_bg`: Table header background (hex)

**Example:**
```python
from md2pdf.theme_builder import generate_css_from_properties

props = {
    "name": "my-theme",
    "background_color": "#ffffff",
    "text_color": "#000000",
    "font_family": "Arial, sans-serif",
    "body_text_size": "11pt",
    "h1_color": "#2c3e50",
    "h2_h6_color": "#2c3e50",
    "accent_color": "#667eea",
    "code_bg_color": "#f5f5f5",
    "table_header_bg": "#667eea"
}

css = generate_css_from_properties(props)
```

**Location:** `md2pdf/theme_builder.py:314`

---

### `save_theme()`

Save theme CSS to themes directory.

**Signature:**
```python
def save_theme(name: str, css_content: str) -> Path
```

**Parameters:**
- `name` (str): Theme name (without .css extension)
- `css_content` (str): CSS content to save

**Returns:**
- `Path`: Path to saved theme file

**Raises:**
- `IOError`: If file cannot be written

**Example:**
```python
from md2pdf.theme_builder import save_theme, generate_css_from_properties

props = {...}  # theme properties
css = generate_css_from_properties(props)
theme_path = save_theme("my-theme", css)
print(f"Theme saved to: {theme_path}")
```

**Location:** `md2pdf/theme_builder.py:528`

---

## Color Utility Functions

Module: `md2pdf.color_utils`

### `parse_color()`

Parse a color string into RGB tuple.

**Signature:**
```python
def parse_color(color_string: str) -> Tuple[int, int, int]
```

**Parameters:**
- `color_string` (str): Color in hex, named, or HSL format

**Returns:**
- `Tuple[int, int, int]`: RGB tuple (r, g, b) with values 0-255

**Raises:**
- `ValueError`: If color format is invalid

**Supported Formats:**
- Hex: `#fff`, `#ffffff`, `#1a2b3c`
- Named: `white`, `black`, `red`, etc.
- HSL: `hsl(210, 50%, 20%)`

**Example:**
```python
from md2pdf.color_utils import parse_color

rgb = parse_color("#667eea")  # Returns (102, 126, 234)
rgb = parse_color("white")     # Returns (255, 255, 255)
rgb = parse_color("hsl(210, 50%, 20%)")  # Returns HSL converted to RGB
```

**Location:** `md2pdf/color_utils.py:32`

---

### `rgb_to_hex()`

Convert RGB tuple to hex string.

**Signature:**
```python
def rgb_to_hex(rgb: Tuple[int, int, int]) -> str
```

**Parameters:**
- `rgb` (Tuple[int, int, int]): RGB tuple (r, g, b) with values 0-255

**Returns:**
- `str`: Hex color string like `#1a2b3c`

**Example:**
```python
from md2pdf.color_utils import rgb_to_hex

hex_color = rgb_to_hex((102, 126, 234))  # Returns "#667eea"
```

**Location:** `md2pdf/color_utils.py:155`

---

### `calculate_contrast_ratio()`

Calculate contrast ratio between two colors per WCAG formula.

**Signature:**
```python
def calculate_contrast_ratio(color1: str, color2: str) -> float
```

**Parameters:**
- `color1` (str): First color (any supported format)
- `color2` (str): Second color (any supported format)

**Returns:**
- `float`: Contrast ratio (1.0 to 21.0)

**Raises:**
- `ValueError`: If color format is invalid

**Example:**
```python
from md2pdf.color_utils import calculate_contrast_ratio

ratio = calculate_contrast_ratio("#000000", "#ffffff")  # Returns 21.0
ratio = calculate_contrast_ratio("black", "white")      # Returns 21.0
```

**Location:** `md2pdf/color_utils.py:199`

---

### `meets_wcag_aa()`

Check if contrast ratio meets WCAG AA standard (4.5:1 minimum).

**Signature:**
```python
def meets_wcag_aa(ratio: float) -> bool
```

**Parameters:**
- `ratio` (float): Contrast ratio

**Returns:**
- `bool`: True if ratio >= 4.5, False otherwise

**Example:**
```python
from md2pdf.color_utils import calculate_contrast_ratio, meets_wcag_aa

ratio = calculate_contrast_ratio("#000000", "#ffffff")
if meets_wcag_aa(ratio):
    print("Contrast is accessible (WCAG AA)")
```

**Location:** `md2pdf/color_utils.py:225`

---

### `meets_wcag_aaa()`

Check if contrast ratio meets WCAG AAA standard (7.0:1 minimum).

**Signature:**
```python
def meets_wcag_aaa(ratio: float) -> bool
```

**Parameters:**
- `ratio` (float): Contrast ratio

**Returns:**
- `bool`: True if ratio >= 7.0, False otherwise

**Example:**
```python
from md2pdf.color_utils import calculate_contrast_ratio, meets_wcag_aaa

ratio = calculate_contrast_ratio("#000000", "#ffffff")
if meets_wcag_aaa(ratio):
    print("Contrast is highly accessible (WCAG AAA)")
```

**Location:** `md2pdf/color_utils.py:237`

---

### `get_contrast_rating()`

Get human-readable rating for contrast ratio.

**Signature:**
```python
def get_contrast_rating(ratio: float) -> str
```

**Parameters:**
- `ratio` (float): Contrast ratio

**Returns:**
- `str`: Rating string: "Excellent - WCAG AAA", "Good - WCAG AA", or "Poor - Below WCAG AA"

**Example:**
```python
from md2pdf.color_utils import calculate_contrast_ratio, get_contrast_rating

ratio = calculate_contrast_ratio("#667eea", "#ffffff")
rating = get_contrast_rating(ratio)
print(f"Contrast rating: {rating}")
```

**Location:** `md2pdf/color_utils.py:249`

---

### `suggest_darker()`

Darken a color by a percentage.

**Signature:**
```python
def suggest_darker(color: str, percentage: float = 15.0) -> str
```

**Parameters:**
- `color` (str): Color in any supported format
- `percentage` (float): Percentage to darken (0-100)

**Returns:**
- `str`: Darkened color as hex string

**Example:**
```python
from md2pdf.color_utils import suggest_darker

darker = suggest_darker("#667eea", 15)  # Darken by 15%
print(f"Darker color: {darker}")
```

**Location:** `md2pdf/color_utils.py:266`

---

### `suggest_lighter()`

Lighten a color by a percentage.

**Signature:**
```python
def suggest_lighter(color: str, percentage: float = 15.0) -> str
```

**Parameters:**
- `color` (str): Color in any supported format
- `percentage` (float): Percentage to lighten (0-100)

**Returns:**
- `str`: Lightened color as hex string

**Example:**
```python
from md2pdf.color_utils import suggest_lighter

lighter = suggest_lighter("#667eea", 15)  # Lighten by 15%
print(f"Lighter color: {lighter}")
```

**Location:** `md2pdf/color_utils.py:286`

---

### `suggest_accessible_color()`

Suggest an adjusted foreground color to meet target contrast ratio.

**Signature:**
```python
def suggest_accessible_color(
    foreground: str,
    background: str,
    target_ratio: float = 4.5
) -> str
```

**Parameters:**
- `foreground` (str): Foreground color (any supported format)
- `background` (str): Background color (any supported format)
- `target_ratio` (float): Target contrast ratio (default: 4.5 for WCAG AA)

**Returns:**
- `str`: Adjusted foreground color as hex string

**Example:**
```python
from md2pdf.color_utils import suggest_accessible_color

# Get accessible text color for a light background
text_color = suggest_accessible_color("#aaaaaa", "#ffffff", target_ratio=4.5)
print(f"Accessible text color: {text_color}")
```

**Location:** `md2pdf/color_utils.py:306`

---

## File Operations Functions

Module: `md2pdf.file_operations`

### `validate_input_file()`

Validate the input markdown file.

**Signature:**
```python
def validate_input_file(input_file: str) -> Path
```

**Parameters:**
- `input_file` (str): Path to the input markdown file

**Returns:**
- `Path`: Validated Path object

**Raises:**
- `InvalidInputError`: If validation fails

**Validation Checks:**
- File exists
- Is a file (not directory)
- Has read permissions
- Has valid markdown extension (warning only)

**Example:**
```python
from md2pdf.file_operations import validate_input_file

try:
    input_path = validate_input_file("document.md")
    print(f"Valid input file: {input_path}")
except InvalidInputError as e:
    print(f"Invalid input: {e}")
```

**Location:** `md2pdf/file_operations.py:14`

---

### `read_markdown_file()`

Read markdown file and return its content.

**Signature:**
```python
def read_markdown_file(path: Path) -> str
```

**Parameters:**
- `path` (Path): Path to markdown file

**Returns:**
- `str`: File content as string

**Raises:**
- `FileOperationError`: If file cannot be read

**Example:**
```python
from pathlib import Path
from md2pdf.file_operations import read_markdown_file

path = Path("document.md")
content = read_markdown_file(path)
print(content)
```

**Location:** `md2pdf/file_operations.py:48`

---

### `determine_output_path()`

Determine the output PDF path with enhanced security validation.

**Signature:**
```python
def determine_output_path(input_path: Path, output_arg: Optional[str]) -> Path
```

**Parameters:**
- `input_path` (Path): Path to input markdown file
- `output_arg` (str, optional): Optional output path argument from CLI

**Returns:**
- `Path`: Path where PDF should be saved (always resolved to absolute path)

**Raises:**
- `InvalidInputError`: If output path is invalid or attempts path traversal

**Security Validation:**
- Prevents path traversal attacks (`../` sequences)
- Prevents symlink attacks
- Validates paths stay within current working directory (for relative paths)

**Example:**
```python
from pathlib import Path
from md2pdf.file_operations import determine_output_path

input_path = Path("document.md")
output_path = determine_output_path(input_path, None)  # Uses default
output_path = determine_output_path(input_path, "custom.pdf")  # Custom name
```

**Location:** `md2pdf/file_operations.py:67`

---

### `preview_file()`

Open a PDF file using the default system viewer.

**Signature:**
```python
def preview_file(pdf_path: Path) -> None
```

**Parameters:**
- `pdf_path` (Path): Path to the PDF file to open

**Platform Support:**
- **Windows**: Uses `os.startfile()`
- **macOS**: Uses `open` command
- **Linux**: Uses `xdg-open` command

**Notes:**
- Validates PDF path exists and is a file before opening
- Includes timeout protection (10 seconds) on macOS and Linux
- Prints warnings to stderr if opening fails

**Example:**
```python
from pathlib import Path
from md2pdf.file_operations import preview_file

pdf_path = Path("output.pdf")
preview_file(pdf_path)
```

**Location:** `md2pdf/file_operations.py:136`

---

## Exception Classes

Module: `md2pdf.exceptions`

All custom exceptions inherit from `Md2PdfError`:

- `Md2PdfError`: Base exception class
- `WkhtmltopdfNotFoundError`: wkhtmltopdf not found on system
- `ConversionError`: PDF conversion failed
- `ThemeNotFoundError`: Theme not found
- `CSSNotFoundError`: Custom CSS file not found
- `InvalidInputError`: Invalid input file or path
- `FileOperationError`: File read/write operation failed

**Example:**
```python
from md2pdf.exceptions import Md2PdfError, ThemeNotFoundError

try:
    # ... conversion code ...
    pass
except ThemeNotFoundError as e:
    print(f"Theme error: {e}")
except Md2PdfError as e:
    print(f"General error: {e}")
```

---

## Usage Examples

### Example 1: Simple Conversion with Error Handling

```python
from md2pdf.core import convert_md_to_pdf
from md2pdf.exceptions import Md2PdfError

try:
    convert_md_to_pdf(
        input_file="README.md",
        output_file="README.pdf",
        theme="professional",
        preview=True
    )
    print("Conversion successful!")
except Md2PdfError as e:
    print(f"Conversion failed: {e}")
```

### Example 2: Batch Processing Multiple Files

```python
from md2pdf.core import convert_batch
import glob

# Get all markdown files in current directory
md_files = glob.glob("*.md")

# Convert all to PDFs in 'output' directory
convert_batch(
    input_files=md_files,
    output_dir="output",
    theme="dark"
)
```

### Example 3: Creating a Custom Theme Programmatically

```python
from md2pdf.theme_builder import generate_css_from_properties, save_theme
from md2pdf.core import convert_md_to_pdf

# Define theme properties
theme_props = {
    "name": "ocean",
    "background_color": "#f0f8ff",
    "text_color": "#1e3a5f",
    "font_family": "Georgia, serif",
    "body_text_size": "12pt",
    "h1_color": "#0077be",
    "h2_h6_color": "#0088cc",
    "accent_color": "#00aaff",
    "code_bg_color": "#e6f3ff",
    "table_header_bg": "#0077be"
}

# Generate and save theme
css = generate_css_from_properties(theme_props)
save_theme("ocean", css)

# Use the new theme
convert_md_to_pdf("document.md", theme="ocean")
```

### Example 4: Checking Theme Availability

```python
from md2pdf.theme_manager import list_available_themes, validate_theme
from md2pdf.exceptions import ThemeNotFoundError

# List all available themes
themes = list_available_themes()
print(f"Available themes: {', '.join(themes)}")

# Validate a specific theme
try:
    validate_theme("dark")
    print("Theme 'dark' is available")
except ThemeNotFoundError as e:
    print(f"Theme not found: {e}")
```

### Example 5: Color Accessibility Validation

```python
from md2pdf.color_utils import (
    calculate_contrast_ratio,
    meets_wcag_aa,
    suggest_accessible_color,
    get_contrast_rating
)

# Check contrast between text and background
text_color = "#667eea"
bg_color = "#ffffff"

ratio = calculate_contrast_ratio(text_color, bg_color)
rating = get_contrast_rating(ratio)

print(f"Contrast ratio: {ratio:.2f}:1")
print(f"Rating: {rating}")

if not meets_wcag_aa(ratio):
    suggested = suggest_accessible_color(text_color, bg_color)
    print(f"Suggested accessible color: {suggested}")
```

### Example 6: Merging Documents with Custom Styling

```python
from md2pdf.core import convert_merge
from md2pdf.theme_manager import load_css

# Load custom CSS
custom_css = load_css(custom_css="my-custom-theme.css")

# Merge chapters into a book
convert_merge(
    input_files=["ch1.md", "ch2.md", "ch3.md", "ch4.md"],
    output_file="complete-book.pdf",
    custom_css="my-custom-theme.css",
    auto_break=True,  # Add page breaks between chapters
    preview=True
)
```

---

## Notes

### Thread Safety

The functions in md2pdf are **not thread-safe**. If you need to perform concurrent conversions, use separate processes instead of threads.

### Performance Considerations

- **Batch Mode**: More efficient than calling `convert_md_to_pdf()` multiple times because PDF engine and CSS are loaded once
- **Merge Mode**: Most efficient for combining many files as it generates a single PDF

### Platform Compatibility

All functions work across Windows, macOS, and Linux. Platform-specific differences are handled internally:
- wkhtmltopdf detection
- PDF preview functionality
- File path handling

---

## Version History

- **0.3.1**: Current version with enhanced theme builder and color utilities
- **0.3.0**: Added theme_builder and color_utils modules
- **0.2.x**: Initial modular architecture

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project overview and development guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [TESTING.md](TESTING.md) - Testing strategy and guidelines

---

**For CLI usage and installation instructions, see the main [README.md](../README.md).**
