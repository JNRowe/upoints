#
# coding=utf-8
"""test___init__ - Test package base"""
# Copyright (C) 2006-2011  James Rowe <jnrowe@gmail.com>
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

from upoints import point


def test_base():
    """
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

    """
