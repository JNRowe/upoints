#
# coding=utf-8
"""test_edist - Test edist interface"""
# Copyright © 2007-2013  James Rowe <jnrowe@gmail.com>
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

import sys

from StringIO import StringIO
from doctest import _ellipsis_match as ellipsis_match
from unittest import TestCase

from expecter import expect
from mock import patch

from upoints.edist import (LocationsError, NumberedPoint, NumberedPoints,
                           main, read_csv)


class TestLocationsError(TestCase):
    with expect.raises(LocationsError, 'Invalid location data.'):
        raise LocationsError()
    with expect.raises(LocationsError,
                       'More than one location is required for distance.'):
        raise LocationsError('distance')
    with expect.raises(LocationsError,
                       "Location parsing failure in location 4 '52;None'."):
        raise LocationsError(data=(4, '52;None'))


class TestNumberedPoint(TestCase):
    def test___repr__(self):
        expect(repr(NumberedPoint(52.015, -0.221, 4))) == \
            "NumberedPoint(52.015, -0.221, 4, 'metric')"
        expect(repr(NumberedPoint(52.015, -0.221, 'Home'))) == \
            "NumberedPoint(52.015, -0.221, 'Home', 'metric')"


class TestNumberedPoints(TestCase):
    def test___repr__(self):
        locations = ['0;0'] * 4
        expect(repr(NumberedPoints(locations))) == \
            "NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(0.0, 0.0, 2, 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric'), NumberedPoint(0.0, 0.0, 4, 'metric')], 'dd', True, True, None, 'km')"

    def test_import_locations(self):
        locs = NumberedPoints(['0;0', 'Home', '0;0'],
                              config_locations={'Home': (52.015, -0.221)})
        expect(repr(locs)) == "NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(52.015, -0.221, 'Home', 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric')], 'dd', True, True, {'Home': (52.015, -0.221)}, 'km')"

    @patch('sys.stdout', new_callable=StringIO)
    def test_display(self, stdout):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.display(None)
        expect(stdout.getvalue()) == (
            'Location Home is N52.015°; W000.221°\n'
            'Location 2 is N52.168°; E000.040°\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_locator(self, stdout):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.format = 'locator'
        locs.display('extsquare')
        expect(stdout.getvalue()) == (
            'Location Home is IO92va33\n'
            'Location 2 is JO02ae40\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_non_verbose(self, stdout):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.format = 'locator'
        locs.verbose = False
        locs.display('extsquare')
        expect(stdout.getvalue()) == 'IO92va33\nJO02ae40\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_distance(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.distance()
        expect(stdout.getvalue()) == 'Location 1 to 2 is 24 kilometres\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_distance_sm(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'],
                                   units='sm')
        locations.distance()
        expect(stdout.getvalue()) == 'Location 1 to 2 is 15 miles\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_distance_nm(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'],
                                   units='nm')
        locations.verbose = False
        locations.distance()
        expect(stdout.getvalue()) == '13.2989574317\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_distance_multi(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                   '51.420;-1.500'])
        locations.distance()
        expect(stdout.getvalue()) == (
            'Location 1 to 2 is 24 kilometres\n'
            'Location 2 to 3 is 134 kilometres\n'
            'Total distance is 159 kilometres\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_bearing(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('bearing', False)
        expect(stdout.getvalue()) == 'Location 1 to 2 is 46°\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_bearing_symbolic(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('bearing', True)
        expect(stdout.getvalue()) == 'Location 1 to 2 is North-east\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_final_bearing(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('final_bearing', False)
        expect(stdout.getvalue()) == \
            'Final bearing from location 1 to 2 is 46°\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_final_bearing_symbolic(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('final_bearing', True)
        expect(stdout.getvalue()) == \
            'Final bearing from location 1 to 2 is North-east\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_bearing_non_verbose(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.bearing('bearing', True)
        expect(stdout.getvalue()) == 'North-east\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_final_bearing_non_verbose(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.bearing('final_bearing', True)
        expect(stdout.getvalue()) == 'North-east\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_range(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.range(20)
        expect(stdout.getvalue()) == \
            'Location 2 is not within 20 kilometres of location 1\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_range2(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.range(30)
        expect(stdout.getvalue()) == \
            'Location 2 is within 30 kilometres of location 1\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_range_non_verbose(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.range(30)
        expect(stdout.getvalue()) == 'True\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_destination(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.destination(42, 240, False)
        expect(stdout.getvalue()) == (
            'Destination from location 1 is N51.825°; W000.751°\n'
            'Destination from location 2 is N51.978°; W000.491°\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_destination_locator(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.format = 'locator'
        locations.destination(42, 240, 'subsquare')
        expect(stdout.getvalue()) == (
            'Destination from location 1 is IO91ot\n'
            'Destination from location 2 is IO91sx\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_destination_locator_non_verbose(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.format = 'locator'
        locations.verbose = False
        locations.destination(42, 240, 'extsquare')
        expect(stdout.getvalue()) == 'IO91ot97\nIO91sx14\n'

    @patch('sys.stdout', new_callable=StringIO)
    def test_sunrise(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.sun_events('sunrise')
        lines = stdout.getvalue().splitlines()
        expect(ellipsis_match('Sunrise at ... in location 1', lines[0])) \
            == True
        expect(ellipsis_match('Sunrise at ... in location 2', lines[1])) \
            == True

    @patch('sys.stdout', new_callable=StringIO)
    def test_sunset(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.sun_events('sunset')
        lines = stdout.getvalue().splitlines()
        expect(ellipsis_match('Sunset at ... in location 1', lines[0])) \
            == True
        expect(ellipsis_match('Sunset at ... in location 2', lines[1])) \
            == True

    @patch('sys.stdout', new_callable=StringIO)
    def test_flight_plan(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                   '52.249;0.130', '52.494;0.654'])
        locations.flight_plan(0, 'h')
        expect(stdout.getvalue()) == (
            'WAYPOINT,BEARING[°],DISTANCE[km],ELAPSED_TIME[h],LATITUDE[d.dd],LONGITUDE[d.dd]\n'
            '1,,,,52.015000,-0.221000\n'
            '2,46,24.6,,52.168000,0.040000\n'
            '3,34,10.9,,52.249000,0.130000\n'
            '4,52,44.8,,52.494000,0.654000\n'
            '-- OVERALL --#,,80.3,,,\n'
            '-- DIRECT --#,47,79.9,,,\n'
        )

    @patch('sys.stdout', new_callable=StringIO)
    def test_flight_plan_minute(self, stdout):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                    '52.249;0.130', '52.494;0.654'],
                                   units='nm')
        locations.flight_plan(20, 'm')
        expect(stdout.getvalue()) == (
            'WAYPOINT,BEARING[°],DISTANCE[nm],ELAPSED_TIME[m],LATITUDE[d.dd],LONGITUDE[d.dd]\n'
            '1,,,,52.015000,-0.221000\n'
            '2,46,13.3,0.7,52.168000,0.040000\n'
            '3,34,5.9,0.3,52.249000,0.130000\n'
            '4,52,24.2,1.2,52.494000,0.654000\n'
            '-- OVERALL --,,43.4,2.2,,\n'
            '-- DIRECT --,47,43.1,2.2,,\n'
        )


def test_read_csv():
    locations, names = read_csv(open('tests/data/gpsbabel'))
    expect(sorted(locations.items())) == \
        [('01:My place', ('52.01500', '-0.22100')),
         ('02:Microsoft Research Cambridge', ('52.16700', '00.39000'))]
    expect(names) == ['01:My place', '02:Microsoft Research Cambridge']


@patch('sys.stdout', new_callable=StringIO)
@patch.object(sys, 'argv', ['edist', '--unicode', 'display', '52.015;-0.221'])
def test_main(stdout):
    main()
    expect(stdout.getvalue()) == 'Location 1 is 52°00′54″N, 000°13′15″W\n'
