#
# coding=utf-8
"""test_utils - Test utility functions"""
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

import datetime

from unittest import TestCase

from expecter import expect

from upoints.point import Point
from upoints.trigpoints import Trigpoint
from upoints.utils import (FileFormatError, Timestamp, TzOffset,
                           angle_to_distance, angle_to_name, calc_radius,
                           distance_to_angle, dump_xearth_markers,
                           from_grid_locator, from_iso6709, parse_location,
                           prepare_csv_read, prepare_read, prepare_xml_read,
                           sun_rise_set, to_dd, to_dms, to_grid_locator,
                           to_iso6709, value_or_empty)


class TestFileFormatError(TestCase):
    with expect.raises(FileFormatError, 'Unsupported data format.'):
        raise FileFormatError
    with expect.raises(
        FileFormatError,
        ("Incorrect data format, if you're using a file downloaded "
         'from test site please report this to James Rowe '
         '<jnrowe@gmail.com>')):
        raise FileFormatError('test site')


def test_value_or_empty():
    expect(value_or_empty(None)) == ''
    expect(value_or_empty('test')) == 'test'


def test_prepare_read():
    expect(prepare_read(open('tests/data/real_file'))) == \
        ['This is a test file-type object\n']
    test_list = ['This is a test list-type object', 'with two elements']
    expect(prepare_read(test_list)) == \
        ['This is a test list-type object', 'with two elements']
    expect(prepare_read(open('tests/data/real_file'), 'read')) == \
        'This is a test file-type object\n'


def test_prepare_csv_read():
    expect(list(prepare_csv_read(open('tests/data/real_file.csv'),
                                 ('type', 'bool', 'string')))) == \
        [{'bool': 'true', 'type': 'file', 'string': 'test'}]
    test_list = ['James,Rowe', 'ell,caro']
    expect(list(prepare_csv_read(test_list, ('first', 'last')))) == \
        [{'last': 'Rowe', 'first': 'James'}, {'last': 'caro', 'first': 'ell'}]


def test_prepare_xml_read():
    data = prepare_xml_read(open('tests/data/real_file.xml'))
    expect(data.find('tag').text) == 'This is a test file-type object'
    test_list = ['<xml>', '<tag>This is a test list</tag>', '</xml>']
    expect(prepare_xml_read(test_list).find('tag').text) == \
        'This is a test list'


def test_to_dms():
    expect(to_dms(52.015)) == (52, 0, 54.0)
    expect(to_dms(-0.221)) == (0, -13, -15.600000000000023)
    expect(to_dms(-0.221, style='dm')) == (0, -13.26)
    with expect.raises(ValueError, 'Unknown style type None'):
        to_dms(-0.221, style=None)


def test_to_dd():
    expect('%.3f' % to_dd(52, 0, 54)) == '52.015'
    expect('%.3f' % to_dd(0, -13, -15)) == '-0.221'
    expect('%.3f' % to_dd(0, -13.25)) == '-0.221'


def test_angle_to_name():
    expect(angle_to_name(0)) == 'North'
    expect(angle_to_name(360)) == 'North'
    expect(angle_to_name(45)) == 'North-east'
    expect(angle_to_name(292)) == 'West'
    expect(angle_to_name(293)) == 'North-west'
    expect(angle_to_name(0, 4)) == 'North'
    expect(angle_to_name(360, 16)) == 'North'
    expect(angle_to_name(45, 4, True)) == 'NE'
    expect(angle_to_name(292, 16, True)) == 'WNW'


class TestTzOffset(TestCase):
    def test__offset(self):
        expect(TzOffset('+00:00').utcoffset()) == datetime.timedelta(0)
        expect(TzOffset('-00:00').utcoffset()) == datetime.timedelta(0)
        expect(TzOffset('+05:30').utcoffset()) == datetime.timedelta(0, 19800)
        expect(TzOffset('-08:00').utcoffset()) == datetime.timedelta(-1, 57600)

    def test___repr__(self):
        expect(repr(TzOffset('+00:00'))) == "TzOffset('+00:00')"
        expect(repr(TzOffset('-00:00'))) == "TzOffset('+00:00')"
        expect(repr(TzOffset('+05:30'))) == "TzOffset('+05:30')"
        expect(repr(TzOffset('-08:00'))) == "TzOffset('-08:00')"


class TestTimestamp(TestCase):
    def parse_isoformat(self):
        expect(Timestamp.parse_isoformat('2008-02-06T13:33:26+0000')) == \
            Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))
        expect(Timestamp.parse_isoformat('2008-02-06T13:33:26+00:00')) == \
            Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))
        expect(Timestamp.parse_isoformat('2008-02-06T13:33:26+05:30')) == \
            Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+05:30'))
        expect(Timestamp.parse_isoformat('2008-02-06T13:33:26-08:00')) == \
            Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('-08:00'))
        expect(Timestamp.parse_isoformat('2008-02-06T13:33:26z')) == \
            Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))


def test_from_iso6709_wiki_page():
    # The following tests are from the examples contained in the wikipedia
    # ISO 6709 page(http://en.wikipedia.org/wiki/ISO_6709)

    #  Atlantic Ocean
    expect(from_iso6709('+00-025/')) == (0.0, -25.0, None)
    #  France
    expect(from_iso6709('+46+002/')) == (46.0, 2.0, None)
    #  Paris
    expect(from_iso6709('+4852+00220/')) == \
        (48.86666666666667, 2.3333333333333335, None)
    #  Eiffel Tower
    expect(from_iso6709('+48.8577+002.295/')) == (48.8577, 2.295, None)
    #  Mount Everest
    expect(from_iso6709('+27.5916+086.5640+8850/')) == \
        (27.5916, 86.564, 8850.0)
    #  North Pole
    expect(from_iso6709('+90+000/')) == (90.0, 0.0, None)
    #  Pacific Ocean
    expect(from_iso6709('+00-160/')) == (0.0, -160.0, None)
    #  South Pole
    expect(from_iso6709('-90+000+2800/')) == (-90.0, 0.0, 2800.0)
    #  United States
    expect(from_iso6709('+38-097/')) == (38.0, -97.0, None)
    #  New York City
    expect(from_iso6709('+40.75-074.00/')) == (40.75, -74.0, None)
    #  Statue of Liberty
    expect(from_iso6709('+40.6894-074.0447/')) == (40.6894, -74.0447, None)


def test_from_iso6709_location_page():
    # The following tests are from the Latitude, Longitude and Altitude format
    # for geospatial information page
    # (http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude)

    #  Mount Everest
    expect(from_iso6709('+27.5916+086.5640+8850/')) == \
        (27.5916, 86.564, 8850.0)
    #  South Pole
    expect(from_iso6709('-90+000+2800/')) == (-90.0, 0.0, 2800.0)
    #  New York City
    expect(from_iso6709('+40.75-074.00/')) == (40.75, -74.0, None)
    #  Mount Fuji
    expect(from_iso6709('+352139+1384339+3776/')) == \
        (35.36083333333333, 138.7275, 3776.0)
    #  Tokyo Tower
    expect(from_iso6709('+35.658632+139.745411/')) == \
        (35.658632, 139.745411, None)

    with expect.raises(ValueError, "Incorrect format for longitude '+1'"):
        from_iso6709('+35.658632+1/')


def test_to_iso6709_wiki_page():
    # The following tests are from the examples contained in the wikipedia
    # ISO 6709 page(http://en.wikipedia.org/wiki/ISO_6709)

    #  Atlantic Ocean
    expect(to_iso6709(0.0, -25.0, None, 'd')) == '+00-025/'
    #  France
    expect(to_iso6709(46.0, 2.0, None, 'd')) == '+46+002/'
    #  Paris
    expect(to_iso6709(48.866666666666667, 2.3333333333333335, None, 'dm')) == \
        '+4852+00220/'

    #FIXME
    #  The following test is skipped, because the example from wikipedia
    #  uses differing precision widths for latitude and longitude. Also,
    #  that degree of formatting flexibility is not seen anywhere else and
    #  adds very little.
    #  Eiffel Tower
    #expect(to_iso6709(48.857700000000001, 2.2949999999999999, None)) == \
    #    '+48.8577+002.295/'

    #  Mount Everest
    expect(to_iso6709(27.5916, 86.563999999999993, 8850.0)) == \
        '+27.5916+086.5640+8850/'
    #  North Pole
    expect(to_iso6709(90.0, 0.0, None, 'd')) == '+90+000/'
    #  Pacific Ocean
    expect(to_iso6709(0.0, -160.0, None, 'd')) == '+00-160/'
    #  South Pole
    expect(to_iso6709(-90.0, 0.0, 2800.0, 'd')) == '-90+000+2800/'
    #  United States
    expect(to_iso6709(38.0, -97.0, None, 'd')) == '+38-097/'
    #  New York City
    expect(to_iso6709(40.75, -74.0, None, precision=2)) == '+40.75-074.00/'
    #  Statue of Liberty
    expect(to_iso6709(40.689399999999999, -74.044700000000006, None)) == \
        '+40.6894-074.0447/'


def test_to_iso6709_location_page():
    # The following tests are from the Latitude, Longitude and Altitude format
    # for geospatial information page
    # (http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude)

    #  Mount Everest
    expect(to_iso6709(27.5916, 86.563999999999993, 8850.0)) == \
        '+27.5916+086.5640+8850/'
    #  South Pole
    expect(to_iso6709(-90.0, 0.0, 2800.0, 'd')) == '-90+000+2800/'
    #  New York City
    expect(to_iso6709(40.75, -74.0, None, precision=2)) == '+40.75-074.00/'
    #  Mount Fuji
    expect(to_iso6709(35.360833333333332, 138.72749999999999, 3776.0,
                      'dms')) == '+352139+1384339+3776/'
    #  Tokyo Tower
    expect(to_iso6709(35.658631999999997, 139.74541099999999, None,
                      precision=6)) == '+35.658632+139.745411/'


def test_angle_to_distance():
    expect('%.3f' % angle_to_distance(1)) == '111.125'
    expect('%i' % angle_to_distance(360, 'imperial')) == '24863'
    expect('%i' % angle_to_distance(1.0 / 60, 'nautical')) == '1'

    with expect.raises(ValueError, "Unknown units type 'baseless'"):
        '%i' % angle_to_distance(10, 'baseless')


def test_distance_to_angle():
    expect('%.3f' % round(distance_to_angle(111.212))) == '1.000'
    expect('%i' % round(distance_to_angle(24882, 'imperial'))) == '360'
    expect('%i' % round(distance_to_angle(60, 'nautical'))) == '1'


def test_from_grid_locator():
    expect('%.3f, %.3f' % from_grid_locator('BL11bh16')) == '21.319, -157.904'
    expect('%.3f, %.3f' % from_grid_locator('IO92va')) == '52.021, -0.208'
    expect('%.3f, %.3f' % from_grid_locator('IO92')) == '52.021, -1.958'


def test_to_grid_locator():
    expect(to_grid_locator(21.319, -157.904, 'extsquare')) == 'BL11bh16'
    expect(to_grid_locator(52.021, -0.208, 'subsquare')) == 'IO92va'
    expect(to_grid_locator(52.021, -1.958)) == 'IO92'


def test_parse_location():
    expect('%.3f;%.3f' % parse_location('52.015;-0.221')) == '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52.015,-0.221')) == '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52.015 -0.221')) == '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52.015N 0.221W')) == '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52.015 N 0.221 W')) == '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52d00m54s N 0d13m15s W')) == \
        '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('52d0m54s N 000d13m15s W')) == \
        '52.015;-0.221'
    expect('%.3f;%.3f' % parse_location('''52d0'54" N 000d13'15" W''')) == \
        '52.015;-0.221'


def test_sun_rise_set():
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15))) == \
        datetime.time(3, 40)
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15),
                        'set')) == \
        datetime.time(20, 22)
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15),
                        timezone=60)) == datetime.time(4, 40)
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), 'set',
                        60)) == datetime.time(21, 22)
    expect(sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11))) == \
        datetime.time(7, 58)
    expect(sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11),
                        'set')) == datetime.time(15, 49)
    expect(sun_rise_set(89, 0, datetime.date(2007, 12, 21))) == None
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 2, 21))) == \
        datetime.time(7, 4)
    expect(sun_rise_set(52.015, -0.221, datetime.date(2007, 1, 21))) == \
        datetime.time(7, 56)


def sun_events():
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15))) == \
        (datetime.time(3, 40), datetime.time(20, 22))
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15), 60)) == \
        (datetime.time(4, 40), datetime.time(21, 22))
    expect(sun_events(52.015, -0.221, datetime.date(1993, 12, 11))) == \
        (datetime.time(7, 58), datetime.time(15, 49))
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15))) == \
        (datetime.time(3, 40), datetime.time(20, 22))
    expect(sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15))) == \
        (datetime.time(9, 23), datetime.time(0, 27))
    expect(sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15))) == \
        (datetime.time(4, 5), datetime.time(20, 15))
    expect(sun_events(35.549999, 139.78333333,
                      datetime.date(2007, 6, 15))) == \
        (datetime.time(19, 24), datetime.time(9, 57))


def sun_events_civil():
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
                      zenith='civil')) == \
        (datetime.time(2, 51), datetime.time(21, 11))
    expect(sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
                      zenith='civil')) == \
        (datetime.time(8, 50), datetime.time(1, 0))
    expect(sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
                      zenith='civil')) == \
        (datetime.time(3, 22), datetime.time(20, 58))
    expect(sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
                      zenith='civil')) == \
        (datetime.time(18, 54), datetime.time(10, 27))


def sun_events_nautical():
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
                      zenith='nautical')) == \
        (datetime.time(1, 32), datetime.time(22, 30))
    expect(sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
                      zenith='nautical')) == \
        (datetime.time(8, 7), datetime.time(1, 44))
    expect(sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
                      zenith='nautical')) == \
        (datetime.time(2, 20), datetime.time(22, 0))
    expect(sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
                      zenith='nautical')) == \
        (datetime.time(18, 17), datetime.time(11, 5))


def sun_events_astronomical():
    expect(sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
                      zenith='astronomical')) == (None, None)
    expect(sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
                      zenith='astronomical')) == \
        (datetime.time(7, 14), datetime.time(2, 36))
    expect(sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
                      zenith='astronomical')) == (None, None)
    expect(sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
                      zenith='astronomical')) == \
        (datetime.time(17, 34), datetime.time(11, 48))


def test_dump_xearth_markers():
    markers = {
        500936: Trigpoint(52.066035, -0.281449, 37.000000, 'Broom Farm'),
        501097: Trigpoint(52.010585, -0.173443, 97.000000, 'Bygrave'),
        505392: Trigpoint(51.910886, -0.186462, 136.000000, 'Sish Lane')
    }
    data = dump_xearth_markers(markers)
    expect(data[0]) == '52.066035 -0.281449 "500936" # Broom Farm, alt 37m'
    expect(data[1]) == '52.010585 -0.173443 "501097" # Bygrave, alt 97m'
    expect(data[2]) == '51.910886 -0.186462 "505392" # Sish Lane, alt 136m'

    data = dump_xearth_markers(markers, 'name')
    expect(data[0]) == '52.066035 -0.281449 "Broom Farm" # 500936, alt 37m'
    expect(data[1]) == '52.010585 -0.173443 "Bygrave" # 501097, alt 97m'
    expect(data[2]) == '51.910886 -0.186462 "Sish Lane" # 505392, alt 136m'

    with expect.raises(ValueError, "Unknown name type 'falseKey'"):
        dump_xearth_markers(markers, 'falseKey')

    points = {
        'Broom Farm': Point(52.066035, -0.281449),
        'Bygrave': Point(52.010585, -0.173443),
        'Sish Lane': Point(51.910886, -0.186462)
    }
    data = dump_xearth_markers(points)
    expect(data[0]) == '52.066035 -0.281449 "Broom Farm"'
    expect(data[1]) == '52.010585 -0.173443 "Bygrave"'
    expect(data[2]) == '51.910886 -0.186462 "Sish Lane"'


def test_calc_radius():
    expect(calc_radius(52.015)) == 6375.166025311857
    expect(calc_radius(0)) == 6335.438700909687
    expect(calc_radius(90)) == 6399.593942121543
    expect(calc_radius(52.015, 'FAI sphere')) == 6371.0
    expect(calc_radius(0, 'Airy (1830)')) == 6335.022178542022
    expect(calc_radius(90, 'International')) == 6399.936553871439
