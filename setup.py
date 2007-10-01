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

import earth_distance as edist

BASE_URL = "http://www.jnrowe.ukfsn.org/"

from sys import version_info
if version_info < (2, 5, 0, 'final'):
    raise SystemError("Requires Python v2.5+ for conditional expressions")

setup(
    name = "earth_distance",
    version = edist.__version__,
    description = re.sub("C{([^}]*)}", r"\1", 
                         edist.__doc__.splitlines()[1]),
    long_description = """\
``earth_distance`` is a collection of `GPL v3`_ licensed modules for working
with points on a spherical object.  It allows you to calculate the distance and
bearings between points, mangle xearth_/xplanet_ data files, work with online UK
trigpoint databases, NOAA_'s weather station database and other such location
databases.

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://www.cs.colorado.edu/~tuna/xearth/
.. _xplanet: http://xplanet.sourceforge.net/
.. _NOAA: http://weather.noaa.gov/
""",
    author = edist.__author__[0:edist.__author__.rfind(" ")],
    author_email = edist.__author__[edist.__author__.rfind(" ") + 2:-1],
    url = BASE_URL + "projects/earth_distance.html",
    download_url = BASE_URL + "data/earth_distance-%s.tar.bz2" \
                   % edist.__version__,
    packages = ['earth_distance'],
    license = edist.__license__,
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

