"""Markdown to HTML processing."""

import re

import markdown

from . import config


def markdown_to_html(content: str) -> str:
    """Convert markdown content to HTML.

    Args:
        content: Markdown content as string

    Returns:
        HTML content as string
    """
    return markdown.markdown(content, extensions=config.MARKDOWN_EXTENSIONS)


def process_page_breaks(html_content: str) -> str:
    """Process HTML comments for page breaks and convert them to CSS page breaks.

    Supports the following markdown comment syntaxes:
    - <!-- pagebreak -->
    - <!-- page-break -->
    - <!-- PAGEBREAK -->
    - <!-- PAGE-BREAK -->

    Args:
        html_content: HTML content to process

    Returns:
        HTML content with page break comments replaced by div elements
    """
    # Pattern matches HTML comments with various page break formats (case-insensitive)
    pattern = r"<!--\s*page[-_\s]*break\s*-->"
    replacement = '<div class="page-break"></div>'
    return re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)


def build_html_document(title: str, body_html: str, css_content: str) -> str:
    """Build complete HTML document with embedded CSS.

    Args:
        title: Document title (for <title> tag)
        body_html: HTML content for body
        css_content: CSS content to embed in <style> tag

    Returns:
        Complete HTML document as string
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        {css_content}
    </style>
</head>
<body>
   {body_html}
</body>
</html>
"""
