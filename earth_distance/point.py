#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""point - Class for working with locations on Earth"""
# Copyright (C) 2007-2008  James Rowe
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

from __future__ import division

import math

from earth_distance import utils

def _manage_location(attr):
    """
    Build managed property interface

    :Parameters:
        attr : `str`
            Property's name
    :rtype: `property`
    :return: Managed property interface
    """
    return property(lambda self: getattr(self, "_%s" % attr),
                    lambda self, value: self._set_location(attr, value))

class Point(object):
    """
    Simple class for representing a location on a sphere

    :since: 0.2.0

    :Ivariables:
        format
            Type of distance units to be used
        latitude
            Location's latitude
        longitude
            Locations's longitude
        rad_latitude
            Location's latitude in radians
        rad_longitude
            Location's longitude in radians
        timezone
            Location's offset from UTC in minutes
    """

    __slots__ = ('format', '_latitude', '_longitude', '_rad_latitude',
                 '_rad_longitude', 'timezone', '_angle')

    def __init__(self, latitude, longitude, format="metric",
                 angle="degrees", timezone=0):
        """
        Initialise a new `Point` object

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
        >>> bad_format = Point(52.015, -0.221, format=None)
        Traceback (most recent call last):
        ...
        ValueError: Unknown unit type `None'

        :Parameters:
            latitude : `float` or coercible to `float`, `tuple` or `list`
                Location's latitude
            longitude : `float` or coercible to `float`, `tuple` or `list`
                Location's longitude
            angle : `str`
                Type for specified angles
            format : `str`
                Unit type to be used for distances
            timezone : `int`
                Offset from UTC in minutes
        :raise ValueError: Unknown value for `angle`
        :raise ValueError: Unknown value for `format`
        :raise ValueError: Invalid value for `latitude` or `longitude`
        """
        super(Point, self).__init__()
        if angle in ("degrees", "radians"):
            self._angle = angle
        else:
            raise ValueError("Unknown angle type `%s'" % angle)
        self._set_location("latitude", latitude)
        self._set_location("longitude", longitude)

        if format in ("imperial", "metric", "nautical"):
            self.format = format
        elif format == "US customary":
            self.format = "imperial"
        else:
            raise ValueError("Unknown unit type `%s'" % format)
        self.timezone = timezone

    def _set_location(self, ltype, value):
        """
        Check supplied location data for validity, and update
        """
        if self._angle == "degrees":
            if isinstance(value, (tuple, list)):
                value = utils.to_dd(*value)
            setattr(self, "_%s" % ltype, float(value))
            setattr(self, "_rad_%s" % ltype, math.radians(float(value)))
        elif self._angle == "radians":
            setattr(self, "_rad_%s" % ltype, float(value))
            setattr(self, "_%s" % ltype, math.degrees(float(value)))
        else:
            raise ValueError("Unknown angle type `%s'" % self._angle)
        if ltype == "latitude" and not -90 <= self._latitude <= 90:
            raise ValueError("Invalid latitude value `%f'" % value)
        elif ltype == "longitude" and not -180 <= self._longitude <= 180:
            raise ValueError("Invalid longitude value `%f'" % value)
    latitude = _manage_location("latitude")
    longitude = _manage_location("longitude")
    rad_latitude = _manage_location("rad_latitude")
    rad_longitude = _manage_location("rad_longitude")

    @property
    def __dict__(self):
        """
        Emulate `__dict__` class attribute for class

        >>> Home = Point(52.015, -0.221)
        >>> sorted(Home.__dict__.items())
        [('_angle', 'degrees'), ('_latitude', 52.015000000000001),
         ('_longitude', -0.221), ('_rad_latitude', 0.90783301042485054),
         ('_rad_longitude', -0.0038571776469074684), ('format', 'metric'),
         ('timezone', 0)]
        >>> class Test(Point):
        ...     __slots__ = ("TEST", )
        ...     def __init__(self, latitude, longitude):
        ...         super(Test, self).__init__(latitude, longitude)
        ...         self.TEST = "tested"
        >>> a = Test(52.015, -0.221)
        >>> sorted(a.__dict__.items())
        [('TEST', 'tested'), ('_angle', 'degrees'),
         ('_latitude', 52.015000000000001), ('_longitude', -0.221),
         ('_rad_latitude', 0.90783301042485054),
         ('_rad_longitude', -0.0038571776469074684), ('format', 'metric'),
         ('timezone', 0)]

        :rtype: `dict`
        :return: Object attributes, as would be provided by a class that didn't
            set ``__slots__``
        """
        slots = []
        cls = self.__class__
        # Build a tuple of __slots__ from all parent classes
        while not cls is object:
            slots.extend(cls.__slots__)
            cls = cls.__base__
        return dict([(item, getattr(self, item)) for item in slots])

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Point(52.015, -0.221)
        Point(52.015, -0.221, 'metric', 'degrees', 0)

        :rtype: `str`
        :return: String to recreate `Point` object
        """
        return utils.repr_assist(self, {"angle": "degrees"})

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

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

        :Parameters:
            mode : `str`
                Coordinate formatting system to use
        :rtype: `str`
        :return: Human readable string representation of `Point` object
        :raise ValueError: Unknown value for `mode`
        """
        text = []
        if mode == "dd":
            text.append("S" if self.latitude < 0 else "N")
            text.append("%06.3f°; " % abs(self.latitude))
            text.append("W" if self.longitude < 0 else "E")
            text.append("%07.3f°" % abs(self.longitude))
        elif mode in ("dm", "dms"):
            latitude_dms = utils.to_dms(self.latitude)
            longitude_dms = utils.to_dms(self.longitude)
            if mode == "dms":
                text.append('''%02i°%02i'%02i"'''
                            % tuple(map(abs, latitude_dms)))
            else:
                text.append("%02i°%05.2f'" % (abs(latitude_dms[0]),
                                              abs(latitude_dms[1] +
                                                  (latitude_dms[2] / 60))))
            text.append("S" if self.latitude < 0 else "N")
            if mode == "dms":
                text.append(''', %03i°%02i'%02i"'''
                            % tuple(map(abs, longitude_dms)))
            else:
                text.append(", %03i°%05.2f'" % (abs(longitude_dms[0]),
                                                abs(longitude_dms[1] +
                                                    (longitude_dms[2] / 60))))
            text.append("W" if self.longitude < 0 else "E")
        elif mode == "locator":
            text.append(self.to_grid_locator())
        else:
            raise ValueError("Unknown mode type `%s'" % mode)

        return "".join(text)

    def __unicode__(self, mode="dd"):
        """
        Pretty printed Unicode location string

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

        :Parameters:
            mode : `str`
                Coordinate formatting system to use
        :rtype: `str`
        :return: Human readable Unicode representation of `Point` object
        :raise ValueError: Unknown value for `mode`
        """
        text = []
        if mode in ("dd", "locator"):
            text.append(self.__str__(mode=mode))
        elif mode in ("dm", "dms"):
            latitude_dms = utils.to_dms(self.latitude)
            longitude_dms = utils.to_dms(self.longitude)
            if mode == "dms":
                text.append('''%02i°%02i′%02i″'''
                            % tuple(map(abs, latitude_dms)))
            else:
                text.append("%02i°%05.2f′" % (abs(latitude_dms[0]),
                                              abs(latitude_dms[1] +
                                                  (latitude_dms[2] / 60))))
            text.append("S" if self.latitude < 0 else "N")
            if mode == "dms":
                text.append(''', %03i°%02i′%02i″'''
                            % tuple(map(abs, longitude_dms)))
            else:
                text.append(", %03i°%05.2f′" % (abs(longitude_dms[0]),
                                                abs(longitude_dms[1] +
                                                    (longitude_dms[2] / 60))))
            text.append("W" if self.longitude < 0 else "E")
        else:
            raise ValueError("Unknown mode type `%s'" % mode)

        return "".join(text)

    def __eq__(self, other, accuracy=None):
        """
        Compare `Point` objects for equality with optional accuracy amount

        >>> Point(52.015, -0.221) == Point(52.015, -0.221)
        True
        >>> Point(52.015, -0.221) == Point(52.6333, -2.5)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 168)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 170)
        True

        :Parameters:
            other : `Point` instance
                Object to test for equality against
            accuracy : `float` or `None`
                Objects are considered equal if within `accuracy`
                `format` units of each other
        :rtype: `bool`
        :return: True if objects are equal
        """
        if accuracy is None:
            return hash(self) == hash(other)
        else:
            return self.distance(other) < accuracy

    def __ne__(self, other, accuracy=None):
        """
        Compare `Point` objects for inequality with optional accuracy amount

        >>> Point(52.015, -0.221) != Point(52.015, -0.221)
        False
        >>> Point(52.015, -0.221) != Point(52.6333, -2.5)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 168)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 170)
        False

        :Parameters:
            other : `Point` instance
                Object to test for inequality against
            accuracy : `float` or `None`
                Objects are considered equal if within `accuracy`
                         `format` units
        :rtype: `bool`
        :return: True if objects are not equal
        """
        return not self.__eq__(other, accuracy)

    def __hash__(self):
        """
        Produce an object hash for equality checks

        This method returns the hash of the return value from the `__str__`
        method.  It guarantees equality for objects that have the same latitude
        and longitude.

        :see: `__str__`

        :rtype: `int`
        :return: Hash of string representation
        """
        return hash(repr(self))

    def to_grid_locator(self, precision="square"):
        """
        Calculate Maidenhead locator from latitude and longitude

        >>> Home = Point(52.015, -0.221)
        >>> Home.to_grid_locator("extsquare")
        'IO92va33'
        >>> Home.to_grid_locator("subsquare")
        'IO92va'
        >>> Home.to_grid_locator()
        'IO92'

        :Parameters:
            precision : `str`
                Precision with which generate locator string
        :rtype: `str`
        :return: Maidenhead locator for latitude and longitude
        """
        return utils.to_grid_locator(self.latitude, self.longitude, precision)

    def distance(self, other, method="haversine"):
        """
        Calculate the distance from self to other

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

        As a smoke test this check uses the example from Wikipedia's
        `Great-circle distance entry
        <http://en.wikipedia.org/wiki/Great-circle_distance>`__ of Nashville
        International Airport to Los Angeles International Airport, and is
        correct to within 2 kilometres of the calculation there.

        >>> to_loc = Point(33.9400, -118.4000)
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc)
        '2884 kM'
        >>> "%i mi" % Point(36.1200, -86.6700, "imperial").distance(to_loc)
        '1792 mi'
        >>> "%i nmi" % Point(36.1200, -86.6700, "nautical").distance(to_loc)
        '1557 nmi'
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc, method="sloc")
        '2884 kM'

        :Parameters:
            other : `Point` instance
                Location to calculate distance to
            method : `str`
                Method used to calculate distance
        :rtype: `float`
        :return: Distance between self and other in `self.format` type units
        :raise ValueError: Unknown value for `method`
        """
        longitude_difference = other.rad_longitude - self.rad_longitude
        latitude_difference = other.rad_latitude - self.rad_latitude

        if method == "haversine":
            temp = math.sin(latitude_difference / 2) ** 2 + \
                   math.cos(self.rad_latitude) * \
                   math.cos(other.rad_latitude) * \
                   math.sin(longitude_difference / 2) ** 2
            distance = 2 * utils.BODY_RADIUS * math.atan2(math.sqrt(temp),
                                                          math.sqrt(1-temp))
        elif method == "sloc":
            distance = math.acos(math.sin(self.rad_latitude) *
                                 math.sin(other.rad_latitude) +
                                 math.cos(self.rad_latitude) *
                                 math.cos(other.rad_latitude) *
                                 math.cos(longitude_difference)) * \
                       utils.BODY_RADIUS
        else:
            raise ValueError("Unknown method type `%s'" % method)

        if self.format == "imperial":
            return distance / utils.STATUTE_MILE
        elif self.format == "nautical":
            return distance / utils.NAUTICAL_MILE
        else:
            return distance

    def bearing(self, other, format="numeric"):
        """
        Calculate the initial bearing from self to other

        :note: Applying common plane Euclidean trigonometry to bearing
            calculations suggests to us that the bearing between point A to
            point B is equal to the inverse of the bearing from Point B to Point
            A, whereas spherical trigonometry is much more fun.  If the
            `bearing` method doesn't make sense to you when calculating return
            bearings there are plenty of resources on the web that explain
            spherical geometry.

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

        :Parameters:
            other : `Point` instance
                Location to calculate bearing to
            format : `str`
                Format of the bearing string to return
        :rtype: `float`
        :return: Initial bearing from self to other in degrees
        :raise ValueError: Unknown value for `format`
        :todo: Add Rhumb line calculation
        """

        longitude_difference = other.rad_longitude - self.rad_longitude

        y = math.sin(longitude_difference) * math.cos(other.rad_latitude)
        x = math.cos(self.rad_latitude) * math.sin(other.rad_latitude) - \
            math.sin(self.rad_latitude) * math.cos(other.rad_latitude) * \
            math.cos(longitude_difference)
        bearing = math.degrees(math.atan2(y, x))
        # Always return positive North-aligned bearing
        bearing = (bearing + 360) % 360
        if format == "numeric":
            return bearing
        elif format == "string":
            return utils.angle_to_name(bearing)
        else:
            raise ValueError("Unknown format type `%s'" % format)

    def midpoint(self, other):
        """
        Calculate the midpoint from self to other

        :see: `bearing`

        >>> Point(52.015, -0.221).midpoint(Point(52.6333, -2.5))
        Point(52.3296314054, -1.35253686056, 'metric', 'degrees', 0)
        >>> Point(36.1200, -86.6700).midpoint(Point(33.9400, -118.4000))
        Point(36.082394919, -102.752173705, 'metric', 'degrees', 0)

        :Parameters:
            other : `Point` instance
                Location to calculate midpoint to
        :rtype: `Point` instance
        :return: Great circle midpoint from self to other
        """
        longitude_difference = other.rad_longitude - self.rad_longitude
        y = math.sin(longitude_difference) * math.cos(other.rad_latitude)
        x = math.cos(other.rad_latitude) * math.cos(longitude_difference)
        latitude = math.atan2(math.sin(self.rad_latitude)
                              + math.sin(other.rad_latitude),
                              math.sqrt((math.cos(self.rad_latitude) + x)**2
                                        + y**2))
        longitude = self.rad_longitude \
                    + math.atan2(y, math.cos(self.rad_latitude) + x)

        return Point(latitude, longitude, angle="radians")

    def final_bearing(self, other, format="numeric"):
        """
        Calculate the final bearing from self to other

        :see: `bearing`

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

        :Parameters:
            other : `Point` instance
                Location to calculate final bearing to
            format : `str`
                Format of the bearing string to return
        :rtype: `float`
        :return: Final bearing from self to other in degrees
        :raise ValueError: Unknown value for `format`
        """
        final_bearing = (other.bearing(self) + 180) % 360
        if format == "numeric":
            return final_bearing
        elif format == "string":
            return utils.angle_to_name(final_bearing)
        else:
            raise ValueError("Unknown format type `%s'" % format)

    def destination(self, bearing, distance):
        """
        Calculate the destination from self given bearing and distance

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

        :Parameters:
            bearing : `float` or coercible to `float`
                Bearing from self
            distance : `float` or coercible to `float`
                Distance from self in `self.format` type units
        :rtype: `Point`
        :return: Location after travelling `distance` along `bearing`
        """
        bearing = math.radians(bearing)

        if self.format == "imperial":
            distance *= utils.STATUTE_MILE
        elif self.format == "nautical":
            distance *= utils.NAUTICAL_MILE

        angular_distance = distance / utils.BODY_RADIUS

        dest_latitude = math.asin(math.sin(self.rad_latitude) *
                                  math.cos(angular_distance) +
                                  math.cos(self.rad_latitude) *
                                  math.sin(angular_distance) *
                                  math.cos(bearing))
        dest_longitude = self.rad_longitude + \
                         math.atan2(math.sin(bearing) *
                                    math.sin(angular_distance) *
                                    math.cos(self.rad_latitude),
                                    math.cos(angular_distance) -
                                    math.sin(self.rad_latitude) *
                                    math.sin(dest_latitude))

        return Point(dest_latitude, dest_longitude, angle="radians")

    def sunrise(self, date=None, zenith=None):
        """
        Calculate the sunrise time for a `Point` object

        :see: `utils.sun_rise_set`

        >>> import datetime
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunrise(date)
        datetime.time(3, 40)
        >>> Point(52.6333, -2.5).sunrise(date)
        datetime.time(3, 45)
        >>> Point(36.1200, -86.6700).sunrise(date)
        datetime.time(10, 29)
        >>> Point(33.9400, -118.4000).sunrise(date)
        datetime.time(12, 41)

        :Parameters:
            date : ``datetime.date``
                Calculate rise or set for given date
            zenith : `None` or `str`
                Calculate rise/set events, or twilight times
        :rtype: ``datetime.datetime``
        :return: The time for the given event in the specified timezone
        """
        return utils.sun_rise_set(self.latitude, self.longitude, date, "rise",
                                  self.timezone, zenith)

    def sunset(self, date=None, zenith=None):
        """
        Calculate the sunset time for a `Point` object

        :see: `utils.sun_rise_set`

        >>> import datetime
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunset(date)
        datetime.time(20, 23)
        >>> Point(52.6333, -2.5).sunset(date)
        datetime.time(20, 36)
        >>> Point(36.1200, -86.6700).sunset(date)
        datetime.time(1, 5)
        >>> Point(33.9400, -118.4000).sunset(date)
        datetime.time(3, 6)

        :Parameters:
            date : ``datetime.date``
                Calculate rise or set for given date
            zenith : `None` or `str`
                Calculate rise/set events, or twilight times
        :rtype: ``datetime.datetime``
        :return: The time for the given event in the specified timezone
        """
        return utils.sun_rise_set(self.latitude, self.longitude, date, "set",
                                  self.timezone, zenith)

    def sun_events(self, date=None, zenith=None):
        """
        Calculate the sunrise time for a `Point` object

        :see: `utils.sun_rise_set`

        >>> import datetime
        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sun_events(date)
        (datetime.time(3, 40), datetime.time(20, 23))
        >>> Point(52.6333, -2.5).sun_events(date)
        (datetime.time(3, 45), datetime.time(20, 36))
        >>> Point(36.1200, -86.6700).sun_events(date)
        (datetime.time(10, 29), datetime.time(1, 5))
        >>> Point(33.9400, -118.4000).sun_events(date)
        (datetime.time(12, 41), datetime.time(3, 6))

        :Parameters:
            date : ``datetime.date``
                Calculate rise or set for given date
            zenith : `None` or `str`
                Calculate rise/set events, or twilight times
        :rtype: `tuple` of ``datetime.datetime``
        :return: The time for the given events in the specified timezone
        """
        return utils.sun_events(self.latitude, self.longitude, date,
                                self.timezone, zenith)

    # Inverse and forward are the common functions expected by people that are
    # familiar with geodesics.
    def inverse(self, other):
        """
        Calculate the inverse geodesic from self to other

        >>> "%i, %i" % Point(52.015, -0.221).inverse(Point(52.6333, -2.5))
        '294, 169'

        :Parameters:
            other : `Point` instance
                Location to calculate inverse geodesic to
        :rtype: `tuple` of `float` objects
        :return: Bearing and distance from self to other
        """
        return (self.bearing(other), self.distance(other))
    # Forward geodesic function maps directly to destination method
    forward = destination

