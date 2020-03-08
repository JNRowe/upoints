#
"""conf - Sphinx configuration information."""
# Copyright © 2008-2017  James Rowe <jnrowe@gmail.com>
#
# This file is part of upoints.
#
# upoints is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# upoints is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# upoints.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import os
import sys
from contextlib import suppress
from pathlib import Path
from subprocess import CalledProcessError, PIPE, run

root_dir = Path(__file__).parent.parents[2]
sys.path.insert(0, str(root_dir))

import upoints  # NOQA: E402

on_rtd = os.getenv('READTHEDOCS')
if not on_rtd:
    import sphinx_rtd_theme

# General configuration {{{
extensions = \
    [f'sphinx.ext.{ext}'
     for ext in ['autodoc', 'coverage', 'doctest', 'extlinks', 'intersphinx',
                 'napoleon', 'todo', 'viewcode']] \
    + [f'sphinxcontrib.{ext}' for ext in []] \
    + []

if not on_rtd:
    # Showing document build durations is only valuable when writing, so we’ll
    # only enable it locally
    extensions.append('sphinx.ext.duration')
    # Only activate spelling if it is installed.  It is not required in the
    # general case and we don’t have the granularity to describe this in a
    # clean way
    try:
        from sphinxcontrib import spelling  # NOQA: F401
    except ImportError:
        pass
    else:
        extensions.append('sphinxcontrib.spelling')

rst_epilog = """
.. |PyPI| replace:: :abbr:`PyPI (Python Package Index)`
.. |modref| replace:: :mod:`upoints`
"""

default_role = 'any'

needs_sphinx = '2.4'

nitpicky = True
# }}}

# Project information {{{
project = 'upoints'
author = 'James Rowe'
copyright = f'2007-2020  {author}'

version = '{major}.{minor}'.format_map(upoints._version.dict)
release = upoints._version.dotted

rst_prolog = """
.. |ISO| replace:: :abbr:`ISO (International Organization for Standardization)`
"""

modindex_common_prefix = [
    'upoints.',
]

trim_footnote_reference_space = True
# }}}

# Options for HTML output {{{
# readthedocs.org handles this setup for their builds, but it is nice to see
# approximately correct builds on the local system too
if not on_rtd:
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [
        sphinx_rtd_theme.get_html_theme_path(),
    ]

with suppress(CalledProcessError):
    proc = run(
        ['git', 'log', '--pretty=format:%ad [%h]', '--date=short', '-n1'],
        stdout=PIPE)
    html_last_updated_fmt = proc.stdout.decode()

html_baseurl = 'https://upoints.readthedocs.io/'

html_copy_source = False
# }}}

# Options for manual page output {{{
man_pages = [('edist.1', 'edist', 'upoints Documentation', [
    'James Rowe',
], 1)]
# }}}

# autodoc extension settings {{{
autoclass_content = 'both'
autodoc_default_options = {
    'members': None,
}
# }}}

# coverage extension settings {{{
coverage_write_headline = False
# }}}

# extlinks extension settings {{{
extlinks = {
    'pypi': ('https://pypi.org/project/%s/', ''),
}
# }}}

# intersphinx extension settings {{{
intersphinx_mapping = {
    k: (v, os.getenv(f'SPHINX_{k.upper()}_OBJECTS'))
    for k, v in {
        'python': 'https://docs.python.org/3/',
    }.items()
}
# }}}

# napoleon extension settings {{{
napoleon_numpy_docstring = False
# }}}

# spelling extension settings {{{
spelling_ignore_acronyms = False
spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'
spelling_ignore_python_builtins = False
spelling_ignore_importable_modules = False
# }}}

# todo extension settings {{{
todo_include_todos = True
# }}}
