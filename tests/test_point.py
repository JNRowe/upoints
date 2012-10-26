#
# coding=utf-8
"""test_point - Test point support"""
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

from upoints import utils
from upoints.point import (KeyedPoints, Point, Points, TimedPoint, TimedPoints)


class TestPoint():
    def __init__(self):
        """
        >>> import math
        >>> Home = Point(52.015, -0.221)
        >>> Home = Point(52.015, -0.221, timezone=60) # BST
        >>> Home = Point(52.015, -0.221, "US customary")
        >>> Home = Point(52.015, -0.221, "nautical")
        >>> test = Point(math.pi / 4, math.pi / 2, angle="radians")
        >>> test.latitude == 45
        True
        >>> test.longitude == 90
        True
        >>> test = Point((50, 20, 10), (-1, -3, -12))
        >>> "%.3f" % test.latitude
        '50.336'
        >>> "%.3f" % test.longitude
        '-1.053'
        >>> bad_angle = Point(52.015, -0.221, angle=None)
        Traceback (most recent call last):
        ...
        ValueError: Unknown angle type `None'
        >>> bad_latitude = Point(-92, -0.221)
        Traceback (most recent call last):
        ...
        ValueError: Invalid latitude value `-92.000000'
        >>> bad_longitude = Point(52.015, 185)
        Traceback (most recent call last):
        ...
        ValueError: Invalid longitude value `185.000000'
        >>> bad_units = Point(52.015, -0.221, units=None)
        Traceback (most recent call last):
        ...
        ValueError: Unknown units type `None'

        """

    def test___dict__(self):
        """
        >>> Home = Point(52.015, -0.221)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> sorted(Home.__dict__.items())
        [('_angle', 'degrees'), ('_latitude', 52.015),
         ('_longitude', -0.221), ('_rad_latitude', 0.9078330104248505),
         ('_rad_longitude', -0.0038571776469074684), ('timezone', 0),
         ('units', 'metric')]
        >>> class Test(Point):
        ...     __slots__ = ("TEST", )
        ...     def test___init__(self):
        ...         super(Test, self).__init__(latitude, longitude)
        ...         self.TEST = "tested"
        >>> a = Test(52.015, -0.221)
        >>> sorted(a.__dict__.items())
        [('TEST', 'tested'), ('_angle', 'degrees'),
         ('_latitude', 52.015), ('_longitude', -0.221),
         ('_rad_latitude', 0.9078330104248505),
         ('_rad_longitude', -0.0038571776469074684), ('timezone', 0),
         ('units', 'metric')]

        """

    def test___repr__(self):
        """
        >>> Point(52.015, -0.221)
        Point(52.015, -0.221, 'metric', 'degrees', 0)

        """

    def test___str__(self):
        """
        >>> print(Point(52.015, -0.221))
        N52.015°; W000.221°
        >>> print(Point(52.015, -0.221).__str__(mode="dm"))
        52°00.90'N, 000°13.26'W
        >>> print(Point(52.015, -0.221).__str__(mode="dms"))
        52°00'54"N, 000°13'15"W
        >>> print(Point(33.9400, -118.4000).__str__(mode="dms"))
        33°56'23"N, 118°24'00"W
        >>> print(Point(52.015, -0.221).__str__(mode="locator"))
        IO92

        """

    def test___unicode__(self):
        """
        >>> print(Point(52.015, -0.221))
        N52.015°; W000.221°
        >>> print(Point(52.015, -0.221).__unicode__(mode="dm"))
        52°00.90′N, 000°13.26′W
        >>> print(Point(52.015, -0.221).__unicode__(mode="dms"))
        52°00′54″N, 000°13′15″W
        >>> print(Point(33.9400, -118.4000).__unicode__(mode="dms"))
        33°56′23″N, 118°24′00″W
        >>> print(Point(52.015, -0.221).__unicode__(mode="locator"))
        IO92

        """

    def test___eq__(self):
        """
        >>> Point(52.015, -0.221) == Point(52.015, -0.221)
        True
        >>> Point(52.015, -0.221) == Point(52.6333, -2.5)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 168)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 170)
        True

        """

    def test___ne__(self):
        """
        >>> Point(52.015, -0.221) != Point(52.015, -0.221)
        False
        >>> Point(52.015, -0.221) != Point(52.6333, -2.5)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 168)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 170)
        False

        """

    def test_to_grid_locator(self):
        """
        >>> Home = Point(52.015, -0.221)
        >>> Home.to_grid_locator("extsquare")
        'IO92va33'
        >>> Home.to_grid_locator("subsquare")
        'IO92va'
        >>> Home.to_grid_locator()
        'IO92'

        """

    def test_distance(self):
        """
        >>> "%i kM" % Point(52.015, -0.221).distance(Point(52.6333, -2.5))
        '169 kM'
        >>> "%i kM" % Point(52.015, -0.221).distance(Point(52.6333, -2.5),
        ...                                          method="sloc")
        '169 kM'
        >>> "%i kM" % Point(52.015, -0.221).distance(Point(52.6333, -2.5),
        ...                                          method="Invalid")
        Traceback (most recent call last):
        ...
        ValueError: Unknown method type `Invalid'

        >>> to_loc = Point(33.9400, -118.4000)
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc)
        '2884 kM'
        >>> "%i mi" % Point(36.1200, -86.6700, "imperial").distance(to_loc)
        '1792 mi'
        >>> "%i nmi" % Point(36.1200, -86.6700, "nautical").distance(to_loc)
        '1557 nmi'
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc, method="sloc")
        '2884 kM'

        """

    def test_bearing(self):
        """
        >>> "%i" % Point(52.015, -0.221).bearing(Point(52.6333, -2.5))
        '294'
        >>> "%i" % Point(52.6333, -2.5).bearing(Point(52.015, -0.221))
        '113'
        >>> "%i" % Point(36.1200, -86.6700).bearing(Point(33.9400,
        ...                                               -118.4000))
        '274'
        >>> "%i" % Point(33.9400, -118.4000).bearing(Point(36.1200,
        ...                                                -86.6700))
        '76'
        >>> Point(52.015, -0.221).bearing(Point(52.6333, -2.5),
        ...                               format="string")
        'North-west'

        """

    def test_midpoint(self):
        """
        >>> Point(52.015, -0.221).midpoint(Point(52.6333, -2.5))
        Point(52.3296314054, -1.35253686056, 'metric', 'degrees', 0)
        >>> Point(36.1200, -86.6700).midpoint(Point(33.9400, -118.4000))
        Point(36.082394919, -102.752173705, 'metric', 'degrees', 0)

        """

    def test_final_bearing(self):
        """
        >>> "%i" % Point(52.015, -0.221).final_bearing(Point(52.6333, -2.5))
        '293'
        >>> "%i" % Point(52.6333, -2.5).final_bearing(Point(52.015, -0.221))
        '114'
        >>> "%i" % Point(36.1200, -86.6700).final_bearing(Point(33.9400,
        ...                                                     -118.4000))
        '256'
        >>> "%i" % Point(33.9400, -118.4000).final_bearing(Point(36.1200,
        ...                                                      -86.6700))
        '94'
        >>> Point(52.015, -0.221).bearing(Point(52.6333, -2.5),
        ...                               format="string")
        'North-west'

        """

    def test_destination(self):
        """
        >>> Point(52.015, -0.221).destination(294, 169)
        Point(52.6116387502, -2.50937408195, 'metric', 'degrees', 0)
        >>> Home = Point(52.015, -0.221, "imperial")
        >>> Home.destination(294, 169 / utils.STATUTE_MILE)
        Point(52.6116387502, -2.50937408195, 'metric', 'degrees', 0)
        >>> Home = Point(52.015, -0.221, "nautical")
        >>> Home.destination(294, 169 / utils.NAUTICAL_MILE)
        Point(52.6116387502, -2.50937408195, 'metric', 'degrees', 0)
        >>> Point(36.1200, -86.6700).destination(274, 2885)
        Point(33.6872799138, -118.327218421, 'metric', 'degrees', 0)

        """

    def test_sunrise(self):
        """
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunrise(date)
        datetime.time(3, 40)
        >>> Point(52.6333, -2.5).sunrise(date)
        datetime.time(3, 45)
        >>> Point(36.1200, -86.6700).sunrise(date)
        datetime.time(10, 29)
        >>> Point(33.9400, -118.4000).sunrise(date)
        datetime.time(12, 41)

        """

    def test_sunset(self):
        """
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunset(date)
        datetime.time(20, 22)
        >>> Point(52.6333, -2.5).sunset(date)
        datetime.time(20, 35)
        >>> Point(36.1200, -86.6700).sunset(date)
        datetime.time(1, 5)
        >>> Point(33.9400, -118.4000).sunset(date)
        datetime.time(3, 6)

        """

    def test_sun_events(self):
        """
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sun_events(date)
        (datetime.time(3, 40), datetime.time(20, 22))
        >>> Point(52.6333, -2.5).sun_events(date)
        (datetime.time(3, 45), datetime.time(20, 35))
        >>> Point(36.1200, -86.6700).sun_events(date)
        (datetime.time(10, 29), datetime.time(1, 5))
        >>> Point(33.9400, -118.4000).sun_events(date)
        (datetime.time(12, 41), datetime.time(3, 6))

        """

    def test_inverse(self):
        """
        >>> "%i, %i" % Point(52.015, -0.221).inverse(Point(52.6333, -2.5))
        '294, 169'

        """


class TestTimedPoint():
    def test___init__(self):
        """
        >>> place = TimedPoint(52.015, -0.221,
        ...                    time=datetime.datetime(2008, 7, 29))

        """

class TestPoints():
    def test___init__(self):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Points([Point(52.015, -0.221), Point(53.645, -0.284)])
        Points([Point(52.015, -0.221, 'metric', 'degrees', 0),
                Point(53.645, -0.284, 'metric', 'degrees', 0)],
               False, 'metric')

        """

    def test___repr__(self):
        """
        >>> locations = [Point(0, 0)] * 4
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Points(locations)
        Points([Point(0.0, 0.0, 'metric', 'degrees', 0),
                Point(0.0, 0.0, 'metric', 'degrees', 0),
                Point(0.0, 0.0, 'metric', 'degrees', 0),
                Point(0.0, 0.0, 'metric', 'degrees', 0)],
               False, 'metric')

        """

    def test_import_locations(self):
        """
        >>> locations = Points()
        >>> locations.import_locations(["0;0", "52.015 -0.221"])
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> locations
        Points([Point(0.0, 0.0, 'metric', 'degrees', 0),
                Point(52.015, -0.221, 'metric', 'degrees', 0)],
                False, 'metric')

        """

    def test_distance(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> "%.3f" % sum(locations.distance())
        '111.632'

        """

    def test_bearing(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> ["%.3f" % x for x in locations.bearing()]
        ['46.242', '28.416']

        """

    def test_final_bearing(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> ["%.3f" % x for x in locations.final_bearing()]
        ['46.448', '28.906']

        """

    def test_inverse(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.inverse())
        [(46.24239319802467, 24.629669163425465),
         (28.41617384845358, 87.00207583308533)]

        """

    def test_midpoint(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.midpoint())
        [Point(52.0915720432, -0.0907237539143, 'metric', 'degrees', 0),
         Point(52.5119010509, 0.346088603087, 'metric', 'degrees', 0)]

        """

    def test_range(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> list(locations.range(Point(52.015, -0.221), 20))
        [Point(52.015, -0.221, 'metric', 'degrees', 0)]

        """

    def test_destination(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.destination(42, 240))
        [Point(53.5956078217, 2.2141813684, 'metric', 'degrees', 0),
         Point(53.7484691495, 2.48403821375, 'metric', 'degrees', 0),
         Point(54.4348338045, 3.14183478498, 'metric', 'degrees', 0)]

        """

    def test_sunrise(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> list(locations.sunrise(datetime.date(2008, 5, 2)))
        [datetime.time(4, 28), datetime.time(4, 26), datetime.time(4, 21)]

        """

    def test_sunset(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> list(locations.sunset(datetime.date(2008, 5, 2)))
        [datetime.time(19, 28), datetime.time(19, 27), datetime.time(19, 27)]

        """

    def test_sun_events(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.sun_events(datetime.date(2008, 5, 2)))
        [(datetime.time(4, 28), datetime.time(19, 28)),
         (datetime.time(4, 26), datetime.time(19, 27)),
         (datetime.time(4, 21), datetime.time(19, 27))]

        """

    def test_to_grid_locator(self):
        """
        >>> locations = Points(["52.015;-0.221", "52.168;0.040",
        ...                     "52.855;0.657"],
        ...                    parse=True)
        >>> list(locations.to_grid_locator("extsquare"))
        ['IO92va33', 'JO02ae40', 'JO02hu85']
        >>> list(locations.to_grid_locator("subsquare"))
        ['IO92va', 'JO02ae', 'JO02hu']

        """


class TestTimedPoints():
    def speed(self):
        """
        >>> locations = TimedPoints()
        >>> locations.extend([
        ...     TimedPoint(52.015, -0.221,
        ...                time=datetime.datetime(2008, 7, 28, 16, 38)),
        ...     TimedPoint(52.168, 0.040,
        ...                time=datetime.datetime(2008, 7, 28, 18, 38)),
        ...     TimedPoint(52.855, 0.657,
        ...                time=datetime.datetime(2008, 7, 28, 19, 17)),
        ... ])
        >>> map(lambda s: "%.3f" % s, locations.speed())
        ['12.315', '133.849']

        """


class TestKeyedPoints():
    def test___init__(self):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> KeyedPoints({"a": Point(52.015, -0.221),
        ...              "b": Point(53.645, -0.284)})
        KeyedPoints({'a': Point(52.015, -0.221, 'metric', 'degrees', 0), 'b': Point(53.645, -0.284, 'metric', 'degrees', 0)}, False, 'metric')

        """

    def test___repr__(self):
        """
        >>> locations = {"a": Point(0, 0), "b": Point(0,0)}
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> KeyedPoints(locations)
        KeyedPoints({'a': Point(0.0, 0.0, 'metric', 'degrees', 0), 'b': Point(0.0, 0.0, 'metric', 'degrees', 0)}, False, 'metric')

        """

    def test_import_locations(self):
        """
        >>> locations = KeyedPoints()
        >>> locations.import_locations([("prime", "0;0"),
        ...                             ("home", "52.015 -0.221")])
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> locations
        KeyedPoints({'prime': Point(0.0, 0.0, 'metric', 'degrees', 0), 'home': Point(52.015, -0.221, 'metric', 'degrees', 0)}, False, 'metric')

        """

    def test_distance(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> "%.3f" % sum(locations.distance(("home", "Carol", "Kenny")))
        '111.632'

        """

    def test_bearing(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> ["%.3f" % x for x in locations.bearing(("home", "Carol", "Kenny"))]
        ['46.242', '28.416']

        """

    def test_final_bearing(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> ["%.3f" % x
        ...  for x in locations.final_bearing(("home", "Carol", "Kenny"))]
        ['46.448', '28.906']

        """

    def test_inverse(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.inverse(("home", "Carol", "Kenny")))
        [(46.24239319802467, 24.629669163425465),
         (28.41617384845358, 87.00207583308533)]

        """

    def test_midpoint(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.midpoint(("home", "Carol", "Kenny")))
        [Point(52.0915720432, -0.0907237539143, 'metric', 'degrees', 0),
         Point(52.5119010509, 0.346088603087, 'metric', 'degrees', 0)]

        """

    def test_range(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> list(locations.range(Point(52.015, -0.221), 20))
        [('home', Point(52.015, -0.221, 'metric', 'degrees', 0))]

        """

    def test_destination(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.destination(42, 240))
        [('home', Point(53.5956078217, 2.2141813684, 'metric', 'degrees', 0)), ('Carol', Point(53.7484691495, 2.48403821375, 'metric', 'degrees', 0)), ('Kenny', Point(54.4348338045, 3.14183478498, 'metric', 'degrees', 0))]

        """

    def test_sunrise(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.sunrise(datetime.date(2008, 5, 2)))
        [('home', datetime.time(4, 28)), ('Carol', datetime.time(4, 26)), ('Kenny', datetime.time(4, 21))]

        """

    def test_sunset(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.sunset(datetime.date(2008, 5, 2)))
        [('home', datetime.time(19, 28)), ('Carol', datetime.time(19, 27)), ('Kenny', datetime.time(19, 27))]

        """

    def test_sun_events(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> list(locations.sun_events(datetime.date(2008, 5, 2)))
        [('home', (datetime.time(4, 28), datetime.time(19, 28))), ('Carol', (datetime.time(4, 26), datetime.time(19, 27))), ('Kenny', (datetime.time(4, 21), datetime.time(19, 27)))]

        """

    def test_to_grid_locator(self):
        """
        >>> locations = KeyedPoints([("home", "52.015;-0.221"),
        ...                          ("Carol", "52.168;0.040"),
        ...                          ("Kenny", "52.855;0.657")],
        ...                         parse=True)
        >>> list(locations.to_grid_locator("extsquare"))
        [('home', 'IO92va33'), ('Carol', 'JO02ae40'), ('Kenny', 'JO02hu85')]
        >>> list(locations.to_grid_locator("subsquare"))
        [('home', 'IO92va'), ('Carol', 'JO02ae'), ('Kenny', 'JO02hu')]

        """
