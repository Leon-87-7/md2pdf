"""Theme management and CSS loading."""

import sys
from pathlib import Path
from typing import Optional

from . import config


def get_themes_directory() -> Path:
    """Get the path to the themes directory.

    Returns:
        Path to the themes directory (in project root).
    """
    return config.PACKAGE_DIR / config.THEMES_DIR_NAME


def list_available_themes() -> list[str]:
    """List all available theme names.

    Returns:
        List of theme names (without .css extension).
    """
    themes_dir = get_themes_directory()
    if not themes_dir.exists():
        return []

    # Get all .css files and remove extension
    return [f.stem for f in themes_dir.glob("*.css")]


def load_css(custom_css: Optional[str] = None, theme: str = "default") -> str:
    """Load CSS content from custom file, theme, or default.

    Args:
        custom_css: Path to custom CSS file, or None to use theme
        theme: Theme name to use (default: "default")

    Returns:
        CSS content as string

    Raises:
        SystemExit: If CSS file is invalid or unreadable
    """
    # --css flag takes precedence over --theme
    if custom_css:
        return _load_custom_css(custom_css)
    else:
        return _load_theme_css(theme)


def _load_custom_css(custom_css_path: str) -> str:
    """Load CSS from a custom file path.

    Args:
        custom_css_path: Path to custom CSS file

    Returns:
        CSS content as string

    Raises:
        SystemExit: If CSS file is invalid or unreadable
    """
    css_path = Path(custom_css_path).resolve()

    # Validate it's a file and exists
    if not css_path.exists():
        print(f"Error: CSS file '{custom_css_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not css_path.is_file():
        print(f"Error: CSS file '{custom_css_path}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # Warn if extension is not .css
    if css_path.suffix.lower() != ".css":
        print(
            f"Warning: '{custom_css_path}' does not have .css extension",
            file=sys.stderr,
        )

    try:
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    except (IOError, PermissionError, UnicodeDecodeError) as e:
        print(f"Error reading CSS file: {e}", file=sys.stderr)
        sys.exit(1)


def _load_theme_css(theme: str) -> str:
    """Load CSS from a theme in the themes directory.

    Args:
        theme: Theme name (without .css extension)

    Returns:
        CSS content as string

    Raises:
        SystemExit: If theme is not found or unreadable
    """
    themes_dir = get_themes_directory()
    theme_path = themes_dir / f"{theme}.css"

    if not theme_path.exists():
        available_themes = list_available_themes()
        print(f"Error: Theme '{theme}' not found.", file=sys.stderr)
        if available_themes:
            print(
                f"Available themes: {', '.join(available_themes)}", file=sys.stderr
            )
        else:
            print("No themes found in themes directory.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            return f.read()
    except (IOError, PermissionError, UnicodeDecodeError) as e:
        print(f"Error reading theme file: {e}", file=sys.stderr)
        sys.exit(1)
