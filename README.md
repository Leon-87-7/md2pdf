# md2pdf

![md2pdf conveyor belt converting Markdown to PDF documents, tacking in md files and outputting PDFs into a folder.](python_md2pdf.v0.2.png)
**md2pdf** is a simple application that converts Markdown files into PDF documents. It provides an easy-to-use interface for generating professional-looking PDFs from your Markdown content, supporting custom styling and formatting options. Ideal for documentation, reports, and sharing readable documents across platforms.

## Features

- Convert Markdown to PDF with a single command
- **Batch processing** - convert multiple files to separate PDFs
- **Merge mode** - combine multiple Markdown files into a single PDF
- **5 pre-built themes** (default, dark, light, minimal, professional)
- **Interactive theme builder** - create custom themes with guided wizard (`--create-theme`)
- **Theme discovery** with `--theme-list` flag to list all available themes
- **Accessibility-first** - built-in WCAG contrast checking for custom themes
- Beautiful default styling with professional typography
- Support for custom CSS styling
- Handles tables, code blocks, lists, and images
- Syntax highlighting for code blocks
- Table of contents generation
- Responsive page layout (A4 size with proper margins)
- Explicit page break support
- **Preview mode** (`-p`) to auto-open PDFs after generation
- **Auto-detection** of wkhtmltopdf across all platforms
- **Modular architecture** with clean separation of concerns
- **Comprehensive test suite** with 116 tests and 69% code coverage

## Prerequisites

Before using md2pdf, you need to install **wkhtmltopdf**. The tool will automatically detect your installation across all platforms.

### Windows

Download and install from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)

### Linux

```bash
sudo apt-get install wkhtmltopdf  # Debian/Ubuntu
sudo dnf install wkhtmltopdf      # Fedora
```

### macOS

```bash
brew install wkhtmltopdf
```

**Note:** md2pdf will automatically detect wkhtmltopdf in standard installation locations or from your system PATH. If not found, it will provide platform-specific installation instructions.

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd md2pdf
```

2. Install the package:

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert a Markdown file to PDF:

```bash
md2pdf document.md
```

This creates `document.pdf` in the same directory.

### Specify Output File

```bash
md2pdf input.md -on output.pdf
```

### Theme Selection

List all available themes:

```bash
md2pdf --theme-list
```

Choose from pre-built themes:

```bash
md2pdf document.md --theme default       # Default gradient theme
md2pdf document.md --theme dark          # Dark mode theme
md2pdf document.md --theme light         # Light theme
md2pdf document.md --theme minimal       # Minimal clean theme
md2pdf document.md --theme professional  # Professional business theme
```

### Creating Custom Themes

Create your own theme interactively with the built-in theme builder:

```bash
md2pdf --create-theme
```

The wizard will guide you through creating a custom theme:

```
╔══════════════════════════════════════════════╗
║     md2pdf Interactive Theme Builder         ║
╚══════════════════════════════════════════════╝

Theme name: my_theme
✓ Name available

Background color [#ffffff]: white
✓ Using: #ffffff

Text color [#000000]:
✓ Using: #000000
✓ Contrast ratio: 21:1 (Excellent - WCAG AAA)

Font family [Arial, sans-serif]: Georgia
✓ Using: Georgia

Body text size [11pt]: 12
✓ Using: 12pt

H1 heading color [#2c3e50]: #1a2332
✓ Using: #1a2332
✓ Contrast ratio: 12.8:1 (Excellent - WCAG AAA)

... (more prompts) ...

✓ CSS file created: themes/my_theme.css
✓ Theme ready to use!

Usage:
  md2pdf document.md --theme my_theme
```

**Theme Builder Features:**
- Guided prompts for 10 theme properties (colors, fonts, sizes)
- Real-time WCAG contrast checking (ensures 4.5:1 minimum ratio)
- Smart defaults - press Enter to accept
- Separate controls for H1 vs H2-H6 heading colors
- Automatic validation and conflict detection
- Generates complete CSS with all required selectors
- Works immediately with all conversion modes

**Accessibility:** All generated themes meet WCAG AA standards for color contrast, ensuring your PDFs are readable by everyone.

### Custom CSS Styling

Use your own CSS file for custom styling (takes precedence over themes):

```bash
md2pdf notes.md --css custom-style.css
```

**Note:** If both `--theme` and `--css` are specified, the custom CSS file takes precedence and a warning will be displayed.

### Preview Mode

Automatically open the PDF after conversion:

```bash
md2pdf document.md -p
```

This will generate the PDF and immediately open it in your system's default PDF viewer.

### Batch Processing

Convert multiple Markdown files to separate PDFs:

```bash
md2pdf file1.md file2.md file3.md
```

This creates `file1.pdf`, `file2.pdf`, and `file3.pdf` in the same directories as their source files.

Specify an output directory for all PDFs:

```bash
md2pdf *.md --output-dir pdfs/
```

### Merge Mode

Combine multiple Markdown files into a single PDF:

```bash
md2pdf chapter1.md chapter2.md chapter3.md --merge -on book.pdf
```

Each source file becomes a section in the merged PDF, with automatic page breaks between sections.

Disable automatic page breaks between merged sections:

```bash
md2pdf intro.md content.md --merge --no-auto-break -on document.pdf
```

### Command Line Options

```
usage: md2pdf [-h] [-on OUTPUT_NAME] [-od OUTPUT_DIR] [-th THEME] [-thl] [--create-theme]
              [-c CSS] [-p] [-m] [-nab] [-v] [input ...]

positional arguments:
  input                 Path to input Markdown file(s). Multiple files triggers batch mode

optional arguments:
  -h, --help            show this help message and exit
  -on, --output-name OUTPUT_NAME
                        Output PDF file (single file mode or merge mode only)
  -od, --output-dir OUTPUT_DIR
                        Output directory for batch mode
  -th, --theme THEME    Theme to use for styling (default: default)
                        Ignored if --css is specified
  -thl, --theme-list    List all available themes and exit
  --create-theme        Launch interactive theme builder wizard and exit
  -c, --css CSS         Path to a custom CSS file for styling the PDF
                        Takes precedence over --theme
  -p, --preview         Open the PDF with the default viewer after conversion
  -m, --merge           Merge multiple input files into a single PDF (requires 2+ files)
  -nab, --no-auto-break
                        Disable automatic page breaks between merged documents
  -v, --version         show program's version number and exit
```

## Examples

### Example 1: Simple Conversion

```bash
md2pdf README.md
```

### Example 2: Custom Output Location

```bash
md2pdf docs/guide.md -on pdfs/user-guide.pdf
```

### Example 3: Listing Available Themes

```bash
md2pdf --theme-list
```

### Example 4: Using Themes

```bash
md2pdf report.md --theme dark
md2pdf notes.md --theme minimal
md2pdf business.md --theme professional
```

### Example 5: Custom Styling

```bash
md2pdf report.md --css styles/corporate.css
```

### Example 6: Preview Mode

```bash
md2pdf document.md -p
```

### Example 7: Theme with Preview

```bash
md2pdf presentation.md --theme dark -p
```

### Example 8: Creating a Custom Theme

```bash
md2pdf --create-theme
# Follow the interactive prompts to create your theme
# Then use it:
md2pdf document.md --theme my_custom_theme
```

### Example 9: Batch Processing

Convert multiple files to separate PDFs:

```bash
md2pdf chapter1.md chapter2.md chapter3.md
```

Convert with output directory:

```bash
md2pdf docs/*.md --output-dir pdfs/ --theme professional
```

### Example 10: Merge Files into Single PDF

Merge with automatic page breaks between sections:

```bash
md2pdf intro.md methods.md results.md conclusion.md --merge -on research_paper.pdf
```

Merge without page breaks:

```bash
md2pdf part1.md part2.md --merge --no-auto-break -on continuous_document.pdf --theme dark
```

## Themes

md2pdf supports multiple pre-built themes located in the `themes/` directory. Each theme is a CSS file that can be selected using the `--theme` flag.

### Discovering Themes

List all available themes:

```bash
md2pdf --theme-list
```

Output:

```
Available themes:
  - dark
  - default
  - light
  - minimal
  - professional

Usage: md2pdf document.md --theme <theme-name>
```

### Available Themes

**default** - Gradient theme with modern styling

- Gradient backgrounds (purple/blue color scheme)
- Professional typography (Segoe UI font family)
- Styled headings with gradient backgrounds
- Code blocks with syntax highlighting
- Responsive tables with alternating row colors
- Styled blockquotes and links
- Image borders and shadows

**dark** - Dark mode theme

- Dark background (#1a1a1a) with light text
- Optimized for reduced eye strain
- Subtle styling for code blocks and tables
- Semi-transparent content boxes

**light** - Clean light theme

- White background with dark text
- Minimal styling for maximum readability
- Professional appearance for business documents

**minimal** - Ultra-minimal styling

- Black and white design
- No backgrounds or decorations
- Maximum readability
- Perfect for printing

**professional** - Business-oriented theme

- Clean, corporate styling
- Traditional typography
- Suitable for formal reports and documentation

### Theme Directory Structure

Themes are stored in the `themes/` directory:

```
md2pdf/
├── md2pdf/
│   ├── cli.py
│   ├── core.py
│   └── ...
├── themes/
│   ├── default.css
│   ├── dark.css
│   ├── light.css
│   ├── minimal.css
│   └── professional.css
```

## Custom CSS

You can create your own CSS file for complete control over styling. The CSS file takes precedence over any theme.

To create a custom CSS file, you can start with one of the existing themes from the `themes/` directory and modify it. The CSS should include styles for:

- Page layout (`@page`)
- Body content
- Headings (h1-h6)
- Paragraphs
- Lists (ul, ol)
- Tables
- Code blocks (code, pre)
- Blockquotes
- Links
- Images
- Page breaks (`.page-break` class)

## Supported Markdown Features

- Headers (H1-H6)
- Bold, italic, and strikethrough text
- Lists (ordered and unordered)
- Tables
- Code blocks with syntax highlighting
- Inline code
- Blockquotes
- Links
- Images
- Horizontal rules
- Table of contents
- **Page breaks** (using HTML comments)

### Page Breaks

You can insert explicit page breaks in your Markdown files using HTML comments. This gives you control over where pages start and end in the generated PDF.

**Supported formats:**

```markdown
<!-- pagebreak -->
<!-- page-break -->
<!-- PAGEBREAK -->
<!-- PAGE-BREAK -->
```

All formats are case-insensitive and work with or without spaces around "page" and "break".

**Example:**

```markdown
# Chapter 1

This content will be on the first page.

<!-- pagebreak -->

# Chapter 2

This content will start on a new page.

<!-- page-break -->

# Chapter 3

And this will be on a third page.
```

## Requirements

- Python 3.9+
- markdown >= 3.4
- pdfkit >= 1.0.0
- wkhtmltopdf (system dependency)

### Development Requirements

- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.11.0

## Development

### Running Tests

md2pdf includes a comprehensive test suite with **148 tests** covering all functionality.

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

For more details, see the [Testing Documentation](docs/TESTING.md).

### Architecture

For developers interested in understanding the internal structure, see the [Architecture Documentation](docs/ARCHITECTURE.md) which covers:

- Package structure and module responsibilities
- Data flow and design principles
- Testing strategy and future extensions

## Troubleshooting

### wkhtmltopdf not found

If you get an error about wkhtmltopdf not being found:

1. Install wkhtmltopdf using the instructions in the Prerequisites section
2. If installed in a non-standard location, add it to your system PATH
3. The tool will show platform-specific installation instructions automatically

The auto-detection checks:

- System PATH (works if wkhtmltopdf is in your PATH)
- Common installation locations for Windows, macOS, and Linux

### File not found error

Ensure the input Markdown file exists and the path is correct.

### Permission errors

Make sure you have write permissions in the output directory.

### Special characters in filenames

Avoid using emojis or non-UTF-8 characters in output filenames, as they may cause issues with wkhtmltopdf.

### Theme not found error

If you get an error about a theme not being found:

1. Ensure the `themes/` directory exists in the same location as `md2pdf.py`
2. Check that the theme file exists (e.g., `themes/default.css`)
3. The tool will list available themes if the requested theme is not found

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
