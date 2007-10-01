#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""Point - Class for working with locations on Earth"""
# Copyright (C) 2007  James Rowe
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

import datetime
import math

from earth_distance import utils

class Point(object):
    """
    Simple class for representing a location on a sphere

    @ivar format: Type of distance units to be used
    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar rad_latitude: Location's latitude in radians
    @ivar rad_longitude: Location's longitude in radians
    @ivar timezone: Location's offset from UTC in minutes
    """

    __slots__ = ('format', 'latitude', 'longitude', 'rad_latitude',
                 'rad_longitude', 'timezone')

    def __init__(self, latitude, longitude, format="metric",
                 angle="degrees", timezone=0):
        """
        Initialise a new C{Point} object

        >>> Home = Point(52.015, -0.221)
        >>> Home = Point(52.015, -0.221, timezone=60) # BST
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

        @type latitude: C{float} or coercible to C{float}, C{tuple} or C{list}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}, C{tuple} or C{list}
        @param longitude: Location's longitude
        @type angle: C{str}
        @param angle: Format for specified angles
        @type format: C{str}
        @param format: Unit type to be used for distances
        @type timezone: C{int}
        @param timezone: Offset from UTC in minutes
        @raise ValueError: Unknown value for C{angle}
        @raise ValueError: Unknown value for C{format}
        @raise ValueError: Invalid value for C{latitude} or C{longitude}
        """
        if angle == "degrees":
            if isinstance(latitude, (tuple, list)):
                latitude = utils.to_dd(*latitude)
            if isinstance(longitude, (tuple, list)):
                longitude = utils.to_dd(*longitude)
            self.latitude = float(latitude)
            self.longitude = float(longitude)
            self.rad_latitude = math.radians(self.latitude)
            self.rad_longitude = math.radians(self.longitude)
        elif angle == "radians":
            self.rad_latitude = float(latitude)
            self.rad_longitude = float(longitude)
            self.latitude = math.degrees(self.rad_latitude)
            self.longitude = math.degrees(self.rad_longitude)
        else:
            raise ValueError("Unknown angle type `%s'" % angle)
        if not -90 <= self.latitude <= 90:
            raise ValueError("Invalid latitude value `%f'" % latitude)
        if not -180 <= self.longitude <= 180:
            raise ValueError("Invalid longitude value `%f'" % longitude)

        if format in ("imperial", "metric", "nautical"):
            self.format = format
        elif format == "US customary":
            self.format = "imperial"
        else:
            raise ValueError("Unknown unit type `%s'" % format)
        self.timezone = timezone

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Point(52.015, -0.221)
        Point(52.015000, -0.221000, 'metric', 0)

        @rtype: C{str}
        @return: String to recreate Point object
        """
        return 'Point(%f, %f, %s, %i)' % (self.latitude, self.longitude,
                                          repr(self.format), self.timezone)

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        >>> print(Point(52.015, -0.221))
        N52.015°; W000.221°
        >>> print(Point(52.015, -0.221).__str__(mode="dm"))
        52°00.90'N, 000°13.25'W
        >>> print(Point(52.015, -0.221).__str__(mode="dms"))
        52°00'54"N, 000°13'15"W
        >>> print(Point(33.9400, -118.4000).__str__(mode="dms"))
        33°56'23"N, 118°24'00"W
        >>> print(Point(52.015, -0.221).__str__(mode="locator"))
        IO92

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of Point object
        @raise ValueError: Unknown value for C{mode}
        """
        if mode == "dd":
            text = "S" if self.latitude < 0 else "N"
            text += "%06.3f°; " % abs(self.latitude)
            text += "W" if self.longitude < 0 else "E"
            text += "%07.3f°" % abs(self.longitude)
        elif mode in ("dm", "dms"):
            latitude_dms = utils.to_dms(self.latitude)
            longitude_dms = utils.to_dms(self.longitude)
            if mode == "dms":
                text = '''%02i°%02i'%02i"''' % \
                       tuple([abs(i) for i in latitude_dms])
            else:
                text = "%02i°%05.2f'" % (abs(latitude_dms[0]),
                                         abs(latitude_dms[1] +
                                             (latitude_dms[2] / 60)))
            text += "S" if self.latitude < 0 else "N"
            if mode == "dms":
                text += ''', %03i°%02i'%02i"''' % \
                        tuple([abs(i) for i in longitude_dms])
            else:
                text += ", %03i°%05.2f'" % (abs(longitude_dms[0]),
                                            abs(longitude_dms[1] +
                                                (longitude_dms[2] / 60)))
            text += "W" if self.longitude < 0 else "E"
        elif mode == "locator":
            text = utils.to_grid_locator(self.latitude, self.longitude)
        else:
            raise ValueError("Unknown mode type `%s'" % mode)

        return text

    def __eq__(self, other, accuracy=None):
        """
        Compare C{Point} objects for equality with optional accuracy amount

        >>> Point(52.015, -0.221) == Point(52.015, -0.221)
        True
        >>> Point(52.015, -0.221) == Point(52.6333, -2.5)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 168)
        False
        >>> Point(52.015, -0.221).__eq__(Point(52.6333, -2.5), 170)
        True

        @type other: C{Point} instance
        @param other: Object to test for equality against
        @type accuracy: C{float} or C{None}
        @param accuracy: Objects are considered equal if within C{accuracy}
                         C{format} units of each other
        @rtype: C{bool}
        @return: True if objects are equal
        """
        if accuracy == None:
            return hash(self) == hash(other)
        else:
            return self.distance(other) < accuracy

    def __ne__(self, other, accuracy=None):
        """
        Compare C{Point} objects for inequality with optional accuracy amount

        >>> Point(52.015, -0.221) != Point(52.015, -0.221)
        False
        >>> Point(52.015, -0.221) != Point(52.6333, -2.5)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 168)
        True
        >>> Point(52.015, -0.221).__ne__(Point(52.6333, -2.5), 170)
        False

        @type other: C{Point} instance
        @param other: Object to test for inequality against
        @type accuracy: C{float} or C{None}
        @param accuracy: Objects are considered equal if within C{accuracy}
                         C{format} units
        @rtype: C{bool}
        @return: True if objects are not equal
        """
        return not self.__eq__(other, accuracy)

    def __hash__(self):
        """
        Produce an object hash for equality checks

        This method returns the hash of the return value from the C{__str__}
        method.  It guarantees equality for objects that have the same latitude
        and longitude.

        @see: C{__str__}

        @rtype: C{int}
        @return: Hash of string representation
        """
        return hash(self.__str__())

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

        @type precision: C{str}
        @param precision: Precision with which generate locator string
        @rtype: C{str}
        @return: Maidenhead locator for latitude and longitude
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

        As a smoke test this check uses the example from Wikipedia's
        U{Great-circle distance entry
        <http://en.wikipedia.org/wiki/Great-circle_distance>} of Nashville
        International Airport to Los Angeles International Airport, and is
        correct to within 2 kilometres of the calculation there.

        >>> to_loc = Point(33.9400, -118.4000)
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc)
        '2886 kM'
        >>> "%i mi" % Point(36.1200, -86.6700, "imperial").distance(to_loc)
        '1794 mi'
        >>> "%i nmi" % Point(36.1200, -86.6700, "nautical").distance(to_loc)
        '1558 nmi'
        >>> "%i kM" % Point(36.1200, -86.6700).distance(to_loc, method="sloc")
        '2886 kM'

        @type other: C{Point} instance
        @param other: Location to calculate distance to
        @type method: C{str}
        @param method: Method used to calculate distance
        @rtype: C{float}
        @return: Distance between self and other in C{self.format} type units
        @raise ValueError: Unknown value for C{method}
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

    def bearing(self, other):
        """
        Calculate the initial bearing from self to other

        @note: Applying common plane Euclidean trigonometry to bearing
        calculations suggests to us that the bearing between point A to point
        B is equal to the inverse of the bearing from Point B to Point A,
        whereas spherical trigonometry is much more fun.  If the C{bearing}
        method doesn't make sense to you when calculating return bearings there
        are plenty of resources on the web that explain spherical geometry.

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

        @type other: C{Point} instance
        @param other: Location to calculate bearing to
        @rtype: C{float}
        @return: Initial bearing from self to other in degrees
        @todo: Add Rhumb line calculation
        """

        longitude_difference = other.rad_longitude - self.rad_longitude

        y = math.sin(longitude_difference) * math.cos(other.rad_latitude)
        x = math.cos(self.rad_latitude) * math.sin(other.rad_latitude) - \
            math.sin(self.rad_latitude) * math.cos(other.rad_latitude) * \
            math.cos(longitude_difference)
        bearing = math.degrees(math.atan2(y, x))
        # Always return positive North-aligned bearing
        return (bearing + 360) % 360

    def final_bearing(self, other):
        """
        Calculate the final bearing from self to other

        @see: C{bearing}

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

        @type other: C{Point} instance
        @param other: Location to calculate final bearing to
        @rtype: C{float}
        @return: Final bearing from self to other in degrees
        """
        return (other.bearing(self) + 180) % 360

    def destination(self, bearing, distance):
        """
        Calculate the destination from self given bearing and distance

        >>> Point(52.015, -0.221).destination(294, 169)
        Point(52.611188, -2.507554, 'metric', 0)
        >>> Home = Point(52.015, -0.221, "imperial")
        >>> Home.destination(294, 169 / utils.STATUTE_MILE)
        Point(52.611188, -2.507554, 'metric', 0)
        >>> Home = Point(52.015, -0.221, "nautical")
        >>> Home.destination(294, 169 / utils.NAUTICAL_MILE)
        Point(52.611188, -2.507554, 'metric', 0)
        >>> Point(36.1200, -86.6700).destination(274, 2885)
        Point(33.692355, -118.303507, 'metric', 0)

        @type bearing: C{float} or coercible to C{float}
        @param bearing: Bearing from self
        @type distance: C{float} or coercible to C{float}
        @param distance: Distance from self in C{self.format} type units
        @rtype: C{Point}
        @return: Location after travelling C{distance} along C{bearing}
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

        return Point(math.degrees(dest_latitude), math.degrees(dest_longitude))

    def sunrise(self, date=datetime.date.today(), zenith=None):
        """
        Calculate the sunrise time for self

        @see: C{utils.sun_rise_set}

        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunrise(date)
        datetime.time(3, 40)
        >>> Point(52.6333, -2.5).sunrise(date)
        datetime.time(3, 45)
        >>> Point(36.1200, -86.6700).sunrise(date)
        datetime.time(10, 29)
        >>> Point(33.9400, -118.4000).sunrise(date)
        datetime.time(12, 41)

        @type date: C{datetime.date}
        @param date: Calculate rise or set for given date
        @type zenith: C{None} or C{str}
        @param zenith: Calculate rise/set events, or twilight times
        @rtype: C{datetime.datetime}
        @return: The time for the given event in the specified timezone
        """
        return utils.sun_rise_set(self.latitude, self.longitude, date, "rise",
                                  self.timezone, zenith)

    def sunset(self, date=datetime.date.today(), zenith=None):
        """
        Calculate the sunrise time for self

        @see: C{utils.sun_rise_set}

        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sunset(date)
        datetime.time(20, 23)
        >>> Point(52.6333, -2.5).sunset(date)
        datetime.time(20, 36)
        >>> Point(36.1200, -86.6700).sunset(date)
        datetime.time(1, 5)
        >>> Point(33.9400, -118.4000).sunset(date)
        datetime.time(3, 6)

        @type date: C{datetime.date}
        @param date: Calculate rise or set for given date
        @type zenith: C{None} or C{str}
        @param zenith: Calculate rise/set events, or twilight times
        @rtype: C{datetime.datetime}
        @return: The time for the given event in the specified timezone
        """
        return utils.sun_rise_set(self.latitude, self.longitude, date, "set",
                                  self.timezone, zenith)

    def sun_events(self, date=datetime.date.today(), zenith=None):
        """
        Calculate the sunrise time for self

        @see: C{utils.sun_rise_set}

        >>> date = datetime.date(2007, 6, 15)
        >>> Point(52.015, -0.221).sun_events(date)
        (datetime.time(3, 40), datetime.time(20, 23))
        >>> Point(52.6333, -2.5).sun_events(date)
        (datetime.time(3, 45), datetime.time(20, 36))
        >>> Point(36.1200, -86.6700).sun_events(date)
        (datetime.time(10, 29), datetime.time(1, 5))
        >>> Point(33.9400, -118.4000).sun_events(date)
        (datetime.time(12, 41), datetime.time(3, 6))

        @type date: C{datetime.date}
        @param date: Calculate rise or set for given date
        @type zenith: C{None} or C{str}
        @param zenith: Calculate rise/set events, or twilight times
        @rtype: C{tuple} of C{datetime.datetime}
        @return: The time for the given events in the specified timezone
        """
        return utils.sun_events(self.latitude, self.longitude, date,
                                self.timezone, zenith)

if __name__ == '__main__':
    utils.run_tests()

