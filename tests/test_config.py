"""Tests for md2pdf.config module."""

from pathlib import Path

from md2pdf import config


class TestConfig:
    """Test configuration constants."""

    def test_version_exists(self):
        """Test that version is defined."""
        assert hasattr(config, "__version__")
        assert isinstance(config.__version__, str)
        assert len(config.__version__) > 0

    def test_version_format(self):
        """Test version follows semantic versioning."""
        parts = config.__version__.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor"
        for part in parts:
            assert part.isdigit(), f"Version part '{part}' should be numeric"

    def test_package_dir_exists(self):
        """Test PACKAGE_DIR points to a valid directory."""
        assert isinstance(config.PACKAGE_DIR, Path)
        assert config.PACKAGE_DIR.exists()
        assert config.PACKAGE_DIR.is_dir()

    def test_themes_dir_name(self):
        """Test THEMES_DIR_NAME is defined."""
        assert config.THEMES_DIR_NAME == "themes"

    def test_markdown_extensions(self):
        """Test markdown extensions are defined correctly."""
        assert isinstance(config.MARKDOWN_EXTENSIONS, list)
        assert len(config.MARKDOWN_EXTENSIONS) > 0
        expected_extensions = ["extra", "codehilite", "tables", "toc"]
        for ext in expected_extensions:
            assert ext in config.MARKDOWN_EXTENSIONS

    def test_pdf_options(self):
        """Test PDF options dictionary."""
        assert isinstance(config.PDF_OPTIONS, dict)
        assert "enable-local-file-access" in config.PDF_OPTIONS
        assert "encoding" in config.PDF_OPTIONS
        assert "page-size" in config.PDF_OPTIONS
        assert config.PDF_OPTIONS["encoding"] == "UTF-8"
        assert config.PDF_OPTIONS["page-size"] == "A4"

    def test_supported_markdown_extensions(self):
        """Test supported markdown file extensions."""
        assert isinstance(config.SUPPORTED_MARKDOWN_EXTENSIONS, list)
        assert ".md" in config.SUPPORTED_MARKDOWN_EXTENSIONS
        assert ".markdown" in config.SUPPORTED_MARKDOWN_EXTENSIONS

    def test_wkhtmltopdf_paths(self):
        """Test wkhtmltopdf paths dictionary."""
        assert isinstance(config.WKHTMLTOPDF_PATHS, dict)
        assert "Windows" in config.WKHTMLTOPDF_PATHS
        assert "Darwin" in config.WKHTMLTOPDF_PATHS
        assert "Linux" in config.WKHTMLTOPDF_PATHS

        # Check that paths are lists
        for platform, paths in config.WKHTMLTOPDF_PATHS.items():
            assert isinstance(paths, list)
            assert len(paths) > 0

    def test_installation_instructions(self):
        """Test installation instructions dictionary."""
        assert isinstance(config.INSTALLATION_INSTRUCTIONS, dict)
        assert "Windows" in config.INSTALLATION_INSTRUCTIONS
        assert "Darwin" in config.INSTALLATION_INSTRUCTIONS
        assert "Linux" in config.INSTALLATION_INSTRUCTIONS
        assert "default" in config.INSTALLATION_INSTRUCTIONS

        # Check that instructions are lists
        for platform, instructions in config.INSTALLATION_INSTRUCTIONS.items():
            assert isinstance(instructions, list)
            assert len(instructions) > 0
