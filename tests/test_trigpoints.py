#
# coding=utf-8
"""test_trigpoints - Test trigpoints support"""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
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
from pytest import mark

from upoints.trigpoints import (Trigpoint, Trigpoints)


class TestTrigpoint(TestCase):
    def test___repr__(self):
        expect(repr(Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave'))) == \
            "Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave', None)"

    def test___str__(self):
        expect(str(Trigpoint(52.010585, -0.173443, 97.0))) == \
            """52°00'38"N, 000°10'24"W alt 97m"""
        expect(str(Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave'))) == \
            """Bygrave (52°00'38"N, 000°10'24"W alt 97m)"""

    @mark.parametrize('style, result', [
        ('dd', """N52.011°; W000.173° alt 97m"""),
        ('dm', """52°00.64'N, 000°10.41'W alt 97m"""),
    ])
    def test___format__(self, style, result):
        expect(format(Trigpoint(52.010585, -0.173443, 97.0), style)) == result


class TestTrigpoints(TestCase):
    def test_import_locations(self):
        markers = Trigpoints(open('tests/data/trigpoints'))
        data = ['%s - %s' % (k, v) for k, v in sorted(markers.items())]
        expect(data) == [
            """500936 - Broom Farm (52°03'57"N, 000°16'53"W alt 37m)""",
            """501097 - Bygrave (52°00'38"N, 000°10'24"W alt 97m)""",
            """505392 - Sish Lane (51°54'39"N, 000°11'11"W alt 136m)""",
        ]
        markers = Trigpoints(open('tests/data/southern_trigpoints'))
        expect(str(markers[1])) == \
            """FakeLand (48°07'23"S, 000°07'23"W alt 12m)"""
        markers = Trigpoints(open('tests/data/broken_trigpoints'))
        data = ['%s - %s' % (k, v) for k, v in sorted(markers.items())]
        expect(data) == [
            """500968 - Brown Hill Nm  See The Heights (53°38'23"N, 001°39'34"W)""",
            """501414 - Cheriton Hill Nm  See Paddlesworth (51°06'03"N, 001°08'33"E)""",
        ]
