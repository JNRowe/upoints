#
"""point - Classes for working with locations on Earth."""
# Copyright © 2008-2021  James Rowe <jnrowe@gmail.com>
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

import math

from . import utils


def _manage_location(attr):
    """Build managed property interface.

    Args:
        attr (str): Property’s name

    Returns:
        property: Managed property interface
    """
    return property(
        lambda self: getattr(self, f'_{attr}'),
        lambda self, value: self._set_location(attr, value),
    )


def _dms_formatter(latitude, longitude, mode):
    """Generate a human readable DM/DMS location string.

    Args:
        latitude (float): Location’s latitude
        longitude (float): Location’s longitude
        mode (str): Coordinate formatting system to use
    """
    chars = ('°', '′', '″')

    latitude_dms = tuple(map(abs, utils.to_dms(latitude, mode)))
    longitude_dms = tuple(map(abs, utils.to_dms(longitude, mode)))
    text = []
    if mode == 'dms':
        text.append('%%02i%s%%02i%s%%02i%s' % chars % latitude_dms)
    else:
        text.append('%%02i%s%%05.2f%s' % chars[:2] % latitude_dms)
    text.append('S' if latitude < 0 else 'N')
    if mode == 'dms':
        text.append(', %%03i%s%%02i%s%%02i%s' % chars % longitude_dms)
    else:
        text.append(', %%03i%s%%05.2f%s' % chars[:2] % longitude_dms)
    text.append('W' if longitude < 0 else 'E')
    return text


class Point:
    """Simple class for representing a location on a sphere.

    .. versionadded:: 0.2.0
    """

    def __init__(
        self, latitude, longitude, units='metric', angle='degrees', timezone=0
    ):
        """Initialise a new ``Point`` object.

        Args:
            latitude (float, tuple or list): Location’s latitude
            longitude (float, tuple or list): Location’s longitude
            angle (str): Type for specified angles
            units (str): Units type to be used for distances
            timezone (int): Offset from UTC in minutes

        Raises:
            ValueError: Unknown value for ``angle``
            ValueError: Unknown value for ``units``
            ValueError: Invalid value for ``latitude`` or ``longitude``
        """
        super(Point, self).__init__()
        if angle in ('degrees', 'radians'):
            self._angle = angle
        else:
            raise ValueError(f'Unknown angle type {angle!r}')
        self._set_location('latitude', latitude)
        self._set_location('longitude', longitude)

        if units in ('imperial', 'metric', 'nautical'):
            self.units = units
        elif units == 'km':
            self.units = 'metric'
        elif units in ('US customary', 'sm'):
            self.units = 'imperial'
        elif units == 'nm':
            self.units = 'nautical'
        else:
            raise ValueError(f'Unknown units type {units!r}')
        self.timezone = timezone

    def _set_location(self, ltype, value):
        """Check supplied location data for validity, and update."""
        if self._angle == 'degrees':
            if isinstance(value, (tuple, list)):
                value = utils.to_dd(*value)
            setattr(self, '_%s' % ltype, float(value))
            setattr(self, '_rad_%s' % ltype, math.radians(float(value)))
        elif self._angle == 'radians':
            setattr(self, '_rad_%s' % ltype, float(value))
            setattr(self, '_%s' % ltype, math.degrees(float(value)))
        else:
            raise ValueError(f'Unknown angle type {self._angle!r}')
        if ltype == 'latitude' and not -90 <= self._latitude <= 90:
            raise ValueError(f'Invalid latitude value {value!r}')
        elif ltype == 'longitude' and not -180 <= self._longitude <= 180:
            raise ValueError(f'Invalid longitude value {value!r}')

    latitude = _manage_location('latitude')
    longitude = _manage_location('longitude')
    rad_latitude = _manage_location('rad_latitude')
    rad_longitude = _manage_location('rad_longitude')

    def __repr__(self):
        """Self-documenting string representation.

        Returnns:
            str: String to recreate ``Point`` object
        """
        return utils.repr_assist(self, {'angle': 'degrees'})

    def __str__(self):
        """Pretty printed location string.

        Returns:
            str: Human readable string representation of ``Point`` object
        """
        return format(self)

    def __unicode__(self):
        """Pretty printed Unicode location string.

        Returns:
            str: Human readable Unicode representation of ``Point`` object
        """
        return _dms_formatter(self, 'dd', True)

    def __format__(self, format_spec='dd'):
        """Extended pretty printing for location strings.

        Args:
            format_spec (str): Coordinate formatting system to use

        Returns:
            str: Human readable string representation of ``Point`` object

        Raises:
            ValueError: Unknown value for ``format_spec``
        """
        text = []
        if not format_spec:  # default format calls set format_spec to ''
            format_spec = 'dd'
        if format_spec == 'dd':
            text.append('S' if self.latitude < 0 else 'N')
            text.append('%06.3f°; ' % abs(self.latitude))
            text.append('W' if self.longitude < 0 else 'E')
            text.append('%07.3f°' % abs(self.longitude))
        elif format_spec in ('dm', 'dms'):
            text = _dms_formatter(self.latitude, self.longitude, format_spec)
        elif format_spec == 'locator':
            text.append(self.to_grid_locator())
        else:
            raise ValueError(f'Unknown format_spec {format_spec!r}')

        return ''.join(text)

    def __eq__(self, other, accuracy=None):
        """Compare ``Point`` objects for equality with optional accuracy amount.

        Args:
            other (Point): Object to test for equality against
            accuracy (float): Objects are considered equal if within
                ``accuracy`` ``units`` distance of each other

        Returns:
            bool: True if objects are equal within given bounds
        """
        if accuracy is None:
            return hash(self) == hash(other)
        else:
            return self.distance(other) < accuracy

    def __ne__(self, other, accuracy=None):
        """Compare ``Point`` objects for inequality with optional accuracy amount.

        Args:
            other (Point): Object to test for inequality against
            accuracy (float): Objects are considered equal if within
                ``accuracy`` ``units`` distance

        Returns:
            bool: True if objects are not equal within given bounds
        """
        return not self.__eq__(other, accuracy)

    def __hash__(self):
        """Produce an object hash for equality checks.

        This method returns the hash of the return value from the ``__str__``
        method.  It guarantees equality for objects that have the same latitude
        and longitude.

        See also:
            __str__

        Returns:
            int: Hash of string representation
        """
        return hash(repr(self))

    def to_grid_locator(self, precision='square'):
        """Calculate Maidenhead locator from latitude and longitude.

        Args:
            precision (str): Precision with which generate locator string

        Returns:
            str: Maidenhead locator for latitude and longitude
        """
        return utils.to_grid_locator(self.latitude, self.longitude, precision)

    def distance(self, other, method='haversine'):
        """Calculate the distance from self to other.

        As a smoke test this check uses the example from Wikipedia’s
        `Great-circle distance entry`_ of Nashville International Airport to
        Los Angeles International Airport, and is correct to within
        2 kilometres of the calculation there.

        Args:
            other (Point): Location to calculate distance to
            method (str): Method used to calculate distance

        Returns:
            float: Distance between self and other in ``units``

        Raises:
            ValueError: Unknown value for ``method``

        .. _Great-circle distance entry:
           http://en.wikipedia.org/wiki/Great-circle_distance
        """
        longitude_difference = other.rad_longitude - self.rad_longitude
        latitude_difference = other.rad_latitude - self.rad_latitude

        if method == 'haversine':
            temp = (
                math.sin(latitude_difference / 2) ** 2
                + math.cos(self.rad_latitude)
                * math.cos(other.rad_latitude)
                * math.sin(longitude_difference / 2) ** 2
            )
            distance = (
                2
                * utils.BODY_RADIUS
                * math.atan2(math.sqrt(temp), math.sqrt(1 - temp))
            )
        elif method == 'sloc':
            distance = (
                math.acos(
                    math.sin(self.rad_latitude) * math.sin(other.rad_latitude)
                    + math.cos(self.rad_latitude)
                    * math.cos(other.rad_latitude)
                    * math.cos(longitude_difference)
                )
                * utils.BODY_RADIUS
            )
        else:
            raise ValueError(f'Unknown method type {method!r}')

        if self.units == 'imperial':
            return distance / utils.STATUTE_MILE
        elif self.units == 'nautical':
            return distance / utils.NAUTICAL_MILE
        else:
            return distance

    def bearing(self, other, format='numeric'):
        """Calculate the initial bearing from self to other.

        Note:
           Applying common plane Euclidean trigonometry to bearing calculations
           suggests to us that the bearing between point A to point B is equal
           to the inverse of the bearing from Point B to Point A, whereas
           spherical trigonometry is much more fun.  If the ``bearing`` method
           doesn't make sense to you when calculating return bearings there are
           plenty of resources on the web that explain spherical geometry.

        .. todo:: Add Rhumb line calculation

        Args:
            other (Point): Location to calculate bearing to
            format (str): Format of the bearing string to return

        Returns:
            float: Initial bearing from self to other in degrees

        Raises:
            ValueError: Unknown value for ``format``
        """
        longitude_difference = other.rad_longitude - self.rad_longitude

        y = math.sin(longitude_difference) * math.cos(other.rad_latitude)
        x = math.cos(self.rad_latitude) * math.sin(
            other.rad_latitude
        ) - math.sin(self.rad_latitude) * math.cos(
            other.rad_latitude
        ) * math.cos(
            longitude_difference
        )
        bearing = math.degrees(math.atan2(y, x))
        # Always return positive North-aligned bearing
        bearing = (bearing + 360) % 360
        if format == 'numeric':
            return bearing
        elif format == 'string':
            return utils.angle_to_name(bearing)
        else:
            raise ValueError(f'Unknown format type {format!r}')

    def midpoint(self, other):
        """Calculate the midpoint from self to other.

        See also:
            bearing

        Args:
            other (Point): Location to calculate midpoint to

        Returns:
            Point: Great circle midpoint from self to other
        """
        longitude_difference = other.rad_longitude - self.rad_longitude
        y = math.sin(longitude_difference) * math.cos(other.rad_latitude)
        x = math.cos(other.rad_latitude) * math.cos(longitude_difference)
        latitude = math.atan2(
            math.sin(self.rad_latitude) + math.sin(other.rad_latitude),
            math.sqrt((math.cos(self.rad_latitude) + x) ** 2 + y ** 2),
        )
        longitude = self.rad_longitude + math.atan2(
            y, math.cos(self.rad_latitude) + x
        )

        return Point(latitude, longitude, angle='radians')

    def final_bearing(self, other, format='numeric'):
        """Calculate the final bearing from self to other.

        See also:
           bearing

        Args:
            other (Point): Location to calculate final bearing to
            format (str): Format of the bearing string to return

        Returns:
            float: Final bearing from self to other in degrees

        Raises:
            ValueError: Unknown value for ``format``
        """
        final_bearing = (other.bearing(self) + 180) % 360
        if format == 'numeric':
            return final_bearing
        elif format == 'string':
            return utils.angle_to_name(final_bearing)
        else:
            raise ValueError(f'Unknown format type {format!r}')

    def destination(self, bearing, distance):
        """Calculate the destination from self given bearing and distance.

        Args:
            bearing (float): Bearing from self
            distance (float): Distance from self in ``self.units``

        Returns:
            Point: Location after travelling ``distance`` along ``bearing``
        """
        bearing = math.radians(bearing)

        if self.units == 'imperial':
            distance *= utils.STATUTE_MILE
        elif self.units == 'nautical':
            distance *= utils.NAUTICAL_MILE

        angular_distance = distance / utils.BODY_RADIUS

        dest_latitude = math.asin(
            math.sin(self.rad_latitude) * math.cos(angular_distance)
            + math.cos(self.rad_latitude)
            * math.sin(angular_distance)
            * math.cos(bearing)
        )
        dest_longitude = self.rad_longitude + math.atan2(
            math.sin(bearing)
            * math.sin(angular_distance)
            * math.cos(self.rad_latitude),
            math.cos(angular_distance)
            - math.sin(self.rad_latitude) * math.sin(dest_latitude),
        )

        return Point(dest_latitude, dest_longitude, angle='radians')

    def sunrise(self, date=None, zenith=None):
        """Calculate the sunrise time for a ``Point`` object.

        See also:
           utils.sun_rise_set

        Args:
            date (datetime.date): Calculate rise or set for given date
            zenith (str): Calculate rise/set events, or twilight times

        Returns:
            datetime.datetime: The time for the given event in the specified
                timezone
        """
        return utils.sun_rise_set(
            self.latitude, self.longitude, date, 'rise', self.timezone, zenith
        )

    def sunset(self, date=None, zenith=None):
        """Calculate the sunset time for a ``Point`` object.

        See also:
           utils.sun_rise_set

        Args:
            date (datetime.date): Calculate rise or set for given date
            zenith (str): Calculate rise/set events, or twilight times

        Returns:
            datetime.datetime: The time for the given event in the specified
                timezone
        """
        return utils.sun_rise_set(
            self.latitude, self.longitude, date, 'set', self.timezone, zenith
        )

    def sun_events(self, date=None, zenith=None):
        """Calculate the sunrise time for a ``Point`` object.

        See also:
           utils.sun_rise_set

        Args:
            date (datetime.date): Calculate rise or set for given date
            zenith (str): Calculate rise/set events, or twilight times

        Returns:
            tuple of datetime.datetime: The time for the given events in the
                specified timezone
        """
        return utils.sun_events(
            self.latitude, self.longitude, date, self.timezone, zenith
        )

    # Inverse and forward are the common functions expected by people that are
    # familiar with geodesics.
    def inverse(self, other):
        """Calculate the inverse geodesic from self to other.

        Args:
            other (Point): Location to calculate inverse geodesic to

        Returns:
            tuple of float objects: Bearing and distance from self to other
        """
        return (self.bearing(other), self.distance(other))

    # Forward geodesic function maps directly to destination method
    forward = destination


class TimedPoint(Point):
    """Class for representing a location with an associated time.

    .. versionadded:: 0.12.0
    """

    def __init__(
        self,
        latitude,
        longitude,
        units='metric',
        angle='degrees',
        timezone=0,
        time=None,
    ):
        """Initialise a new ``TimedPoint`` object.

        Args:
            latitude (float, tuple or list): Location’s latitude
            longitude (float, tuple or list): Location’s longitude
            angle (str): Type for specified angles
            units (str): Units type to be used for distances
            timezone (int): Offset from UTC in minutes
            time (datetime.datetime): Time associated with the location
        """
        super(TimedPoint, self).__init__(
            latitude, longitude, units, angle, timezone
        )
        self.time = time


class Points(list):
    """Class for representing a group of :class:`Point` objects.

    .. versionadded:: 0.2.0
    """

    def __init__(self, points=None, parse=False, units='metric'):
        """Initialise a new ``Points`` object.

        Args:
            points (list of Point): :class:`Point` objects to wrap
            parse (bool): Whether to attempt import of ``points``
            units (str): Unit type to be used for distances when parsing string
                locations
        """
        super(Points, self).__init__()
        self._parse = parse
        self.units = units
        if points:
            if parse:
                self.import_locations(points)
            else:
                if not all(x for x in points if isinstance(x, Point)):
                    raise TypeError(
                        'All `points` elements must be an '
                        'instance of the `Point` class'
                    )
                self.extend(points)

    def __repr__(self):
        """Self-documenting string representation.

        Returns:
            str: String to recreate ``Points`` object
        """
        return utils.repr_assist(self, {'points': self[:]})

    def import_locations(self, locations):
        """Import locations from arguments.

        Args:
            locations (list of str or tuple): Location identifiers
        """
        for location in locations:
            data = utils.parse_location(location)
            if data:
                latitude, longitude = data
            else:
                latitude, longitude = utils.from_grid_locator(location)
            self.append(Point(latitude, longitude, self.units))

    def distance(self, method='haversine'):
        """Calculate distances between locations.

        Args:
            method (str): Method used to calculate distance

        Returns:
            list of float: Distance between points in series
        """
        if not len(self) > 1:
            raise RuntimeError('More than one location is required')
        return (
            self[i].distance(self[i + 1], method) for i in range(len(self) - 1)
        )

    def bearing(self, format='numeric'):
        """Calculate bearing between locations.

        Args:
            format (str): Format of the bearing string to return

        Returns:
            list of float: Bearing between points in series
        """
        if not len(self) > 1:
            raise RuntimeError('More than one location is required')
        return (
            self[i].bearing(self[i + 1], format) for i in range(len(self) - 1)
        )

    def final_bearing(self, format='numeric'):
        """Calculate final bearing between locations.

        Args:
            format (str): Format of the bearing string to return

        Returns:
            list of float: Bearing between points in series
        """
        if len(self) == 1:
            raise RuntimeError('More than one location is required')
        return (
            self[i].final_bearing(self[i + 1], format)
            for i in range(len(self) - 1)
        )

    def inverse(self):
        """Calculate the inverse geodesic between locations.

        Returns:
            list of 2-tuple of float: Bearing and distance between points in
                series
        """
        return (
            (self[i].bearing(self[i + 1]), self[i].distance(self[i + 1]))
            for i in range(len(self) - 1)
        )

    def midpoint(self):
        """Calculate the midpoint between locations.

        Returns:
            list of Point: Midpoint between points in series
        """
        return (self[i].midpoint(self[i + 1]) for i in range(len(self) - 1))

    def range(self, location, distance):
        """Test whether locations are within a given range of ``location``.

        Args:
            location (Point): Location to test range against
            distance (float): Distance to test location is within

        Returns:
            list of Point: Points within range of the specified location
        """
        return (x for x in self if location.__eq__(x, distance))

    def destination(self, bearing, distance):
        """Calculate destination locations for given distance and bearings.

        Args:
            bearing (float): Bearing to move on in degrees
            distance (float): Distance in kilometres

        Returns:
            list of Point: Points shifted by ``distance`` and ``bearing``
        """
        return (x.destination(bearing, distance) for x in self)

    forward = destination

    def sunrise(self, date=None, zenith=None):
        """Calculate sunrise times for locations.

        Args:
            date (datetime.date): Calculate sunrise for given date
            zenith (str): Calculate sunrise events, or end of twilight

        Returns:
            list of datetime.datetime: The time for the sunrise for each point
        """
        return (x.sunrise(date, zenith) for x in self)

    def sunset(self, date=None, zenith=None):
        """Calculate sunset times for locations.

        Args:
            date (datetime.date): Calculate sunset for given date
            zenith (str): Calculate sunset events, or start of twilight

        Returns:
            list of datetime.datetime: The time for the sunset for each point
        """
        return (x.sunset(date, zenith) for x in self)

    def sun_events(self, date=None, zenith=None):
        """Calculate sunrise/sunset times for locations.

        Args:
            date (datetime.date): Calculate rise or set for given date
            zenith (str): Calculate rise/set events, or twilight times

        Returns:
            list of 2-tuple of datetime.datetime: The time for the sunrise and
                sunset events for each point
        """
        return (x.sun_events(date, zenith) for x in self)

    def to_grid_locator(self, precision='square'):
        """Calculate Maidenhead locator for locations.

        Args:
            precision (str): Precision with which generate locator string

        Returns:
            list of str: Maidenhead locator for each point
        """
        return (x.to_grid_locator(precision) for x in self)


class TimedPoints(Points):
    def speed(self):
        """Calculate speed between :class:`Points`.

        Returns:
            list of float: Speed between :class:`Point` elements in km/h
        """
        if not len(self) > 1:
            raise RuntimeError('More than one location is required')
        try:
            times = [i.time for i in self]
        except AttributeError:
            raise NotImplementedError(
                'Not all Point objects include time ' 'attribute'
            )

        return (
            distance / ((times[i + 1] - times[i]).seconds / 3600)
            for i, distance in enumerate(self.distance())
        )


class KeyedPoints(dict):
    """Class for representing a keyed group of :class:`Point` objects.

    .. versionadded:: 0.2.0
    """

    def __init__(self, points=None, parse=False, units='metric'):
        """Initialise a new ``KeyedPoints`` object.

        Args:
            points (dict of Point): :class:`Point` objects to wrap
            points (bool): Whether to attempt import of ``points``
            units (str): Unit type to be used for distances when parsing string
                locations
        """
        super(KeyedPoints, self).__init__()
        self._parse = parse
        self.units = units
        if points:
            if parse:
                self.import_locations(points)
            else:
                if not all(x for x in points.values() if isinstance(x, Point)):
                    raise TypeError(
                        'All `points` element’s values must be an '
                        'instance of the `Point` class'
                    )
                self.update(points)

    def __repr__(self):
        """Self-documenting string representation.

        Returns:
            str: String to recreate ``KeyedPoints`` object
        """
        return utils.repr_assist(self, {'points': dict(self.items())})

    def import_locations(self, locations):
        """Import locations from arguments.

        Args:
            locations (list of 2-tuple of str): Identifiers and locations
        """
        for identifier, location in locations:
            data = utils.parse_location(location)
            if data:
                latitude, longitude = data
            else:
                latitude, longitude = utils.from_grid_locator(location)
            self[identifier] = Point(latitude, longitude, self.units)

    def distance(self, order, method='haversine'):
        """Calculate distances between locations.

        Args:
            order (list): Order to process elements in
            method (str): Method used to calculate distance

        Returns:
            list of float: Distance between points in ``order``
        """
        if not len(self) > 1:
            raise RuntimeError('More than one location is required')
        return (
            self[order[i]].distance(self[order[i + 1]], method)
            for i in range(len(order) - 1)
        )

    def bearing(self, order, format='numeric'):
        """Calculate bearing between locations.

        Args:
            order (list): Order to process elements in
            format (str): Format of the bearing string to return

        Returns:
            list of float: Bearing between points in series
        """
        if not len(self) > 1:
            raise RuntimeError('More than one location is required')
        return (
            self[order[i]].bearing(self[order[i + 1]], format)
            for i in range(len(order) - 1)
        )

    def final_bearing(self, order, format='numeric'):
        """Calculate final bearing between locations.

        Args:
            order (list): Order to process elements in
            format (str): Format of the bearing string to return

        Returns:
            list of float: Bearing between points in series
        """
        if len(self) == 1:
            raise RuntimeError('More than one location is required')
        return (
            self[order[i]].final_bearing(self[order[i + 1]], format)
            for i in range(len(order) - 1)
        )

    def inverse(self, order):
        """Calculate the inverse geodesic between locations.

        Args:
            order (list): Order to process elements in

        Returns:
            list of 2-tuple of float: Bearing and distance between points in
                series
        """
        return (
            (
                self[order[i]].bearing(self[order[i + 1]]),
                self[order[i]].distance(self[order[i + 1]]),
            )
            for i in range(len(order) - 1)
        )

    def midpoint(self, order):
        """Calculate the midpoint between locations.

        Args:
            order (list): Order to process elements in

        Returns:
            list of Point: Midpoint between points in series
        """
        return (
            self[order[i]].midpoint(self[order[i + 1]])
            for i in range(len(order) - 1)
        )

    def range(self, location, distance):
        """Test whether locations are within a given range of the first.

        Args:
            location (Point): Location to test range against
            distance (float): Distance to test location is within

        Returns:
            list of Point: Objects within specified range
        """
        return (x for x in self.items() if location.__eq__(x[1], distance))

    def destination(self, bearing, distance):
        """Calculate destination locations for given distance and bearings.

        Args:
            bearing (float): Bearing to move on in degrees
            distance (float): Distance in kilometres
        """
        return (
            (x[0], x[1].destination(bearing, distance)) for x in self.items()
        )

    forward = destination

    def sunrise(self, date=None, zenith=None):
        """Calculate sunrise times for locations.

        Args:
            date (datetime.date): Calculate sunrise for given date
            zenith (str): Calculate sunrise events, or end of twilight

        Returns:
            list of datetime.datetime: The time for the sunrise for each point
        """
        return ((x[0], x[1].sunrise(date, zenith)) for x in self.items())

    def sunset(self, date=None, zenith=None):
        """Calculate sunset times for locations.

        Args:
            date (datetime.date): Calculate sunset for given date
            zenith (str): Calculate sunset events, or start of twilight

        Returns:
            list of datetime.datetime: The time for the sunset for each point
        """
        return ((x[0], x[1].sunset(date, zenith)) for x in self.items())

    def sun_events(self, date=None, zenith=None):
        """Calculate sunrise/sunset times for locations.

        Args:
            date (datetime.date): Calculate rise or set for given date
            zenith (str): Calculate rise/set events, or twilight times

        Returns:
            list of 2-tuple of datetime.datetime: The time for the sunrise and
                sunset events for each point
        """
        return ((x[0], x[1].sun_events(date, zenith)) for x in self.items())

    def to_grid_locator(self, precision='square'):
        """Calculate Maidenhead locator for locations.

        Args:
            precision (str): Precision with which generate locator string

        Returns:
            list of str: Maidenhead locator for each point
        """
        return ((x[0], x[1].to_grid_locator(precision)) for x in self.items())
