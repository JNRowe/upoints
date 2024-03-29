#
"""test_utils - Test utility functions"""
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

import datetime

from pytest import approx, mark, raises

from upoints.point import Point
from upoints.trigpoints import Trigpoint
from upoints.utils import (
    FileFormatError,
    Timestamp,
    TzOffset,
    angle_to_distance,
    angle_to_name,
    calc_radius,
    distance_to_angle,
    dump_xearth_markers,
    from_grid_locator,
    from_iso6709,
    parse_location,
    prepare_csv_read,
    prepare_read,
    prepare_xml_read,
    sun_events,
    sun_rise_set,
    to_dd,
    to_dms,
    to_grid_locator,
    to_iso6709,
    value_or_empty,
)


class TestFileFormatError:
    with raises(FileFormatError, match='Unsupported data format.'):
        raise FileFormatError
    with raises(
        FileFormatError,
        match=(
            'Incorrect data format, if you’re using a file downloaded from '
            'test site please report this to James Rowe '
            '<jnrowe@gmail.com>'
        ),
    ):
        raise FileFormatError('test site')


@mark.parametrize(
    'val, result',
    [
        (None, ''),
        ('test', 'test'),
    ],
)
def test_value_or_empty(val, result):
    assert value_or_empty(val) == result


@mark.parametrize(
    'data, result',
    [
        (open('tests/data/real_file'), ['This is a test file-type object\n']),
        (
            ['This is a test list-type object', 'with two elements'],
            ['This is a test list-type object', 'with two elements'],
        ),
    ],
)
def test_prepare_read(data, result):
    assert prepare_read(data) == result


def test_prepare_read_read():
    with open('tests/data/real_file') as f:
        assert prepare_read(f) == [
            'This is a test file-type object\n',
        ]


@mark.parametrize(
    'data, keys, result',
    [
        (
            open('tests/data/real_file.csv'),
            ('type', 'bool', 'string'),
            [{'bool': 'true', 'type': 'file', 'string': 'test'}],
        ),
        (
            ['James,Rowe', 'ell,caro'],
            ('first', 'last'),
            [
                {'last': 'Rowe', 'first': 'James'},
                {'last': 'caro', 'first': 'ell'},
            ],
        ),
    ],
)
def test_prepare_csv_read(data, keys, result):
    assert list(prepare_csv_read(data, keys)) == result


@mark.parametrize(
    'data, result',
    [
        (open('tests/data/real_file.xml'), 'This is a test file-type object'),
        (
            ['<xml>', '<tag>This is a test list</tag>', '</xml>'],
            'This is a test list',
        ),
    ],
)
def test_prepare_xml_read(data, result):
    xml = prepare_xml_read(data)
    assert xml.find('tag').text == result


@mark.parametrize(
    'angle, result',
    [
        (52.015, (52, 0, 54.0)),
        (-0.221, (0, -13, -15.600000000000023)),
    ],
)
def test_to_dms(angle, result):
    assert to_dms(angle) == result


def test_to_dms_style():
    assert to_dms(-0.221, style='dm') == (0, -13.26)


def test_to_dms_error():
    with raises(ValueError, match='Unknown style type None'):
        to_dms(-0.221, style=None)


@mark.parametrize(
    'angle, result',
    [
        ((52, 0, 54), 52.015),
        ((0, -13, -15), -0.221),
        ((0, -13.25), -0.221),
    ],
)
def test_to_dd(angle, result):
    assert to_dd(*angle) == approx(result, rel=0.001)


@mark.parametrize(
    'args, result',
    [
        ((0,), 'North'),
        ((360,), 'North'),
        ((45,), 'North-east'),
        ((292,), 'West'),
        ((293,), 'North-west'),
        ((0, 4), 'North'),
        ((360, 16), 'North'),
        ((45, 4, True), 'NE'),
        ((292, 16, True), 'WNW'),
    ],
)
def test_angle_to_name(args, result):
    assert angle_to_name(*args) == result


class TestTzOffset:
    @mark.parametrize(
        'string, result',
        [
            ('+00:00', datetime.timedelta(0)),
            ('-00:00', datetime.timedelta(0)),
            ('+05:30', datetime.timedelta(0, 19800)),
            ('-08:00', datetime.timedelta(-1, 57600)),
        ],
    )
    def test__offset(self, string, result):
        assert TzOffset(string).utcoffset() == result

    @mark.parametrize(
        'string',
        [
            '+00:00',
            '+05:30',
            '-08:00',
        ],
    )
    def test___repr__(self, string):
        assert repr(TzOffset(string)) == f"TzOffset('{string}')"

    def test___repr___normalise(self):
        assert repr(TzOffset('-00:00')) == "TzOffset('+00:00')"


class TestTimestamp:
    @mark.parametrize(
        'string, result',
        [
            ('2008-02-06T13:33:26+0000', TzOffset('+00:00')),
            ('2008-02-06T13:33:26+00:00', TzOffset('+00:00')),
            ('2008-02-06T13:33:26+05:30', TzOffset('+05:30')),
            ('2008-02-06T13:33:26-08:00', TzOffset('-08:00')),
            ('2008-02-06T13:33:26z', TzOffset('+00:00')),
        ],
    )
    def test_parse_isoformat(self, string, result):
        assert Timestamp.parse_isoformat(string) == Timestamp(
            2008, 2, 6, 13, 33, 26, tzinfo=result
        )


@mark.parametrize(
    'string, result',
    [
        ('+00-025/', (0.0, -25.0, None)),  # Atlantic Ocean
        ('+46+002/', (46.0, 2.0, None)),  # France
        (
            '+4852+00220/',
            (48.86666666666667, 2.3333333333333335, None),
        ),  # Paris
        ('+48.8577+002.295/', (48.8577, 2.295, None)),  # Eiffel Tower
        (
            '+27.5916+086.5640+8850/',
            (27.5916, 86.564, 8850.0),
        ),  # Mount Everest
        ('+90+000/', (90.0, 0.0, None)),  # North Pole
        ('+00-160/', (0.0, -160.0, None)),  # Pacific Ocean
        ('-90+000+2800/', (-90.0, 0.0, 2800.0)),  # South Pole
        ('+38-097/', (38.0, -97.0, None)),  # United States
        ('+40.75-074.00/', (40.75, -74.0, None)),  # New York City
        ('+40.6894-074.0447/', (40.6894, -74.0447, None)),  # Statue of Liberty
    ],
)
def test_from_iso6709_wiki_page(string, result):
    # These tests are from the examples contained in the wikipedia ISO 6709
    # page(http://en.wikipedia.org/wiki/ISO_6709)
    assert from_iso6709(string) == result


@mark.parametrize(
    'string, result',
    [
        ('-90+000+2800/', (-90.0, 0.0, 2800.0)),  # South Pole
        (
            '+352139+1384339+3776/',
            (35.36083333333333, 138.7275, 3776.0),
        ),  # Mount Fuji
        (
            '+35.658632+139.745411/',
            (35.658632, 139.745411, None),
        ),  # Tokyo Tower
    ],
)
def test_from_iso6709_location_page(string, result):
    # These tests are from the Latitude, Longitude and Altitude format for
    # geospatial information page
    # (http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude)
    assert from_iso6709(string) == result


def test_from_iso6709_error():
    with raises(ValueError, match=r"Incorrect format for longitude '\+1'"):
        from_iso6709('+35.658632+1/')


@mark.parametrize(
    'data, result',
    [
        ((0.0, -25.0, None, 'd'), '+00-025/'),  # Atlantic Ocean
        ((46.0, 2.0, None, 'd'), '+46+002/'),  # France
        (
            (48.866666666666667, 2.3333333333333335, None, 'dm'),
            '+4852+00220/',
        ),  # Paris
        (
            (27.5916, 86.563999999999993, 8850.0),
            '+27.5916+086.5640+8850/',
        ),  # Mount Everest
        ((90.0, 0.0, None, 'd'), '+90+000/'),  # North Pole
        ((0.0, -160.0, None, 'd'), '+00-160/'),  # Pacific Ocean
        ((-90.0, 0.0, 2800.0, 'd'), '-90+000+2800/'),  # South Pole
        ((38.0, -97.0, None, 'd'), '+38-097/'),  # United States
        (
            (40.689399999999999, -74.044700000000006, None),
            '+40.6894-074.0447/',
        ),  # Statue of Liberty
    ],
)
def test_to_iso6709_wiki_page(data, result):
    # These tests are from the examples contained in the wikipedia ISO 6709
    # page(http://en.wikipedia.org/wiki/ISO_6709)
    assert to_iso6709(*data) == result


@mark.parametrize(
    'args, kwargs, result',
    [
        (
            (27.5916, 86.563999999999993, 8850.0),
            {},
            '+27.5916+086.5640+8850/',
        ),  # Mount Everest
        ((-90.0, 0.0, 2800.0, 'd'), {}, '-90+000+2800/'),  # South Pole
        (
            (40.75, -74.0, None),
            {'precision': 2},
            '+40.75-074.00/',
        ),  # New York City
        (
            (35.360833333333332, 138.72749999999999, 3776.0, 'dms'),
            {},
            '+352139+1384339+3776/',
        ),  # Mount Fuji
        (
            (35.658631999999997, 139.74541099999999, None),
            {'precision': 6},
            '+35.658632+139.745411/',
        ),  # Tokyo Tower
    ],
)
def test_to_iso6709_location_page(args, kwargs, result):
    # These tests are from the Latitude, Longitude and Altitude format for
    # geospatial information page
    # (http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude)

    assert to_iso6709(*args, **kwargs) == result


def test_angle_to_distance():
    assert angle_to_distance(1) == approx(111.125, rel=0.001)
    assert angle_to_distance(360, 'imperial') == approx(24863, rel=0.001)
    assert angle_to_distance(1.0 / 60, 'nautical') == approx(1, rel=0.001)

    with raises(ValueError, match="Unknown units type 'baseless'"):
        angle_to_distance(10, 'baseless')


def test_distance_to_angle():
    assert round(distance_to_angle(111.212)) == 1
    assert round(distance_to_angle(24882, 'imperial')) == 360
    assert round(distance_to_angle(60, 'nautical')) == 1


@mark.parametrize(
    'locator, result',
    [
        ('BL11bh16', '21.319, -157.904'),
        ('IO92va', '52.021, -0.208'),
        ('IO92', '52.021, -1.958'),
    ],
)
def test_from_grid_locator(locator, result):
    assert '%.3f, %.3f' % from_grid_locator(locator) == result


@mark.parametrize(
    'data, result',
    [
        ((21.319, -157.904, 'extsquare'), 'BL11bh16'),
        ((52.021, -0.208, 'subsquare'), 'IO92va'),
        ((52.021, -1.958), 'IO92'),
    ],
)
def test_to_grid_locator(data, result):
    assert to_grid_locator(*data) == result


@mark.parametrize(
    'location, result',
    [
        ('52.015;-0.221', '52.015;-0.221'),
        ('52.015,-0.221', '52.015;-0.221'),
        ('52.015 -0.221', '52.015;-0.221'),
        ('52.015N 0.221W', '52.015;-0.221'),
        ('52.015 N 0.221 W', '52.015;-0.221'),
        ('52d00m54s N 0d13m15s W', '52.015;-0.221'),
        ('52d0m54s N 000d13m15s W', '52.015;-0.221'),
        ('''52d0'54" N 000d13'15" W''', '52.015;-0.221'),
        ('52d0′54″ N 000d13′15″ W', '52.015;-0.221'),
    ],
)
def test_parse_location(location, result):
    assert '%.3f;%.3f' % parse_location(location) == result


@mark.parametrize(
    'date, result',
    [
        (datetime.date(2007, 6, 15), datetime.time(3, 40)),
        (datetime.date(1993, 12, 11), datetime.time(7, 58)),
        (datetime.date(2007, 2, 21), datetime.time(7, 4)),
        (datetime.date(2007, 1, 21), datetime.time(7, 56)),
    ],
)
def test_sun_rise(date, result):
    assert sun_rise_set(52.015, -0.221, date) == result


def test_sun_no_rise():
    assert sun_rise_set(89, 0, datetime.date(2007, 12, 21)) is None


def test_sun_rise_zone():
    assert sun_rise_set(
        52.015, -0.221, datetime.date(2007, 6, 15), timezone=60
    ) == datetime.time(4, 40)


@mark.parametrize(
    'date, result',
    [
        (datetime.date(2007, 6, 15), datetime.time(20, 22)),
        (datetime.date(1993, 12, 11), datetime.time(15, 49)),
    ],
)
def test_sun_set(date, result):
    assert sun_rise_set(52.015, -0.221, date, 'set') == result


def test_sun_set_zone():
    assert sun_rise_set(
        52.015, -0.221, datetime.date(2007, 6, 15), 'set', 60
    ) == datetime.time(21, 22)


@mark.parametrize(
    'date, result',
    [
        (
            datetime.date(2007, 6, 15),
            (datetime.time(3, 40), datetime.time(20, 22)),
        ),
        (
            datetime.date(1993, 12, 11),
            (datetime.time(7, 58), datetime.time(15, 49)),
        ),
        (
            datetime.date(2007, 6, 15),
            (datetime.time(3, 40), datetime.time(20, 22)),
        ),
    ],
)
def test_sun_events(date, result):
    assert sun_events(52.015, -0.221, date) == result


def test_sun_events_zone():
    assert sun_events(52.015, -0.221, datetime.date(2007, 6, 15), 60) == (
        datetime.time(4, 40),
        datetime.time(21, 22),
    )


@mark.parametrize(
    'date, result',
    [
        (
            datetime.date(2007, 6, 15),
            (datetime.time(9, 23), datetime.time(0, 27)),
        ),
        (
            datetime.date(2007, 6, 15),
            (datetime.time(9, 23), datetime.time(0, 27)),
        ),
    ],
)
def test_sun_events2(date, result):
    assert sun_events(40.638611, -73.762222, date) == result


def test_sun_events3():
    assert sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15)) == (
        datetime.time(19, 24),
        datetime.time(9, 57),
    )


@mark.parametrize(
    'zenith, results',
    [
        (
            'civil',
            [
                (datetime.time(2, 51), datetime.time(21, 11)),
                (datetime.time(8, 50), datetime.time(1, 0)),
                (datetime.time(3, 22), datetime.time(20, 58)),
                (datetime.time(18, 54), datetime.time(10, 27)),
            ],
        ),
        (
            'nautical',
            [
                (datetime.time(1, 32), datetime.time(22, 30)),
                (datetime.time(8, 7), datetime.time(1, 44)),
                (datetime.time(2, 20), datetime.time(22, 0)),
                (datetime.time(18, 17), datetime.time(11, 5)),
            ],
        ),
        (
            'astronomical',
            [
                (None, None),
                (datetime.time(7, 14), datetime.time(2, 36)),
                (None, None),
                (datetime.time(17, 34), datetime.time(11, 48)),
            ],
        ),
    ],
)
def test_sun_events_zenith(zenith, results):
    assert (
        sun_events(52.015, -0.221, datetime.date(2007, 6, 15), zenith=zenith)
        == results[0]
    )
    assert (
        sun_events(
            40.638611, -73.762222, datetime.date(2007, 6, 15), zenith=zenith
        )
        == results[1]
    )
    assert (
        sun_events(
            49.016666, -2.5333333, datetime.date(2007, 6, 15), zenith=zenith
        )
        == results[2]
    )
    assert (
        sun_events(
            35.549999, 139.78333333, datetime.date(2007, 6, 15), zenith=zenith
        )
        == results[3]
    )


def test_dump_xearth_markers():
    markers = {
        500936: Trigpoint(52.066035, -0.281449, 37.000000, 'Broom Farm'),
        501097: Trigpoint(52.010585, -0.173443, 97.000000, 'Bygrave'),
        505392: Trigpoint(51.910886, -0.186462, 136.000000, 'Sish Lane'),
    }
    assert dump_xearth_markers(markers) == [
        '52.066035 -0.281449 "500936" # Broom Farm, alt 37m',
        '52.010585 -0.173443 "501097" # Bygrave, alt 97m',
        '51.910886 -0.186462 "505392" # Sish Lane, alt 136m',
    ]

    assert dump_xearth_markers(markers, 'name') == [
        '52.066035 -0.281449 "Broom Farm" # 500936, alt 37m',
        '52.010585 -0.173443 "Bygrave" # 501097, alt 97m',
        '51.910886 -0.186462 "Sish Lane" # 505392, alt 136m',
    ]

    with raises(ValueError, match="Unknown name type 'falseKey'"):
        dump_xearth_markers(markers, 'falseKey')


def test_dump_xearth_markers2():
    points = {
        'Broom Farm': Point(52.066035, -0.281449),
        'Bygrave': Point(52.010585, -0.173443),
        'Sish Lane': Point(51.910886, -0.186462),
    }
    assert dump_xearth_markers(points) == [
        '52.066035 -0.281449 "Broom Farm"',
        '52.010585 -0.173443 "Bygrave"',
        '51.910886 -0.186462 "Sish Lane"',
    ]


@mark.parametrize(
    'args, result',
    [
        ((52.015,), 6375.166025311857),
        ((0,), 6335.438700909687),
        ((90,), 6399.593942121543),
        ((52.015, 'FAI sphere'), 6371.0),
        ((0, 'Airy (1830)'), 6335.022178542022),
        ((90, 'International'), 6399.936553871439),
    ],
)
def test_calc_radius(args, result):
    assert calc_radius(*args) == result
