#
# coding=utf-8
"""test_utils - Test utility functions"""
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

import datetime

from upoints.utils import (FileFormatError, Timestamp, TzOffset,
                           angle_to_distance, angle_to_name, calc_radius,
                           distance_to_angle, dump_xearth_markers,
                           from_grid_locator, from_iso6709, parse_location,
                           prepare_csv_read, prepare_read, prepare_xml_read,
                           sun_rise_set, to_dd, to_dms, to_grid_locator,
                           to_iso6709, value_or_empty)


class TestFileFormatError():
    """
    >>> raise FileFormatError
    Traceback (most recent call last):
        ...
    FileFormatError: Unsupported data format.
    >>> from dtopt import NORMALIZE_WHITESPACE
    >>> raise FileFormatError("test site")
    Traceback (most recent call last):
        ...
    FileFormatError: Incorrect data format, if you're using a file downloaded
    from test site please report this to James Rowe <jnrowe@gmail.com>

    """

def test_value_or_empty():
    """
    >>> value_or_empty(None)
    ''
    >>> value_or_empty("test")
    'test'

    """


def test_prepare_read():
    """
    >>> prepare_read(open("test/data/real_file"))
    ['This is a test file-type object\\n']
    >>> test_list = ['This is a test list-type object', 'with two elements']
    >>> prepare_read(test_list)
    ['This is a test list-type object', 'with two elements']
    >>> prepare_read(open("test/data/real_file"), "read")
    'This is a test file-type object\\n'

    """


def test_prepare_csv_read():
    """
    >>> list(prepare_csv_read(open("test/data/real_file.csv"),
    ...                       ("type", "bool", "string")))
    [{'bool': 'true', 'type': 'file', 'string': 'test'}]
    >>> test_list = ['James,Rowe', 'ell,caro']
    >>> list(prepare_csv_read(test_list, ("first", "last")))
    [{'last': 'Rowe', 'first': 'James'}, {'last': 'caro', 'first': 'ell'}]

    """


def test_prepare_xml_read():
    """
    >>> prepare_xml_read(open("test/data/real_file.xml")).find("tag").text
    'This is a test file-type object'
    >>> test_list = ['<xml>', '<tag>This is a test list</tag>', '</xml>']
    >>> prepare_xml_read(test_list).find("tag").text
    'This is a test list'

    """


def test_to_dms():
    """
    >>> to_dms(52.015)
    (52, 0, 54.0)
    >>> to_dms(-0.221)
    (0, -13, -15.600000000000023)
    >>> to_dms(-0.221, style="dm")
    (0, -13.26)
    >>> to_dms(-0.221, style=None)
    Traceback (most recent call last):
        ...
    ValueError: Unknown style type `None'

    """


def test_to_dd():
    """
    >>> "%.3f" % to_dd(52, 0, 54)
    '52.015'
    >>> "%.3f" % to_dd(0, -13, -15)
    '-0.221'
    >>> "%.3f" % to_dd(0, -13.25)
    '-0.221'

    """


def test_angle_to_name():
    """
    >>> angle_to_name(0)
    'North'
    >>> angle_to_name(360)
    'North'
    >>> angle_to_name(45)
    'North-east'
    >>> angle_to_name(292)
    'West'
    >>> angle_to_name(293)
    'North-west'
    >>> angle_to_name(0, 4)
    'North'
    >>> angle_to_name(360, 16)
    'North'
    >>> angle_to_name(45, 4, True)
    'NE'
    >>> angle_to_name(292, 16, True)
    'WNW'

    """


class TestTzOffset():
    def test___init__(self):
        """
        >>> TzOffset("+00:00").utcoffset()
        datetime.timedelta(0)
        >>> TzOffset("-00:00").utcoffset()
        datetime.timedelta(0)
        >>> TzOffset("+05:30").utcoffset()
        datetime.timedelta(0, 19800)
        >>> TzOffset("-08:00").utcoffset()
        datetime.timedelta(-1, 57600)

        """

    def test___repr__(self):
        """
        >>> TzOffset("+00:00")
        TzOffset('+00:00')
        >>> TzOffset("-00:00")
        TzOffset('+00:00')
        >>> TzOffset("+05:30")
        TzOffset('+05:30')
        >>> TzOffset("-08:00")
        TzOffset('-08:00')

        """


class TestTimestamp():
    def parse_isoformat(self):
        """
        >>> Timestamp.parse_isoformat("2008-02-06T13:33:26+0000")
        Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))
        >>> Timestamp.parse_isoformat("2008-02-06T13:33:26+00:00")
        Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))
        >>> Timestamp.parse_isoformat("2008-02-06T13:33:26+05:30")
        Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+05:30'))
        >>> Timestamp.parse_isoformat("2008-02-06T13:33:26-08:00")
        Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('-08:00'))
        >>> Timestamp.parse_isoformat("2008-02-06T13:33:26z")
        Timestamp(2008, 2, 6, 13, 33, 26, tzinfo=TzOffset('+00:00'))

        """


def test_from_iso6709():
    """
    The following tests are from the examples contained in the `wikipedia
    ISO 6709 page`_:

    >>> from_iso6709("+00-025/") # Atlantic Ocean
    (0.0, -25.0, None)
    >>> from_iso6709("+46+002/") # France
    (46.0, 2.0, None)
    >>> from_iso6709("+4852+00220/") # Paris
    (48.86666666666667, 2.3333333333333335, None)
    >>> from_iso6709("+48.8577+002.295/") # Eiffel Tower
    (48.8577, 2.295, None)
    >>> from_iso6709("+27.5916+086.5640+8850/") # Mount Everest
    (27.5916, 86.564, 8850.0)
    >>> from_iso6709("+90+000/") # North Pole
    (90.0, 0.0, None)
    >>> from_iso6709("+00-160/") # Pacific Ocean
    (0.0, -160.0, None)
    >>> from_iso6709("-90+000+2800/") # South Pole
    (-90.0, 0.0, 2800.0)
    >>> from_iso6709("+38-097/") # United States
    (38.0, -97.0, None)
    >>> from_iso6709("+40.75-074.00/") # New York City
    (40.75, -74.0, None)
    >>> from_iso6709("+40.6894-074.0447/") # Statue of Liberty
    (40.6894, -74.0447, None)

    The following tests are from the `Latitude, Longitude and Altitude format
    for geospatial information`_ page:

    >>> from_iso6709("+27.5916+086.5640+8850/") # Mount Everest
    (27.5916, 86.564, 8850.0)
    >>> from_iso6709("-90+000+2800/") # South Pole
    (-90.0, 0.0, 2800.0)
    >>> from_iso6709("+40.75-074.00/") # New York City
    (40.75, -74.0, None)
    >>> from_iso6709("+352139+1384339+3776/") # Mount Fuji
    (35.36083333333333, 138.7275, 3776.0)
    >>> from_iso6709("+35.658632+139.745411/") # Tokyo Tower
    (35.658632, 139.745411, None)
    >>> from_iso6709("+35.658632+1/") # Broken
    Traceback (most recent call last):
        ...
    ValueError: Incorrect format for longitude `+1'

    .. _wikipedia ISO 6709 page: http://en.wikipedia.org/wiki/ISO_6709
    .. _Latitude, Longitude and Altitude format for geospatial information: http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude

    """


def test_to_iso6709():
    """
    The following tests are from the examples contained in the `wikipedia
    ISO 6709 page`_:

    >>> to_iso6709(0.0, -25.0, None, "d")  # Atlantic Ocean
    '+00-025/'
    >>> to_iso6709(46.0, 2.0, None, "d")  # France
    '+46+002/'
    >>> to_iso6709(48.866666666666667, 2.3333333333333335, None, "dm")  # Paris
    '+4852+00220/'
    >>> # The following test is skipped, because the example from wikipedia
    >>> # uses differing precision widths for latitude and longitude. Also,
    >>> # that degree of formatting flexibility is not seen anywhere else and
    >>> # adds very little.
    >>> to_iso6709(48.857700000000001, 2.2949999999999999, None)  # Eiffel Tower # doctest: +SKIP
    '+48.8577+002.295/'
    >>> to_iso6709(27.5916, 86.563999999999993, 8850.0)  # Mount Everest
    '+27.5916+086.5640+8850/'
    >>> to_iso6709(90.0, 0.0, None, "d")  # North Pole
    '+90+000/'
    >>> to_iso6709(0.0, -160.0, None, "d")  # Pacific Ocean
    '+00-160/'
    >>> to_iso6709(-90.0, 0.0, 2800.0, "d")  # South Pole
    '-90+000+2800/'
    >>> to_iso6709(38.0, -97.0, None, "d")  # United States
    '+38-097/'
    >>> to_iso6709(40.75, -74.0, None, precision=2)  # New York City
    '+40.75-074.00/'
    >>> to_iso6709(40.689399999999999, -74.044700000000006, None)  # Statue of Liberty
    '+40.6894-074.0447/'

    The following tests are from the `Latitude, Longitude and Altitude format
    for geospatial information`_ page:

    >>> to_iso6709(27.5916, 86.563999999999993, 8850.0) # Mount Everest
    '+27.5916+086.5640+8850/'
    >>> to_iso6709(-90.0, 0.0, 2800.0, "d") # South Pole
    '-90+000+2800/'
    >>> to_iso6709(40.75, -74.0, None, precision=2) # New York City
    '+40.75-074.00/'
    >>> to_iso6709(35.360833333333332, 138.72749999999999, 3776.0, "dms")  # Mount Fuji
    '+352139+1384339+3776/'
    >>> to_iso6709(35.658631999999997, 139.74541099999999, None, precision=6)  # Tokyo Tower
    '+35.658632+139.745411/'

    .. _wikipedia ISO 6709 page: http://en.wikipedia.org/wiki/ISO_6709
    .. _Latitude, Longitude and Altitude format for geospatial information: http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude

    """


def test_angle_to_distance():
    """
    >>> "%.3f" % angle_to_distance(1)
    '111.125'
    >>> "%i" % angle_to_distance(360, "imperial")
    '24863'
    >>> "%i" % angle_to_distance(1.0/60, "nautical")
    '1'
    >>> "%i" % angle_to_distance(10, "baseless")
    Traceback (most recent call last):
        ...
    ValueError: Unknown units type `baseless'

    """


def test_distance_to_angle():
    """

    >>> "%.3f" % round(distance_to_angle(111.212))
    '1.000'
    >>> "%i" % round(distance_to_angle(24882, "imperial"))
    '360'
    >>> "%i" % round(distance_to_angle(60, "nautical"))
    '1'

    """


def test_from_grid_locator():
    """
    >>> "%.3f, %.3f" % from_grid_locator("BL11bh16")
    '21.319, -157.904'
    >>> "%.3f, %.3f" % from_grid_locator("IO92va")
    '52.021, -0.208'
    >>> "%.3f, %.3f" % from_grid_locator("IO92")
    '52.021, -1.958'

    """


def test_to_grid_locator():
    """
    >>> to_grid_locator(21.319, -157.904, "extsquare")
    'BL11bh16'
    >>> to_grid_locator(52.021, -0.208, "subsquare")
    'IO92va'
    >>> to_grid_locator(52.021, -1.958)
    'IO92'

    """


def test_parse_location():
    """
    >>> "%.3f;%.3f" % parse_location("52.015;-0.221")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52.015,-0.221")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52.015 -0.221")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52.015N 0.221W")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52.015 N 0.221 W")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52d00m54s N 0d13m15s W")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location("52d0m54s N 000d13m15s W")
    '52.015;-0.221'
    >>> "%.3f;%.3f" % parse_location('''52d0'54" N 000d13'15" W''')
    '52.015;-0.221'

    """

def test_sun_rise_set():
    """
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15))
    datetime.time(3, 40)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), "set")
    datetime.time(20, 22)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), timezone=60)
    datetime.time(4, 40)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), "set", 60)
    datetime.time(21, 22)
    >>> sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11))
    datetime.time(7, 58)
    >>> sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11), "set")
    datetime.time(15, 49)
    >>> sun_rise_set(89, 0, datetime.date(2007, 12, 21))
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 2, 21))
    datetime.time(7, 4)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 1, 21))
    datetime.time(7, 56)

        ``None`` if the event doesn't occur on the given date
    :raise ValueError: Unknown value for ``mode``

    """


def sun_events(latitude, longitude, date, timezone=0, zenith=None):
    """

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15))
    (datetime.time(3, 40), datetime.time(20, 22))
    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15), 60)
    (datetime.time(4, 40), datetime.time(21, 22))
    >>> sun_events(52.015, -0.221, datetime.date(1993, 12, 11))
    (datetime.time(7, 58), datetime.time(15, 49))
    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15))
    (datetime.time(3, 40), datetime.time(20, 22))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15))  # JFK
    (datetime.time(9, 23), datetime.time(0, 27))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15))  # CDG
    (datetime.time(4, 5), datetime.time(20, 15))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15))  # TIA
    (datetime.time(19, 24), datetime.time(9, 57))

    Civil twilight starts/ends when the Sun's centre is 6 degrees below
    the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15), zenith="civil")
    (datetime.time(2, 51), datetime.time(21, 11))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="civil") # JFK
    (datetime.time(8, 50), datetime.time(1, 0))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="civil") # CDG
    (datetime.time(3, 22), datetime.time(20, 58))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="civil") # TIA
    (datetime.time(18, 54), datetime.time(10, 27))

    Nautical twilight starts/ends when the Sun's centre is 12 degrees
    below the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
    ...            zenith="nautical")
    (datetime.time(1, 32), datetime.time(22, 30))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # JFK
    (datetime.time(8, 7), datetime.time(1, 44))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # CDG
    (datetime.time(2, 20), datetime.time(22, 0))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # TIA
    (datetime.time(18, 17), datetime.time(11, 5))

    Astronomical twilight starts/ends when the Sun's centre is 18 degrees below
    the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
    ...            zenith="astronomical")
    (None, None)
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # JFK
    (datetime.time(7, 14), datetime.time(2, 36))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # CDG
    (None, None)
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # TIA
    (datetime.time(17, 34), datetime.time(11, 48))

    """

def test_dump_xearth_markers():
    """
    >>> from upoints.trigpoints import Trigpoint
    >>> markers = {
    ...     500936: Trigpoint(52.066035, -0.281449, 37.000000, "Broom Farm"),
    ...     501097: Trigpoint(52.010585, -0.173443, 97.000000, "Bygrave"),
    ...     505392: Trigpoint(51.910886, -0.186462, 136.000000, "Sish Lane")
    ... }
    >>> print("\\n".join(dump_xearth_markers(markers)))
    52.066035 -0.281449 "500936" # Broom Farm, alt 37m
    52.010585 -0.173443 "501097" # Bygrave, alt 97m
    51.910886 -0.186462 "505392" # Sish Lane, alt 136m
    >>> print("\\n".join(dump_xearth_markers(markers, "name")))
    52.066035 -0.281449 "Broom Farm" # 500936, alt 37m
    52.010585 -0.173443 "Bygrave" # 501097, alt 97m
    51.910886 -0.186462 "Sish Lane" # 505392, alt 136m
    >>> print("\\n".join(dump_xearth_markers(markers, "falseKey")))
    Traceback (most recent call last):
        ...
    ValueError: Unknown name type `falseKey'

    >>> from upoints.point import Point
    >>> points = {
    ...     "Broom Farm": Point(52.066035, -0.281449),
    ...     "Bygrave": Point(52.010585, -0.173443),
    ...     "Sish Lane": Point(51.910886, -0.186462)
    ... }
    >>> print("\\n".join(dump_xearth_markers(points)))
    52.066035 -0.281449 "Broom Farm"
    52.010585 -0.173443 "Bygrave"
    51.910886 -0.186462 "Sish Lane"

    """


def test_calc_radius():
    """
    >>> calc_radius(52.015)
    6375.166025311857
    >>> calc_radius(0)
    6335.438700909687
    >>> calc_radius(90)
    6399.593942121543
    >>> calc_radius(52.015, "FAI sphere")
    6371.0
    >>> calc_radius(0, "Airy (1830)")
    6335.022178542022
    >>> calc_radius(90, "International")
    6399.936553871439

    """
