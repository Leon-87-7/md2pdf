"""Core conversion orchestrator for md2pdf."""

import sys
from typing import Optional

from . import file_operations, markdown_processor, pdf_engine, theme_manager


def convert_md_to_pdf(
    input_file: str,
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:
    """Convert a Markdown file to PDF.

    This is the main orchestrator function that coordinates all the modules
    to perform the Markdown to PDF conversion.

    Args:
        input_file: Path to the input Markdown file
        output_file: Path to the output PDF file (optional, defaults to input name with .pdf)
        custom_css: Path to a custom CSS file (optional, takes precedence over theme)
        theme: Theme name to use (default: "default", ignored if custom_css is provided)
        preview: Whether to open the PDF after generation (default: False)

    Raises:
        SystemExit: If conversion fails or dependencies are missing
    """
    # 1. Setup: Warn if both custom_css and theme are specified
    if custom_css and theme != "default":
        print(
            f"Warning: Both --css and --theme specified. Using custom CSS file, ignoring theme '{theme}'.",
            file=sys.stderr,
        )

    # 2. PDF Engine: Find and configure wkhtmltopdf
    engine_path = pdf_engine.find_wkhtmltopdf()
    if engine_path is None:
        pdf_engine.print_installation_help()
        sys.exit(1)

    pdf_config = pdf_engine.create_pdf_configuration(engine_path)

    # 3. File I/O: Validate input and determine output path
    input_path = file_operations.validate_input_file(input_file)
    output_path = file_operations.determine_output_path(input_path, output_file)
    markdown_content = file_operations.read_markdown_file(input_path)

    # 4. Processing: Convert Markdown → HTML with styling
    html_body = markdown_processor.markdown_to_html(markdown_content)
    html_body = markdown_processor.process_page_breaks(html_body)
    css_content = theme_manager.load_css(custom_css, theme)
    full_html = markdown_processor.build_html_document(
        title=input_path.stem, body_html=html_body, css_content=css_content
    )

    # 5. PDF Generation: Convert HTML to PDF
    pdf_engine.convert_html_to_pdf(full_html, output_path, pdf_config)

    # 6. Success: Print message and optionally preview
    print(f"Successfully converted '{input_file}' to '{output_path}'")

    if preview:
        file_operations.preview_file(output_path)
