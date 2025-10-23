"""Tests for md2pdf.markdown_processor module."""

import pytest

from md2pdf import markdown_processor


class TestMarkdownProcessor:
    """Test markdown processing functionality."""

    def test_markdown_to_html_basic(self):
        """Test basic markdown to HTML conversion."""
        md = "# Hello World"
        html = markdown_processor.markdown_to_html(md)
        # Markdown adds id attribute to headings
        assert "<h1" in html
        assert "Hello World</h1>" in html

    def test_markdown_to_html_bold_italic(self):
        """Test bold and italic formatting."""
        md = "This is **bold** and *italic* text."
        html = markdown_processor.markdown_to_html(md)
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html

    def test_markdown_to_html_lists(self):
        """Test list conversion."""
        md = """- Item 1
- Item 2
- Item 3"""
        html = markdown_processor.markdown_to_html(md)
        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html

    def test_markdown_to_html_code_blocks(self):
        """Test code block conversion."""
        md = """```python
def hello():
    print("Hello")
```"""
        html = markdown_processor.markdown_to_html(md)
        assert "<code>" in html or "<pre>" in html

    def test_markdown_to_html_tables(self):
        """Test table conversion."""
        md = """| Col 1 | Col 2 |
|-------|-------|
| A     | B     |"""
        html = markdown_processor.markdown_to_html(md)
        assert "<table>" in html
        assert "<th>Col 1</th>" in html
        assert "<td>A</td>" in html

    def test_markdown_to_html_links(self):
        """Test link conversion."""
        md = "[Google](https://google.com)"
        html = markdown_processor.markdown_to_html(md)
        assert '<a href="https://google.com">Google</a>' in html

    def test_markdown_to_html_empty_string(self):
        """Test empty markdown input."""
        html = markdown_processor.markdown_to_html("")
        assert html == ""

    def test_process_page_breaks_basic(self):
        """Test basic page break processing."""
        html = "<p>Page 1</p><!-- pagebreak --><p>Page 2</p>"
        result = markdown_processor.process_page_breaks(html)
        assert '<div class="page-break"></div>' in result
        assert "<!-- pagebreak -->" not in result

    def test_process_page_breaks_hyphen_format(self):
        """Test page break with hyphen format."""
        html = "<p>Page 1</p><!-- page-break --><p>Page 2</p>"
        result = markdown_processor.process_page_breaks(html)
        assert '<div class="page-break"></div>' in result

    def test_process_page_breaks_uppercase(self):
        """Test page break with uppercase."""
        html = "<p>Page 1</p><!-- PAGEBREAK --><p>Page 2</p>"
        result = markdown_processor.process_page_breaks(html)
        assert '<div class="page-break"></div>' in result

    def test_process_page_breaks_mixed_case(self):
        """Test page break with mixed case."""
        html = "<p>Page 1</p><!-- PageBreak --><p>Page 2</p>"
        result = markdown_processor.process_page_breaks(html)
        assert '<div class="page-break"></div>' in result

    def test_process_page_breaks_with_spaces(self):
        """Test page break with extra spaces."""
        html = "<p>Page 1</p><!--  page break  --><p>Page 2</p>"
        result = markdown_processor.process_page_breaks(html)
        assert '<div class="page-break"></div>' in result

    def test_process_page_breaks_multiple(self):
        """Test multiple page breaks."""
        html = """<p>Page 1</p>
<!-- pagebreak -->
<p>Page 2</p>
<!-- pagebreak -->
<p>Page 3</p>"""
        result = markdown_processor.process_page_breaks(html)
        assert result.count('<div class="page-break"></div>') == 2

    def test_process_page_breaks_no_breaks(self):
        """Test HTML without page breaks."""
        html = "<p>No breaks here</p>"
        result = markdown_processor.process_page_breaks(html)
        assert result == html

    def test_build_html_document_structure(self):
        """Test HTML document building."""
        title = "Test Document"
        body = "<h1>Hello</h1>"
        css = "body { color: red; }"

        html = markdown_processor.build_html_document(title, body, css)

        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_build_html_document_title(self):
        """Test that title is included in HTML."""
        html = markdown_processor.build_html_document(
            "My Title", "<p>Body</p>", "/* css */"
        )
        assert "<title>My Title</title>" in html

    def test_build_html_document_css_embedded(self):
        """Test that CSS is embedded in style tag."""
        css = "body { font-size: 14pt; }"
        html = markdown_processor.build_html_document("Title", "<p>Body</p>", css)
        assert "<style>" in html
        assert css in html
        assert "</style>" in html

    def test_build_html_document_body_content(self):
        """Test that body content is included."""
        body = "<h1>Heading</h1><p>Paragraph</p>"
        html = markdown_processor.build_html_document("Title", body, "")
        assert body in html

    def test_build_html_document_charset_utf8(self):
        """Test that UTF-8 charset is specified."""
        html = markdown_processor.build_html_document("Title", "<p>Body</p>", "")
        assert '<meta charset="utf-8">' in html

    def test_full_workflow(self, sample_markdown):
        """Test complete workflow: markdown -> HTML -> page breaks -> document."""
        # Convert markdown to HTML
        html_body = markdown_processor.markdown_to_html(sample_markdown)

        # Process page breaks
        html_body = markdown_processor.process_page_breaks(html_body)

        # Build full document
        css = "body { color: #333; }"
        full_html = markdown_processor.build_html_document(
            "Test", html_body, css
        )

        # Verify structure
        assert "<!DOCTYPE html>" in full_html
        assert "<h1" in full_html
        assert "Test Document</h1>" in full_html
        assert '<div class="page-break"></div>' in full_html
        assert css in full_html
        assert "<table>" in full_html  # From sample markdown