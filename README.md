# md2pdf

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

Before installing md2pdf, you need to install **wkhtmltopdf**:

### Windows

Download and install from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)

The default installation path is `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

### Linux

```bash
sudo apt-get install wkhtmltopdf  # Debian/Ubuntu
sudo yum install wkhtmltopdf      # CentOS/RHEL
```

### macOS

```bash
brew install wkhtmltopdf
```

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

## Configuration

If `wkhtmltopdf` is installed in a different location, edit [md2pdf.py](md2pdf.py#L9-L11):

```python
config = pdfkit.configuration(
    wkhtmltopdf="/path/to/wkhtmltopdf"
)
```

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

## Requirements

- Python 3.6+
- markdown >= 3.4
- pdfkit >= 1.0.0
- wkhtmltopdf (system dependency)

## Troubleshooting

### wkhtmltopdf not found

If you get an error about wkhtmltopdf not being found, ensure:

1. wkhtmltopdf is installed on your system
2. The path in the configuration (line 9-11 in [md2pdf.py](md2pdf.py)) matches your installation

### File not found error

Ensure the input Markdown file exists and the path is correct.

### Permission errors

Make sure you have write permissions in the output directory.

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
