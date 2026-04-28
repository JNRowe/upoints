#
"""test_point - Test point support"""
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
import math

from hypothesis import given
from hypothesis import strategies as st
from pytest import approx, fixture, mark, raises

from upoints import utils
from upoints.point import KeyedPoints, Point, Points, TimedPoint, TimedPoints


def test_Point___init__():
    test = Point(math.pi / 4, math.pi / 2, angle="radians")
    assert test.latitude == 45
    assert test.longitude == 90

    test = Point((50, 20, 10), (-1, -3, -12))
    assert test.latitude == approx(50.336, rel=0.001)
    assert test.longitude == approx(-1.053, rel=0.001)


@given(
    st.floats(min_value=-90, max_value=90),
    st.floats(min_value=180, max_value=180),
)
def test_Point___init___invariant(lat, lon):
    test = Point(lat, lon, angle="degrees")
    assert test.latitude == lat
    assert test.longitude == lon


def test_Point___init___validity():
    with raises(ValueError, match="Unknown angle type None"):
        Point(52.015, -0.221, angle=None)
    with raises(ValueError, match="Invalid latitude value -92"):
        Point(-92, -0.221)
    with raises(ValueError, match="Invalid longitude value 185"):
        Point(52.015, 185)
    with raises(ValueError, match="Unknown units type None"):
        Point(52.015, -0.221, units=None)


def test_Point___dict__():
    home = Point(52.015, -0.221)
    assert home.__dict__ == {
        "_angle": "degrees",
        "_latitude": 52.015,
        "_longitude": -0.221,
        "_rad_latitude": 0.9078330104248505,
        "_rad_longitude": -0.0038571776469074684,
        "timezone": 0,
        "units": "metric",
    }


def test_Point___dict___custom_class():
    class Test(Point):
        def __init__(self, latitude, longitude):
            super(Test, self).__init__(latitude, longitude)
            self.TEST = "tested"

    assert Test(52.015, -0.221).__dict__ == {
        "TEST": "tested",
        "_angle": "degrees",
        "_latitude": 52.015,
        "_longitude": -0.221,
        "_rad_latitude": 0.9078330104248505,
        "_rad_longitude": -0.0038571776469074684,
        "timezone": 0,
        "units": "metric",
    }


def test_Point___repr__():
    assert (
        repr(Point(52.015, -0.221))
        == "Point(52.015, -0.221, 'metric', 'degrees', 0)"
    )


def test_Point___str__():
    assert str(Point(52.015, -0.221)) == "N52.015°; W000.221°"


@mark.parametrize(
    "style, result",
    [
        ("dm", "52°00.90′N, 000°13.26′W"),
        ("dms", """52°00′54″N, 000°13′15″W"""),
        ("locator", "IO92"),
    ],
)
def test_Point___format__(style, result):
    assert format(Point(52.015, -0.221), style) == result


def test_Point___unicode__():
    assert str(Point(52.015, -0.221)) == "N52.015°; W000.221°"


def test_Point___eq__():
    assert Point(52.015, -0.221) == Point(52.015, -0.221)


def test_Point___ne__():
    assert Point(52.015, -0.221) != Point(52.6333, -2.5)


@mark.parametrize(
    "accuracy, result",
    [
        ("extsquare", "IO92va33"),
        ("subsquare", "IO92va"),
    ],
)
def test_Point_to_grid_locator(accuracy, result):
    assert Point(52.015, -0.221).to_grid_locator(accuracy) == result


def test_Point_to_grid_locator_default():
    assert Point(52.015, -0.221).to_grid_locator() == "IO92"


def test_Point_distance():
    home = Point(52.015, -0.221)
    dest = Point(52.6333, -2.5)
    assert home.distance(dest) == approx(169, rel=0.5)
    assert home.distance(dest, method="sloc") == approx(169, rel=0.5)

    with raises(ValueError, match="Unknown method type 'Invalid'"):
        home.distance(dest, method="Invalid")


@mark.parametrize(
    "units, result",
    [
        ("imperial", 1792),
        ("nautical", 1557),
        ("metric", 2884),
    ],
)
def test_Point_distance2(units, result):
    start = Point(36.1200, -86.6700, units=units)
    dest = Point(33.9400, -118.4000)
    assert int(start.distance(dest)) == result


@mark.parametrize(
    "p1, p2, result",
    [
        (Point(52.015, -0.221), Point(52.6333, -2.5), 294),
        (Point(52.6333, -2.5), Point(52.015, -0.221), 113),
        (Point(36.1200, -86.6700), Point(33.9400, -118.4000), 274),
        (Point(33.9400, -118.4000), Point(36.1200, -86.6700), 76),
    ],
)
def test_Point_bearing(p1, p2, result):
    assert int(p1.bearing(p2)) == result


def test_Point_bearing_format():
    assert (
        Point(52.015, -0.221).bearing(Point(52.6333, -2.5), format="string")
        == "North-west"
    )


@mark.parametrize(
    "p1, p2, result",
    [
        (
            Point(52.015, -0.221),
            Point(52.6333, -2.5),
            Point(52.329631405407014, -1.3525368605590993),
        ),
        (
            Point(36.1200, -86.6700),
            Point(33.9400, -118.4000),
            Point(36.08239491900365, -102.75217370539663),
        ),
    ],
)
def test_Point_midpoint(p1, p2, result):
    assert p1.midpoint(p2) == result


@mark.parametrize(
    "p1, p2, result",
    [
        (Point(52.015, -0.221), Point(52.6333, -2.5), 293),
        (Point(52.6333, -2.5), Point(52.015, -0.221), 114),
        (Point(36.1200, -86.6700), Point(33.9400, -118.4000), 256),
        (Point(33.9400, -118.4000), Point(36.1200, -86.6700), 94),
    ],
)
def test_Point_final_bearing(p1, p2, result):
    assert int(p1.final_bearing(p2)) == result


def test_Point_final_bearing_format():
    assert (
        Point(52.015, -0.221).bearing(Point(52.6333, -2.5), format="string")
        == "North-west"
    )


@mark.parametrize(
    "units, multiplier",
    [
        ("metric", 1),
        ("imperial", utils.STATUTE_MILE),
        ("nautical", utils.NAUTICAL_MILE),
    ],
)
def test_Point_destination(units, multiplier):
    home = Point(52.015, -0.221, units=units)
    assert home.destination(294, 169 / multiplier) == Point(
        52.611638750214745, -2.509374081952352
    )


def test_Point_destination2():
    assert Point(36.1200, -86.6700).destination(274, 2885) == Point(
        33.6872799137609, -118.32721842114393
    )


@mark.parametrize(
    "p1, result",
    [
        (Point(52.015, -0.221), datetime.time(3, 40)),
        (Point(52.6333, -2.5), datetime.time(3, 45)),
        (Point(36.1200, -86.6700), datetime.time(10, 29)),
        (Point(33.9400, -118.4000), datetime.time(12, 41)),
    ],
)
def test_Point_sunrise(p1, result):
    date = datetime.date(2007, 6, 15)
    assert p1.sunrise(date) == result


@mark.parametrize(
    "p1, result",
    [
        (Point(52.015, -0.221), datetime.time(20, 22)),
        (Point(52.6333, -2.5), datetime.time(20, 35)),
        (Point(36.1200, -86.6700), datetime.time(1, 5)),
        (Point(33.9400, -118.4000), datetime.time(3, 6)),
    ],
)
def test_Point_sunset(p1, result):
    date = datetime.date(2007, 6, 15)
    assert p1.sunset(date) == result


@mark.parametrize(
    "p1, result",
    [
        (
            Point(52.015, -0.221),
            (datetime.time(3, 40), datetime.time(20, 22)),
        ),
        (
            Point(52.6333, -2.5),
            (datetime.time(3, 45), datetime.time(20, 35)),
        ),
        (
            Point(36.1200, -86.6700),
            (datetime.time(10, 29), datetime.time(1, 5)),
        ),
        (
            Point(33.9400, -118.4000),
            (datetime.time(12, 41), datetime.time(3, 6)),
        ),
    ],
)
def test_Point_sun_events(p1, result):
    date = datetime.date(2007, 6, 15)
    assert p1.sun_events(date) == result


def test_Point_inverse():
    bearing, dist = Point(52.015, -0.221).inverse(Point(52.6333, -2.5))
    assert int(bearing) == 294
    assert int(dist) == 169


@fixture
def sample_Points():
    yield Points(["52.015;-0.221", "52.168;0.040", "52.855;0.657"], parse=True)


def test_Points___repr__(sample_Points):
    locations = [Point(0, 0)] * 4
    assert repr(Points(locations)) == (
        "Points([Point(0.0, 0.0, 'metric', 'degrees', 0), "
        "Point(0.0, 0.0, 'metric', 'degrees', 0), "
        "Point(0.0, 0.0, 'metric', 'degrees', 0), "
        "Point(0.0, 0.0, 'metric', 'degrees', 0)], "
        "False, 'metric')"
    )


def test_Points_import_locations(sample_Points):
    locations = Points()
    locations.import_locations(["0;0", "52.015 -0.221"])
    assert repr(locations) == (
        "Points([Point(0.0, 0.0, 'metric', 'degrees', 0), "
        "Point(52.015, -0.221, 'metric', 'degrees', 0)], "
        "False, 'metric')"
    )


def test_Points_distance(sample_Points):
    assert sum(sample_Points.distance()) == approx(111.632, rel=0.001)


def test_Points_bearing(sample_Points):
    assert list(sample_Points.bearing()) == [
        approx(46.242, rel=0.001),
        approx(28.416, rel=0.001),
    ]


def test_Points_final_bearing(sample_Points):
    assert list(sample_Points.final_bearing()) == [
        approx(46.448, rel=0.001),
        approx(28.906, rel=0.001),
    ]


def test_Points_inverse(sample_Points):
    assert list(sample_Points.inverse()) == [
        (46.24239319802467, 24.629669163425465),
        (28.41617384845358, 87.00207583308533),
    ]


def test_Points_midpoint(sample_Points):
    assert list(sample_Points.midpoint()) == [
        Point(52.09157204324692, -0.09072375391429187, "metric", "degrees", 0),
        Point(52.51190105089283, 0.3460886030865466, "metric", "degrees", 0),
    ]


def test_Points_range(sample_Points):
    assert list(sample_Points.range(Point(52.015, -0.221), 20)) == [
        Point(52.015, -0.221, "metric", "degrees", 0)
    ]


def test_Points_destination(sample_Points):
    assert list(sample_Points.destination(42, 240)) == [
        Point(53.59560782169536, 2.2141813683976777, "metric", "degrees", 0),
        Point(53.74846914951471, 2.4840382137470614, "metric", "degrees", 0),
        Point(54.43483380445103, 3.1418347849815293, "metric", "degrees", 0),
    ]


def test_Points_sunrise(sample_Points):
    assert list(sample_Points.sunrise(datetime.date(2008, 5, 2))) == [
        datetime.time(4, 28),
        datetime.time(4, 26),
        datetime.time(4, 21),
    ]


def test_Points_sunset(sample_Points):
    assert list(sample_Points.sunset(datetime.date(2008, 5, 2))) == [
        datetime.time(19, 28),
        datetime.time(19, 27),
        datetime.time(19, 27),
    ]


def test_Points_sun_events(sample_Points):
    assert list(sample_Points.sun_events(datetime.date(2008, 5, 2))) == [
        (datetime.time(4, 28), datetime.time(19, 28)),
        (datetime.time(4, 26), datetime.time(19, 27)),
        (datetime.time(4, 21), datetime.time(19, 27)),
    ]


@mark.parametrize(
    "accuracy, result",
    [
        ("extsquare", ["IO92va33", "JO02ae40", "JO02hu85"]),
        ("subsquare", ["IO92va", "JO02ae", "JO02hu"]),
    ],
)
def test_Points_to_grid_locator(sample_Points, accuracy, result):
    assert list(sample_Points.to_grid_locator(accuracy)) == result


def test_TimedPoints_speed():
    locations = TimedPoints()
    locations.extend([
        TimedPoint(52.015, -0.221, time=datetime.datetime(2008, 7, 28, 16, 38)),
        TimedPoint(52.168, 0.040, time=datetime.datetime(2008, 7, 28, 18, 38)),
        TimedPoint(52.855, 0.657, time=datetime.datetime(2008, 7, 28, 19, 17)),
    ])
    assert list(locations.speed()) == [
        approx(12.315, rel=0.001),
        approx(133.849, rel=0.001),
    ]


@fixture
def sample_KeyedPoints():
    yield KeyedPoints(
        [
            ("home", "52.015;-0.221"),
            ("Carol", "52.168;0.040"),
            ("Kenny", "52.855;0.657"),
        ],
        parse=True,
    )


def test_import_locations(sample_KeyedPoints):
    locations = KeyedPoints()
    locations.import_locations([
        ("prime", "0;0"),
        ("home", "52.015 -0.221"),
    ])
    assert locations == KeyedPoints(
        {
            "prime": Point(0.0, 0.0, "metric", "degrees", 0),
            "home": Point(52.015, -0.221, "metric", "degrees", 0),
        },
        False,
        "metric",
    )


def test_distance(sample_KeyedPoints):
    assert sum(
        sample_KeyedPoints.distance(("home", "Carol", "Kenny"))
    ) == approx(111.632, rel=0.001)


def test_bearing(sample_KeyedPoints):
    assert list(sample_KeyedPoints.bearing(("home", "Carol", "Kenny"))) == [
        approx(46.242, rel=0.001),
        approx(28.416, rel=0.001),
    ]


def test_final_bearing(sample_KeyedPoints):
    assert list(
        sample_KeyedPoints.final_bearing(("home", "Carol", "Kenny"))
    ) == [
        approx(46.448, rel=0.001),
        approx(28.906, rel=0.001),
    ]


def test_inverse(sample_KeyedPoints):
    assert list(sample_KeyedPoints.inverse(("home", "Carol", "Kenny"))) == [
        (46.24239319802467, 24.629669163425465),
        (28.41617384845358, 87.00207583308533),
    ]


def test_midpoint(sample_KeyedPoints):
    assert list(sample_KeyedPoints.midpoint(("home", "Carol", "Kenny"))) == [
        Point(52.09157204324692, -0.09072375391429187, "metric", "degrees", 0),
        Point(52.51190105089283, 0.3460886030865466, "metric", "degrees", 0),
    ]


def test_range(sample_KeyedPoints):
    assert list(sample_KeyedPoints.range(Point(52.015, -0.221), 20)) == [
        ("home", Point(52.015, -0.221, "metric", "degrees", 0))
    ]


def test_destination(sample_KeyedPoints):
    assert sorted(sample_KeyedPoints.destination(42, 240)) == [
        (
            "Carol",
            Point(
                53.74846914951471,
                2.4840382137470614,
                "metric",
                "degrees",
                0,
            ),
        ),
        (
            "Kenny",
            Point(
                54.43483380445103,
                3.1418347849815293,
                "metric",
                "degrees",
                0,
            ),
        ),
        (
            "home",
            Point(
                53.59560782169536,
                2.2141813683976777,
                "metric",
                "degrees",
                0,
            ),
        ),
    ]


def test_sunrise(sample_KeyedPoints):
    assert sorted(sample_KeyedPoints.sunrise(datetime.date(2008, 5, 2))) == [
        ("Carol", datetime.time(4, 26)),
        ("Kenny", datetime.time(4, 21)),
        ("home", datetime.time(4, 28)),
    ]


def test_sunset(sample_KeyedPoints):
    assert sorted(sample_KeyedPoints.sunset(datetime.date(2008, 5, 2))) == [
        ("Carol", datetime.time(19, 27)),
        ("Kenny", datetime.time(19, 27)),
        ("home", datetime.time(19, 28)),
    ]


def test_sun_events(sample_KeyedPoints):
    assert sorted(sample_KeyedPoints.sun_events(datetime.date(2008, 5, 2))) == [
        ("Carol", (datetime.time(4, 26), datetime.time(19, 27))),
        ("Kenny", (datetime.time(4, 21), datetime.time(19, 27))),
        ("home", (datetime.time(4, 28), datetime.time(19, 28))),
    ]


@mark.parametrize(
    "accuracy, result",
    [
        (
            "extsquare",
            [
                ("Carol", "JO02ae40"),
                ("Kenny", "JO02hu85"),
                ("home", "IO92va33"),
            ],
        ),
        (
            "subsquare",
            [("Carol", "JO02ae"), ("Kenny", "JO02hu"), ("home", "IO92va")],
        ),
    ],
)
def test_to_grid_locator(sample_KeyedPoints, accuracy, result):
    assert sorted(sample_KeyedPoints.to_grid_locator(accuracy)) == result
