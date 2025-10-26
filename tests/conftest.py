"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path

import pytest  # type: ignore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Test Document

This is a test paragraph with **bold** and *italic* text.

## Section 1

- Item 1
- Item 2
- Item 3

### Code Example

```python
def hello():
    print("Hello, World!")
```

## Section 2

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

<!-- pagebreak -->

## Page 2

This is on a new page.
"""


@pytest.fixture
def sample_markdown_file(temp_dir, sample_markdown):
    """Create a temporary markdown file with sample content."""
    md_file = temp_dir / "test.md"
    md_file.write_text(sample_markdown, encoding="utf-8")
    return md_file


@pytest.fixture
def sample_css():
    """Sample CSS content for testing."""
    return """
body {
    font-family: Arial, sans-serif;
    color: #333;
}

h1 {
    color: #0066cc;
}
"""


@pytest.fixture
def sample_css_file(temp_dir, sample_css):
    """Create a temporary CSS file with sample content."""
    css_file = temp_dir / "test.css"
    css_file.write_text(sample_css, encoding="utf-8")
    return css_file


@pytest.fixture
def mock_wkhtmltopdf_path(tmp_path):
    """Mock path to wkhtmltopdf executable."""
    if Path.cwd().drive:  # Windows
        return "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    else:
        return "/usr/local/bin/wkhtmltopdf"
