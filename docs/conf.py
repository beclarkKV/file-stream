"""Sphinx configuration."""

project = "File Stream"
author = "Benjamin Clark"
copyright = "2025, Benjamin Clark"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
