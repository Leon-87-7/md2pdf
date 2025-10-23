"""Theme management and CSS loading."""

import sys
from pathlib import Path
from typing import Optional

from . import config
from .exceptions import CSSNotFoundError, FileOperationError, ThemeNotFoundError


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


def validate_theme(theme: str) -> None:
    """Validate that a theme exists before conversion starts.

    Args:
        theme: Theme name (without .css extension)

    Raises:
        ThemeNotFoundError: If theme is not found
    """
    themes_dir = get_themes_directory()
    theme_path = themes_dir / f"{theme}.css"

    if not theme_path.exists():
        available_themes = list_available_themes()
        raise ThemeNotFoundError(theme, available_themes)


def load_css(custom_css: Optional[str] = None, theme: str = "default") -> str:
    """Load CSS content from custom file, theme, or default.

    Args:
        custom_css: Path to custom CSS file, or None to use theme
        theme: Theme name to use (default: "default")

    Returns:
        CSS content as string

    Raises:
        CSSNotFoundError: If custom CSS file is not found
        ThemeNotFoundError: If theme is not found
        FileOperationError: If CSS file cannot be read
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
        CSSNotFoundError: If CSS file is not found
        FileOperationError: If CSS file cannot be read
    """
    css_path = Path(custom_css_path).resolve()

    # Validate it's a file and exists
    if not css_path.exists():
        raise CSSNotFoundError(f"CSS file '{custom_css_path}' does not exist.")

    if not css_path.is_file():
        raise CSSNotFoundError(f"CSS file '{custom_css_path}' is not a file.")

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
        raise FileOperationError(f"Error reading CSS file: {e}") from e


def _load_theme_css(theme: str) -> str:
    """Load CSS from a theme in the themes directory.

    Args:
        theme: Theme name (without .css extension)

    Returns:
        CSS content as string

    Raises:
        ThemeNotFoundError: If theme is not found
        FileOperationError: If theme file cannot be read
    """
    themes_dir = get_themes_directory()
    theme_path = themes_dir / f"{theme}.css"

    if not theme_path.exists():
        available_themes = list_available_themes()
        raise ThemeNotFoundError(theme, available_themes)

    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            return f.read()
    except (IOError, PermissionError, UnicodeDecodeError) as e:
        raise FileOperationError(f"Error reading theme file: {e}") from e
