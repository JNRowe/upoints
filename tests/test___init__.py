#
# coding=utf-8
"""test___init__ - Test package base"""
# Copyright © 2012  James Rowe <jnrowe@gmail.com>
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

import datetime

from expecter import expect

from upoints import point


def test_base():
    Home = point.Point(52.015, -0.221)
    Telford = point.Point(52.6333, -2.5000)
    expect(int(Home.distance(Telford))) == 169
    expect(int(Home.bearing(Telford))) == 294
    expect(int(Home.final_bearing(Telford))) == 293

    expect(Home.sun_events(datetime.date(2007, 6, 28))) == \
        (datetime.time(3, 42), datetime.time(20, 24))
    expect(Home.sunrise(datetime.date(2007, 6, 28))) == \
        datetime.time(3, 42)
    expect(Home.sunset(datetime.date(2007, 6, 28))) == \
        datetime.time(20, 24)
