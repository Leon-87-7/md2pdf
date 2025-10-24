# Deep Dive: Understanding md2pdf.py

## Table of Contents
1. [Module Structure & Imports](#module-structure--imports)
2. [Type Hints & Modern Python](#type-hints--modern-python)
3. [Auto-Detection with find_wkhtmltopdf()](#auto-detection-with-find_wkhtmltopdf)
4. [Theme System & File Operations](#theme-system--file-operations)
5. [CSS Styling & Multi-line Strings](#css-styling--multi-line-strings)
6. [Regular Expressions for Pattern Matching](#regular-expressions-for-pattern-matching)
7. [Cross-Platform Compatibility](#cross-platform-compatibility)
8. [Validation & Error Handling](#validation--error-handling)
9. [Path Handling with pathlib](#path-handling-with-pathlib)
10. [HTML Generation & String Formatting](#html-generation--string-formatting)
11. [Command-Line Interface with argparse](#command-line-interface-with-argparse)

---

## 1. Module Structure & Imports

### Shebang Line
```python
#! /usr/bin/env python3
```
**What it does**: Tells Unix-like systems to run this file with Python 3.
**Why it matters**: Makes the file executable on Linux/macOS (`chmod +x md2pdf.py` then `./md2pdf.py`).

### Standard Library Imports
```python
import argparse      # Command-line argument parsing
import os            # OS-level operations (file permissions, startfile)
import platform      # Detect OS (Windows, macOS, Linux)
import re            # Regular expressions for pattern matching
import shutil        # High-level file operations (which())
import subprocess    # Run external commands
import sys           # System-specific parameters (exit, stderr)
```

**Key learning**: Organize imports in order: standard library → third-party → local modules.

### Advanced Imports
```python
from pathlib import Path         # Object-oriented path handling
from typing import Optional      # Type hints for optional values
```

**`Optional[str]`**: Means the value can be a `str` OR `None`.

### Third-Party Imports
```python
import markdown  # Markdown → HTML conversion
import pdfkit    # HTML → PDF conversion (wraps wkhtmltopdf)
```

### Version Declaration
```python
__version__ = "0.1.0"
```
**Pattern**: Dunder (double underscore) variables are special module-level metadata.

---

## 2. Type Hints & Modern Python

### Function Signatures with Type Hints

#### Example: find_wkhtmltopdf()
```python
def find_wkhtmltopdf() -> Optional[str]:
    """Auto-detect wkhtmltopdf installation path."""
```

**Breakdown**:
- `-> Optional[str]`: Function returns either a `str` or `None`
- Helps IDEs provide autocomplete
- Makes code self-documenting
- Enables type checking with tools like `mypy`

#### Example: _validate_input_file()
```python
def _validate_input_file(input_file: str) -> Path:
```

**Breakdown**:
- `input_file: str`: Parameter must be a string
- `-> Path`: Function returns a `pathlib.Path` object
- Notice the leading underscore `_`: Convention for "private" helper functions

#### Modern Python Type Hints: list[str]
```python
def _list_available_themes() -> list[str]:
    """List all available theme names."""
```

**Python 3.9+ Feature**: Use `list[str]` instead of `typing.List[str]`
- Cleaner syntax
- Built-in generic types (no import needed)
- Also works with `dict[str, int]`, `tuple[str, ...]`, etc.

---

## 3. Auto-Detection with find_wkhtmltopdf()

### Algorithm Flow
```python
def find_wkhtmltopdf() -> Optional[str]:
    # Step 1: Check system PATH
    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if wkhtmltopdf_path:
        return wkhtmltopdf_path

    # Step 2: Check common installation locations
    system = platform.system()
    common_paths = []

    if system == "Windows":
        common_paths = [
            "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
            # ... more paths
        ]
    # ... other platforms
```

### Key Concepts

#### 1. shutil.which()
```python
wkhtmltopdf_path = shutil.which("wkhtmltopdf")
```
**What it does**: Searches the system's `PATH` environment variable for an executable.
**Returns**: Full path to executable, or `None` if not found.
**Example**: On Linux, might return `/usr/bin/wkhtmltopdf`.

#### 2. platform.system()
```python
system = platform.system()
# Returns: "Windows", "Darwin" (macOS), "Linux", etc.
```

#### 3. Path.home()
```python
Path.home() / "AppData/Local/Programs/wkhtmltopdf/bin/wkhtmltopdf.exe"
```
**What it does**: Gets the user's home directory (`C:\Users\username` on Windows).
**The `/` operator**: `pathlib` overloads `/` for path joining (cross-platform!).

#### 4. List Iteration with Validation
```python
for path in common_paths:
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_file():
        return str(path_obj)
```
**Pattern**:
- Convert string to `Path` object
- Check if it exists AND is a file (not a directory)
- Return as string when found

---

## 4. Theme System & File Operations

### Understanding the Theme System

The code uses a **theme-based system** instead of hardcoded CSS. This is a much better design pattern!

#### Getting the Script's Directory
```python
def _get_themes_directory() -> Path:
    """Get the path to the themes directory."""
    script_dir = Path(__file__).parent
    return script_dir / "themes"
```

**`Path(__file__)`**: Special variable that contains the path to the current Python file.
**`.parent`**: Gets the directory containing the file.

**Example**:
```python
# If script is at: /home/user/md2pdf/md2pdf.py
Path(__file__)           # /home/user/md2pdf/md2pdf.py
Path(__file__).parent    # /home/user/md2pdf
Path(__file__).parent / "themes"  # /home/user/md2pdf/themes
```

#### Listing Available Themes
```python
def _list_available_themes() -> list[str]:
    """List all available theme names."""
    themes_dir = _get_themes_directory()
    if not themes_dir.exists():
        return []

    # Get all .css files and remove extension
    return [f.stem for f in themes_dir.glob("*.css")]
```

**Key concepts**:
1. **`.glob("*.css")`**: Find all files matching the pattern
   - `*` is a wildcard (matches anything)
   - Returns an iterator of `Path` objects
2. **List comprehension**: `[f.stem for f in ...]`
   - Iterate through all `.css` files
   - Extract the stem (filename without extension)
3. **`.stem` property**:
   - `Path("default.css").stem` → `"default"`
   - `Path("dark.css").stem` → `"dark"`

### Loading CSS with Theme Support
```python
def _load_css(custom_css: Optional[str] = None, theme: str = "default") -> str:
    """Load CSS content from custom file, theme, or default."""
    # --css flag takes precedence over --theme
    if custom_css:
        # ... load custom CSS file
    else:
        # Load from themes directory
        themes_dir = _get_themes_directory()
        theme_path = themes_dir / f"{theme}.css"

        if not theme_path.exists():
            available_themes = _list_available_themes()
            print(f"Error: Theme '{theme}' not found.", file=sys.stderr)
            if available_themes:
                print(f"Available themes: {', '.join(available_themes)}", file=sys.stderr)
            sys.exit(1)
```

**Design Pattern: Precedence & Fallback**
1. Custom CSS (highest priority) → Load from user-provided path
2. Theme → Load from themes directory
3. Error handling → Show available options

**String joining**:
```python
themes = ["default", "dark", "minimal"]
', '.join(themes)  # "default, dark, minimal"
```

---

## 5. CSS Styling & Multi-line Strings

### Theme Files

Instead of hardcoded CSS, themes are now stored in separate `.css` files in the `themes/` directory:

```
md2pdf/
├── md2pdf.py
└── themes/
    ├── default.css      # Purple gradient theme
    ├── dark.css         # Dark mode theme
    ├── light.css        # Light theme
    ├── minimal.css      # Minimalist theme
    └── professional.css # Professional theme
```

### Benefits of External Theme Files

#### Before (Hardcoded - OLD APPROACH):
```python
@lru_cache(maxsize=1)
def get_default_css() -> str:
    return """
    @page { size: A4; margin: 2cm; }
    body { font-family: 'Segoe UI'... }
    # ... 200+ lines of CSS ...
    """
```

**Problems**:
- ❌ CSS mixed with Python code
- ❌ Hard to edit styling
- ❌ Can't switch themes easily
- ❌ Need to modify code to change appearance

#### After (Theme System - NEW APPROACH):
```python
def _load_css(custom_css: Optional[str] = None, theme: str = "default") -> str:
    themes_dir = _get_themes_directory()
    theme_path = themes_dir / f"{theme}.css"

    with open(theme_path, "r", encoding="utf-8") as f:
        return f.read()
```

**Advantages**:
- ✅ Separation of concerns (code vs styling)
- ✅ Easy to add new themes (just drop a `.css` file)
- ✅ Users can customize without touching code
- ✅ Switch themes via command-line flag

### CSS Concepts in the Themes

#### @page Rule (PDF-specific)
```css
@page {
    size: A4;      /* Paper size */
    margin: 2cm;   /* Page margins */
}
```

#### Linear Gradients
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
**Breakdown**:
- `135deg`: Diagonal direction (top-left to bottom-right)
- `#667eea 0%`: Start color (purple-blue)
- `#764ba2 100%`: End color (deeper purple)

#### RGBA Colors
```css
background: rgba(255, 255, 255, 0.95);
```
**Breakdown**: Red, Green, Blue, Alpha (opacity)
- `255, 255, 255` = white
- `0.95` = 95% opaque (5% transparent)

#### nth-child Selector
```css
tr:nth-child(even) td {
    background-color: rgba(248, 249, 250, 0.95);
}
```
**What it does**: Styles every even table row (zebra striping).

---

## 6. Regular Expressions for Pattern Matching

### process_page_breaks() Function
```python
def process_page_breaks(html_content: str) -> str:
    pattern = r"<!--\s*page[-_\s]*break\s*-->"
    replacement = '<div class="page-break"></div>'
    return re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)
```

### Regex Breakdown

#### Raw String Prefix
```python
pattern = r"<!--\s*page[-_\s]*break\s*-->"
#         ^ r prefix = raw string (backslashes are literal)
```

#### Pattern Components
```regex
<!--        # HTML comment start (literal)
\s*         # Zero or more whitespace characters
page        # Literal text "page"
[-_\s]*     # Zero or more: hyphens, underscores, or whitespace
break       # Literal text "break"
\s*         # Zero or more whitespace characters
-->         # HTML comment end (literal)
```

#### Matches All These
```html
<!-- pagebreak -->
<!-- page-break -->
<!-- page_break -->
<!-- page break -->
<!--pagebreak-->
<!--   page   break   -->
```

#### re.sub() Parameters
```python
re.sub(
    pattern,           # What to find
    replacement,       # What to replace with
    html_content,      # String to search in
    flags=re.IGNORECASE  # Case-insensitive matching
)
```

**flags=re.IGNORECASE**: Also matches `<!-- PAGEBREAK -->`, `<!-- PageBreak -->`, etc.

---

## 7. Cross-Platform Compatibility

### open_pdf() Function
```python
def open_pdf(pdf_path: Path) -> None:
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
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Warning: Could not open PDF: {e}", file=sys.stderr)
```

### Platform-Specific Commands

#### Windows: os.startfile()
```python
os.startfile(str(pdf_path))
```
**What it does**: Opens file with default associated program (like double-clicking in Explorer).

#### macOS: `open` command
```python
subprocess.run(["open", str(pdf_path)], check=True)
```
**What it does**: Uses macOS's `open` command (equivalent to double-clicking in Finder).

#### Linux: `xdg-open` command
```python
subprocess.run(["xdg-open", str(pdf_path)], check=True)
```
**What it does**: Uses freedesktop.org's standard to open with default viewer.

### subprocess.run() Parameters
```python
subprocess.run(
    ["open", str(pdf_path)],  # Command as list of strings
    check=True                 # Raise exception if command fails
)
```

**Key concept**: Commands are passed as lists:
- `["open", "file.pdf"]` ✓ Correct
- `"open file.pdf"` ✗ Wrong (shell injection risk!)

---

## 8. Validation & Error Handling

### _validate_input_file() Function
```python
def _validate_input_file(input_file: str) -> Path:
    input_path = Path(input_file)

    # Check 1: Does it exist?
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Check 2: Is it a file (not a directory)?
    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # Check 3: Extension validation (warning only)
    if input_path.suffix.lower() not in [".md", ".markdown", ".txt"]:
        print(f"Warning: '{input_file}' does not have a markdown extension",
              file=sys.stderr)

    # Check 4: Permission check
    if not os.access(input_path, os.R_OK):
        print(f"Error: No read permission for '{input_file}'.", file=sys.stderr)
        sys.exit(1)

    return input_path
```

### Key Concepts

#### Path Methods
```python
input_path.exists()     # Does the path exist?
input_path.is_file()    # Is it a file (not a directory)?
input_path.suffix       # File extension (".md", ".txt", etc.)
input_path.suffix.lower()  # Lowercase extension
```

#### sys.exit(1)
```python
sys.exit(1)  # Exit with error code 1 (indicates failure)
sys.exit(0)  # Exit with code 0 (success)
```
**Why it matters**: Exit codes let scripts detect failures:
```bash
md2pdf file.md
if [ $? -eq 0 ]; then echo "Success!"; fi
```

#### file=sys.stderr
```python
print(f"Error: ...", file=sys.stderr)
```
**Standard streams**:
- `stdout` (default): Normal output
- `stderr`: Error messages
**Why separate**: Allows redirecting errors separately:
```bash
md2pdf file.md > output.log 2> errors.log
```

#### os.access() for Permissions
```python
os.access(input_path, os.R_OK)  # Check read permission
```
**Flags**:
- `os.R_OK`: Read permission
- `os.W_OK`: Write permission
- `os.X_OK`: Execute permission

---

## 9. Path Handling with pathlib

### Why pathlib Over os.path

#### Old Way (os.path)
```python
import os
path = os.path.join("folder", "subfolder", "file.txt")
if os.path.exists(path) and os.path.isfile(path):
    extension = os.path.splitext(path)[1]
```

#### Modern Way (pathlib)
```python
from pathlib import Path
path = Path("folder") / "subfolder" / "file.txt"
if path.exists() and path.is_file():
    extension = path.suffix
```

### Path Operations in md2pdf

#### Creating Paths
```python
# From string
input_path = Path(input_file)

# Joining paths with /
css_path = Path.home() / "AppData" / "Local" / "file.css"

# With suffix
output_path = input_path.with_suffix(".pdf")
```

#### Path Properties
```python
path = Path("/Users/john/documents/report.md")

path.name        # "report.md"
path.stem        # "report" (name without extension)
path.suffix      # ".md"
path.parent      # Path("/Users/john/documents")
path.resolve()   # Absolute path with symlinks resolved
```

#### Converting to String
```python
pdf_path = Path("output.pdf")
os.startfile(str(pdf_path))  # Many functions need strings
```

### Security: Path Traversal Prevention
```python
css_path = Path(custom_css).resolve()
```

**`.resolve()`**:
- Converts to absolute path
- Resolves `..` (parent directory references)
- Resolves symlinks

**Example**:
```python
# User provides: "../../../etc/passwd"
Path("../../../etc/passwd").resolve()
# Returns: "/etc/passwd" (absolute)

# Now you can validate it's in an allowed directory!
```

---

## 10. HTML Generation & String Formatting

### f-Strings (Formatted String Literals)
```python
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
```

### How f-Strings Work

#### Basic Interpolation
```python
name = "Alice"
age = 30
print(f"Hello, {name}! You are {age} years old.")
# Output: Hello, Alice! You are 30 years old.
```

#### Expressions Inside
```python
print(f"Next year you'll be {age + 1}")
# Output: Next year you'll be 31
```

#### Method Calls
```python
input_path = Path("document.md")
print(f"Title: {input_path.stem}")
# Output: Title: document
```

### Markdown to HTML Conversion
```python
html_content = markdown.markdown(
    md_content,
    extensions=["extra", "codehilite", "tables", "toc"]
)
```

**Extensions explained**:
- `extra`: Enables abbreviations, footnotes, attributes
- `codehilite`: Syntax highlighting for code blocks
- `tables`: GitHub-flavored table support
- `toc`: Table of contents generation

**Example transformation**:
```markdown
# Hello World
This is **bold** text.
```
↓
```html
<h1>Hello World</h1>
<p>This is <strong>bold</strong> text.</p>
```

---

## 11. Command-Line Interface with argparse

### main() Function Breakdown
```python
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF with custom styles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  md2pdf document.md                                    # Use default theme
  md2pdf input.md -o output.pdf                        # Specify output file
  md2pdf notes.md --theme dark                         # Use dark theme
  md2pdf notes.md --theme minimal                      # Use minimal theme
  md2pdf notes.md --css custom-style.css               # Use custom CSS file
  md2pdf report.md --theme dark -p                     # Use dark theme and preview
  md2pdf report.md --theme minimal --css custom.css    # CSS takes precedence (with warning)
  """
    )
```

### Adding Arguments

#### Positional Argument
```python
parser.add_argument("input", help="Path to the input Markdown file.")
```
**Usage**: `md2pdf file.md` (required, no flag)

#### Optional Arguments
```python
parser.add_argument(
    "-o", "--output",
    help="Output PDF file (default: same name as input)"
)
```
**Features**:
- Short form: `-o output.pdf`
- Long form: `--output output.pdf`
- Optional (can be omitted)

#### Theme Argument (Theme System Feature!)
```python
parser.add_argument(
    "--theme",
    default="default",
    help="Theme to use for styling (default: default). Ignored if --css is specified."
)
```
**Features**:
- Default value: `"default"`
- Only takes effect if `--css` is not provided
- Users can switch themes easily

**Usage**:
```bash
md2pdf file.md                  # Uses default theme
md2pdf file.md --theme dark     # Uses dark theme
md2pdf file.md --theme minimal  # Uses minimal theme
```

#### Boolean Flags
```python
parser.add_argument(
    "-p", "--preview",
    action="store_true",
    help="Open the PDF with the default viewer after conversion"
)
```
**`action="store_true"`**: Presence of flag sets value to `True`, absence = `False`.

**Usage**:
```bash
md2pdf file.md -p      # preview=True
md2pdf file.md         # preview=False
```

#### Version Argument
```python
parser.add_argument(
    "-v", "--version",
    action="version",
    version=f"md2pdf {__version__}"
)
```
**Usage**: `md2pdf --version` prints version and exits.

### Parsing Arguments
```python
args = parser.parse_args()

convert_md_to_pdf(
    args.input,    # Positional argument
    args.output,   # -o/--output
    args.css,      # --css
    args.theme,    # --theme (Theme System!)
    args.preview   # -p/--preview
)
```

### Flag Precedence Pattern

```python
def convert_md_to_pdf(
    input_file: str,
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:
    # Warn if both custom_css and theme are specified
    if custom_css and theme != "default":
        print(
            f"Warning: Both --css and --theme specified. Using custom CSS file, ignoring theme '{theme}'.",
            file=sys.stderr,
        )
```

**Design pattern**: When two options conflict, warn the user and apply precedence rules:
1. Custom CSS (highest priority)
2. Theme
3. Default theme (fallback)

---

## Advanced Python Patterns Used

### 1. Guard Clauses (Early Returns)
```python
def find_wkhtmltopdf() -> Optional[str]:
    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if wkhtmltopdf_path:
        return wkhtmltopdf_path  # Early return if found

    # Continue only if not found...
```

**Pattern**: Return early on success, reduces nesting.

### 2. Exception Tuples
```python
except (IOError, OSError, PermissionError) as e:
    print(f"Error: {e}")
```

**Pattern**: Catch multiple exception types with same handler.

### 3. Context Managers (with statement)
```python
with open(input_path, "r", encoding="utf-8") as f:
    md_content = f.read()
```

**Why**:
- Automatically closes file (even if exception occurs)
- Better than manual `f.close()`

### 4. Dictionary for Configuration
```python
options = {
    "enable-local-file-access": None,
    "encoding": "UTF-8",
    "quiet": ""
}
pdfkit.from_string(full_html, str(output_path),
                   configuration=config, options=options)
```

**Pattern**: Pass options as dictionary for flexibility.

### 5. String Conversion for Compatibility
```python
pdfkit.from_string(full_html, str(output_path), ...)
#                              ^^^ Convert Path to string
```

**Why**: Many libraries expect strings, not Path objects.

### 6. Separation of Concerns
```python
# Separate CSS styling from code logic
themes_dir = _get_themes_directory()
css_content = _load_css(custom_css, theme)
```

**Design principle**:
- Configuration (CSS) separated from code
- Each function has a single responsibility
- Easy to extend and maintain

---

## Testing Your Understanding

### Quiz Questions

1. **Why use external theme files instead of hardcoded CSS?**
   <details>
   <summary>Answer</summary>
   - Separation of concerns (styling vs logic)<br>
   - Easy to add/modify themes without changing code<br>
   - Users can customize appearance easily<br>
   - Better maintainability
   </details>

2. **What does `Path(__file__).parent` return?**
   <details>
   <summary>Answer</summary>
   The directory containing the current Python script. For example, if the script is at /home/user/md2pdf/md2pdf.py, it returns /home/user/md2pdf.
   </details>

3. **What does `.glob("*.css")` do?**
   <details>
   <summary>Answer</summary>
   Returns an iterator of all Path objects matching the pattern (all files ending with .css). The * is a wildcard that matches any characters.
   </details>

4. **Why use `file=sys.stderr` for error messages?**
   <details>
   <summary>Answer</summary>
   Separates error messages from normal output, allowing users to redirect them separately (e.g., to a log file).
   </details>

5. **What's the difference between `Path.name`, `Path.stem`, and `Path.suffix`?**
   <details>
   <summary>Answer</summary>
   For Path("report.md"): name="report.md", stem="report", suffix=".md"
   </details>

6. **Why does the code check `if custom_css and theme != "default"`?**
   <details>
   <summary>Answer</summary>
   To warn users when both --css and --theme are specified (but only if theme is not the default). This prevents confusion about which styling is actually being used.
   </details>

---

## Exercises to Deepen Learning

### Exercise 1: Add a New Theme
Create a new theme file called `ocean.css` in the themes directory with a blue color scheme.

**Hints**:
- Copy `default.css` as a starting point
- Change gradient colors to ocean blues (#0077be, #00a8e8)
- Test with: `md2pdf test.md --theme ocean`

### Exercise 2: List Available Themes
Add a `--list-themes` flag that displays all available themes and exits.

**Hints**:
```python
parser.add_argument(
    "--list-themes",
    action="store_true",
    help="List all available themes and exit"
)

if args.list_themes:
    themes = _list_available_themes()
    print("Available themes:")
    for theme in themes:
        print(f"  - {theme}")
    sys.exit(0)
```

### Exercise 3: Add Theme Metadata
Create a JSON file for each theme with metadata (description, author, colors).

**Hints**:
```json
{
  "name": "dark",
  "description": "A dark mode theme for reduced eye strain",
  "author": "Your Name",
  "primary_color": "#2d3748"
}
```

### Exercise 4: Add Landscape Support
Add support for a `--landscape` flag that changes the page orientation.

**Hints**:
- Modify the CSS `@page` rule dynamically
- Add an argument to `argparse`
- Inject landscape CSS into the HTML

---

## Resources for Further Learning

### Python Concepts
- **pathlib**: [https://docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html)
- **argparse**: [https://docs.python.org/3/library/argparse.html](https://docs.python.org/3/library/argparse.html)
- **Type hints**: [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)
- **Regular expressions**: [https://docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html)
- **glob patterns**: [https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob)

### Design Patterns
- **Separation of concerns**: Keep code logic separate from configuration/data
- **Guard clauses**: Early returns for cleaner code
- **DRY principle**: Helper functions eliminate repetition
- **Precedence rules**: Clear hierarchy when multiple options conflict

### Best Practices Demonstrated
✓ Type hints for clarity
✓ Comprehensive error handling
✓ Cross-platform compatibility
✓ Security considerations (path validation)
✓ Separation of concerns (themes vs code)
✓ Clear documentation (docstrings)
✓ User-friendly CLI interface
✓ Helpful error messages with context

---

**Happy Learning!** 🚀