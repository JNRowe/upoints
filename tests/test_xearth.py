#
"""test_xearth - Test xearth support"""
# Copyright © 2012-2021  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

from pytest import mark

from upoints.xearth import Xearth, Xearths


class TestXearth:
    def test___repr__(self):
        assert (
            repr(Xearth(52.015, -0.221, 'James Rowe’s house'))
            == "Xearth(52.015, -0.221, 'James Rowe’s house')"
        )

    def test___str__(self):
        assert str(Xearth(52.015, -0.221)) == 'N52.015°; W000.221°'
        assert (
            str(Xearth(52.015, -0.221, 'James Rowe’s house'))
            == 'James Rowe’s house (N52.015°; W000.221°)'
        )

    @mark.parametrize(
        'style, result',
        [
            ('dms', '52°00′54″N, 000°13′15″W'),
            ('dm', '52°00.90′N, 000°13.26′W'),
        ],
    )
    def test___format__(self, style, result):
        assert format(Xearth(52.015, -0.221), style) == result


class TestXearths:
    def setup(self):
        with open('tests/data/xearth') as f:
            self.markers = Xearths(f)

    def test___str__(self):
        assert self.markers.__str__().splitlines() == [
            '52.015000 -0.221000 "Home"',
            '52.633300 -2.500000 "Telford"',
        ]

    @mark.parametrize(
        'marker, result',
        [
            ('Home', 'James Rowe’s home (N52.015°; W000.221°)'),
            ('Telford', 'N52.633°; W002.500°'),
        ],
    )
    def test_import_locations(self, marker, result):
        assert str(self.markers[marker]) == result
