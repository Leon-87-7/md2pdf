"""Interactive theme builder wizard for creating custom themes."""

import sys
from pathlib import Path
from typing import Dict, Optional

from . import color_utils
from .theme_manager import get_themes_directory, list_available_themes


def print_header():
    """Print wizard header."""
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     md2pdf Interactive Theme Builder         ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print("Let's create a custom theme for your PDF documents.")
    print("Press Enter to accept default values in [brackets].")
    print()


def prompt_with_validation(
    prompt_text: str,
    default: str,
    validator=None,
    allow_empty: bool = True,
) -> str:
    """Prompt user for input with optional validation.

    Args:
        prompt_text: Prompt to display
        default: Default value (shown in brackets)
        validator: Optional function to validate input (should raise ValueError)
        allow_empty: Whether to allow empty input (use default)

    Returns:
        User input or default value
    """
    while True:
        user_input = input(f"{prompt_text} [{default}]: ").strip()

        if not user_input:
            if allow_empty:
                return default
            else:
                print("✗ This field is required.", file=sys.stderr)
                continue

        if validator:
            try:
                validator(user_input)
                return user_input
            except ValueError as e:
                print(f"✗ {e}", file=sys.stderr)
                continue
        else:
            return user_input


def validate_theme_name(name: str) -> None:
    """Validate theme name.

    Args:
        name: Theme name to validate

    Raises:
        ValueError: If name is invalid or already exists
    """
    if not name:
        raise ValueError("Theme name cannot be empty")

    # Check for valid characters (alphanumeric, dash, underscore)
    if not all(c.isalnum() or c in "-_" for c in name):
        raise ValueError(
            "Theme name can only contain letters, numbers, hyphens, and underscores"
        )

    # Check if theme already exists
    existing_themes = list_available_themes()
    if name in existing_themes:
        raise ValueError(
            f"Theme '{name}' already exists. Choose a different name or delete the existing theme."
        )


def validate_color_input(color: str) -> None:
    """Validate color input format.

    Args:
        color: Color string to validate

    Raises:
        ValueError: If color format is invalid
    """
    # This will raise ValueError if invalid
    color_utils.parse_color(color)


def validate_font_size(size: str) -> None:
    """Validate font size input.

    Args:
        size: Font size to validate (should be number or number with 'pt')

    Raises:
        ValueError: If font size is invalid
    """
    size = size.strip()

    # Remove 'pt' suffix if present
    if size.endswith("pt"):
        size = size[:-2]

    try:
        value = float(size)
        if value <= 0:
            raise ValueError("Font size must be positive")
        if value > 100:
            raise ValueError("Font size seems too large (max 100pt)")
    except ValueError:
        raise ValueError(
            f"Invalid font size: '{size}'. Use a number (e.g., 11) or with 'pt' (e.g., 11pt)"
        )


def check_contrast_and_warn(
    foreground: str, background: str, element_name: str
) -> bool:
    """Check contrast ratio and warn if below WCAG AA.

    Args:
        foreground: Foreground color
        background: Background color
        element_name: Name of element for warning message

    Returns:
        True if user wants to continue, False if they want to re-enter
    """
    ratio = color_utils.calculate_contrast_ratio(foreground, background)
    rating = color_utils.get_contrast_rating(ratio)

    print(f"✓ Contrast ratio: {ratio:.1f}:1 ({rating})")

    if not color_utils.meets_wcag_aa(ratio):
        print(f"⚠ Warning: {element_name} contrast is below WCAG AA standard (4.5:1)")

        # Suggest accessible alternative
        suggestion = color_utils.suggest_accessible_color(foreground, background)
        suggestion_ratio = color_utils.calculate_contrast_ratio(suggestion, background)
        print(
            f"  Suggestion: Try {suggestion} for {suggestion_ratio:.1f}:1 ratio (WCAG AA)"
        )

        response = input("  Continue with current color anyway? [y/N]: ").strip().lower()
        return response == "y"

    return True


def prompt_theme_properties() -> Dict[str, str]:
    """Prompt user for all theme properties interactively.

    Returns:
        Dictionary of theme properties
    """
    props = {}

    # Theme name (required, unique)
    print_header()
    props["name"] = prompt_with_validation(
        "Theme name",
        "",
        validator=validate_theme_name,
        allow_empty=False,
    )
    print("✓ Name available")
    print()

    # Background color
    while True:
        props["background_color"] = prompt_with_validation(
            "Background color",
            "#ffffff",
            validator=validate_color_input,
        )
        # Convert to hex for consistency
        props["background_color"] = color_utils.rgb_to_hex(
            color_utils.parse_color(props["background_color"])
        )
        print(f"✓ Using: {props['background_color']}")
        print()
        break

    # Text color (with contrast check)
    while True:
        props["text_color"] = prompt_with_validation(
            "Text color",
            "#000000",
            validator=validate_color_input,
        )
        props["text_color"] = color_utils.rgb_to_hex(
            color_utils.parse_color(props["text_color"])
        )
        print(f"✓ Using: {props['text_color']}")

        if check_contrast_and_warn(
            props["text_color"], props["background_color"], "Body text"
        ):
            print()
            break

    # Font family
    props["font_family"] = prompt_with_validation(
        "Font family",
        "Arial, sans-serif",
    )
    print(f"✓ Using: {props['font_family']}")
    print()

    # Body text size
    props["body_text_size"] = prompt_with_validation(
        "Body text size",
        "11pt",
        validator=validate_font_size,
    )
    # Ensure 'pt' suffix
    if not props["body_text_size"].endswith("pt"):
        props["body_text_size"] += "pt"
    print(f"✓ Using: {props['body_text_size']}")
    print()

    # H1 heading color (with contrast check)
    while True:
        props["h1_color"] = prompt_with_validation(
            "H1 heading color",
            "#2c3e50",
            validator=validate_color_input,
        )
        props["h1_color"] = color_utils.rgb_to_hex(
            color_utils.parse_color(props["h1_color"])
        )
        print(f"✓ Using: {props['h1_color']}")

        if check_contrast_and_warn(
            props["h1_color"], props["background_color"], "H1 heading"
        ):
            print()
            break

    # H2-H6 heading color (with contrast check)
    while True:
        props["h2_h6_color"] = prompt_with_validation(
            "H2-H6 heading color",
            "#2c3e50",
            validator=validate_color_input,
        )
        props["h2_h6_color"] = color_utils.rgb_to_hex(
            color_utils.parse_color(props["h2_h6_color"])
        )
        print(f"✓ Using: {props['h2_h6_color']}")

        if check_contrast_and_warn(
            props["h2_h6_color"], props["background_color"], "H2-H6 headings"
        ):
            print()
            break

    # Accent color (for links, borders - with contrast check)
    while True:
        props["accent_color"] = prompt_with_validation(
            "Accent color (links, borders)",
            "#667eea",
            validator=validate_color_input,
        )
        props["accent_color"] = color_utils.rgb_to_hex(
            color_utils.parse_color(props["accent_color"])
        )
        print(f"✓ Using: {props['accent_color']}")

        if check_contrast_and_warn(
            props["accent_color"], props["background_color"], "Link"
        ):
            print()
            break

    # Code block background
    props["code_bg_color"] = prompt_with_validation(
        "Code block background",
        "#f5f5f5",
        validator=validate_color_input,
    )
    props["code_bg_color"] = color_utils.rgb_to_hex(
        color_utils.parse_color(props["code_bg_color"])
    )
    print(f"✓ Using: {props['code_bg_color']}")
    print()

    # Table header background
    props["table_header_bg"] = prompt_with_validation(
        "Table header background",
        "#667eea",
        validator=validate_color_input,
    )
    props["table_header_bg"] = color_utils.rgb_to_hex(
        color_utils.parse_color(props["table_header_bg"])
    )
    print(f"✓ Using: {props['table_header_bg']}")
    print()

    return props


def generate_css_from_properties(props: Dict[str, str]) -> str:
    """Generate complete CSS file from theme properties.

    Args:
        props: Dictionary of theme properties

    Returns:
        Complete CSS content as string
    """
    # Generate derived colors
    hover_color = color_utils.suggest_darker(props["accent_color"], 15)
    table_alt_row = color_utils.suggest_lighter(props["background_color"], 5)
    code_border = color_utils.suggest_darker(props["code_bg_color"], 10)

    css_template = f"""/* Theme: {props['name']} */
/* Generated by md2pdf Interactive Theme Builder */

@page {{
    size: A4;
    margin: 0;
}}

body {{
    font-family: '{props['font_family']}';
    font-size: {props['body_text_size']};
    line-height: 1.6;
    color: {props['text_color']};
    background-color: {props['background_color']};
    padding: 2cm;
}}

h1,
h2,
h3,
h4,
h5,
h6 {{
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}}

h1 {{
    font-size: 32pt;
    color: {props['h1_color']};
    background: {props['code_bg_color']};
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-weight: 700;
    border-left: 5px solid {props['accent_color']};
}}

#document-section-header {{
    font-size: 28pt;
    color: {props['h1_color']};
    padding: 20px;
    text-align: right;
    font-weight: 600;
}}

h2 {{
    font-size: 24pt;
    color: {props['h2_h6_color']};
    background: {props['code_bg_color']};
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid {props['accent_color']};
}}

h3 {{
    font-size: 18pt;
    color: {props['h2_h6_color']};
    background: {props['code_bg_color']};
    padding: 10px;
    border-radius: 5px;
    font-weight: 600;
}}

h4 {{
    font-size: 16pt;
    color: {props['h2_h6_color']};
    font-weight: 600;
}}

h5 {{
    font-size: 14pt;
    color: {props['h2_h6_color']};
    font-weight: 600;
}}

h6 {{
    font-size: 12pt;
    color: {props['h2_h6_color']};
    font-weight: 600;
}}

p {{
    margin: 10px 0;
    font-size: {props['body_text_size']};
}}

ul,
ol {{
    padding: 0 0 0 2em;
    margin: 10px 0;
    font-size: {props['body_text_size']};
    line-height: 1.6;
}}

li {{
    margin: 5px 0;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 10pt;
    border-radius: 8px;
    overflow: hidden;
}}

th {{
    background: {props['table_header_bg']};
    color: white;
    padding: 14px;
    text-align: left;
    font-weight: 600;
}}

td {{
    padding: 12px;
    border: 1px solid {code_border};
}}

tr:nth-child(even) td {{
    background-color: {table_alt_row};
}}

code {{
    background: {props['code_bg_color']};
    padding: 4px 8px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    border: 1px solid {code_border};
}}

pre {{
    background: {props['code_bg_color']};
    border: 1px solid {code_border};
    border-left: 5px solid {props['accent_color']};
    border-radius: 5px;
    padding: 18px;
    overflow-x: auto;
    margin: 15px 0;
    font-size: 10pt;
}}

pre code {{
    background: none;
    padding: 0;
    border: none;
}}

blockquote {{
    border-left: 5px solid {props['accent_color']};
    padding-left: 2em;
    margin: 15px 0;
    font-style: italic;
    background: {props['code_bg_color']};
    padding: 18px 18px 18px 2em;
    border-radius: 5px;
}}

a {{
    color: {props['accent_color']};
    text-decoration: none;
    font-weight: 500;
}}

a:hover {{
    color: {hover_color};
    text-decoration: underline;
}}

hr {{
    border: none;
    height: 2px;
    background: {props['accent_color']};
    margin: 25px 0;
}}

img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    border: 2px solid {code_border};
}}

.page-break {{
    page-break-after: always;
    break-after: page;
    height: 0;
    margin: 2cm 0;
    padding: 0;
    border: none;
}}
"""

    return css_template


def save_theme(name: str, css_content: str) -> Path:
    """Save theme CSS to themes directory.

    Args:
        name: Theme name (without .css extension)
        css_content: CSS content to save

    Returns:
        Path to saved theme file

    Raises:
        IOError: If file cannot be written
    """
    themes_dir = get_themes_directory()
    theme_path = themes_dir / f"{name}.css"

    try:
        with open(theme_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        return theme_path
    except (IOError, PermissionError) as e:
        raise IOError(f"Failed to save theme: {e}") from e


def display_summary(props: Dict[str, str]) -> None:
    """Display theme summary before confirmation.

    Args:
        props: Dictionary of theme properties
    """
    print("─" * 48)
    print()
    print("Theme Summary:")
    print(f"  • Name: {props['name']}")
    print(f"  • Background: {props['background_color']}")
    print(f"  • Text: {props['text_color']}, {props['font_family']}, {props['body_text_size']}")
    print(f"  • H1: {props['h1_color']}")
    print(f"  • H2-H6: {props['h2_h6_color']}")
    print(f"  • Accent: {props['accent_color']}")

    # Check overall accessibility
    all_accessible = True
    for element, color in [
        ("text", props["text_color"]),
        ("H1", props["h1_color"]),
        ("H2-H6", props["h2_h6_color"]),
        ("links", props["accent_color"]),
    ]:
        ratio = color_utils.calculate_contrast_ratio(color, props["background_color"])
        if not color_utils.meets_wcag_aa(ratio):
            all_accessible = False
            break

    if all_accessible:
        print("  • All contrast ratios meet WCAG AA standards ✓")
    else:
        print("  • ⚠ Some contrast ratios are below WCAG AA")

    print()


def run_theme_wizard() -> None:
    """Run the interactive theme builder wizard."""
    try:
        # Prompt for theme properties
        props = prompt_theme_properties()

        # Display summary
        display_summary(props)

        # Confirm creation
        response = input("Create theme? [Y/n]: ").strip().lower()
        if response and response != "y":
            print("Theme creation cancelled.")
            return

        print()
        print(f"Generating theme '{props['name']}'...")

        # Generate CSS
        css_content = generate_css_from_properties(props)

        # Save to themes directory
        theme_path = save_theme(props["name"], css_content)

        print(f"✓ CSS file created: {theme_path.relative_to(Path.cwd())}")
        print("✓ Theme ready to use!")
        print()
        print("Usage:")
        print(f"  md2pdf document.md --theme {props['name']}")
        print(f"  md2pdf *.md --merge --theme {props['name']} -on book.pdf")
        print()

    except KeyboardInterrupt:
        print("\n\nTheme creation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
