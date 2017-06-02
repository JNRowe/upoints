#
# coding=utf-8
"""conf - Sphinx configuration information"""
# Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>
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

from subprocess import (CalledProcessError, check_output)

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, root_dir)


import upoints

extensions = \
    ['sphinx.ext.%s' % ext for ext in ['autodoc', 'coverage', 'doctest',
                                       'intersphinx', 'viewcode', 'todo']] \
    + ['sphinxcontrib.%s' % ext for ext in []]

# Only activate spelling, if it is installed.  It is not required in the
# general case and we don't have the granularity to describe this in a clean
# way
try:
    from sphinxcontrib import spelling  # NOQA
except ImportError:
    pass
else:
    extensions.append('sphinxcontrib.spelling')

master_doc = 'index'
source_suffix = '.rst'

project = u'upoints'
copyright = upoints.__copyright__

version = '.'.join(map(str, upoints._version.tuple[:2]))
release = upoints._version.dotted

pygments_style = 'sphinx'
html_theme_options = {
    'externalrefs': True,
}
try:
    html_last_updated_fmt = check_output(['git', 'log',
                                          "--pretty=format:'%ad [%h]'",
                                          '--date=short', '-n1'])
except CalledProcessError:
    pass

man_pages = [
    ('edist.1', 'edist', u'upoints Documentation', [u'James Rowe'], 1)
]

todo_include_todos = True

# Autodoc extension settings
autoclass_content = 'both'
autodoc_default_flags = ['members', 'show-inheritance']

intersphinx_mapping = {
    'python': ('http://docs.python.org/', os.getenv('SPHINX_PYTHON_OBJECTS')),
}

spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'
