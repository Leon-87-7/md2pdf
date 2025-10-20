# md2pdf

![md2pdf conveyor belt converting Markdown to PDF documents, tacking in md files and outputting PDFs into a folder.](python_md2pdf.v0.2.png)
**md2pdf** is a simple application that converts Markdown files into PDF documents. It provides an easy-to-use interface for generating professional-looking PDFs from your Markdown content, supporting custom styling and formatting options. Ideal for documentation, reports, and sharing readable documents across platforms.

## Features

- Convert Markdown to PDF with a single command
- Beautiful default gradient styling with professional typography
- Support for custom CSS styling
- Handles tables, code blocks, lists, and images
- Syntax highlighting for code blocks
- Table of contents generation
- Responsive page layout (A4 size with proper margins)

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
md2pdf input.md -o output.pdf
```

### Custom CSS Styling

Use your own CSS file for custom styling:

```bash
md2pdf notes.md --css custom-style.css
```

### Preview Mode

Automatically open the PDF after conversion:

```bash
md2pdf document.md -p
```

This will generate the PDF and immediately open it in your system's default PDF viewer.

### Command Line Options

```
usage: md2pdf [-h] [-o OUTPUT] [--css CSS] [-p] [-v] input

positional arguments:
  input                 Path to the input Markdown file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output PDF file (default: same name as input)
  --css CSS             Path to a custom CSS file for styling the PDF
  -p, --preview         Open the PDF with the default viewer after conversion
  -v, --version         show program's version number and exit
```

## Examples

### Example 1: Simple Conversion

```bash
md2pdf README.md
```

### Example 2: Custom Output Location

```bash
md2pdf docs/guide.md -o pdfs/user-guide.pdf
```

### Example 3: Custom Styling

```bash
md2pdf report.md --css styles/corporate.css
```

### Example 4: Preview Mode

```bash
md2pdf document.md -p
```

## Default Styling

The default CSS includes:

- Gradient backgrounds with modern color schemes
- Professional typography (Segoe UI font family)
- Styled headings with gradient backgrounds
- Code blocks with syntax highlighting
- Responsive tables with alternating row colors
- Styled blockquotes and links
- Image borders and shadows

## Custom CSS

To create a custom CSS file, you can start with the default styling and modify it. The CSS should include styles for:

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

- Python 3.6+
- markdown >= 3.4
- pdfkit >= 1.0.0
- wkhtmltopdf (system dependency)

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

## Future features

### Priority Order:

- Preview Mode (Priority 1) ✅ COMPLETED
  Auto-open PDF after conversion with -p flag

- Auto-detect wkhtmltopdf (Priority 2) ✅ COMPLETED
  Automatically find wkhtmltopdf installation across platforms
  Checks system PATH and common installation locations for Windows, macOS, and Linux
  Provides helpful platform-specific error messages if not found

- Page Breaks (Priority 3) ✅ COMPLETED
  Support explicit page break markers in Markdown
  Supports multiple formats: <!-- pagebreak -->, <!-- page-break -->, case-insensitive
  Uses CSS page-break-after to create new pages in PDF

- Multiple CSS Themes via --theme (Priority 4) ⏳ NEXT
  Pre-built themes: gradient (current), minimal, corporate, academic, dark
  Select with --theme flag

- Batch Processing (Priority 5)
  Convert multiple files to separate PDFs
  md2pdf file1.md file2.md file3.md → creates file1.pdf, file2.pdf, file3.pdf

- Multiple Input Files (Priority 6)
  Combine multiple MD files into single PDF
  md2pdf chapter1.md chapter2.md --merge -o book.pdf

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
