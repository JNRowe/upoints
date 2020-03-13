#
"""test_point - Test point support"""
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
import math

from pytest import approx, mark, raises

from upoints import utils
from upoints.point import (KeyedPoints, Point, Points, TimedPoint, TimedPoints)


class TestPoint:
    def test___init__(self):
        test = Point(math.pi / 4, math.pi / 2, angle='radians')
        assert test.latitude == 45
        assert test.longitude == 90

        test = Point((50, 20, 10), (-1, -3, -12))
        assert test.latitude == approx(50.336, rel=0.001)
        assert test.longitude == approx(-1.053, rel=0.001)

    def test___init___validity(self):
        with raises(ValueError, match='Unknown angle type None'):
            Point(52.015, -0.221, angle=None)
        with raises(ValueError, match='Invalid latitude value -92'):
            Point(-92, -0.221)
        with raises(ValueError, match='Invalid longitude value 185'):
            Point(52.015, 185)
        with raises(ValueError, match='Unknown units type None'):
            Point(52.015, -0.221, units=None)

    def test___dict__(self):
        home = Point(52.015, -0.221)
        assert home.__dict__ == {
            '_angle': 'degrees',
            '_latitude': 52.015,
            '_longitude': -0.221,
            '_rad_latitude': 0.9078330104248505,
            '_rad_longitude': -0.0038571776469074684,
            'timezone': 0,
            'units': 'metric',
        }

    def test___dict___custom_class(self):
        class Test(Point):
            __slots__ = ('TEST', )

            def __init__(self, latitude, longitude):
                super(Test, self).__init__(latitude, longitude)
                self.TEST = 'tested'

        assert Test(52.015, -0.221).__dict__ == {
            'TEST': 'tested',
            '_angle': 'degrees',
            '_latitude':  52.015,
            '_longitude': -0.221,
            '_rad_latitude': 0.9078330104248505,
            '_rad_longitude': -0.0038571776469074684,
            'timezone': 0,
            'units': 'metric',
        }

    def test___repr__(self):
        assert repr(Point(52.015, -0.221)) == \
            "Point(52.015, -0.221, 'metric', 'degrees', 0)"

    def test___str__(self):
        assert str(Point(52.015, -0.221)) == 'N52.015°; W000.221°'

    @mark.parametrize('style, result', [
        ('dm', "52°00.90′N, 000°13.26′W"),
        ('dms', """52°00′54″N, 000°13′15″W"""),
        ('locator', 'IO92'),
    ])
    def test___format__(self, style, result):
        assert format(Point(52.015, -0.221), style) == result

    def test___unicode__(self):
        assert str(Point(52.015, -0.221)) == 'N52.015°; W000.221°'

    def test___eq__(self):
        assert Point(52.015, -0.221) == Point(52.015, -0.221)

    def test___ne__(self):
        assert Point(52.015, -0.221) != Point(52.6333, -2.5)

    @mark.parametrize('accuracy, result', [
        ('extsquare', 'IO92va33'),
        ('subsquare', 'IO92va'),
    ])
    def test_to_grid_locator(self, accuracy, result):
        assert Point(52.015, -0.221).to_grid_locator(accuracy) == result

    def test_to_grid_locator_default(self):
        assert Point(52.015, -0.221).to_grid_locator() == 'IO92'

    def test_distance(self):
        home = Point(52.015, -0.221)
        dest = Point(52.6333, -2.5)
        assert home.distance(dest) == approx(169, rel=0.5)
        assert home.distance(dest, method='sloc') == approx(169, rel=0.5)

        with raises(ValueError, match="Unknown method type 'Invalid'"):
            home.distance(dest, method='Invalid')

    @mark.parametrize('units, result', [
        ('imperial', 1792),
        ('nautical', 1557),
        ('metric', 2884),
    ])
    def test_distance2(self, units, result):
        start = Point(36.1200, -86.6700, units=units)
        dest = Point(33.9400, -118.4000)
        assert int(start.distance(dest)) == result

    @mark.parametrize('p1, p2, result', [
        (Point(52.015, -0.221), Point(52.6333, -2.5), 294),
        (Point(52.6333, -2.5), Point(52.015, -0.221), 113),
        (Point(36.1200, -86.6700), Point(33.9400, -118.4000), 274),
        (Point(33.9400, -118.4000), Point(36.1200, -86.6700), 76),
    ])
    def test_bearing(self, p1, p2, result):
        assert int(p1.bearing(p2)) == result

    def test_bearing_format(self):
        assert Point(52.015, -0.221).bearing(Point(52.6333, -2.5),
                                             format='string') == 'North-west'

    @mark.parametrize('p1, p2, result', [
        (Point(52.015, -0.221), Point(52.6333, -2.5),
         Point(52.329631405407014, -1.3525368605590993)),
        (Point(36.1200, -86.6700), Point(33.9400, -118.4000),
         Point(36.08239491900365, -102.75217370539663)),
    ])
    def test_midpoint(self, p1, p2, result):
        assert p1.midpoint(p2) == result

    @mark.parametrize('p1, p2, result', [
        (Point(52.015, -0.221), Point(52.6333, -2.5), 293),
        (Point(52.6333, -2.5), Point(52.015, -0.221), 114),
        (Point(36.1200, -86.6700), Point(33.9400, -118.4000), 256),
        (Point(33.9400, -118.4000), Point(36.1200, -86.6700), 94),
    ])
    def test_final_bearing(self, p1, p2, result):
        assert int(p1.final_bearing(p2)) == result

    def test_final_bearing_format(self):
        assert Point(52.015, -0.221).bearing(Point(52.6333, -2.5),
                                             format='string') == 'North-west'

    @mark.parametrize('units, multiplier', [
        ('metric', 1),
        ('imperial', utils.STATUTE_MILE),
        ('nautical', utils.NAUTICAL_MILE),
    ])
    def test_destination(self, units, multiplier):
        home = Point(52.015, -0.221, units=units)
        assert home.destination(294, 169 / multiplier) == \
            Point(52.611638750214745, -2.509374081952352)

    def test_destination2(self):
        assert Point(36.1200, -86.6700).destination(274, 2885) == \
            Point(33.6872799137609, -118.32721842114393)

    @mark.parametrize('p1, result', [
        (Point(52.015, -0.221), datetime.time(3, 40)),
        (Point(52.6333, -2.5), datetime.time(3, 45)),
        (Point(36.1200, -86.6700), datetime.time(10, 29)),
        (Point(33.9400, -118.4000), datetime.time(12, 41)),
    ])
    def test_sunrise(self, p1, result):
        date = datetime.date(2007, 6, 15)
        assert p1.sunrise(date) == result

    @mark.parametrize('p1, result', [
        (Point(52.015, -0.221), datetime.time(20, 22)),
        (Point(52.6333, -2.5), datetime.time(20, 35)),
        (Point(36.1200, -86.6700), datetime.time(1, 5)),
        (Point(33.9400, -118.4000), datetime.time(3, 6)),
    ])
    def test_sunset(self, p1, result):
        date = datetime.date(2007, 6, 15)
        assert p1.sunset(date) == result

    @mark.parametrize('p1, result', [
        (Point(52.015, -0.221), (datetime.time(3, 40), datetime.time(20, 22))),
        (Point(52.6333, -2.5), (datetime.time(3, 45), datetime.time(20, 35))),
        (Point(36.1200, -86.6700),
         (datetime.time(10, 29), datetime.time(1, 5))),
        (Point(33.9400, -118.4000),
         (datetime.time(12, 41), datetime.time(3, 6))),
    ])
    def test_sun_events(self, p1, result):
        date = datetime.date(2007, 6, 15)
        assert p1.sun_events(date) == result

    def test_inverse(self):
        bearing, dist = Point(52.015, -0.221).inverse(Point(52.6333, -2.5))
        assert int(bearing) == 294
        assert int(dist) == 169


class TestPoints:
    def setup(self):
        self.locs = Points(['52.015;-0.221', '52.168;0.040', '52.855;0.657'],
                           parse=True)

    def test___repr__(self):
        locations = [Point(0, 0)] * 4
        assert repr(Points(locations)) == \
            ("Points([Point(0.0, 0.0, 'metric', 'degrees', 0), "
             "Point(0.0, 0.0, 'metric', 'degrees', 0), "
             "Point(0.0, 0.0, 'metric', 'degrees', 0), "
             "Point(0.0, 0.0, 'metric', 'degrees', 0)], "
             "False, 'metric')")

    def test_import_locations(self):
        locations = Points()
        locations.import_locations(['0;0', '52.015 -0.221'])
        assert repr(locations) == \
            ("Points([Point(0.0, 0.0, 'metric', 'degrees', 0), "
             "Point(52.015, -0.221, 'metric', 'degrees', 0)], "
             "False, 'metric')")

    def test_distance(self):
        assert sum(self.locs.distance()) == approx(111.632, rel=0.001)

    def test_bearing(self):
        assert list(self.locs.bearing()) == [approx(46.242, rel=0.001),
                                             approx(28.416, rel=0.001)]

    def test_final_bearing(self):
        assert list(self.locs.final_bearing()) == \
            [approx(46.448, rel=0.001), approx(28.906, rel=0.001)]

    def test_inverse(self):
        assert list(self.locs.inverse()) == \
            [(46.24239319802467, 24.629669163425465),
             (28.41617384845358, 87.00207583308533)]

    def test_midpoint(self):
        assert list(self.locs.midpoint()) == \
            [Point(52.09157204324692, -0.09072375391429187, 'metric',
                   'degrees', 0),
             Point(52.51190105089283, 0.3460886030865466, 'metric',
                   'degrees', 0)]

    def test_range(self):
        assert list(self.locs.range(Point(52.015, -0.221), 20)) == \
            [Point(52.015, -0.221, 'metric', 'degrees', 0)]

    def test_destination(self):
        assert list(self.locs.destination(42, 240)) == \
            [Point(53.59560782169536, 2.2141813683976777, 'metric', 'degrees',
                   0),
             Point(53.74846914951471, 2.4840382137470614, 'metric', 'degrees',
                   0),
             Point(54.43483380445103, 3.1418347849815293, 'metric', 'degrees',
                   0)]

    def test_sunrise(self):
        assert list(self.locs.sunrise(datetime.date(2008, 5, 2))) == \
            [datetime.time(4, 28), datetime.time(4, 26), datetime.time(4, 21)]

    def test_sunset(self):
        assert list(self.locs.sunset(datetime.date(2008, 5, 2))) == \
            [datetime.time(19, 28), datetime.time(19, 27),
             datetime.time(19, 27)]

    def test_sun_events(self):
        assert list(self.locs.sun_events(datetime.date(2008, 5, 2))) == \
            [(datetime.time(4, 28), datetime.time(19, 28)),
             (datetime.time(4, 26), datetime.time(19, 27)),
             (datetime.time(4, 21), datetime.time(19, 27))]

    @mark.parametrize('accuracy, result', [
        ('extsquare', ['IO92va33', 'JO02ae40', 'JO02hu85']),
        ('subsquare', ['IO92va', 'JO02ae', 'JO02hu']),
    ])
    def test_to_grid_locator(self, accuracy, result):
        assert list(self.locs.to_grid_locator(accuracy)) == result


class TestTimedPoints:
    def test_speed(self):
        locations = TimedPoints()
        locations.extend([
            TimedPoint(52.015, -0.221,
                       time=datetime.datetime(2008, 7, 28, 16, 38)),
            TimedPoint(52.168, 0.040,
                       time=datetime.datetime(2008, 7, 28, 18, 38)),
            TimedPoint(52.855, 0.657,
                       time=datetime.datetime(2008, 7, 28, 19, 17)),
        ])
        assert list(locations.speed()) == \
            [approx(12.315, rel=0.001), approx(133.849, rel=0.001)]


class TestKeyedPoints:
    def setup(self):
        self.locs = KeyedPoints([('home', '52.015;-0.221'),
                                 ('Carol', '52.168;0.040'),
                                 ('Kenny', '52.855;0.657')],
                                parse=True)

    def test_import_locations(self):
        locations = KeyedPoints()
        locations.import_locations([('prime', '0;0'),
                                    ('home', '52.015 -0.221')])
        assert locations == \
            KeyedPoints({'prime': Point(0.0, 0.0, 'metric', 'degrees', 0),
                         'home': Point(52.015, -0.221, 'metric', 'degrees',
                                       0)},
                        False, 'metric')

    def test_distance(self):
        assert sum(self.locs.distance(('home', 'Carol', 'Kenny'))) == \
            approx(111.632, rel=0.001)

    def test_bearing(self):
        assert list(self.locs.bearing(('home', 'Carol', 'Kenny'))) == \
            [approx(46.242, rel=0.001), approx(28.416, rel=0.001)]

    def test_final_bearing(self):
        assert list(self.locs.final_bearing(('home', 'Carol', 'Kenny'))) == \
            [approx(46.448, rel=0.001), approx(28.906, rel=0.001)]

    def test_inverse(self):
        assert list(self.locs.inverse(('home', 'Carol', 'Kenny'))) == \
            [(46.24239319802467, 24.629669163425465),
             (28.41617384845358, 87.00207583308533)]

    def test_midpoint(self):
        assert list(self.locs.midpoint(('home', 'Carol', 'Kenny'))) == \
            [Point(52.09157204324692, -0.09072375391429187, 'metric',
                   'degrees', 0),
             Point(52.51190105089283, 0.3460886030865466, 'metric', 'degrees',
                   0)]

    def test_range(self):
        assert list(self.locs.range(Point(52.015, -0.221), 20)) == \
            [('home', Point(52.015, -0.221, 'metric', 'degrees', 0))]

    def test_destination(self):
        assert sorted(self.locs.destination(42, 240)) == \
            [('Carol', Point(53.74846914951471, 2.4840382137470614, 'metric',
                             'degrees', 0)),
             ('Kenny', Point(54.43483380445103, 3.1418347849815293, 'metric',
                             'degrees', 0)),
             ('home', Point(53.59560782169536, 2.2141813683976777, 'metric',
                            'degrees', 0))]

    def test_sunrise(self):
        assert sorted(self.locs.sunrise(datetime.date(2008, 5, 2))) == \
            [('Carol', datetime.time(4, 26)),
             ('Kenny', datetime.time(4, 21)),
             ('home', datetime.time(4, 28))]

    def test_sunset(self):
        assert sorted(self.locs.sunset(datetime.date(2008, 5, 2))) == \
            [('Carol', datetime.time(19, 27)),
             ('Kenny', datetime.time(19, 27)),
             ('home', datetime.time(19, 28))]

    def test_sun_events(self):
        assert sorted(self.locs.sun_events(datetime.date(2008, 5, 2))) == \
            [('Carol', (datetime.time(4, 26), datetime.time(19, 27))),
             ('Kenny', (datetime.time(4, 21), datetime.time(19, 27))),
             ('home', (datetime.time(4, 28), datetime.time(19, 28)))]

    @mark.parametrize('accuracy, result', [
        ('extsquare',
         [('Carol', 'JO02ae40'), ('Kenny', 'JO02hu85'), ('home', 'IO92va33')]),
        ('subsquare',
         [('Carol', 'JO02ae'), ('Kenny', 'JO02hu'), ('home', 'IO92va')]),
    ])
    def test_to_grid_locator(self, accuracy, result):
        assert sorted(self.locs.to_grid_locator(accuracy)) == result
