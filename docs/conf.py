# type:ignore
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from sphinx_pyproject import SphinxConfig

sys.path.insert(0, os.path.abspath("../src"))
config = SphinxConfig("../pyproject.toml", globalns=globals())
