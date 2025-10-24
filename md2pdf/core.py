"""Core conversion orchestrator for md2pdf."""

import html
import sys
from pathlib import Path
from typing import Optional

from . import file_operations, markdown_processor, pdf_engine, theme_manager
from .exceptions import Md2PdfError, WkhtmltopdfNotFoundError


def _setup_conversion_environment(
    custom_css: Optional[str] = None, theme: str = "default"
) -> tuple:
    """Setup PDF engine and CSS once for efficiency.

    This function is shared by all conversion modes (single, batch, merge)
    to avoid redundant setup operations.

    Args:
        custom_css: Path to custom CSS file (optional)
        theme: Theme name to use (default: "default")

    Returns:
        Tuple of (pdf_config, css_content)

    Raises:
        WkhtmltopdfNotFoundError: If wkhtmltopdf is not found
        ThemeNotFoundError: If theme is not found
        CSSNotFoundError: If custom CSS file is not found
    """
    # Warn if both custom_css and theme are specified
    if custom_css and theme != "default":
        print(
            f"Warning: Both --css and --theme specified. Using custom CSS file, ignoring theme '{theme}'.",
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


def _merge_html_bodies(html_bodies: list[tuple[str, str]], auto_break: bool = True) -> str:
    """Merge multiple HTML body sections into a single HTML body.

    Args:
        html_bodies: List of tuples (filename, html_body)
        auto_break: Whether to add page breaks between documents (default: True)

    Returns:
        Merged HTML body string

    Note:
        Filenames are HTML-escaped to prevent injection attacks.
    """
    merged_parts = []

    for i, (filename, html_body) in enumerate(html_bodies):
        # Escape filename to prevent HTML injection
        safe_filename = html.escape(filename)
        # Add a section header with the filename
        section_header = f'<h1 class="document-section-header">{safe_filename}</h1>\n'
        merged_parts.append(section_header)
        merged_parts.append(html_body)

        # Add page break between documents (except after the last one)
        if auto_break and i < len(html_bodies) - 1:
            merged_parts.append('<div class="page-break"></div>\n')

    return "\n".join(merged_parts)


def _process_single_file(input_file: str, pdf_config, css_content: str) -> tuple:
    """Read and process a single markdown file to HTML.

    This function is shared by all conversion modes to process individual files.

    Args:
        input_file: Path to input markdown file
        pdf_config: PDF configuration object (unused here, for consistency)
        css_content: CSS content (unused here, for consistency)

    Returns:
        Tuple of (input_path, html_body)

    Raises:
        InvalidInputError: If input file validation fails
        FileOperationError: If file read fails
    """
    # Validate input file
    input_path = file_operations.validate_input_file(input_file)

    # Read markdown content
    markdown_content = file_operations.read_markdown_file(input_path)

    # Convert Markdown → HTML with styling
    html_body = markdown_processor.markdown_to_html(markdown_content)
    html_body = markdown_processor.process_page_breaks(html_body)

    return input_path, html_body


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
        WkhtmltopdfNotFoundError: If wkhtmltopdf is not found on the system
        ConversionError: If PDF conversion fails
        ThemeNotFoundError: If the requested theme is not found
        CSSNotFoundError: If the custom CSS file is not found
        InvalidInputError: If input file validation fails
        FileOperationError: If file read/write operations fail
    """
    # 1. Setup: PDF engine and CSS (shared function)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)

    # 2. Process file: Read and convert to HTML (shared function)
    input_path, html_body = _process_single_file(input_file, pdf_config, css_content)

    # 3. Determine output path
    output_path = file_operations.determine_output_path(input_path, output_file)

    # 4. Build complete HTML document
    full_html = markdown_processor.build_html_document(
        title=input_path.stem, body_html=html_body, css_content=css_content
    )

    # 5. PDF Generation: Convert HTML to PDF
    pdf_engine.convert_html_to_pdf(full_html, output_path, pdf_config)

    # 6. Success: Print message and optionally preview
    print(f"Successfully converted '{input_file}' to '{output_path}'")

    if preview:
        file_operations.preview_file(output_path)


def convert_batch(
    input_files: list[str],
    output_dir: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    preview: bool = False,
) -> None:
    """Convert multiple Markdown files to PDFs in batch mode.

    Each input file is converted to a separate PDF. Output files are named
    based on the input filenames and placed in the specified output directory
    (or the same directory as each input file if no output_dir is specified).

    Args:
        input_files: List of paths to input Markdown files
        output_dir: Directory for output PDFs (optional, defaults to each input's directory)
        custom_css: Path to a custom CSS file (optional, takes precedence over theme)
        theme: Theme name to use (default: "default", ignored if custom_css is provided)
        preview: Whether to open the PDFs after generation (default: False)

    Raises:
        WkhtmltopdfNotFoundError: If wkhtmltopdf is not found on the system
        ConversionError: If PDF conversion fails for any file
        ThemeNotFoundError: If the requested theme is not found
        CSSNotFoundError: If the custom CSS file is not found
        InvalidInputError: If input file validation fails
        FileOperationError: If file read/write operations fail
    """
    if not input_files:
        print("Error: No input files specified for batch conversion.", file=sys.stderr)
        return

    # 1. Setup once for all conversions (efficiency)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)

    # Create output directory if specified
    output_path_obj = None
    if output_dir:
        output_path_obj = Path(output_dir)
        # Use exist_ok=True to handle race conditions where directory might
        # be created between check and creation (e.g., by another process)
        try:
            output_path_obj.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Error: Cannot create output directory '{output_dir}': {e}", file=sys.stderr)
            return

    # 2. Process each file
    converted_files = []
    failed_files = []

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

        except Md2PdfError as e:
            # Catch all md2pdf-specific errors (file operations, conversion, validation, etc.)
            failed_files.append((input_file, str(e)))
            print(f"[FAILED] '{input_file}': {e}", file=sys.stderr)
        except (OSError, IOError, PermissionError) as e:
            # Catch system-level file errors
            failed_files.append((input_file, f"System error: {e}"))
            print(f"[FAILED] '{input_file}': System error: {e}", file=sys.stderr)

    # 3. Print summary
    print("\n--- Batch Conversion Summary ---")
    print(f"Total files: {len(input_files)}")
    print(f"Successful: {len(converted_files)}")
    print(f"Failed: {len(failed_files)}")

    if failed_files:
        print("\nFailed files:")
        for input_file, error in failed_files:
            print(f"  - {input_file}: {error}")

    # 4. Optionally preview first file
    if preview and converted_files:
        first_output = converted_files[0][1]
        print(f"\nPreviewing first file: {first_output}")
        file_operations.preview_file(first_output)


def convert_merge(
    input_files: list[str],
    output_file: Optional[str] = None,
    custom_css: Optional[str] = None,
    theme: str = "default",
    auto_break: bool = True,
    preview: bool = False,
) -> None:
    """Merge multiple Markdown files into a single PDF.

    All input files are combined into one PDF document with optional page breaks
    between sections. Each section starts with a header showing the source filename.

    Args:
        input_files: List of paths to input Markdown files
        output_file: Path to the output merged PDF (default: "merged_output.pdf")
        custom_css: Path to a custom CSS file (optional, takes precedence over theme)
        theme: Theme name to use (default: "default", ignored if custom_css is provided)
        auto_break: Whether to add page breaks between documents (default: True)
        preview: Whether to open the PDF after generation (default: False)

    Raises:
        WkhtmltopdfNotFoundError: If wkhtmltopdf is not found on the system
        ConversionError: If PDF conversion fails
        ThemeNotFoundError: If the requested theme is not found
        CSSNotFoundError: If the custom CSS file is not found
        InvalidInputError: If input file validation fails
        FileOperationError: If file read/write operations fail
    """
    if not input_files:
        print("Error: No input files specified for merge.", file=sys.stderr)
        return

    if len(input_files) < 2:
        print(
            "Warning: Merge mode requires at least 2 files. Use single file mode for one file.",
            file=sys.stderr,
        )

    # 1. Setup once for all conversions (efficiency)
    pdf_config, css_content = _setup_conversion_environment(custom_css, theme)

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

        except Md2PdfError as e:
            # Catch all md2pdf-specific errors (file operations, conversion, validation, etc.)
            failed_files.append((input_file, str(e)))
            print(f"[FAILED] '{input_file}': {e}", file=sys.stderr)
        except (OSError, IOError, PermissionError) as e:
            # Catch system-level file errors
            failed_files.append((input_file, f"System error: {e}"))
            print(f"[FAILED] '{input_file}': System error: {e}", file=sys.stderr)

    # 3. Check if we have at least one successful file
    if not html_bodies:
        print("Error: No files were successfully processed. Cannot create PDF.", file=sys.stderr)
        return

    # 4. Merge HTML bodies
    merged_html_body = _merge_html_bodies(html_bodies, auto_break)

    # 5. Determine output path
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = Path("merged_output.pdf")

    # 6. Build complete HTML document with merged content
    full_html = markdown_processor.build_html_document(
        title="Merged Document", body_html=merged_html_body, css_content=css_content
    )

    # 7. PDF Generation: Convert HTML to PDF
    pdf_engine.convert_html_to_pdf(full_html, output_path, pdf_config)

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

    # 9. Optionally preview
    if preview:
        file_operations.preview_file(output_path)
