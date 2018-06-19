#
# coding=utf-8
"""test_edist - Test edist interface"""
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

import sys

from doctest import _ellipsis_match as ellipsis_match
from unittest import skipIf

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from click.testing import CliRunner
from pytest import mark, raises

from upoints.compat import PY2
from upoints.edist import (LocationsError, NumberedPoint, NumberedPoints,
                           cli, read_csv)


class TestLocationsError:
    with raises(LocationsError, message='Invalid location data.'):
        raise LocationsError()
    with raises(LocationsError,
                message='More than one location is required for distance.'):
        raise LocationsError('distance')
    with raises(LocationsError,
                message="Location parsing failure in location 4 '52;None'."):
        raise LocationsError(data=(4, '52;None'))


class TestNumberedPoint:
    @mark.parametrize('args, result', [
        ((52.015, -0.221, 4), "NumberedPoint(52.015, -0.221, 4, 'metric')"),
        ((52.015, -0.221, 'Home'),
         "NumberedPoint(52.015, -0.221, 'Home', 'metric')"),
    ])
    def test___repr__(self, args, result):
        assert repr(NumberedPoint(*args)) == result


class TestNumberedPoints:
    def test___repr__(self):
        locations = ['0;0'] * 4
        assert repr(NumberedPoints(locations)) == \
            "NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(0.0, 0.0, 2, 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric'), NumberedPoint(0.0, 0.0, 4, 'metric')], 'dd', True, None, 'km')"

    @skipIf(sys.version_info < (2, 7),
            'Float formatting changes cause failure')
    def test_import_locations(self):
        locs = NumberedPoints(['0;0', 'Home', '0;0'],
                              config_locations={'Home': (52.015, -0.221)})
        assert repr(locs) == "NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(52.015, -0.221, 'Home', 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric')], 'dd', True, {'Home': (52.015, -0.221)}, 'km')"

    def test_display(self, capsys):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.display(None)
        stdout = capsys.readouterr()[0]
        if PY2:
            stdout = stdout.encode('utf-8')
        assert stdout == (
            "Location Home is 52°00.90'N, 000°13.26'W\n"
            "Location 2 is 52°10.08'N, 000°02.40'E\n"
        )

    def test_display_locator(self, capsys):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.format = 'locator'
        locs.display('extsquare')
        assert capsys.readouterr()[0] == (
            'Location Home is IO92va33\n'
            'Location 2 is JO02ae40\n'
        )

    def test_display_non_verbose(self, capsys):
        locs = NumberedPoints(['Home', '52.168;0.040'],
                              config_locations={'Home': (52.015, -0.221)})
        locs.format = 'locator'
        locs.verbose = False
        locs.display('extsquare')
        assert capsys.readouterr()[0] == 'IO92va33\nJO02ae40\n'

    @mark.parametrize('units, result', [
        ('metric', '24 kilometres'),
        ('sm', '15 miles'),
        ('nm', '13 nautical miles'),
    ])
    def test_distance(self, units, result, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'],
                                   units=units)
        locations.distance()
        assert capsys.readouterr()[0] == 'Location 1 to 2 is %s\n' % result

    def test_distance_multi(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                    '51.420;-1.500'])
        locations.distance()
        assert capsys.readouterr()[0] == (
            'Location 1 to 2 is 24 kilometres\n'
            'Location 2 to 3 is 134 kilometres\n'
            'Total distance is 159 kilometres\n'
        )

    def test_bearing(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('bearing', False)
        if PY2:
            output = capsys.readouterr()[0].encode('utf-8')
        else:
            output = capsys.readouterr()[0]
        assert output == 'Location 1 to 2 is 46°\n'

    def test_bearing_symbolic(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('bearing', True)
        assert capsys.readouterr()[0] == 'Location 1 to 2 is North-east\n'

    def test_final_bearing(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('final_bearing', False)
        if PY2:
            output = capsys.readouterr()[0].encode('utf-8')
        else:
            output = capsys.readouterr()[0]
        assert output == 'Final bearing from location 1 to 2 is 46°\n'

    def test_final_bearing_symbolic(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.bearing('final_bearing', True)
        assert capsys.readouterr()[0] == \
            'Final bearing from location 1 to 2 is North-east\n'

    def test_bearing_non_verbose(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.bearing('bearing', True)
        assert capsys.readouterr()[0] == 'North-east\n'

    def test_final_bearing_non_verbose(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.bearing('final_bearing', True)
        assert capsys.readouterr()[0] == 'North-east\n'

    @mark.parametrize('distance, result', [
        (20, False),
        (30, True),
    ])
    def test_range(self, distance, result, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.range(distance)
        stdout = capsys.readouterr()[0]
        if result is True:
            assert 'is within' in stdout
        else:
            assert 'is not within' in stdout

    @mark.parametrize('distance, result', [
        (20, 'False'),
        (30, 'True'),
    ])
    def test_range_non_verbose(self, distance, result, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.verbose = False
        locations.range(distance)
        assert capsys.readouterr()[0] == result + '\n'

    def test_destination(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.destination(42, 240, False)
        stdout = capsys.readouterr()[0]
        if PY2:
            stdout = stdout.encode('utf-8')
        assert stdout == (
            "Destination from location 1 is 52°00.90'N, 000°13.26'W\n"
            "Destination from location 2 is 52°10.08'N, 000°02.40'E\n"
        )

    def test_destination_locator(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.format = 'locator'
        locations.destination(42, 240, 'subsquare')
        assert capsys.readouterr()[0] == (
            'Destination from location 1 is IO91ot\n'
            'Destination from location 2 is IO91sx\n'
        )

    def test_destination_locator_non_verbose(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.format = 'locator'
        locations.verbose = False
        locations.destination(42, 240, 'extsquare')
        assert capsys.readouterr()[0] == 'IO91ot97\nIO91sx14\n'

    def test_sunrise(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.sun_events('sunrise')
        lines = capsys.readouterr()[0].splitlines()
        assert ellipsis_match('Sunrise at ... in location 1', lines[0]) \
            == True
        assert ellipsis_match('Sunrise at ... in location 2', lines[1]) \
            == True

    def test_sunset(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040'])
        locations.sun_events('sunset')
        lines = capsys.readouterr()[0].splitlines()
        assert ellipsis_match('Sunset at ... in location 1', lines[0]) \
            == True
        assert ellipsis_match('Sunset at ... in location 2', lines[1]) \
            == True

    def test_flight_plan(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                    '52.249;0.130', '52.494;0.654'])
        locations.flight_plan(0, 'h')
        if PY2:
            output = capsys.readouterr()[0].encode('utf-8')
        else:
            output = capsys.readouterr()[0]
        assert output == (
            'WAYPOINT,BEARING[°],DISTANCE[km],ELAPSED_TIME[h],LATITUDE[d.dd],LONGITUDE[d.dd]\n'
            '1,,,,52.015000,-0.221000\n'
            '2,46,24.6,,52.168000,0.040000\n'
            '3,34,10.9,,52.249000,0.130000\n'
            '4,52,44.8,,52.494000,0.654000\n'
            '-- OVERALL --#,,80.3,,,\n'
            '-- DIRECT --#,47,79.9,,,\n'
        )

    def test_flight_plan_minute(self, capsys):
        locations = NumberedPoints(['52.015;-0.221', '52.168;0.040',
                                    '52.249;0.130', '52.494;0.654'],
                                   units='nm')
        locations.flight_plan(20, 'm')
        if PY2:
            output = capsys.readouterr()[0].encode('utf-8')
        else:
            output = capsys.readouterr()[0]
        assert output == (
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
    assert sorted(locations.items()) == \
        [('01:My place', ('52.01500', '-0.22100')),
         ('02:Microsoft Research Cambridge', ('52.16700', '00.39000'))]
    assert names == ['01:My place', '02:Microsoft Research Cambridge']


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, ['--location', '52.015;-0.221', '--verbose',
                                 'display'])
    if PY2:
        output = result.output.encode('utf-8')
    else:
        output = result.output
    assert output == \
        "Location 1 is 52°00.90'N, 000°13.26'W\n"
