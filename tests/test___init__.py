#
# coding=utf-8
"""test___init__ - Test package base"""
# Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>
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

import datetime

from upoints import point


def test_base():
    home = point.Point(52.015, -0.221)
    telford = point.Point(52.6333, -2.5000)
    assert int(home.distance(telford)) == 169
    assert int(home.bearing(telford)) == 294
    assert int(home.final_bearing(telford)) == 293

    assert home.sun_events(datetime.date(2007, 6, 28)) == \
        (datetime.time(3, 42), datetime.time(20, 24))
    assert home.sunrise(datetime.date(2007, 6, 28)) == \
        datetime.time(3, 42)
    assert home.sunset(datetime.date(2007, 6, 28)) == \
        datetime.time(20, 24)
