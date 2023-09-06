
import os
import sys
import sphinx.errors
sys.path.insert(0, os.path.abspath("../src"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DubiousDiscord'
copyright = '2023, Carl Best'
author = 'lapras'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

autodoc_default_options = {
    "member-order": "bysource",
}
autodoc_type_aliases = {
    "ps_CallbackArgs": "ps_CallbackArgs"
}
autodoc_typehints_format = "short"

def missing_reference(_app, _domain, node, _contnode):
    print(node["reftarget"])
    if any([ignore in node["reftarget"] for ignore in ["ClassVar", "InitVar", "ps_CallbackArgs"]]):
        raise sphinx.errors.NoUri()

def setup(app):
    app.connect("missing-reference", missing_reference)

nitpicky = True

python_display_short_literal_types = True
python_use_unqualified_type_names = True
maximum_signature_line_length = 200

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    "flask": ("https://flask.palletsprojects.com/en/2.3.x", None),
    "requests": ("https://requests.readthedocs.io/en/latest", None)
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
