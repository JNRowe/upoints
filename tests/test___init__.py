#
# coding=utf-8
"""test___init__ - Test package base"""
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

import datetime

from expecter import expect

from upoints import point


def test_base():
    home = point.Point(52.015, -0.221)
    telford = point.Point(52.6333, -2.5000)
    expect(int(home.distance(telford))) == 169
    expect(int(home.bearing(telford))) == 294
    expect(int(home.final_bearing(telford))) == 293

    expect(home.sun_events(datetime.date(2007, 6, 28))) == \
        (datetime.time(3, 42), datetime.time(20, 24))
    expect(home.sunrise(datetime.date(2007, 6, 28))) == \
        datetime.time(3, 42)
    expect(home.sunset(datetime.date(2007, 6, 28))) == \
        datetime.time(20, 24)
