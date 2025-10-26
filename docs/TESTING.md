# Testing Guide for md2pdf

This document provides comprehensive information about the test suite for md2pdf.

## Overview

The md2pdf project uses **pytest** as its testing framework with comprehensive unit and integration tests achieving **84% code coverage**.

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_cli.py              # CLI interface tests
├── test_config.py           # Configuration module tests
├── test_file_operations.py  # File I/O tests
├── test_markdown_processor.py # Markdown processing tests
├── test_pdf_engine.py       # PDF generation engine tests
└── test_theme_manager.py    # Theme management tests
```

## Installation

Install the development dependencies:

```bash
pip install -e ".[dev]"
```

This installs:
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.11.0` - Mocking utilities

## Running Tests

### Run all tests

```bash
pytest
```

### Run tests with verbose output

```bash
pytest -v
```

### Run tests without coverage

```bash
pytest --no-cov
```

### Run specific test file

```bash
pytest tests/test_cli.py
```

### Run specific test class

```bash
pytest tests/test_cli.py::TestDisplayThemes
```

### Run specific test function

```bash
pytest tests/test_cli.py::TestDisplayThemes::test_display_themes_with_themes
```

### Run tests matching a pattern

```bash
pytest -k "theme"
```

## Coverage Reports

### View coverage in terminal

```bash
pytest
```

The coverage report is displayed after test execution.

### Generate HTML coverage report

```bash
pytest
# Then open htmlcov/index.html in your browser
```

### Coverage by module

Current coverage (as of last run):

| Module                    | Statements | Missing | Coverage |
|---------------------------|------------|---------|----------|
| `__init__.py`             | 4          | 0       | 100%     |
| `cli.py`                  | 31         | 1       | 97%      |
| `config.py`               | 9          | 0       | 100%     |
| `markdown_processor.py`   | 11         | 0       | 100%     |
| `pdf_engine.py`           | 45         | 0       | 100%     |
| `file_operations.py`      | 44         | 5       | 89%      |
| `theme_manager.py`        | 47         | 8       | 83%      |
| `core.py`                 | 22         | 18      | 18%      |
| **TOTAL**                 | **216**    | **35**  | **84%**  |

## Test Categories

### Unit Tests

Tests for individual functions and classes in isolation:

- **test_config.py**: Configuration constants validation
- **test_markdown_processor.py**: Markdown to HTML conversion
- **test_theme_manager.py**: Theme loading and CSS management
- **test_pdf_engine.py**: PDF generation utilities
- **test_file_operations.py**: File validation and I/O

### Integration Tests

Tests for CLI and core workflow:

- **test_cli.py**: Command-line argument parsing and execution
- Tests for core.py integration (to be added)

## Test Fixtures

Common fixtures are defined in `conftest.py`:

### `temp_dir`
Creates a temporary directory for test files.

```python
def test_example(temp_dir):
    file = temp_dir / "test.md"
    file.write_text("# Test")
```

### `sample_markdown`
Provides sample markdown content with various features.

```python
def test_example(sample_markdown):
    assert "# Test Document" in sample_markdown
```

### `sample_markdown_file`
Creates a temporary markdown file with sample content.

```python
def test_example(sample_markdown_file):
    assert sample_markdown_file.exists()
```

### `sample_css` and `sample_css_file`
Provide sample CSS content and files for testing.

## Mocking

Tests use `unittest.mock` and `pytest-mock` for isolating external dependencies:

### Mocking file system operations

```python
@patch("pathlib.Path.exists")
def test_example(mock_exists):
    mock_exists.return_value = True
```

### Mocking wkhtmltopdf

```python
@patch("pdfkit.from_string")
def test_pdf_generation(mock_from_string):
    mock_from_string.return_value = None
```

### Mocking platform-specific behavior

```python
@patch("platform.system")
def test_platform(mock_system):
    mock_system.return_value = "Linux"
```

## Writing New Tests

### Test naming convention

- Files: `test_<module>.py`
- Classes: `Test<Feature>`
- Functions: `test_<specific_behavior>`

### Example test structure

```python
"""Tests for md2pdf.my_module module."""

import pytest
from md2pdf import my_module


class TestMyFeature:
    """Test my feature functionality."""

    def test_basic_behavior(self):
        """Test basic behavior of my feature."""
        result = my_module.my_function("input")
        assert result == "expected"

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_module.my_function(None)

    def test_with_fixture(self, temp_dir):
        """Test using a fixture."""
        file = temp_dir / "test.txt"
        file.write_text("test")
        assert my_module.process_file(file) is True
```

### Assertion best practices

- Use descriptive assertions
- Test one thing per test
- Use `pytest.raises()` for exception testing
- Use parametrize for similar tests with different inputs

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert my_function(input) == expected
```

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest
```

## Test Coverage Goals

- **Overall**: Maintain >80% coverage
- **Critical modules**: Aim for >90% coverage
  - `pdf_engine.py` ✅ 100%
  - `markdown_processor.py` ✅ 100%
  - `config.py` ✅ 100%
- **CLI**: >95% coverage ✅ 97%

## Common Issues

### Tests fail with "wkhtmltopdf not found"

This is expected. Tests mock wkhtmltopdf to avoid requiring it as a test dependency.

### Coverage shows missing lines in error handling

Some error paths are intentionally difficult to test (e.g., OS-level errors). Focus on testing the happy path and critical error cases.

### Tests are slow

Use `pytest -n auto` with pytest-xdist for parallel execution:

```bash
pip install pytest-xdist
pytest -n auto
```

## Future Improvements

- [ ] Add integration tests for `core.py` (currently 18% coverage)
- [ ] Add end-to-end tests that generate actual PDFs
- [ ] Add performance benchmarks
- [ ] Add tests for __main__.py entry point
- [ ] Increase theme_manager.py coverage from 83% to >90%
- [ ] Add mutation testing with `mutmut`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)