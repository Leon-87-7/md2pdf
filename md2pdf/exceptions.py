"""Custom exceptions for md2pdf package."""


class Md2PdfError(Exception):
    """Base exception for all md2pdf errors."""

    pass


class WkhtmltopdfNotFoundError(Md2PdfError):
    """Raised when wkhtmltopdf executable is not found on the system."""

    pass


class ConversionError(Md2PdfError):
    """Raised when PDF conversion fails."""

    pass


class FileOperationError(Md2PdfError):
    """Raised when file read/write operations fail."""

    pass


class ThemeNotFoundError(Md2PdfError):
    """Raised when a requested theme is not found."""

    def __init__(self, theme: str, available_themes: list[str] | None = None):
        """Initialize ThemeNotFoundError.

        Args:
            theme: The theme name that was not found
            available_themes: Optional list of available themes
        """
        self.theme = theme
        self.available_themes = available_themes or []

        message = f"Theme '{theme}' not found."
        if self.available_themes:
            message += f" Available themes: {', '.join(sorted(self.available_themes))}"
        else:
            message += " No themes found in themes directory."

        super().__init__(message)


class CSSNotFoundError(Md2PdfError):
    """Raised when a custom CSS file is not found."""

    pass


class InvalidInputError(Md2PdfError):
    """Raised when input validation fails."""

    pass
