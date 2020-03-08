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

import os
import sys

from contextlib import suppress
from subprocess import (CalledProcessError, run)

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)


import upoints  # NOQA

extensions = \
    ['sphinx.ext.%s' % ext for ext in ['autodoc', 'coverage', 'doctest',
                                       'intersphinx', 'napoleon', 'todo',
                                       'viewcode']] \
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
author = 'James Rowe'
copyright = upoints.__copyright__

version = '.'.join(map(str, upoints._version.tuple[:2]))
release = upoints._version.dotted

pygments_style = 'sphinx'
with suppress(CalledProcessError):
    proc = run(['git', 'log', "--pretty=format:'%ad [%h]'", '--date=short',
                '-n1'], stdout=PIPE)
    html_last_updated_fmt = proc.stdout.decode()

html_baseurl = 'https://hubugs.readthedocs.io/'

man_pages = [
    ('edist.1', 'edist', u'upoints Documentation', [u'James Rowe'], 1)
]

# Autodoc extension settings
autoclass_content = 'both'
autodoc_default_options = {
    'members': None,
}

# intersphinx extension settings
intersphinx_mapping = {k: (v, os.getenv('SPHINX_%s_OBJECTS' % k.upper()))
                       for k, v in {
                           'python': 'http://docs.python.org/',
}.items()}

# spelling extension settings
spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'

# napoleon extension settings
napoleon_numpy_docstring = False

# todo extension settings
todo_include_todos = True
