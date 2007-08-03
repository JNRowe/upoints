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

long_description = """
``earth_distance`` is a collection of GPL v3 licensed modules for working with
points on a spherical object.  It allows you to calculate the distance and
bearings between points, mangle xearth_/xplanet_ data files, work with online UK
trigpoint databases, `GNU miscfiles`_ city databases and NOAA_'s weather station
database.

The ``earth_distance.point`` module is the simplest interface available, and is
mainly useful as a naïve object for simple calculation and for subclassing for
specific usage.  An example of how to use it follows::

    >>> Home = point.Point(52.015, -0.221)
    >>> Telford = point.Point(52.6333, -2.5000)
    >>> int(Home.distance(Telford))
    169
    >>> int(Home.bearing(Telford))
    294
    >>> int(Home.final_bearing(Telford))
    293
    >>> import datetime
    >>> Home.sun_events(datetime.date(2007, 6, 28))
    (datetime.time(3, 42), datetime.time(20, 25))
    >>> Home.sunrise(datetime.date(2007, 6, 28))
    datetime.time(3, 42)
    >>> Home.sunset(datetime.date(2007, 6, 28))
    datetime.time(20, 25)

.. _xearth: http://www.cs.colorado.edu/~tuna/xearth/
.. _xplanet: http://xplanet.sourceforge.net/
.. _GNU miscfiles: http://www.gnu.org/directory/miscfiles.html
.. _NOAA: http://weather.noaa.gov/
"""

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

