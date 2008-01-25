#! /usr/bin/python -tt
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

from distutils.dep_util import newer
from distutils.errors import DistutilsModuleError
from re import sub

try:
    import Image
    IMAGE = True #: True if C{Image} module is available
except ImportError:
    IMAGE = False

import earth_distance
module = earth_distance

import edist
scripts = [edist, ]

description = sub("C{([^}]*)}", r"\1",
                  earth_distance.__doc__.splitlines()[0][:-1])
long_description = """\
``earth_distance`` is a collection of `GPL v3`_ licensed modules for working
with points on Earth, or other near spherical objects.  It allows you to
calculate the distance and bearings between points, mangle xearth_/xplanet_
data files, work with online UK trigpoint databases, NOAA_'s weather station
database and other such location databases.

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://www.cs.colorado.edu/~tuna/xearth/
.. _xplanet: http://xplanet.sourceforge.net/
.. _NOAA: http://weather.noaa.gov/
"""

keywords = ['navigation', 'xearth', 'trigpointing', 'cities', 'baken',
            'weather', 'geonames', 'openstreetmap', 'nmea', 'gpx']
classifiers = [
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

test_extraglobs = ["pymetar", ]

def BuildDoc_run(dry_run, force):
    """
    Non-standard C{setup.BuildDoc} commands
    """
    if not IMAGE:
        raise DistutilsModuleError("Image(python-imaging) import failed, "
                                   "can't generate image thumbnails")
    for image in ["ranged_trigpoints", "Scotland_trigpoints", "xearth_trip",
                  "xplanet_trip_date"]:
        original = "doc/images/%s.png" % image
        thumb = "doc/images/%s_mini.png" % image
        if force or newer(original, thumb):
            print("Generating thumbnail %s" % thumb)
            if dry_run:
                continue
            im = Image.open(original)
            im.thumbnail((256, 192))
            im.save(thumb)
