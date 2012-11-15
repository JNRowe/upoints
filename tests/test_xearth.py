#
# coding=utf-8
"""test_xearth - Test xearth support"""
# Copyright (C) 2006-2012  James Rowe <jnrowe@gmail.com>
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

from unittest import TestCase

from expecter import expect

from upoints.xearth import (Xearth, Xearths)


class TestXearth(TestCase):
    def test___repr__(self):
        expect(repr(Xearth(52.015, -0.221, "James Rowe's house"))) == \
            """Xearth(52.015, -0.221, "James Rowe's house")"""

    def test___str__(self):
        expect(str(Xearth(52.015, -0.221))) == 'N52.015°; W000.221°'
        expect(str(Xearth(52.015, -0.221).__str__(mode="dms"))) == \
            """52°00'54"N, 000°13'15"W"""
        expect(str(Xearth(52.015, -0.221).__str__(mode="dm"))) == \
            "52°00.90'N, 000°13.26'W"
        expect(str(Xearth(52.015, -0.221, "James Rowe's house"))) == \
            "James Rowe's house (N52.015°; W000.221°)"


class TestXearths(TestCase):
    def test___str__(self):
        markers = Xearths(open("test/data/xearth"))
        expect(markers.__str__().splitlines()) == \
            ['52.015000 -0.221000 "Home"', '52.633300 -2.500000 "Telford"']

    def test_import_locations(self):
        markers = Xearths(open("test/data/xearth"))
        expect(str(markers['Home'])) == \
            "James Rowe's home (N52.015°; W000.221°)"
        expect(str(markers['Telford'])) == "N52.633°; W002.500°"
