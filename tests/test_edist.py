#
# coding=utf-8
"""test_edist - Test edist interface"""
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

import sys

from edist import (LocationsError, NumberedPoint, NumberedPoints,
                   process_command_line, read_csv)


class TestLocationsError():
    """
    >>> raise LocationsError
    Traceback (most recent call last):
        ...
    LocationsError: Invalid location data.
    >>> raise LocationsError("distance")
    Traceback (most recent call last):
        ...
    LocationsError: More than one location is required for distance.
    >>> raise LocationsError(data=(4, "52;None"))
    Traceback (most recent call last):
        ...
    LocationsError: Location parsing failure in location 4 `52;None'.

    """


class TestNumberedPoint():
    def Test___init__(self):
        """
        >>> NumberedPoint(52.015, -0.221, 4)
        NumberedPoint(52.015, -0.221, 4, 'metric')
        >>> NumberedPoint(52.015, -0.221, "Home")
        NumberedPoint(52.015, -0.221, 'Home', 'metric')

        """


class TestNumberedPoints():
    def test___repr__(self):
        """
        >>> locations = ["0;0"] * 4
        >>> NumberedPoints(locations)
        NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(0.0, 0.0, 2, 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric'), NumberedPoint(0.0, 0.0, 4, 'metric')], 'dd', True, True, None, 'km')

        """

    def test_import_locations(self):
        """
        >>> NumberedPoints(["0;0", "Home", "0;0"],
        ...                config_locations={"Home": (52.015, -0.221)})
        NumberedPoints([NumberedPoint(0.0, 0.0, 1, 'metric'), NumberedPoint(52.015, -0.221, 'Home', 'metric'), NumberedPoint(0.0, 0.0, 3, 'metric')], 'dd', True, True, {'Home': (52.015, -0.221)}, 'km')

        """

    def test_display(self):
        """
        >>> locs = NumberedPoints(["Home", "52.168;0.040"],
        ...                       config_locations={"Home": (52.015, -0.221)})
        >>> locs.display(None)
        Location Home is N52.015°; W000.221°
        Location 2 is N52.168°; E000.040°
        >>> locs.format = "locator"
        >>> locs.display("extsquare")
        Location Home is IO92va33
        Location 2 is JO02ae40
        >>> locs.verbose = False
        >>> locs.display("extsquare")
        IO92va33
        JO02ae40

        """

    def test_distance(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.distance()
        Location 1 to 2 is 24 kilometres
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"],
        ...                            units="sm")
        >>> locations.distance()
        Location 1 to 2 is 15 miles
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"],
        ...                            units="nm")
        >>> locations.verbose = False
        >>> locations.distance()
        13.2989574317
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040",
        ...                             "51.420;-1.500"])
        >>> locations.distance()
        Location 1 to 2 is 24 kilometres
        Location 2 to 3 is 134 kilometres
        Total distance is 159 kilometres

        """

    def test_bearing(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.bearing("bearing", False)
        Location 1 to 2 is 46°
        >>> locations.bearing("bearing", True)
        Location 1 to 2 is North-east
        >>> locations.bearing("final_bearing", False)
        Final bearing from location 1 to 2 is 46°
        >>> locations.bearing("final_bearing", True)
        Final bearing from location 1 to 2 is North-east
        >>> locations.verbose = False
        >>> locations.bearing("bearing", True)
        North-east
        >>> locations.verbose = False
        >>> locations.bearing("final_bearing", True)
        North-east

        """

    def test_range(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.range(20)
        Location 2 is not within 20 kilometres of location 1
        >>> locations.range(30)
        Location 2 is within 30 kilometres of location 1
        >>> locations.verbose = False
        >>> locations.range(30)
        True

        """

    def test_destination(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.destination((42, 240), False)
        Destination from location 1 is N51.825°; W000.751°
        Destination from location 2 is N51.978°; W000.491°
        >>> locations.format = "locator"
        >>> locations.destination((42, 240), "subsquare")
        Destination from location 1 is IO91ot
        Destination from location 2 is IO91sx
        >>> locations.verbose = False
        >>> locations.destination((42, 240), "extsquare")
        IO91ot97
        IO91sx14

        """

    def test_sun_events(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> from dtopt import ELLIPSIS
        >>> locations.sun_events("sunrise")
        Sunrise at ... in location 1
        Sunrise at ... in location 2
        >>> locations.sun_events("sunset")
        Sunset at ... in location 1
        Sunset at ... in location 2

        """

    def test_flight_plan(self):
        """
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040",
        ...                             "52.249;0.130", "52.494;0.654"])
        >>> locations.flight_plan(0, "h")
        WAYPOINT,BEARING[°],DISTANCE[km],ELAPSED_TIME[h],LATITUDE[d.dd],LONGITUDE[d.dd]
        1,,,,52.015000,-0.221000
        2,46,24.6,,52.168000,0.040000
        3,34,10.9,,52.249000,0.130000
        4,52,44.8,,52.494000,0.654000
        -- OVERALL --#,,80.3,,,
        -- DIRECT --#,47,79.9,,,
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040",
        ...                             "52.249;0.130", "52.494;0.654"],
        ...                            units="nm")
        >>> locations.flight_plan(20, "m")
        WAYPOINT,BEARING[°],DISTANCE[nm],ELAPSED_TIME[m],LATITUDE[d.dd],LONGITUDE[d.dd]
        1,,,,52.015000,-0.221000
        2,46,13.3,0.7,52.168000,0.040000
        3,34,5.9,0.3,52.249000,0.130000
        4,52,24.2,1.2,52.494000,0.654000
        -- OVERALL --,,43.4,2.2,,
        -- DIRECT --,47,43.1,2.2,,

        """


def test_process_command_line():
    """
    >>> saved_args = sys.argv[1:]
    >>> sys.argv[1:] = ["-p", "52.015;-0.221"]
    >>> modes, opts, args = process_command_line()
    >>> modes, args
    (['display'], ['52.015;-0.221'])
    >>> sys.argv[1:] = ["-d", "-b", "52.015;-0.221", "52.168;0.040"]
    >>> modes, opts, args = process_command_line()
    >>> modes, args
    (['distance', 'bearing'], ['52.015;-0.221', '52.168;0.040'])
    >>> sys.argv[1:] = saved_args

    """


def test_read_csv():
    """
    >>> locations, names = read_csv(open("test/data/gpsbabel"))
    >>> sorted(locations.items())
    [('01:My place', ('52.01500', '-0.22100')),
     ('02:Microsoft Research Cambridge', ('52.16700', '00.39000'))]
    >>> names
    ['01:My place', '02:Microsoft Research Cambridge']

    """


def main():
    """
    >>> saved_args = sys.argv[1:]
    >>> sys.argv[1:] = ["-p", "52.015;-0.221"]
    >>> main()
    Location 1 is 52°00′54″N, 000°13′15″W
    >>> sys.argv[1:] = ["-s", "22@40", "52.015;-0.221"]
    >>> main()
    Destination from location 1 is 52°09′59″N, 000°00′48″W
    >>> sys.argv[1:] = saved_args

    """
