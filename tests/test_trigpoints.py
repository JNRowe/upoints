#
"""test_trigpoints - Test trigpoints support"""
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

from upoints.trigpoints import Trigpoint, Trigpoints


class TestTrigpoint:
    def test___repr__(self):
        assert (
            repr(Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave'))
            == "Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave', None)"
        )

    def test___str__(self):
        assert (
            str(Trigpoint(52.010585, -0.173443, 97.0))
            == '52°00′38″N, 000°10′24″W alt 97m'
        )
        assert (
            str(Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave'))
            == 'Bygrave (52°00′38″N, 000°10′24″W alt 97m)'
        )

    @mark.parametrize(
        'style, result',
        [
            ('dd', 'N52.011°; W000.173° alt 97m'),
            ('dm', '52°00.64′N, 000°10.41′W alt 97m'),
        ],
    )
    def test___format__(self, style, result):
        assert format(Trigpoint(52.010585, -0.173443, 97.0), style) == result


class TestTrigpoints:
    def test_import_locations(self):
        with open('tests/data/trigpoints') as f:
            markers = Trigpoints(f)
        data = ['%s - %s' % (k, v) for k, v in sorted(markers.items())]
        assert data == [
            '500936 - Broom Farm (52°03′57″N, 000°16′53″W alt 37m)',
            '501097 - Bygrave (52°00′38″N, 000°10′24″W alt 97m)',
            '505392 - Sish Lane (51°54′39″N, 000°11′11″W alt 136m)',
        ]
        with open('tests/data/southern_trigpoints') as f:
            markers = Trigpoints(f)
        assert str(markers[1]) == 'FakeLand (48°07′23″S, 000°07′23″W alt 12m)'
        with open('tests/data/broken_trigpoints') as f:
            markers = Trigpoints(f)
        data = ['%s - %s' % (k, v) for k, v in sorted(markers.items())]
        assert data == [
            '500968 - Brown Hill Nm  See The Heights (53°38′23″N, 001°39′34″W)',
            '501414 - Cheriton Hill Nm  See Paddlesworth (51°06′03″N, 001°08′33″E)',
        ]
