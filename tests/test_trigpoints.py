#
# coding=utf-8
"""test_trigpoints - Test trigpoints support"""
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

from upoints.trigpoints import (Trigpoint, Trigpoints)


class TestTrigpoint():
    def test___init__(self):
        """
        >>> Trigpoint(52.010585, -0.173443, 97.0, "Bygrave")
        Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave', None)

        """

    def test___str__(self):
        """
        >>> print(Trigpoint(52.010585, -0.173443, 97.0))
        52°00'38"N, 000°10'24"W alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0).__str__(mode="dd"))
        N52.011°; W000.173° alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0).__str__(mode="dm"))
        52°00.64'N, 000°10.41'W alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0, "Bygrave"))
        Bygrave (52°00'38"N, 000°10'24"W alt 97m)

        """


class TestTrigpoints():
    def test_import_locations(self):
        """
        >>> marker_file = open("test/data/trigpoints")
        >>> markers = Trigpoints(marker_file)
        >>> for key, value in sorted(markers.items()):
        ...     print("%s - %s" % (key, value))
        500936 - Broom Farm (52°03'57"N, 000°16'53"W alt 37m)
        501097 - Bygrave (52°00'38"N, 000°10'24"W alt 97m)
        505392 - Sish Lane (51°54'39"N, 000°11'11"W alt 136m)
        >>> marker_file.seek(0)
        >>> markers = Trigpoints(marker_file.readlines())
        >>> markers = Trigpoints(open("test/data/southern_trigpoints"))
        >>> print(markers[1])
        FakeLand (48°07'23"S, 000°07'23"W alt 12m)
        >>> markers = Trigpoints(open("test/data/broken_trigpoints"))
        >>> for key, value in sorted(markers.items()):
        ...     print("%s - %s" % (key, value))
        500968 - Brown Hill Nm  See The Heights (53°38'23"N, 001°39'34"W)
        501414 - Cheriton Hill Nm  See Paddlesworth (51°06'03"N, 001°08'33"E)

        """
