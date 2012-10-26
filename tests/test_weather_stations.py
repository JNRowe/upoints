#
# coding=utf-8
"""test_weather_stations - Test weather stations support"""
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

from upoints.weather_stations import (Station, Stations)


class TestStation():
    def test___init__(self):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Station('EGLL', 'London / Heathrow Airport', None,
        ...         'United Kingdom', 6, 51.4833333333, -0.45, None, None, 24,
        ...         0, True)
        Station('EGLL', 'London / Heathrow Airport', None, 'United Kingdom', 6,
                51.4833333333, -0.45, None, None, 24, 0, True)

        """

    def test___str__(self):
        """
        >>> Heathrow = Station("EGLL", "London / Heathrow Airport", None,
        ...                    "United Kingdom", 6, 51.048333, -0.450000, None,
        ...                    None, 24, 0, True)
        >>> print(Heathrow)
        London / Heathrow Airport (EGLL - N51.048°; W000.450°)
        >>> print(Heathrow.__str__(mode="dms"))
        London / Heathrow Airport (EGLL - 51°02'53"N, 000°27'00"W)
        >>> print(Heathrow.__str__(mode="dm"))
        London / Heathrow Airport (EGLL - 51°02.90'N, 000°27.00'W)
        >>> Heathrow.alt_id = None
        >>> print(Heathrow)
        London / Heathrow Airport (N51.048°; W000.450°)

        """


class TestStations():
    def test_import_locations(self):
        """
        >>> stations = Stations(open("test/data/WMO_stations"))
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        00000 - Buckland, Buckland Airport (PABL - N65.982°; W161.152°)
        01001 - Jan Mayen (ENJA - N70.933°; W008.667°)
        01002 - Grahuken (N79.783°; E014.467°)
        >>> stations = Stations(open("test/data/ICAO_stations"), "ICAO")
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        AYMD - Madang (94014 - S05.217°; E145.783°)
        AYMO - Manus Island/Momote (S02.062°; E147.424°)
        AYPY - Moresby (94035 - S09.433°; E147.217°)
        >>> stations = Stations(open("test/data/broken_WMO_stations"))
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        71046 - Komakuk Beach, Y. T. (CWKM - N69.617°; W140.200°)
        71899 - Langara, B. C. (CWLA - N54.250°; W133.133°)
        >>> stations = Stations(open("test/data/broken_ICAO_stations"), "ICAO")
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        KBRX - Bordeaux (N41.933°; W104.950°)
        KCQB - Chandler, Chandler Municipal Airport (N35.724°; W096.820°)
        KTYR - Tyler, Tyler Pounds Field (N32.359°; W095.404°)

        """
