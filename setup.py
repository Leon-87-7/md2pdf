from setuptools import setup

setup(
    name="md2pdf",
    version="0.1.0",
    py_modules=["md2pdf"],
    entry_points={"console_scripts": ["md2pdf = md2pdf:main"]},
)
