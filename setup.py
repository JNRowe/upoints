#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""earth_distance - Modules for working with points on a spherical object"""
# Copyright (C) 2007  James Rowe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from distutils.core import setup

import re
import textwrap

import earth_distance

from sys import version_info
if version_info < (2, 5, 0, 'final'):
    raise SystemExit("Requires Python v2.5+ for conditional expressions")

# Pull the documentation from main docstring, and remove links
long_description = re.sub("U{([^<]*)[^}]*}", r"\1",
                          earth_distance.__doc__[:earth_distance.__doc__.rfind('\n\n')])
# Convert epytext style command markup to reST.
long_description = re.sub("C{([^}]*)}", r"``\1``",
                          long_description).splitlines()[1:]
# Refill the text, to fix the formatting post-substition
long_description = textwrap.fill("".join(long_description))

setup(
    name = "earth_distance",
    version = earth_distance.__version__,
    description = re.sub("C{([^}]*)}", r"\1", 
                         earth_distance.__doc__.splitlines()[1]),
    long_description = long_description,
    author = earth_distance.__author__[0:earth_distance.__author__.rfind(" ")],
    author_email = earth_distance.__author__[earth_distance.__author__.rfind(" ") + 2:-1],
    url = "http://www.jnrowe.ukfsn.org/projects/earth_distance.html",
    download_url = "http://www.jnrowe.ukfsn.org/data/earth_distance-%s.tar.bz2" \
                   % earth_distance.__version__,
    packages = ['earth_distance'],
    license = earth_distance.__license__,
    keywords = ['navigation', 'xearth', 'trigpointing', 'cities', 'weather'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Text Processing :: Filters',
    ],
    options = {'sdist': {'formats': 'bztar'}},
)

