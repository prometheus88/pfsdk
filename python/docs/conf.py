import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'PostFiat Python SDK'
author = 'PostFiat'
version = '0.1.0-dev'
release = 'v0.1.0-dev'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'autoapi.extension',
]

autoapi_dirs = ['../postfiat']
autoapi_type = 'python'
autoapi_file_patterns = ['*.py']
autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary']
autoapi_add_toctree_entry = True
autoapi_keep_files = True
autoapi_root = 'api'
autoapi_python_use_implicit_namespaces = True

html_theme = 'sphinx_rtd_theme'
html_static_path = []

master_doc = 'index'