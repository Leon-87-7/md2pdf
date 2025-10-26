# Deep Dive: Understanding md2pdf v0.3.0 - Batch Processing & Merge Mode

## Table of Contents

### Core Concepts (from v0.1.0)
1. [Module Structure & Imports](#1-module-structure--imports)
2. [Type Hints & Modern Python](#2-type-hints--modern-python)
3. [Path Handling with pathlib](#3-path-handling-with-pathlib)

### New in v0.3.0
4. [Shared Helper Functions Pattern](#4-shared-helper-functions-pattern)
5. [Batch Processing Architecture](#5-batch-processing-architecture)
6. [Merge Mode Implementation](#6-merge-mode-implementation)
7. [HTML Body Merging with Page Breaks](#7-html-body-merging-with-page-breaks)
8. [Multi-Mode CLI Design](#8-multi-mode-cli-design)
9. [Error Recovery in Batch Operations](#9-error-recovery-in-batch-operations)
10. [Tuple Unpacking and List Comprehensions](#10-tuple-unpacking-and-list-comprehensions)

### Advanced Topics
11. [Design Patterns in Action](#11-design-patterns-in-action)
12. [Performance Optimization](#12-performance-optimization)
13. [Testing Your Understanding](#13-testing-your-understanding)

---

## What's New in v0.3.0?

Version 0.3.0 introduces **two major features**:

### 1. **Batch Processing Mode**
Convert multiple Markdown files to separate PDFs in one command:
```bash
md2pdf file1.md file2.md file3.md
md2pdf *.md --output-dir pdfs/
```

### 2. **Merge Mode**
Combine multiple Markdown files into a single PDF:
```bash
md2pdf chapter1.md chapter2.md --merge -o book.pdf
```

These features demonstrate important software engineering concepts:
- **Code reuse** through shared helper functions
- **Error recovery** in batch operations
- **Mode detection** and routing
- **Efficient resource usage** (setup once, use many times)

---

## 1. Module Structure & Imports

### New Imports in v0.3.0

The modular architecture uses these key imports:

```python
from pathlib import Path
from typing import Optional

from . import file_operations, markdown_processor, pdf_engine, theme_manager
from .exceptions import WkhtmltopdfNotFoundError
```

**Key concepts**:
- **Relative imports** with `.`: Import from same package
- **Module importing**: Import entire modules, not individual functions
- **Exception importing**: Custom exceptions for better error handling

**Why this structure?**
```python
# ✅ Good: Clear which module provides the function
file_operations.validate_input_file(path)
markdown_processor.markdown_to_html(content)

# ❌ Bad: Where does validate_input_file come from?
from file_operations import *
validate_input_file(path)  # Unclear origin
```

---

## 2. Type Hints & Modern Python

### Type Hints in v0.3.0

#### List Type Hints (Python 3.9+)
```python
def convert_batch(
    input_files: list[str],  # List of strings
    output_dir: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:  # Returns nothing
```

**Breaking down the types**:
- `list[str]`: A list containing strings
  - Old way: `from typing import List` then `List[str]`
  - New way (3.9+): Built-in `list[str]`
- `Optional[str]`: Either a string OR `None`
  - Equivalent to `str | None` in Python 3.10+
- `-> None`: Function has side effects, doesn't return a value

#### Tuple Type Hints
```python
def _process_single_file(
    input_file: str,
    pdf_config,
    css_content: str
) -> tuple:  # Returns a tuple
    # ...
    return input_path, html_body
```

**More specific version**:
```python
def _process_single_file(...) -> tuple[Path, str]:
    # Returns: (Path object, HTML string)
    return input_path, html_body
```

**Why type hints matter**:
```python
# Your IDE can now help you!
result = _process_single_file("file.md", config, css)
# IDE knows: result is a tuple
# IDE knows: result[0] is a Path
# IDE knows: result[1] is a str

input_path, html_body = result
# IDE knows: input_path is Path, html_body is str
```

---

## 3. Path Handling with pathlib

### Path Operations in v0.3.0

#### Creating Output Directories
```python
if output_dir:
    output_path_obj = Path(output_dir)
    output_path_obj.mkdir(parents=True, exist_ok=True)
```

**Understanding `mkdir()` parameters**:
- `parents=True`: Create parent directories if they don't exist
  ```python
  Path("pdfs/2024/reports").mkdir(parents=True)
  # Creates: pdfs/ → pdfs/2024/ → pdfs/2024/reports/
  ```
- `exist_ok=True`: Don't raise error if directory already exists
  ```python
  # Without exist_ok=True:
  Path("pdfs").mkdir()  # First time: OK
  Path("pdfs").mkdir()  # Second time: FileExistsError!

  # With exist_ok=True:
  Path("pdfs").mkdir(exist_ok=True)  # Always OK
  ```

#### Path Division Operator
```python
output_file = output_path_obj / f"{input_path.stem}.pdf"
```

**Why use `/` operator?**
```python
# Cross-platform path joining
output_dir = Path("pdfs")
filename = "report.pdf"

# ✅ Good: Works on all platforms
path = output_dir / filename
# Windows: pdfs\report.pdf
# Linux/Mac: pdfs/report.pdf

# ❌ Bad: Hardcoded separators
path = f"{output_dir}\\{filename}"  # Breaks on Linux!
```

#### Path Properties Refresher
```python
input_path = Path("documents/report.md")

input_path.name      # "report.md" (full filename)
input_path.stem      # "report" (without extension)
input_path.suffix    # ".md" (just extension)
input_path.parent    # Path("documents")
```

---

## 4. Shared Helper Functions Pattern

### The Problem: Code Duplication

**Before v0.3.0** (hypothetical):
```python
def convert_md_to_pdf(...):
    # Find wkhtmltopdf
    engine_path = pdf_engine.find_wkhtmltopdf()
    if engine_path is None:
        instructions = pdf_engine.get_installation_instructions()
        raise WkhtmltopdfNotFoundError(instructions)

    pdf_config = pdf_engine.create_pdf_configuration(engine_path)
    css_content = theme_manager.load_css(custom_css, theme)
    # ... conversion logic ...

def convert_batch(...):
    # Same setup code repeated!
    engine_path = pdf_engine.find_wkhtmltopdf()
    if engine_path is None:
        instructions = pdf_engine.get_installation_instructions()
        raise WkhtmltopdfNotFoundError(instructions)

    pdf_config = pdf_engine.create_pdf_configuration(engine_path)
    css_content = theme_manager.load_css(custom_css, theme)
    # ... batch logic ...
```

**Problems**:
- ❌ Code duplication (DRY violation)
- ❌ Bug fixes needed in multiple places
- ❌ Hard to maintain consistency
- ❌ Inefficient (setup happens per file in batch mode)

### The Solution: Shared Helper Function

```python
def _setup_conversion_environment(
    custom_css: Optional[str] = None, theme: str = "default"
) -> tuple:
    """Setup PDF engine and CSS once for efficiency.

    This function is shared by all conversion modes (single, batch, merge)
    to avoid redundant setup operations.

    Returns:
        Tuple of (pdf_config, css_content)

    Raises:
        WkhtmltopdfNotFoundError: If wkhtmltopdf is not found
        ThemeNotFoundError: If theme is not found
    """
    # Warn if both custom_css and theme are specified
    if custom_css and theme != "default":
        print(
            f"Warning: Both --css and --theme specified. "
            f"Using custom CSS file, ignoring theme '{theme}'.",
            file=sys.stderr,
        )

    # Validate theme early if not using custom CSS
    if not custom_css:
        theme_manager.validate_theme(theme)

    # Find and configure wkhtmltopdf once
    engine_path = pdf_engine.find_wkhtmltopdf()
    if engine_path is None:
        instructions = pdf_engine.get_installation_instructions()
        raise WkhtmltopdfNotFoundError(instructions)

    pdf_config = pdf_engine.create_pdf_configuration(engine_path)

    # Load CSS once
    css_content = theme_manager.load_css(custom_css, theme)

    return pdf_config, css_content
```

**Key design decisions**:

1. **Leading underscore `_`**: Private helper function (not part of public API)
   ```python
   _setup_conversion_environment()  # Internal use only
   convert_md_to_pdf()              # Public function
   ```

2. **Return tuple**: Multiple values returned together
   ```python
   pdf_config, css_content = _setup_conversion_environment(...)
   # Unpacks tuple into two variables
   ```

3. **Early validation**: Check theme exists before doing expensive setup
   ```python
   # Validate theme early
   if not custom_css:
       theme_manager.validate_theme(theme)  # Fail fast!

   # Then do expensive operations
   engine_path = pdf_engine.find_wkhtmltopdf()
   ```

4. **Single Responsibility**: Function does ONE thing - setup
   - Doesn't read files
   - Doesn't convert anything
   - Just prepares the environment

### Using the Helper Function

Now all three modes use the same setup:

```python
def convert_md_to_pdf(...):
    # 1. Setup (shared)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)
    # 2. Single file logic
    # ...

def convert_batch(...):
    # 1. Setup once for all files (shared)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)
    # 2. Batch logic
    for input_file in input_files:
        # Uses same pdf_config and css_content
        # ...

def convert_merge(...):
    # 1. Setup once (shared)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)
    # 2. Merge logic
    # ...
```

**Benefits**:
- ✅ Fix bug once → fixed everywhere
- ✅ Add feature once → works everywhere
- ✅ Easy to test (test one function)
- ✅ Clear separation of concerns
- ✅ Efficient (setup once in batch mode)

---

## 5. Batch Processing Architecture

### The Batch Processing Function

```python
def convert_batch(
    input_files: list[str],
    output_dir: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:
    """Convert multiple Markdown files to PDFs in batch mode."""
```

### Step-by-Step Breakdown

#### Step 1: Input Validation
```python
if not input_files:
    print("Error: No input files specified for batch conversion.", file=sys.stderr)
    return  # Early return pattern
```

**Early return pattern**:
- Check for error conditions first
- Return immediately if invalid
- Main logic runs only with valid input
- Reduces nesting depth

#### Step 2: Shared Setup (Efficiency!)
```python
# 1. Setup once for all conversions (efficiency)
pdf_config, css_content = _setup_conversion_environment(custom_css, theme)
```

**Why this matters**:
```python
# ❌ Bad: Setup for each file
for file in files:
    pdf_config = setup()  # Slow! Repeated setup
    convert(file, pdf_config)

# ✅ Good: Setup once
pdf_config = setup()  # Fast! One-time setup
for file in files:
    convert(file, pdf_config)
```

**Performance impact**:
- Setup includes: finding wkhtmltopdf, loading CSS, creating config
- For 10 files: 10x speedup by doing setup once!

#### Step 3: Output Directory Creation
```python
# Create output directory if specified
output_path_obj = None
if output_dir:
    output_path_obj = Path(output_dir)
    output_path_obj.mkdir(parents=True, exist_ok=True)
```

**Conditional path creation**:
- If `--output-dir` specified: use it
- If not specified: use each file's directory (determined later)

#### Step 4: Process Files with Error Recovery
```python
# 2. Process each file
converted_files = []  # Track successes
failed_files = []     # Track failures

for input_file in input_files:
    try:
        # Process file: Read and convert to HTML
        input_path, html_body = _process_single_file(
            input_file, pdf_config, css_content
        )

        # Determine output path
        if output_path_obj:
            output_file = output_path_obj / f"{input_path.stem}.pdf"
        else:
            output_file = file_operations.determine_output_path(input_path, None)

        # Build complete HTML document
        full_html = markdown_processor.build_html_document(
            title=input_path.stem, body_html=html_body, css_content=css_content
        )

        # PDF Generation
        pdf_engine.convert_html_to_pdf(full_html, output_file, pdf_config)

        converted_files.append((input_file, output_file))
        print(f"[OK] Converted '{input_file}' to '{output_file}'")

    except Exception as e:
        failed_files.append((input_file, str(e)))
        print(f"[FAILED] '{input_file}': {e}", file=sys.stderr)
```

**Error recovery pattern**:
```python
for item in items:
    try:
        process(item)
        successes.append(item)
    except Exception as e:
        failures.append((item, e))
        # Continue processing remaining items!
```

**Why catch broad `Exception`?**

This is one case where catching all exceptions is appropriate:

✅ **Good use case** (batch processing):
```python
# We want to:
# 1. Process as many files as possible
# 2. Report all errors to user
# 3. Provide summary of what worked/failed

for file in files:
    try:
        convert(file)
    except Exception as e:  # Catch everything
        log_error(file, e)
        continue  # Keep going!
```

❌ **Bad use case** (single operation):
```python
try:
    critical_operation()
except Exception:
    pass  # Silent failure - never do this!
```

#### Step 5: Summary Report
```python
# 3. Print summary
print("\n--- Batch Conversion Summary ---")
print(f"Total files: {len(input_files)}")
print(f"Successful: {len(converted_files)}")
print(f"Failed: {len(failed_files)}")

if failed_files:
    print("\nFailed files:")
    for input_file, error in failed_files:
        print(f"  - {input_file}: {error}")
```

**User-friendly reporting**:
- Total count (all files attempted)
- Success count (how many worked)
- Failure count (how many failed)
- Detailed error list (what went wrong)

**Example output**:
```
[OK] Converted 'file1.md' to 'pdfs\file1.pdf'
[OK] Converted 'file2.md' to 'pdfs\file2.pdf'
[FAILED] 'file3.md': File not found

--- Batch Conversion Summary ---
Total files: 3
Successful: 2
Failed: 1

Failed files:
  - file3.md: File not found
```

---

## 6. Merge Mode Implementation

### The Merge Function

```python
def convert_merge(
    input_files: list[str],
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    auto_break: bool = True,  # New parameter!
    preview: bool = False,
) -> None:
    """Merge multiple Markdown files into a single PDF."""
```

### Step-by-Step Breakdown

#### Step 1: Validation
```python
if not input_files:
    print("Error: No input files specified for merge.", file=sys.stderr)
    return

if len(input_files) < 2:
    print(
        "Warning: Merge mode requires at least 2 files. "
        "Use single file mode for one file.",
        file=sys.stderr,
    )
```

**Validation levels**:
1. **Must have files**: Empty list is error
2. **Should have 2+**: One file is warning (still works)

#### Step 2: Shared Setup
```python
# 1. Setup once for all conversions (efficiency)
pdf_config, css_content = _setup_conversion_environment(custom_css, theme)
```

Same efficient pattern as batch mode!

#### Step 3: Process and Collect HTML Bodies
```python
# 2. Process all files and collect HTML bodies
html_bodies = []
failed_files = []

print(f"Merging {len(input_files)} files into a single PDF...")

for input_file in input_files:
    try:
        # Process file: Read and convert to HTML
        input_path, html_body = _process_single_file(
            input_file, pdf_config, css_content
        )
        html_bodies.append((input_path.name, html_body))
        print(f"[OK] Processed '{input_file}'")

    except Exception as e:
        failed_files.append((input_file, str(e)))
        print(f"[FAILED] '{input_file}': {e}", file=sys.stderr)
```

**Key data structure**:
```python
html_bodies = [
    ("file1.md", "<h1>Chapter 1</h1><p>...</p>"),
    ("file2.md", "<h1>Chapter 2</h1><p>...</p>"),
    ("file3.md", "<h1>Chapter 3</h1><p>...</p>"),
]
# List of tuples: (filename, HTML content)
```

**Why tuples?**
- Tuples are **immutable** (can't accidentally modify)
- Pairs of related data (filename + HTML)
- Unpacks nicely in loops (see next section)

#### Step 4: Check for Success
```python
# 3. Check if we have at least one successful file
if not html_bodies:
    print("Error: No files were successfully processed. Cannot create PDF.",
          file=sys.stderr)
    return
```

**Graceful degradation**:
- If ALL files failed: Can't create PDF
- If SOME failed: Continue with successful ones

#### Step 5: Merge HTML Bodies
```python
# 4. Merge HTML bodies
merged_html_body = _merge_html_bodies(html_bodies, auto_break)
```

This calls our merge helper function (explained next!).

#### Step 6: Determine Output
```python
# 5. Determine output path
if output_file:
    output_path = Path(output_file)
else:
    output_path = Path("merged_output.pdf")  # Default name
```

**Fallback pattern**:
- User specified name: use it
- No name given: use default

#### Step 7: Build and Convert
```python
# 6. Build complete HTML document with merged content
full_html = markdown_processor.build_html_document(
    title="Merged Document",
    body_html=merged_html_body,
    css_content=css_content
)

# 7. PDF Generation: Convert HTML to PDF
pdf_engine.convert_html_to_pdf(full_html, output_path, pdf_config)
```

#### Step 8: Report Results
```python
# 8. Print summary
print("\n--- Merge Summary ---")
print(f"Total files: {len(input_files)}")
print(f"Successfully merged: {len(html_bodies)}")
print(f"Failed: {len(failed_files)}")

if failed_files:
    print("\nFailed files:")
    for input_file, error in failed_files:
        print(f"  - {input_file}: {error}")

print(f"\nMerged PDF created: '{output_path}'")
```

---

## 7. HTML Body Merging with Page Breaks

### The Merge Helper Function

```python
def _merge_html_bodies(
    html_bodies: list[tuple[str, str]],
    auto_break: bool = True
) -> str:
    """Merge multiple HTML body sections into a single HTML body.

    Args:
        html_bodies: List of tuples (filename, html_body)
        auto_break: Whether to add page breaks between documents (default: True)

    Returns:
        Merged HTML body string
    """
    merged_parts = []

    for i, (filename, html_body) in enumerate(html_bodies):
        # Add a section header with the filename
        section_header = f'<h1 class="document-section-header">{filename}</h1>\n'
        merged_parts.append(section_header)
        merged_parts.append(html_body)

        # Add page break between documents (except after the last one)
        if auto_break and i < len(html_bodies) - 1:
            merged_parts.append('<div class="page-break"></div>\n')

    return "\n".join(merged_parts)
```

### Understanding Tuple Unpacking in Loops

```python
for i, (filename, html_body) in enumerate(html_bodies):
    # ...
```

**What's happening here?**

Let's break it down step by step:

#### 1. The Data Structure
```python
html_bodies = [
    ("chapter1.md", "<h1>Chapter 1</h1>..."),
    ("chapter2.md", "<h1>Chapter 2</h1>..."),
]
```

#### 2. Basic Loop
```python
for item in html_bodies:
    print(item)
# Output:
# ("chapter1.md", "<h1>Chapter 1</h1>...")
# ("chapter2.md", "<h1>Chapter 2</h1>...")
```

#### 3. Add Index with `enumerate()`
```python
for i, item in enumerate(html_bodies):
    print(f"Index {i}: {item}")
# Output:
# Index 0: ("chapter1.md", "<h1>Chapter 1</h1>...")
# Index 1: ("chapter2.md", "<h1>Chapter 2</h1>...")
```

#### 4. Unpack Tuple with `(filename, html_body)`
```python
for i, (filename, html_body) in enumerate(html_bodies):
    print(f"Index {i}: {filename}")
# Output:
# Index 0: chapter1.md
# Index 1: chapter2.md
```

**Complete breakdown**:
```python
# enumerate() gives us:
# (0, ("chapter1.md", "<h1>..."))
# (1, ("chapter2.md", "<h1>..."))

# Unpacking happens in two steps:
# i, (filename, html_body)
# ↓
# i = 0
# (filename, html_body) = ("chapter1.md", "<h1>...")
# ↓
# filename = "chapter1.md"
# html_body = "<h1>..."
```

### The List Building Pattern

```python
merged_parts = []  # 1. Start with empty list

for i, (filename, html_body) in enumerate(html_bodies):
    merged_parts.append(section_header)  # 2. Add piece
    merged_parts.append(html_body)        # 3. Add piece
    if condition:
        merged_parts.append(page_break)   # 4. Add piece

return "\n".join(merged_parts)  # 5. Join into string
```

**Why build list then join?**

```python
# ❌ Bad: String concatenation in loop
result = ""
for part in parts:
    result += part  # Creates new string each time!
    # With 1000 parts: 1000 string objects created

# ✅ Good: Build list, join once
result = "".join(parts)  # Single operation
# With 1000 parts: 1 final string created
```

**Performance explanation**:
- Strings are **immutable** in Python
- Each `+=` creates a new string, copying all previous data
- Lists just add references (fast!)
- `join()` creates the string once at the end

### Conditional Page Breaks

```python
if auto_break and i < len(html_bodies) - 1:
    merged_parts.append('<div class="page-break"></div>\n')
```

**Logic breakdown**:
```python
# Condition 1: auto_break is True
# Condition 2: i < len(html_bodies) - 1
#              ↓
#              Not the last item

# Examples with 3 files:
# i=0: 0 < 3-1 → 0 < 2 → True  (add break)
# i=1: 1 < 3-1 → 1 < 2 → True  (add break)
# i=2: 2 < 3-1 → 2 < 2 → False (no break after last)
```

**Why skip last page break?**
- Page breaks create new page AFTER content
- Last file doesn't need page after it
- Avoids blank page at end of PDF

### Example Output

**With `auto_break=True`**:
```html
<h1 class="document-section-header">chapter1.md</h1>
<h1>Chapter 1</h1>
<p>Content...</p>
<div class="page-break"></div>

<h1 class="document-section-header">chapter2.md</h1>
<h1>Chapter 2</h1>
<p>Content...</p>
<div class="page-break"></div>

<h1 class="document-section-header">chapter3.md</h1>
<h1>Chapter 3</h1>
<p>Content...</p>
```

**With `auto_break=False`**:
```html
<h1 class="document-section-header">chapter1.md</h1>
<h1>Chapter 1</h1>
<p>Content...</p>

<h1 class="document-section-header">chapter2.md</h1>
<h1>Chapter 2</h1>
<p>Content...</p>

<h1 class="document-section-header">chapter3.md</h1>
<h1>Chapter 3</h1>
<p>Content...</p>
```

---

## 8. Multi-Mode CLI Design

### CLI Argument Changes

#### Before (v0.2.1): Single File Only
```python
parser.add_argument(
    "input",
    nargs="?",  # Optional single argument
    help="Path to the input Markdown file."
)
```

#### After (v0.3.0): Multiple Files
```python
parser.add_argument(
    "input",
    nargs="*",  # Zero or more arguments
    help="Path to input Markdown file(s). Multiple files triggers batch mode.",
)
```

### Understanding `nargs` Options

```python
# No nargs (default)
parser.add_argument("file")
# Usage: cmd file.txt
# Result: args.file = "file.txt"

# nargs="?"  - Zero or one
parser.add_argument("file", nargs="?")
# Usage: cmd file.txt  → args.file = "file.txt"
# Usage: cmd           → args.file = None

# nargs="*"  - Zero or more (returns list)
parser.add_argument("files", nargs="*")
# Usage: cmd                    → args.files = []
# Usage: cmd f1.txt             → args.files = ["f1.txt"]
# Usage: cmd f1.txt f2.txt      → args.files = ["f1.txt", "f2.txt"]

# nargs="+"  - One or more (returns list)
parser.add_argument("files", nargs="+")
# Usage: cmd                    → ERROR (at least one required)
# Usage: cmd f1.txt             → args.files = ["f1.txt"]
# Usage: cmd f1.txt f2.txt      → args.files = ["f1.txt", "f2.txt"]
```

**Why we use `nargs="*"`**:
- Allows `md2pdf --theme-list` (zero files, just show themes)
- Allows `md2pdf file.md` (single file)
- Allows `md2pdf f1.md f2.md` (multiple files)

**Why not `nargs="+"`?**
- Would require at least one file
- `md2pdf --theme-list` would fail!

### New CLI Arguments

```python
# Batch mode output directory
parser.add_argument(
    "--output-dir",
    help="Output directory for batch mode (default: same directory as each input file)",
)

# Merge mode flag
parser.add_argument(
    "--merge",
    action="store_true",
    help="Merge multiple input files into a single PDF (requires 2+ files)",
)

# Disable page breaks in merge mode
parser.add_argument(
    "--no-auto-break",
    action="store_true",
    help="Disable automatic page breaks between merged documents (merge mode only)",
)
```

### Mode Detection Logic

```python
try:
    # Determine conversion mode
    if args.merge:
        # MERGE MODE: Combine files into one PDF
        if len(args.input) < 2:
            print("Error: Merge mode requires at least 2 input files.",
                  file=sys.stderr)
            sys.exit(1)

        auto_break = not args.no_auto_break
        convert_merge(
            args.input, args.output, args.css, args.theme, auto_break, args.preview
        )

    elif len(args.input) > 1:
        # BATCH MODE: Convert files to separate PDFs
        convert_batch(
            args.input, args.output_dir, args.css, args.theme, args.preview
        )

    else:
        # SINGLE FILE MODE: Original behavior
        convert_md_to_pdf(
            args.input[0], args.output, args.css, args.theme, args.preview
        )
```

**Decision tree**:
```
Is --merge specified?
├─ Yes → MERGE MODE
│   └─ Check: 2+ files? ✓ or ✗
│
└─ No → How many input files?
    ├─ 0 files → ERROR (unless --theme-list)
    ├─ 1 file  → SINGLE MODE
    └─ 2+ files → BATCH MODE
```

### Flag Validation and Warnings

```python
# In MERGE mode:
if args.output_dir:
    print(
        "Warning: --output-dir flag is ignored in merge mode. Use --output instead.",
        file=sys.stderr,
    )

# In BATCH mode:
if args.output:
    print(
        "Warning: --output flag is ignored in batch mode. Use --output-dir instead.",
        file=sys.stderr,
    )

# In SINGLE mode:
if args.output_dir:
    print(
        "Warning: --output-dir flag is ignored in single file mode. Use --output instead.",
        file=sys.stderr,
    )

if args.no_auto_break:
    print(
        "Warning: --no-auto-break flag is only valid in merge mode.",
        file=sys.stderr,
    )
```

**User-friendly design**:
- Don't fail silently (tell user about ignored flags)
- Suggest correct flag for their use case
- Help users learn the correct command patterns

---

## 9. Error Recovery in Batch Operations

### The Pattern: Continue on Failure

```python
converted_files = []  # Successes
failed_files = []     # Failures

for input_file in input_files:
    try:
        # Process file
        result = process(input_file)
        converted_files.append(result)
        print(f"[OK] {input_file}")

    except Exception as e:
        failed_files.append((input_file, str(e)))
        print(f"[FAILED] {input_file}: {e}", file=sys.stderr)
        # Notice: No 'raise' - we continue!

# Summary at the end
print(f"Success: {len(converted_files)}, Failed: {len(failed_files)}")
```

### Why This Pattern?

**Scenario**: User converts 100 files, file #15 has an error.

❌ **Without error recovery**:
```python
for file in files:
    convert(file)  # Raises exception on error
# Result: 14 files converted, program crashes, user sad
```

✅ **With error recovery**:
```python
for file in files:
    try:
        convert(file)
    except Exception as e:
        log_error(file, e)
        continue
# Result: 99 files converted, 1 failed (reported), user happy
```

### Storing Error Information

```python
failed_files.append((input_file, str(e)))
#                    ↓            ↓
#                    filename     error message
```

**Why tuple?**
- Associates file with its error
- Easy to iterate later for reporting
- Immutable (can't accidentally modify)

**Why `str(e)`?**
```python
# Exception objects become strings
try:
    open("missing.txt")
except FileNotFoundError as e:
    print(str(e))
    # Output: [Errno 2] No such file or directory: 'missing.txt'
```

### Error Reporting

```python
if failed_files:
    print("\nFailed files:")
    for input_file, error in failed_files:
        print(f"  - {input_file}: {error}")
```

**Tuple unpacking in action**:
```python
failed_files = [
    ("file1.md", "File not found"),
    ("file2.md", "Permission denied"),
]

for input_file, error in failed_files:
    # input_file = "file1.md"
    # error = "File not found"
    print(f"  - {input_file}: {error}")
```

### When to Use Broad Exception Catching

**✅ Good use cases**:
1. **Batch processing** (our case)
   - Want to process as many items as possible
   - Report all errors at the end

2. **Top-level error handlers**
   ```python
   def main():
       try:
           run_application()
       except Exception as e:
           log_error(e)
           display_user_friendly_message()
   ```

3. **Background tasks**
   ```python
   def process_queue():
       for task in tasks:
           try:
               execute(task)
           except Exception as e:
               retry_queue.add(task)
   ```

**❌ Bad use cases**:
1. **Silent failures**
   ```python
   try:
       critical_operation()
   except Exception:
       pass  # Never do this!
   ```

2. **Single operations**
   ```python
   try:
       user_login(username, password)
   except Exception:  # Too broad!
       print("Login failed")
   # Better: catch specific exceptions
   ```

---

## 10. Tuple Unpacking and List Comprehensions

### Tuple Unpacking Patterns

#### Basic Unpacking
```python
# Creating a tuple
point = (10, 20)

# Unpacking
x, y = point
# x = 10, y = 20
```

#### Function Returns
```python
def get_user_info():
    return "Alice", 30, "alice@example.com"
    # Returns a tuple: ("Alice", 30, "alice@example.com")

# Unpacking the return value
name, age, email = get_user_info()
```

#### Unpacking in Loops
```python
users = [
    ("Alice", 30),
    ("Bob", 25),
    ("Charlie", 35),
]

for name, age in users:
    print(f"{name} is {age} years old")
```

#### Combining with `enumerate()`
```python
files = ["a.md", "b.md", "c.md"]

for i, filename in enumerate(files):
    print(f"{i}: {filename}")
# Output:
# 0: a.md
# 1: b.md
# 2: c.md
```

#### Complex Unpacking (Our Use Case)
```python
html_bodies = [
    ("file1.md", "<h1>Title</h1>"),
    ("file2.md", "<h1>Another</h1>"),
]

for i, (filename, html) in enumerate(html_bodies):
    # i = index (0, 1, ...)
    # filename = "file1.md", "file2.md", ...
    # html = "<h1>Title</h1>", ...
    print(f"File {i}: {filename}")
```

### List Comprehensions

#### Basic Pattern
```python
# Traditional loop
numbers = []
for i in range(10):
    numbers.append(i * 2)

# List comprehension (same result)
numbers = [i * 2 for i in range(10)]
```

#### With Conditions
```python
# Only even numbers
evens = [i for i in range(10) if i % 2 == 0]
# [0, 2, 4, 6, 8]

# Only positive numbers
values = [-2, -1, 0, 1, 2]
positives = [x for x in values if x > 0]
# [1, 2]
```

#### Transformations
```python
# Uppercase all names
names = ["alice", "bob", "charlie"]
upper_names = [name.upper() for name in names]
# ["ALICE", "BOB", "CHARLIE"]

# Get file stems
from pathlib import Path
files = [Path("a.md"), Path("b.md"), Path("c.md")]
stems = [f.stem for f in files]
# ["a", "b", "c"]
```

#### In md2pdf Code
```python
# List available themes (from LEARNING_GUIDE_V010.md)
def _list_available_themes() -> list[str]:
    themes_dir = _get_themes_directory()
    if not themes_dir.exists():
        return []

    # Get all .css files and remove extension
    return [f.stem for f in themes_dir.glob("*.css")]
    #      ↓
    #      For each file in *.css, get its stem (name without extension)
```

**Breaking it down**:
```python
# Long form:
themes = []
for f in themes_dir.glob("*.css"):
    themes.append(f.stem)
return themes

# Comprehension (same thing, more concise):
return [f.stem for f in themes_dir.glob("*.css")]
```

---

## 11. Design Patterns in Action

### 1. DRY Principle (Don't Repeat Yourself)

**Before**:
```python
def convert_md_to_pdf(...):
    engine_path = pdf_engine.find_wkhtmltopdf()
    pdf_config = pdf_engine.create_pdf_configuration(engine_path)
    css_content = theme_manager.load_css(custom_css, theme)
    # ...

def convert_batch(...):
    engine_path = pdf_engine.find_wkhtmltopdf()  # Duplicate!
    pdf_config = pdf_engine.create_pdf_configuration(engine_path)
    css_content = theme_manager.load_css(custom_css, theme)
    # ...
```

**After**:
```python
def _setup_conversion_environment(custom_css, theme):
    engine_path = pdf_engine.find_wkhtmltopdf()
    pdf_config = pdf_engine.create_pdf_configuration(engine_path)
    css_content = theme_manager.load_css(custom_css, theme)
    return pdf_config, css_content

# All functions call this
def convert_md_to_pdf(...):
    pdf_config, css_content = _setup_conversion_environment(...)

def convert_batch(...):
    pdf_config, css_content = _setup_conversion_environment(...)
```

### 2. Single Responsibility Principle

Each function has ONE clear job:

```python
_setup_conversion_environment()  # Setup PDF engine and CSS
_process_single_file()           # Process one markdown file to HTML
_merge_html_bodies()             # Merge HTML bodies with breaks

convert_md_to_pdf()              # Orchestrate single file conversion
convert_batch()                  # Orchestrate batch conversion
convert_merge()                  # Orchestrate merge conversion
```

**Benefits**:
- Easy to test each piece
- Easy to understand what each does
- Easy to reuse in different contexts

### 3. Fail Fast Principle

```python
def convert_batch(input_files, ...):
    # Check inputs immediately
    if not input_files:
        print("Error: No input files specified")
        return  # Fail fast!

    # Validate theme early
    if not custom_css:
        theme_manager.validate_theme(theme)  # Fail before expensive setup

    # Now do expensive operations
    pdf_config, css_content = _setup_conversion_environment(...)
```

**Why fail fast?**
- Don't waste time on doomed operations
- Give user quick feedback
- Easier to debug (error is close to cause)

### 4. Guard Clauses (Early Returns)

```python
def process_data(data):
    # ❌ Bad: Nested if statements
    if data:
        if validate(data):
            if transform(data):
                return save(data)
            else:
                return None
        else:
            return None
    else:
        return None

# ✅ Good: Guard clauses
def process_data(data):
    if not data:
        return None  # Guard clause

    if not validate(data):
        return None  # Guard clause

    if not transform(data):
        return None  # Guard clause

    return save(data)  # Main logic, not nested
```

### 5. Separation of Concerns

```python
# ✅ Good: Each module has clear responsibility
file_operations.validate_input_file(path)       # File I/O
markdown_processor.markdown_to_html(content)    # Markdown processing
pdf_engine.convert_html_to_pdf(html, path)     # PDF generation
theme_manager.load_css(theme)                   # Theme management

# ❌ Bad: Everything in one function
def do_everything(path):
    # Validate file
    # Read markdown
    # Convert to HTML
    # Load CSS
    # Generate PDF
    # ... 500 lines later ...
```

### 6. Error Accumulation Pattern

```python
successes = []
failures = []

for item in items:
    try:
        result = process(item)
        successes.append(result)
    except Exception as e:
        failures.append((item, e))

# Report at the end
report(successes, failures)
```

**Use when**:
- Processing multiple independent items
- Want to process as many as possible
- Need summary report at end

---

## 12. Performance Optimization

### 1. Setup Once, Use Many Times

**Inefficient** (setup per file):
```python
for file in files:
    pdf_config = setup_pdf_engine()  # Slow!
    css = load_css()                 # Slow!
    convert(file, pdf_config, css)
```

**Efficient** (setup once):
```python
pdf_config = setup_pdf_engine()  # Once
css = load_css()                 # Once

for file in files:
    convert(file, pdf_config, css)  # Fast!
```

**Impact**: With 100 files, this is ~100x faster!

### 2. List Join vs String Concatenation

**Inefficient**:
```python
result = ""
for part in parts:
    result += part  # Creates new string each time!
    # With 1000 parts: creates 1000 string objects
```

**Efficient**:
```python
result = "".join(parts)  # Creates 1 string object
```

**Why?**
- Strings are immutable (can't be changed)
- `+=` creates a new string with all the old data + new data
- `join()` calculates final size, allocates once, copies once

### 3. Generator vs List (Bonus Topic)

**When you need all items**:
```python
# List comprehension (good)
items = [process(x) for x in data]
# All items created immediately, stored in memory
```

**When you process one at a time**:
```python
# Generator expression (better for large data)
items = (process(x) for x in data)
# Items created on-demand as you iterate
```

**Example**:
```python
# List: All 1 million items in memory
squares = [x*x for x in range(1000000)]

# Generator: One item at a time
squares = (x*x for x in range(1000000))

for square in squares:
    print(square)  # Generated on-demand
```

---

## 13. Testing Your Understanding

### Quiz Questions

#### Question 1: Type Hints
What does this function signature tell you?
```python
def _merge_html_bodies(
    html_bodies: list[tuple[str, str]],
    auto_break: bool = True
) -> str:
```

<details>
<summary>Answer</summary>

- **Parameter 1** (`html_bodies`): A list of tuples, where each tuple contains two strings
  - Example: `[("file1.md", "<html>..."), ("file2.md", "<html>...")]`
- **Parameter 2** (`auto_break`): A boolean with default value `True`
- **Returns**: A single string
- Function merges HTML bodies into one string, optionally adding page breaks

</details>

#### Question 2: Tuple Unpacking
What gets printed?
```python
data = [("Alice", 30), ("Bob", 25)]

for i, (name, age) in enumerate(data):
    if i == 1:
        print(f"{name}: {age}")
```

<details>
<summary>Answer</summary>

**Output**: `Bob: 25`

Breakdown:
- Iteration 0: i=0, name="Alice", age=30 (if condition false)
- Iteration 1: i=1, name="Bob", age=25 (if condition true, prints)

</details>

#### Question 3: Error Handling
Why do we catch broad `Exception` in batch processing but not in single file mode?

<details>
<summary>Answer</summary>

**Batch processing**: We want to continue processing remaining files even if one fails. Catching all exceptions ensures we process as many files as possible and report all errors at the end.

**Single file mode**: We want to know exactly what went wrong. Catching specific exceptions (FileNotFoundError, PermissionError, etc.) gives us precise error information and lets unexpected errors bubble up for debugging.

</details>

#### Question 4: nargs Parameter
What's the difference between `nargs="*"` and `nargs="+"`?

<details>
<summary>Answer</summary>

- **`nargs="*"`**: Zero or more arguments (can be empty list)
  - `cmd` → `args.input = []` (OK)
  - `cmd file.md` → `args.input = ["file.md"]` (OK)

- **`nargs="+"`**: One or more arguments (requires at least one)
  - `cmd` → ERROR
  - `cmd file.md` → `args.input = ["file.md"]` (OK)

We use `"*"` to allow `md2pdf --theme-list` without requiring input files.

</details>

#### Question 5: List Building
Why is this pattern used for merging HTML?
```python
merged_parts = []
for part in parts:
    merged_parts.append(part)
return "\n".join(merged_parts)
```

Instead of:
```python
result = ""
for part in parts:
    result += part
return result
```

<details>
<summary>Answer</summary>

**Performance**: Strings are immutable in Python. Each `+=` creates a new string object, copying all previous data. With many parts, this is very slow.

List append is fast (just adds a reference). `join()` creates the final string in one operation.

**Example impact**: Merging 1000 parts:
- String concatenation: ~1000 string objects created
- List + join: ~1 string object created

</details>

#### Question 6: Early Returns
What pattern is this, and why use it?
```python
def process(data):
    if not data:
        return None

    if not validate(data):
        return None

    # Main logic here...
```

<details>
<summary>Answer</summary>

**Pattern**: Guard clauses (early returns)

**Benefits**:
1. Reduces nesting (no deep if/else blocks)
2. Error conditions checked first
3. Main logic isn't indented deeply
4. Easier to read and maintain
5. Clear what's an error vs normal flow

</details>

---

## Exercises to Deepen Learning

### Exercise 1: Add Verbose Mode

Add a `--verbose` flag that shows detailed processing information.

**Requirements**:
- Show when setup starts/ends
- Show file size for each input file
- Show processing time per file
- Show total elapsed time

**Hints**:
```python
import time

# In argparse
parser.add_argument("--verbose", "-v", action="store_true",
                    help="Show detailed processing information")

# In convert_batch
if args.verbose:
    print(f"Processing {input_file} ({input_path.stat().st_size} bytes)...")
    start_time = time.time()

# After conversion
if args.verbose:
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")
```

### Exercise 2: Add Progress Bar

Use the `tqdm` library to show a progress bar during batch processing.

**Installation**:
```bash
pip install tqdm
```

**Hints**:
```python
from tqdm import tqdm

# Wrap your loop
for input_file in tqdm(input_files, desc="Converting files"):
    # Process file...
```

### Exercise 3: Add Dry-Run Mode

Add a `--dry-run` flag that shows what would be done without actually doing it.

**Requirements**:
- Show which files would be processed
- Show where output files would be created
- Don't actually create any PDFs
- Show merge structure if using `--merge`

**Hints**:
```python
parser.add_argument("--dry-run", action="store_true",
                    help="Show what would be done without doing it")

if args.dry_run:
    print(f"Would convert '{input_file}' to '{output_file}'")
    continue  # Skip actual conversion
```

### Exercise 4: Add Table of Contents to Merged PDFs

When merging files, create a table of contents at the beginning listing all merged files.

**Requirements**:
- Show list of all source files
- Add page numbers (if possible)
- Put TOC on its own page

**Hints**:
```python
def _create_toc(html_bodies):
    toc_html = "<h1>Table of Contents</h1>\n<ul>\n"
    for filename, _ in html_bodies:
        toc_html += f"<li>{filename}</li>\n"
    toc_html += "</ul>\n<div class='page-break'></div>\n"
    return toc_html

# In convert_merge, before merging
toc = _create_toc(html_bodies)
merged_html_body = toc + _merge_html_bodies(html_bodies, auto_break)
```

### Exercise 5: Add File Filtering

Add glob pattern support for input files.

**Requirements**:
- Support patterns like `docs/*.md`
- Support multiple patterns
- Warn if pattern matches no files

**Hints**:
```python
from pathlib import Path

def expand_patterns(patterns):
    """Expand glob patterns to file paths."""
    files = []
    for pattern in patterns:
        matches = list(Path(".").glob(pattern))
        if not matches:
            print(f"Warning: Pattern '{pattern}' matched no files")
        files.extend(matches)
    return [str(f) for f in files]

# In main
actual_files = expand_patterns(args.input)
convert_batch(actual_files, ...)
```

---

## Key Takeaways

### What We Learned

1. **Shared helper functions** eliminate code duplication and improve efficiency
2. **Tuple unpacking** makes code more readable and Pythonic
3. **Error recovery** in batch operations provides better user experience
4. **Early validation** (fail fast) saves time and provides quick feedback
5. **List building + join** is more efficient than string concatenation
6. **Guard clauses** reduce nesting and improve readability
7. **Type hints** make code self-documenting and enable better tooling
8. **Mode detection** creates flexible CLIs that adapt to user input

### Design Principles Applied

✅ **DRY (Don't Repeat Yourself)**: Shared helper functions
✅ **Single Responsibility**: Each function does one thing
✅ **Fail Fast**: Validate early, fail with helpful messages
✅ **Separation of Concerns**: Each module has clear purpose
✅ **User-Friendly**: Helpful warnings, progress tracking, summaries
✅ **Error Recovery**: Continue processing when possible

### Python Features Mastered

- Type hints with `list`, `tuple`, `Optional`
- Tuple unpacking in loops
- `enumerate()` for index + value
- List comprehensions
- `nargs` in argparse
- Early returns / guard clauses
- Context of broad vs specific exception handling
- `pathlib` for cross-platform paths
- f-strings with expressions

---

## Resources for Further Learning

### Python Documentation
- **Type Hints**: https://docs.python.org/3/library/typing.html
- **pathlib**: https://docs.python.org/3/library/pathlib.html
- **argparse**: https://docs.python.org/3/library/argparse.html
- **Exception Handling**: https://docs.python.org/3/tutorial/errors.html

### Design Patterns
- **SOLID Principles**: Single Responsibility, DRY, etc.
- **Error Handling Patterns**: Fail fast, error accumulation
- **Iterator Patterns**: Generators, list comprehensions

### Next Steps
1. Read through the actual source code in `md2pdf/core.py`
2. Try the exercises above
3. Look at the test suite to see how the code is tested
4. Experiment with adding your own features!

---

**Happy Learning!** 🚀🐍

*Remember: The best way to learn is by doing. Don't just read - try modifying the code and see what happens!*
