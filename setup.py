from pathlib import Path
import re
from setuptools import setup


def get_version():
    """Extract version from md2pdf.py"""
    content = Path("md2pdf.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in md2pdf.py")


setup(
    name="md2pdf",
    version=get_version(),
    py_modules=["md2pdf"],
    entry_points={"console_scripts": ["md2pdf = md2pdf:main"]},
)
