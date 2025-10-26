from pathlib import Path
import re
from setuptools import setup, find_packages


def get_version():
    """Extract version from md2pdf/config.py"""
    content = Path("md2pdf/config.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in md2pdf/config.py")


def get_long_description():
    """Read the README.md file"""
    readme_path = Path("README.md")
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return ""


setup(
    name="md2pdf",
    version=get_version(),
    description="Convert Markdown files to PDF with beautiful themes",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Leon Eidelman",
    author_email="leon.eidelman@yahoo.com",
    url="https://github.com/leon-87-7/md2pdf",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "markdown>=3.4",
        "pdfkit>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "md2pdf=md2pdf.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
)
