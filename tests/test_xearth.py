#
# coding=utf-8
"""test_xearth - Test xearth support"""
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

from unittest import TestCase

from expecter import expect
from nose2.tools import params

from upoints.xearth import (Xearth, Xearths)


class TestXearth(TestCase):
    def test___repr__(self):
        expect(repr(Xearth(52.015, -0.221, "James Rowe's house"))) == \
            """Xearth(52.015, -0.221, "James Rowe's house")"""

    def test___str__(self):
        expect(str(Xearth(52.015, -0.221))) == 'N52.015°; W000.221°'
        expect(str(Xearth(52.015, -0.221, "James Rowe's house"))) == \
            "James Rowe's house (N52.015°; W000.221°)"

    @params(
        ('dms', """52°00'54"N, 000°13'15"W"""),
        ('dm', "52°00.90'N, 000°13.26'W"),
    )
    def test___format__(self, style, result):
        expect(format(Xearth(52.015, -0.221), style)) == result


class TestXearths(TestCase):
    def setUp(self):
        self.markers = Xearths(open('tests/data/xearth'))

    def test___str__(self):
        expect(self.markers.__str__().splitlines()) == \
            ['52.015000 -0.221000 "Home"', '52.633300 -2.500000 "Telford"']

    @params(
        ('Home', "James Rowe's home (N52.015°; W000.221°)"),
        ('Telford', 'N52.633°; W002.500°'),
    )
    def test_import_locations(self, marker, result):
        expect(str(self.markers[marker])) == result
