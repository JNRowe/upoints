#
# coding=utf-8
"""test_nmea - Test NMEA support"""
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

import datetime

from unittest import TestCase

from pytest import mark

from upoints.nmea import (Fix, Locations, LoranPosition, Position, Waypoint,
                          calc_checksum, nmea_latitude, nmea_longitude,
                          parse_latitude, parse_longitude)


@mark.parametrize('start, end', [
    ('$', '*6B'),
    ('', '*6B'),
    ('$', ''),
    ('', ''),
])
def test_calc_checksum(start, end):
    s = 'GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,'
    assert calc_checksum(start + s + end) == 107


def test_nmea_latitude():
    assert nmea_latitude(53.144023333333337) == ('5308.6414', 'N')


def test_nmea_longitude():
    assert nmea_longitude(-3.0154283333333334) == ('00300.9257', 'W')


def test_parse_latitude():
    assert parse_latitude('5308.6414', 'N') == 53.14402333333334


def test_parse_longitude():
    assert parse_longitude('00300.9257', 'W') == -3.0154283333333334


class TestLoranPosition(TestCase):
    @mark.parametrize('args, result', [
        ((53.1440233333, -3.01542833333, datetime.time(14, 20, 58, 14), True,
          None),
         'LoranPosition(53.1440233333, -3.01542833333, '
                        'datetime.time(14, 20, 58, 14), True, None)'),
        ((53.1440233333, -3.01542833333, datetime.time(14, 20, 58, 14), True,
          'A'),
         'LoranPosition(53.1440233333, -3.01542833333, '
                        "datetime.time(14, 20, 58, 14), True, 'A')"),
    ])
    def test___repr__(self, args, result):
        assert repr(LoranPosition(*args)) == result

    @mark.parametrize('args, result', [
        ((53.1440233333, -3.01542833333, datetime.time(14, 20, 58, 14), True,
          None),
         '$GPGLL,5308.6414,N,00300.9257,W,142058.00,A*1F\r'),
        ((53.1440233333, -3.01542833333, datetime.time(14, 20, 58, 14), True,
          'A'),
         '$GPGLL,5308.6414,N,00300.9257,W,142058.00,A,A*72\r'),
    ])
    def test___str__(self, args, result):
        assert str(LoranPosition(*args)) == result

    def test_mode_string(self):
        position = LoranPosition(53.1440233333, -3.01542833333,
                                 datetime.time(14, 20, 58), True, None)
        assert str(position.mode_string()) == 'Unknown'
        position.mode = 'A'
        assert str(position.mode_string()) == 'Autonomous'

    def test_parse_elements(self):
        assert LoranPosition.parse_elements(['52.32144', 'N', '00300.9257', 'W',
                                             '14205914', 'A']) == \
            LoranPosition(52.005357333333336, -3.0154283333333334,
                          datetime.time(14, 20, 59, 140000), True, None)


class TestPosition(TestCase):
    def setUp(self):
        self.x = Position(datetime.time(14, 20, 58), True, 53.1440233333,
                          -3.01542833333, 109394.7, 202.9,
                          datetime.date(2007, 11, 19), 5.0)

    def test___repr__(self):
        assert repr(self.x) == \
            ('Position(datetime.time(14, 20, 58), True, 53.1440233333, '
             '-3.01542833333, 109394.7, 202.9, datetime.date(2007, 11, 19), '
             '5.0, None)')

    def test___str__(self):
        assert str(self.x) == \
            '$GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E*41\r'

    def test_mode_string(self):
        assert str(self.x.mode_string()) == 'Unknown'
        self.x.mode = 'A'
        assert str(self.x.mode_string()) == 'Autonomous'

    def test_parse_elements(self):
        assert repr(Position.parse_elements(['142058', 'A', '5308.6414', 'N',
                                             '00300.9257', 'W', '109394.7',
                                             '202.9', '191107', '5', 'E', 'A'])) == \
            ('Position(datetime.time(14, 20, 58), True, %s, %s, 109394.7, '
             "202.9, datetime.date(2007, 11, 19), 5.0, 'A')"
             % (53.14402333333334, -3.0154283333333334))
        assert repr(Position.parse_elements(['142100', 'A', '5200.9000', 'N',
                                             '00316.6600', 'W', '123142.7',
                                             '188.1', '191107', '5', 'E', 'A'])) == \
            ('Position(datetime.time(14, 21), True, 52.015, %s, 123142.7, '
             "188.1, datetime.date(2007, 11, 19), 5.0, 'A')"
             % (-3.2776666666666667))


class TestFix(TestCase):
    def setUp(self):
        self.x = Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667,
                     1, 4, 5.6, 1052.3, 34.5)

    def test___repr__(self):
        assert repr(self.x) == \
            ('Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, '
             '1, 4, 5.6, 1052.3, 34.5, None, None, None)')
        self.x.dgps_delta = 12
        self.x.dgps_station = 4
        assert repr(self.x) == \
            ('Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, '
             '1, 4, 5.6, 1052.3, 34.5, 12, 4, None)')

    def test___str__(self):
        assert str(self.x) == \
            '$GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,,*61\r'
        self.x.dgps_delta = 12
        self.x.dgps_station = 4
        assert str(self.x) == \
            '$GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,12.0,0004*78\r'

    def test_quality_string(self):
        assert str(self.x.quality_string()) == 'GPS'

    @mark.parametrize('elements, result', [
        (['142058', '5308.6414', 'N', '00300.9257', 'W', '1', '04', '5.6',
          '1374.6', 'M', '34.5', 'M', '', ''],
         'Fix(datetime.time(14, 20, 58), %s, %s, 1, 4, 5.6, 1374.6, 34.5, '
         'None, None, None)' % (53.14402333333334, -3.0154283333333334)),
        (['142100', '5200.9000', 'N', '00316.6600', 'W', '1', '04', '5.6',
          '1000.0', 'M', '34.5', 'M', '', ''],
         'Fix(datetime.time(14, 21), %s, %s, 1, 4, 5.6, 1000.0, 34.5, None, '
         'None, None)' % (52.015, -3.2776666666666667)),
    ])
    def test_parse_elements(self, elements, result):
        assert repr(Fix.parse_elements(elements)) == result


class TestWaypoint(TestCase):
    def test___repr__(self):
        assert repr(Waypoint(52.015, -0.221, 'Home')) == \
            "Waypoint(52.015, -0.221, 'HOME')"

    def test___str__(self):
        assert str(Waypoint(52.015, -0.221, 'Home')) == \
            '$GPWPL,5200.9000,N,00013.2600,W,HOME*5E\r'

    def test_parse_elements(self):
        assert repr(Waypoint.parse_elements(['5200.9000', 'N', '00013.2600',
                                             'W', 'HOME'])) == \
            "Waypoint(52.015, -0.221, 'HOME')"


class TestLocations(TestCase):
    def test_import_locations(self):
        locations = Locations(open('tests/data/gpsdata'))
        assert [str(x) for x in locations] == [
            '$GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,*6B\r',
            '$GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E,A*2C\r',
            '$GPWPL,5200.9000,N,00013.2600,W,HOME*5E\r',
            '$GPGGA,142100,5200.9000,N,00316.6600,W,1,04,5.6,1000.0,M,34.5,M,,*68\r',
            '$GPRMC,142100,A,5200.9000,N,00316.6600,W,123142.7,188.1,191107,5,E,A*21\r',
        ]
