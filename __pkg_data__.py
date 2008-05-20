#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""Per-package configuration data"""
# Copyright (C) 2008  James Rowe
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

import sys

import upoints
MODULE = upoints

import edist
SCRIPTS = [edist, ]

DESCRIPTION = upoints.__doc__.splitlines()[0][:-1]
LONG_DESCRIPTION = "\n\n".join(upoints.__doc__.split("\n\n")[1:3])

KEYWORDS = ['navigation', 'xearth', 'trigpointing', 'cities', 'baken',
            'weather', 'geonames', 'openstreetmap', 'nmea', 'gpx']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
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
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing :: Filters',
]

OBSOLETES = ["earth_distance", ]

GRAPH_TYPE = None

TEST_EXTRAGLOBS = ["pymetar", ]

def TestCode_run(dry_run, force):
    """Display a warning about test failures when using lxml"""
    if "lxml" in sys.modules:
        print("Tests are designed to be run using cElementTree, running them "
              "with lxml will result in failures due to output format "
              "differences between the modules.")
TestDoc_run = TestCode_run

