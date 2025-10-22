#!/usr/bin/env python3
"""Quick test script to verify refactored md2pdf.py works correctly."""

import tempfile
from pathlib import Path
from md2pdf import (
    find_wkhtmltopdf,
    process_page_breaks,
    _load_css,
    _get_themes_directory,
    convert_md_to_pdf,
    __version__,
)


def test_version():
    """Test version is accessible."""
    assert __version__ == "0.1.0"
    print("[PASS] Version check passed")


def test_find_wkhtmltopdf():
    """Test wkhtmltopdf detection."""
    result = find_wkhtmltopdf()
    print(
        f"[PASS] wkhtmltopdf detection: {result if result else 'Not found (OK for test)'}"
    )


def test_process_page_breaks():
    """Test page break processing."""
    test_cases = [
        ("Text<!-- pagebreak -->More", '<div class="page-break"></div>'),
        ("Text<!-- page-break -->More", '<div class="page-break"></div>'),
        ("Text<!-- PAGEBREAK -->More", '<div class="page-break"></div>'),
        ("Text<!--page_break-->More", '<div class="page-break"></div>'),
    ]

    for html, expected in test_cases:
        result = process_page_breaks(html)
        assert expected in result, f"Failed for {html}: {result}"

    print("[PASS] Page break processing passed")


def test_load_css():
    """Test CSS loading from themes and custom files."""
    # Test loading default theme
    themes_dir = _get_themes_directory()
    default_theme_path = themes_dir / "default.css"

    if default_theme_path.exists():
        css = _load_css(theme="default")
        assert len(css) > 0, "CSS content should not be empty"
        assert "@page" in css or "body" in css, "CSS should contain styling rules"
        print("[PASS] Default theme loading passed")
    else:
        print(f"[SKIP] Default theme not found at {default_theme_path}")

    # Test loading custom CSS file
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_css_path = Path(tmpdir) / "custom.css"
        custom_css_path.write_text("body { color: red; }", encoding="utf-8")

        css = _load_css(custom_css=str(custom_css_path))
        assert "color: red" in css
        print("[PASS] Custom CSS loading passed")

    # Test non-existent custom CSS (should exit)
    try:
        _load_css(custom_css="nonexistent.css")
        assert False, "Should have exited for non-existent CSS"
    except SystemExit as e:
        assert e.code == 1
        print("[PASS] Non-existent CSS validation passed")


def test_convert_basic():
    """Test basic markdown to PDF conversion."""
    wkhtmltopdf_path = find_wkhtmltopdf()
    if not wkhtmltopdf_path:
        print("[SKIP] PDF conversion test - wkhtmltopdf not found")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test markdown file
        md_file = Path(tmpdir) / "test.md"
        md_file.write_text(
            "# Test\n\nThis is a test.\n\n<!-- pagebreak -->\n\n## Page 2",
            encoding="utf-8",
        )

        pdf_file = Path(tmpdir) / "test.pdf"

        # Convert
        convert_md_to_pdf(str(md_file), str(pdf_file))

        # Verify PDF was created
        assert pdf_file.exists(), "PDF file was not created"
        assert pdf_file.stat().st_size > 0, "PDF file is empty"

        print(f"[PASS] PDF conversion passed (size: {pdf_file.stat().st_size} bytes)")


def test_validation_errors():
    """Test input validation."""

    # Test non-existent file
    try:
        convert_md_to_pdf("nonexistent_file.md")
        assert False, "Should have exited"
    except SystemExit as e:
        assert e.code == 1
        print("[PASS] Non-existent file validation passed")

    # Test with temporary directory (not a file)
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            convert_md_to_pdf(tmpdir)
            assert False, "Should have exited"
        except SystemExit as e:
            assert e.code == 1
            print("[PASS] Directory validation passed")


if __name__ == "__main__":
    print("Running refactoring tests...\n")

    test_version()
    test_find_wkhtmltopdf()
    test_process_page_breaks()
    test_load_css()
    test_convert_basic()
    test_validation_errors()

    print("\n All tests passed!")
