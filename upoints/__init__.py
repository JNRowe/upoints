#
# coding=utf-8
"""upoints - Modules for working with points on Earth"""
# Copyright © 2007-2014  James Rowe <jnrowe@gmail.com>
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

from upoints import _version


__version__ = _version.dotted
__date__ = _version.date
__author__ = 'James Rowe <jnrowe@gmail.com>'
__copyright__ = 'Copyright (C) 2007-2014  James Rowe <jnrowe@gmail.com>'
__license__ = 'GNU General Public License Version 3'
__credits__ = 'Cédric Dufour, Thomas Traber, Kelly Turner, Simon Woods'
__history__ = 'See git repository'

from email.utils import parseaddr

__doc__ += """.

``upoints`` is a collection of `GPL v3`_ licensed modules for working with
points on Earth, or other near spherical objects.  It allows you to calculate
the distance and bearings between points, mangle xearth_/xplanet_ data files,
work with online UK trigpoint databases, NOAA_'s weather station database and
other such location databases.

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://hewgill.com/xearth/original/
.. _xplanet: http://xplanet.sourceforge.net/
.. _NOAA: http://weather.noaa.gov/

The :mod:`upoints.point` module is the simplest interface available, and is
mainly useful as a naïve object for simple calculation and subclassing for
specific usage.  An example of how to use it follows:

>>> from upoints import point
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
(datetime.time(3, 42), datetime.time(20, 24))
>>> Home.sunrise(datetime.date(2007, 6, 28))
datetime.time(3, 42)
>>> Home.sunset(datetime.date(2007, 6, 28))
datetime.time(20, 24)

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

from upoints import (baken, cellid, cities, geonames, gpx, kml, nmea, osm,
                     point, trigpoints, tzdata, utils, weather_stations,
                     xearth)

__all__ = (baken, cellid, cities, geonames, gpx, kml, nmea, osm, point,
           trigpoints, tzdata, utils, weather_stations, xearth)
