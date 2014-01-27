#
# coding=utf-8
"""test_weather_stations - Test weather stations support"""
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

from unittest import TestCase

from expecter import expect

from upoints.weather_stations import (Station, Stations)


class TestStation(TestCase):
    def setUp(self):
        self.x = Station('EGLL', 'London / Heathrow Airport', None,
                         'United Kingdom', 6, 51.4833333333, -0.45, None, None,
                         24, 0, True)

    def test___repr__(self):
        expect(repr(self.x)) == \
            ("Station('EGLL', 'London / Heathrow Airport', None, "
             "'United Kingdom', 6, 51.4833333333, -0.45, None, None, 24, 0, "
             'True)')

    def test___str__(self):
        expect(str(self.x)) == \
            'London / Heathrow Airport (EGLL - N51.483°; W000.450°)'
        self.x.alt_id = None
        expect(str(self.x)) == \
            'London / Heathrow Airport (N51.483°; W000.450°)'
        self.x.alt_id = 'EGLL'

    def test___format__(self):
        expect(format(self.x, 'dms')) == \
            """London / Heathrow Airport (EGLL - 51°28'59"N, 000°27'00"W)"""
        expect(format(self.x, 'dm')) == \
            "London / Heathrow Airport (EGLL - 51°29.00'N, 000°27.00'W)"


class TestStations(TestCase):
    def test_import_locations_wmo(self):
        stations = Stations(open('tests/data/WMO_stations'))
        data = sorted(stations.items())
        expect('%s - %s' % data[0]) == \
            '00000 - Buckland, Buckland Airport (PABL - N65.982°; W161.152°)'
        expect('%s - %s' % data[1]) == \
            '01001 - Jan Mayen (ENJA - N70.933°; W008.667°)'
        expect('%s - %s' % data[2]) == \
            '01002 - Grahuken (N79.783°; E014.467°)'

    def test_import_locations_icao(self):
        stations = Stations(open('tests/data/ICAO_stations'), 'ICAO')
        data = sorted(stations.items())
        expect('%s - %s' % data[0]) == \
            'AYMD - Madang (94014 - S05.217°; E145.783°)'
        expect('%s - %s' % data[1]) == \
            'AYMO - Manus Island/Momote (S02.062°; E147.424°)'
        expect('%s - %s' % data[2]) == \
            'AYPY - Moresby (94035 - S09.433°; E147.217°)'

    def test_import_locations_broken_wmo(self):
        stations = Stations(open('tests/data/broken_WMO_stations'))
        data = sorted(stations.items())
        expect('%s - %s' % data[0]) == \
            '71046 - Komakuk Beach, Y. T. (CWKM - N69.617°; W140.200°)'
        expect('%s - %s' % data[1]) == \
            '71899 - Langara, B. C. (CWLA - N54.250°; W133.133°)'

    def test_import_locations_broken_icao(self):
        stations = Stations(open('tests/data/broken_ICAO_stations'), 'ICAO')
        data = sorted(stations.items())
        expect('%s - %s' % data[0]) == \
            'KBRX - Bordeaux (N41.933°; W104.950°)'
        expect('%s - %s' % data[1]) == \
            'KCQB - Chandler, Chandler Municipal Airport (N35.724°; W096.820°)'
        expect('%s - %s' % data[2]) == \
            'KTYR - Tyler, Tyler Pounds Field (N32.359°; W095.404°)'
