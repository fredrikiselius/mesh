# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

BASE = os.path.abspath('.')
ROOT = os.path.dirname(BASE)
sys.path.insert(0, ROOT)

for entry in os.listdir(os.path.join(ROOT, 'mesh')):
    if entry.startswith('__'):
        continue

    module_name, _ = os.path.splitext(entry)
    path = os.path.join(BASE, 'modules', f'{module_name}.rst')
    with open(path, 'w') as f:
        f.writelines([
            module_name.capitalize(), '\n',
            '-' * len(module_name),' \n'
            f'.. automodule:: mesh.{module_name}', '\n',
            '\t:members:', '\n',
            '\t:undoc-members:', '\n',
        ])


# -- Project information -----------------------------------------------------

project = 'Mesh'
copyright = '2020, Fredrik Iselius'
author = 'Fredrik Iselius'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode',
              'sphinx_rtd_theme']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options autodoc ---------------------------------------------------------

# The order for members when using autodoc
# Possible values alphabetical, bysource, groupwise
autodoc_member_order = 'bysource'


# -- Options autodoc ---------------------------------------------------------

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']