#
# coding=utf-8
"""utils - Support code for :mod:upoints"""
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

from __future__ import division

#: Address for use in messages
__bug_report__ = 'James Rowe <jnrowe@gmail.com>'

import csv
import datetime
import inspect
import math
import re

from functools import reduce

from lxml import etree
from lxml import objectify as _objectify

from operator import add

from upoints.compat import (basestring, mangle_repr_type)


#: Body radii of various solar system objects
BODIES = {
    # Body radii in kilometres
    'Sun': 696000,

    # Terrestrial inner planets
    'Mercury': 2440,
    'Venus': 6052,
    'Earth': 6367,
    'Mars': 3390,

    # Gas giant outer planets
    'Jupiter': 69911,
    'Saturn': 58232,
    'Uranus': 25362,
    'Neptune': 24622,

    # only satellite to be added
    'Moon': 1738,

    # dwarf planets may be added
    'Pluto': 1153,
    'Ceres': 475,
    'Eris': 1200,
}

#: Default body radius to use for calculations
BODY_RADIUS = BODIES['Earth']
#: Number of kilometres per nautical mile
NAUTICAL_MILE = 1.852
#: Number of kilometres per statute mile
STATUTE_MILE = 1.609

#: Maidenhead locator constants
LONGITUDE_FIELD = 20
LATITUDE_FIELD = 10
LONGITUDE_SQUARE = LONGITUDE_FIELD / 10
LATITUDE_SQUARE = LATITUDE_FIELD / 10
LONGITUDE_SUBSQUARE = LONGITUDE_SQUARE / 24
LATITUDE_SUBSQUARE = LATITUDE_SQUARE / 24
LONGITUDE_EXTSQUARE = LONGITUDE_SUBSQUARE / 10
LATITUDE_EXTSQUARE = LATITUDE_SUBSQUARE / 10


class FileFormatError(ValueError):

    """Error object for data parsing error.

    .. versionadded:: 0.3.0

    """

    def __init__(self, site=None):
        """Initialise a new ``FileFormatError`` object.

        :param str site: Remote site name to display in error message

        """
        super(FileFormatError, self).__init__()
        self.site = site

    def __str__(self):
        """Pretty printed error string.

        :rtype: ``str``
        :return: Human readable error string

        """
        if self.site:
            return ("Incorrect data format, if you're using a file downloaded "
                    'from %s please report this to %s' % (self.site,
                                                          __bug_report__))
        else:
            return 'Unsupported data format.'


#{ Implementation utilities
def value_or_empty(value):
    """Return an empty string for display when value is ``None``.

    :param str value: Value to prepare for display
    :rtype: ``str``
    :return: String representation of ``value``

    """
    return value if value else ''


def repr_assist(obj, remap=None):
    """Helper function to simplify ``__repr__`` methods.

    :param obj: Object to pull argument values for
    :param dict remap: Argument pairs to remap before output
    :rtype: ``str``
    :return: Self-documenting representation of ``value``

    """
    if not remap:
        remap = {}
    data = []
    for arg in inspect.getargspec(getattr(obj.__class__, '__init__'))[0]:
        if arg == 'self':
            continue
        elif arg in remap:
            value = remap[arg]
        else:
            try:
                value = getattr(obj, arg)
            except AttributeError:
                value = getattr(obj, '_%s' % arg)
        if isinstance(value, (type(None), list, basestring, datetime.date,
                              datetime.time)):
            data.append(repr(value))
        else:
            data.append(str(value))
    return u"%s(%s)" % (obj.__class__.__name__, u', '.join(data))


def prepare_read(data, method='readlines', mode='r'):
    """Prepare various input types for parsing.

    :type data: ``file`` like object, ``list``, ``str``
    :param data: Data to read
    :param str method: Method to process data with
    :param str mode: Custom mode to process with, if data is a file
    :rtype: ``list``
    :return: List suitable for parsing
    :raise TypeError: Invalid value for data

    """
    if hasattr(data, 'readlines'):
        data = getattr(data, method)()
    elif isinstance(data, list):
        if method == 'read':
            return ''.join(data)
    elif isinstance(data, basestring):
        data = getattr(open(data, mode), method)()
    else:
        raise TypeError('Unable to handle data of type %r' % type(data))
    return data


def prepare_csv_read(data, field_names, *args, **kwargs):
    """Prepare various input types for CSV parsing.

    :type data: ``file`` like object, ``list``, ``str``
    :param data: Data to read
    :type field_names: ``tuple`` of ``str``
    :param field_names: Ordered names to assign to fields
    :rtype: `csv.DictReader`
    :return: CSV reader suitable for parsing
    :raise TypeError: Invalid value for data

    """
    if hasattr(data, 'readlines') or isinstance(data, list):
        pass
    elif isinstance(data, basestring):
        data = open(data)
    else:
        raise TypeError('Unable to handle data of type %r' % type(data))
    return csv.DictReader(data, field_names, *args, **kwargs)


def prepare_xml_read(data, objectify=False):
    """Prepare various input types for XML parsing.

    :type data: ``file`` like object, ``list``, ``str``
    :param data: Data to read
    :type objectify: bool
    :param objectify: Parse using lxml's objectify data binding
    :rtype: :class:`etree.ElementTree`
    :return: Tree suitable for parsing
    :raise TypeError: Invalid value for data

    """
    mod = _objectify if objectify else etree
    if hasattr(data, 'readlines'):
        data = mod.parse(data).getroot()
    elif isinstance(data, list):
        data = mod.fromstring(''.join(data))
    elif isinstance(data, basestring):
        data = mod.parse(open(data)).getroot()
    else:
        raise TypeError('Unable to handle data of type %r' % type(data))
    return data


def element_creator(namespace=None):
    """Create a simple namespace-aware objectify element creator.

    :param str namespace: Namespace to work in
    :rtype: ``function``
    :return: Namespace-aware element creator

    """
    ELEMENT_MAKER = _objectify.ElementMaker(namespace=namespace,
                                            annotate=False)

    def create_elem(tag, attr=None, text=None):
        """:class:`objectify.Element` wrapper with namespace defined.

        :param str tag: Tag name
        :param dict attr: Default attributes for tag
        :param str text: Text content for the tag
        :rtype: ``_objectify.ObjectifiedElement``
        :return: objectify element

        """
        if not attr:
            attr = {}
        if text:
            element = getattr(ELEMENT_MAKER, tag)(text, **attr)
        else:
            element = getattr(ELEMENT_MAKER, tag)(**attr)
        return element

    return create_elem

#}


#{ Angle conversion utilities
def to_dms(angle, style='dms'):
    """Convert decimal angle to degrees, minutes and possibly seconds.

    :param float angle: Angle to convert
    :param str style: Return fractional or whole minutes values
    :rtype: ``tuple`` of ``int`` objects for values
    :return: Angle converted to degrees, minutes and possibly seconds
    :raise ValueError: Unknown value for ``style``

    """
    sign = 1 if angle >= 0 else -1
    angle = abs(angle) * 3600
    minutes, seconds = divmod(angle, 60)
    degrees, minutes = divmod(minutes, 60)
    if style == 'dms':
        return tuple(sign * abs(i) for i in (int(degrees), int(minutes),
                                             seconds))
    elif style == 'dm':
        return tuple(sign * abs(i) for i in (int(degrees),
                                             (minutes + seconds / 60)))
    else:
        raise ValueError('Unknown style type %r' % style)


def to_dd(degrees, minutes, seconds=0):
    """Convert degrees, minutes and optionally seconds to decimal angle.

    :param float degrees: Number of degrees
    :param float minutes: Number of minutes
    :param float seconds: Number of seconds
    :rtype: ``float``
    :return: Angle converted to decimal degrees

    """
    sign = -1 if any(i < 0 for i in (degrees, minutes, seconds)) else 1
    return sign * (abs(degrees) + abs(minutes) / 60 + abs(seconds) / 3600)


def __chunk(segment, abbr=False):
    """Generate a ``tuple`` of compass direction names.

    :param list segment: Compass segment to generate names for
    :param bool abbr: Names should use single letter abbreviations
    :rtype: ``tuple``
    :return: Direction names for compass segment

    """
    names = ('north', 'east', 'south', 'west', 'north')
    if not abbr:
        sjoin = '-'
    else:
        names = [s[0].upper() for s in names]
        sjoin = ''
    if segment % 2 == 0:
        return (names[segment].capitalize(),
                sjoin.join((names[segment].capitalize(), names[segment],
                            names[segment + 1])),
                sjoin.join((names[segment].capitalize(), names[segment + 1])),
                sjoin.join((names[segment + 1].capitalize(), names[segment],
                            names[segment + 1])))
    else:
        return (names[segment].capitalize(),
                sjoin.join((names[segment].capitalize(), names[segment + 1],
                            names[segment])),
                sjoin.join((names[segment + 1].capitalize(), names[segment])),
                sjoin.join((names[segment + 1].capitalize(),
                            names[segment + 1], names[segment])))
COMPASS_NAMES = reduce(add, map(__chunk, range(4)))
COMPASS_NAMES_ABBR = reduce(add, [__chunk(x, True) for x in range(4)])


def angle_to_name(angle, segments=8, abbr=False):
    """Convert angle in to direction name.

    :param float angle: Angle in degrees to convert to direction name
    :param int segments: Number of segments to split compass in to
    :param bool abbr: Whether to return abbreviated direction string
    :rtype: ``str``
    :return: Direction name for ``angle``

    """
    if segments == 4:
        string = COMPASS_NAMES[int((angle + 45) / 90) % 4 * 2]
    elif segments == 8:
        string = COMPASS_NAMES[int((angle + 22.5) / 45) % 8 * 2]
    elif segments == 16:
        string = COMPASS_NAMES[int((angle + 11.25) / 22.5) % 16]
    else:
        raise ValueError('Segments parameter must be 4, 8 or 16 not %r'
                         % segments)
    if abbr:
        return ''.join(i[0].capitalize() for i in string.split('-'))
    else:
        return string
#}


#{ Date and time handling utilities
@mangle_repr_type
class TzOffset(datetime.tzinfo):

    """Time offset from UTC."""

    def __init__(self, tzstring):
        """Initialise a new ``TzOffset`` object.

        :param str tzstring: `ISO 8601`_ style timezone definition

        .. _ISO 8601: http://www.cl.cam.ac.uk/~mgk25/iso-time.html

        """
        super(TzOffset, self).__init__()
        hours, minutes = map(int, tzstring.split(':'))

        self.__offset = datetime.timedelta(hours=hours, minutes=minutes)

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: ``str``
        :return: String to recreate ``TzOffset`` object

        """
        return repr_assist(self, {'tzstring': self.as_timezone()})

    def dst(self, dt=None):
        """Daylight Savings Time offset.

        .. note::
           This method is only for compatibility with the ``tzinfo`` interface,
           and does nothing

        :param dt: For compatibility with parent classes

        """
        return datetime.timedelta(0)

    def as_timezone(self):
        """Create a human-readable timezone string.

        :rtype: ``str``
        :return: Human-readable timezone definition

        """
        offset = self.utcoffset()
        hours, minutes = divmod(offset.seconds / 60, 60)
        if offset.days == -1:
            hours = -24 + hours

        return '%+03i:%02i' % (hours, minutes)

    def utcoffset(self, dt=None):
        """Return the offset in minutes from UTC.

        :param dt: For compatibility with parent classes

        """
        return self.__offset


class Timestamp(datetime.datetime):

    """Class for representing an OSM timestamp value."""

    def isoformat(self):
        """Generate an ISO 8601 formatted time stamp.

        :rtype: ``str``
        :return: `ISO 8601`_ formatted time stamp

        .. _ISO 8601: http://www.cl.cam.ac.uk/~mgk25/iso-time.html

        """
        text = [self.strftime('%Y-%m-%dT%H:%M:%S'), ]
        if self.tzinfo:
            text.append(self.tzinfo.as_timezone())
        else:
            text.append('+00:00')
        return ''.join(text)

    @staticmethod
    def parse_isoformat(timestamp):
        """Parse an ISO 8601 formatted time stamp.

        :param str timestamp: Timestamp to parse
        :rtype: ``Timestamp``
        :return: Parsed timestamp

        """
        if len(timestamp) == 20:
            zone = TzOffset('+00:00')
            timestamp = timestamp[:-1]
        elif len(timestamp) == 24:
            zone = TzOffset('%s:%s' % (timestamp[-5:-2], timestamp[-2:]))
            timestamp = timestamp[:-5]
        elif len(timestamp) == 25:
            zone = TzOffset(timestamp[-6:])
            timestamp = timestamp[:-6]
        timestamp = Timestamp.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        timestamp = timestamp.replace(tzinfo=zone)
        return timestamp

#}

#{ Coordinate conversion utilities

iso6709_matcher = re.compile(r'^([-+][\d.]+)([-+][\d.]+)([+-][\d.]+)?/$')


def from_iso6709(coordinates):
    """Parse ISO 6709 coordinate strings.

    This function will parse ISO 6709-1983(E) "Standard representation of
    latitude, longitude and altitude for geographic point locations" elements.
    Unfortunately, the standard is rather convoluted and this implementation is
    incomplete, but it does support most of the common formats in the wild.

    The W3C has a simplified profile for ISO 6709 in `Latitude, Longitude and
    Altitude format for geospatial information`_.  It unfortunately hasn't
    received widespread support as yet, but hopefully it will grow just as the
    `simplified ISO 8601 profile`_ has.

    .. seealso::

       :func:`to_iso6709`

    :page str coordinates: ISO 6709 coordinates string
    :rtype: ``tuple``
    :return: A tuple consisting of latitude and longitude in degrees, along
        with the elevation in metres
    :raise ValueError: Input string is not ISO 6709 compliant
    :raise ValueError: Invalid value for latitude
    :raise ValueError: Invalid value for longitude

    .. _simplified ISO 8601 profile: http://www.w3.org/TR/NOTE-datetime

    """
    matches = iso6709_matcher.match(coordinates)
    if matches:
        latitude, longitude, altitude = matches.groups()
    else:
        raise ValueError('Incorrect format for string')
    sign = 1 if latitude[0] == '+' else -1
    latitude_head = len(latitude.split('.')[0])
    if latitude_head == 3:  # ±DD(.D{1,4})?
        latitude = float(latitude)
    elif latitude_head == 5:  # ±DDMM(.M{1,4})?
        latitude = float(latitude[:3]) + (sign * (float(latitude[3:]) / 60))
    elif latitude_head == 7:  # ±DDMMSS(.S{1,4})?
        latitude = float(latitude[:3]) + (sign * (float(latitude[3:5]) / 60)) \
            + (sign * (float(latitude[5:]) / 3600))
    else:
        raise ValueError('Incorrect format for latitude %r' % latitude)
    sign = 1 if longitude[0] == '+' else -1
    longitude_head = len(longitude.split('.')[0])
    if longitude_head == 4:  # ±DDD(.D{1,4})?
        longitude = float(longitude)
    elif longitude_head == 6:  # ±DDDMM(.M{1,4})?
        longitude = float(longitude[:4]) + (sign * (float(longitude[4:]) / 60))
    elif longitude_head == 8:  # ±DDDMMSS(.S{1,4})?
        longitude = float(longitude[:4]) \
            + (sign * (float(longitude[4:6]) / 60)) \
            + (sign * (float(longitude[6:]) / 3600))
    else:
        raise ValueError('Incorrect format for longitude %r' % longitude)
    if altitude:
        altitude = float(altitude)
    return latitude, longitude, altitude


def to_iso6709(latitude, longitude, altitude=None, format='dd', precision=4):
    """Produce ISO 6709 coordinate strings.

    This function will produce ISO 6709-1983(E) "Standard representation of
    latitude, longitude and altitude for geographic point locations" elements.

    .. seealso::

       :func:`from_iso6709`

    :param float latitude: Location's latitude
    :param float longitude: Location's longitude
    :param float altitude: Location's altitude
    :param str format: Format type for string
    :param int precision: Latitude/longitude precision
    :rtype: ``str``
    :return: ISO 6709 coordinates string
    :raise ValueError: Unknown value for ``format``

    .. _Latitude, Longitude and Altitude format for geospatial information:
       http://www.w3.org/2005/Incubator/geo/Wiki/LatitudeLongitudeAltitude
    .. _wikipedia ISO 6709 page: http://en.wikipedia.org/wiki/ISO_6709

    """
    text = []
    if format == 'd':
        text.append('%+03i%+04i' % (latitude, longitude))
    elif format == 'dd':
        text.append('%+0*.*f%+0*.*f' % (precision + 4, precision, latitude,
                                        precision + 5, precision, longitude))
    elif format in ('dm', 'dms'):
        if format == 'dm':
            latitude_dms = to_dms(latitude, 'dm')
            longitude_dms = to_dms(longitude, 'dm')
        elif format == 'dms':
            latitude_dms = to_dms(latitude)
            longitude_dms = to_dms(longitude)
        latitude_sign = '-' if any(i < 0 for i in latitude_dms) else '+'
        latitude_dms = tuple(abs(i) for i in latitude_dms)
        longitude_sign = '-' if any(i < 0 for i in longitude_dms) else '+'
        longitude_dms = tuple(abs(i) for i in longitude_dms)
        if format == 'dm':
            text.append('%s%02i%02i' % ((latitude_sign, ) + latitude_dms))
            text.append('%s%03i%02i' % ((longitude_sign, ) + longitude_dms))
        elif format == 'dms':
            text.append('%s%02i%02i%02i' % ((latitude_sign, ) + latitude_dms))
            text.append('%s%03i%02i%02i'
                        % ((longitude_sign, ) + longitude_dms))
    else:
        raise ValueError('Unknown format type %r' % format)
    if altitude and int(altitude) == altitude:
        text.append('%+i' % altitude)
    elif altitude:
        text.append('%+.3f' % altitude)
    text.append('/')
    return ''.join(text)


def angle_to_distance(angle, units='metric'):
    """Convert angle in to distance along a great circle.

    :param float angle: Angle in degrees to convert to distance
    :param str units: Unit type to be used for distances
    :rtype: ``float``
    :return: Distance in ``units``
    :raise ValueError: Unknown value for ``units``

    """
    distance = math.radians(angle) * BODY_RADIUS

    if units in ('km', 'metric'):
        return distance
    elif units in ('sm', 'imperial', 'US customary'):
        return distance / STATUTE_MILE
    elif units in ('nm', 'nautical'):
        return distance / NAUTICAL_MILE
    else:
        raise ValueError('Unknown units type %r' % units)


def distance_to_angle(distance, units='metric'):
    """Convert a distance in to an angle along a great circle.

    :param float distance: Distance to convert to degrees
    :param str units: Unit type to be used for distances
    :rtype: ``float``
    :return: Angle in degrees
    :raise ValueError: Unknown value for ``units``

    """
    if units in ('km', 'metric'):
        pass
    elif units in ('sm', 'imperial', 'US customary'):
        distance *= STATUTE_MILE
    elif units in ('nm', 'nautical'):
        distance *= NAUTICAL_MILE
    else:
        raise ValueError('Unknown units type %r' % units)

    return math.degrees(distance / BODY_RADIUS)


def from_grid_locator(locator):
    """Calculate geodesic latitude/longitude from Maidenhead locator.

    :param str locator: Maidenhead locator string
    :rtype: ``tuple`` of ``float`` objects
    :return: Geodesic latitude and longitude values
    :raise ValueError: Incorrect grid locator length
    :raise ValueError: Invalid values in locator string

    """
    if not len(locator) in (4, 6, 8):
        raise ValueError('Locator must be 4, 6 or 8 characters long %r'
                         % locator)

    # Convert the locator string to a list, because we need it to be mutable to
    # munge the values
    locator = list(locator)

    # Convert characters to numeric value, fields are always uppercase
    locator[0] = ord(locator[0]) - 65
    locator[1] = ord(locator[1]) - 65

    # Values for square are always integers
    locator[2] = int(locator[2])
    locator[3] = int(locator[3])

    if len(locator) >= 6:
        # Some people use uppercase for the subsquare data, in spite of
        # lowercase being the accepted style, so handle that too.
        locator[4] = ord(locator[4].lower()) - 97
        locator[5] = ord(locator[5].lower()) - 97

    if len(locator) == 8:
        # Extended square values are always integers
        locator[6] = int(locator[6])
        locator[7] = int(locator[7])

    # Check field values within 'A'(0) to 'R'(17), and square values are within
    # 0 to 9
    if not 0 <= locator[0] <= 17 \
       or not 0 <= locator[1] <= 17 \
       or not 0 <= locator[2] <= 9 \
       or not 0 <= locator[3] <= 9:
        raise ValueError('Invalid values in locator %r' % locator)

    # Check subsquare values are within 'a'(0) to 'x'(23)
    if len(locator) >= 6:
        if not 0 <= locator[4] <= 23 \
           or not 0 <= locator[5] <= 23:
            raise ValueError('Invalid values in locator %r' % locator)

    # Extended square values must be within 0 to 9
    if len(locator) == 8:
        if not 0 <= locator[6] <= 9 \
           or not 0 <= locator[7] <= 9:
            raise ValueError('Invalid values in locator %r' % locator)

    longitude = LONGITUDE_FIELD * locator[0] \
        + LONGITUDE_SQUARE * locator[2]
    latitude = LATITUDE_FIELD * locator[1] \
        + LATITUDE_SQUARE * locator[3]

    if len(locator) >= 6:
        longitude += LONGITUDE_SUBSQUARE * locator[4]
        latitude += LATITUDE_SUBSQUARE * locator[5]

    if len(locator) == 8:
        longitude += LONGITUDE_EXTSQUARE * locator[6] + LONGITUDE_EXTSQUARE / 2
        latitude += LATITUDE_EXTSQUARE * locator[7] + LATITUDE_EXTSQUARE / 2
    else:
        longitude += LONGITUDE_EXTSQUARE * 5
        latitude += LATITUDE_EXTSQUARE * 5

    # Rebase longitude and latitude to normal geodesic
    longitude -= 180
    latitude -= 90

    return latitude, longitude


def to_grid_locator(latitude, longitude, precision='square'):
    """Calculate Maidenhead locator from latitude and longitude.

    :param float latitude: Position's latitude
    :param float longitude: Position's longitude
    :param str precision: Precision with which generate locator string
    :rtype: ``str``
    :return: Maidenhead locator for latitude and longitude
    :raise ValueError: Invalid precision identifier
    :raise ValueError: Invalid latitude or longitude value

    """
    if not precision in ('square', 'subsquare', 'extsquare'):
        raise ValueError('Unsupported precision value %r' % precision)

    if not -90 <= latitude <= 90:
        raise ValueError('Invalid latitude value %r' % latitude)
    if not -180 <= longitude <= 180:
        raise ValueError('Invalid longitude value %r' % longitude)

    latitude += 90.0
    longitude += 180.0

    locator = []

    field = int(longitude / LONGITUDE_FIELD)
    locator.append(chr(field + 65))
    longitude -= field * LONGITUDE_FIELD

    field = int(latitude / LATITUDE_FIELD)
    locator.append(chr(field + 65))
    latitude -= field * LATITUDE_FIELD

    square = int(longitude / LONGITUDE_SQUARE)
    locator.append(str(square))
    longitude -= square * LONGITUDE_SQUARE

    square = int(latitude / LATITUDE_SQUARE)
    locator.append(str(square))
    latitude -= square * LATITUDE_SQUARE

    if precision in ('subsquare', 'extsquare'):
        subsquare = int(longitude / LONGITUDE_SUBSQUARE)
        locator.append(chr(subsquare + 97))
        longitude -= subsquare * LONGITUDE_SUBSQUARE

        subsquare = int(latitude / LATITUDE_SUBSQUARE)
        locator.append(chr(subsquare + 97))
        latitude -= subsquare * LATITUDE_SUBSQUARE

    if precision == 'extsquare':
        extsquare = int(longitude / LONGITUDE_EXTSQUARE)
        locator.append(str(extsquare))

        extsquare = int(latitude / LATITUDE_EXTSQUARE)
        locator.append(str(extsquare))

    return ''.join(locator)


def parse_location(location):
    """Parse latitude and longitude from string location.

    :param str location: String to parse
    :rtype: ``tuple`` of ``float`` objects
    :return: Latitude and longitude of location

    """

    def split_dms(text, hemisphere):
        """Split degrees, minutes and seconds string.

        :param str text: Text to split
        :rtype: ``float``
        :return: Decimal degrees

        """
        out = []
        sect = []
        for i in text:
            if i.isdigit():
                sect.append(i)
            else:
                out.append(sect)
                sect = []
        d, m, s = [float(''.join(i)) for i in out]
        if hemisphere in 'SW':
            d, m, s = [-1 * x for x in (d, m, s)]
        return to_dd(d, m, s)

    for sep in ';, ':
        chunks = location.split(sep)
        if len(chunks) == 2:
            if chunks[0].endswith('N'):
                latitude = float(chunks[0][:-1])
            elif chunks[0].endswith('S'):
                latitude = -1 * float(chunks[0][:-1])
            else:
                latitude = float(chunks[0])
            if chunks[1].endswith('E'):
                longitude = float(chunks[1][:-1])
            elif chunks[1].endswith('W'):
                longitude = -1 * float(chunks[1][:-1])
            else:
                longitude = float(chunks[1])
            return latitude, longitude
        elif len(chunks) == 4:
            if chunks[0].endswith(('s', '"')):
                latitude = split_dms(chunks[0], chunks[1])
            else:
                latitude = float(chunks[0])
                if chunks[1] == 'S':
                    latitude = -1 * latitude
            if chunks[2].endswith(('s', '"')):
                longitude = split_dms(chunks[2], chunks[3])
            else:
                longitude = float(chunks[2])
                if chunks[3] == 'W':
                    longitude = -1 * longitude
            return latitude, longitude
#}

#{ Solar event utilities

#: Sunrise/-set mappings from name to angle
ZENITH = {
    # All values are specified in degrees!

    # Sunrise/sunset is defined as the moment the upper limb becomes visible,
    # taking in to account atmospheric refraction.  That is 34' for atmospheric
    # refraction and 16' for angle between the Sun's centre and it's upper
    # limb, resulting in a combined 50' below the horizon.
    #
    # We're totally ignoring how temperature and pressure change the amount of
    # atmospheric refraction, because their effects are drowned out by rounding
    # errors in the equation.
    None: -50 / 60,

    # Twilight definitions specify the angle in degrees of the Sun below the
    # horizon
    'civil': -6,
    'nautical': -12,
    'astronomical': -18,
}


def sun_rise_set(latitude, longitude, date, mode='rise', timezone=0,
                 zenith=None):
    """Calculate sunrise or sunset for a specific location.

    This function calculates the time sunrise or sunset, or optionally the
    beginning or end of a specified twilight period.

    Source::

        Almanac for Computers, 1990
        published by Nautical Almanac Office
        United States Naval Observatory
        Washington, DC 20392

    :param float latitude: Location's latitude
    :param float longitude: Location's longitude
    :param datetime.date date: Calculate rise or set for given date
    :param str mode: Which time to calculate
    :param int timezone: Offset from UTC in minutes
    :param str zenith: Calculate rise/set events, or twilight times
    :rtype: :class:`datetime.time` or ``None``
    :return: The time for the given event in the specified timezone, or
        ``None`` if the event doesn't occur on the given date
    :raise ValueError: Unknown value for ``mode``

    """
    if not date:
        date = datetime.date.today()

    zenith = ZENITH[zenith]

    # First calculate the day of the year
    # Thanks, datetime this would have been ugly without you!!!
    n = (date - datetime.date(date.year - 1, 12, 31)).days

    # Convert the longitude to hour value and calculate an approximate time
    lng_hour = longitude / 15

    if mode == 'rise':
        t = n + ((6 - lng_hour) / 24)
    elif mode == 'set':
        t = n + ((18 - lng_hour) / 24)
    else:
        raise ValueError('Unknown mode value %r' % mode)

    # Calculate the Sun's mean anomaly
    m = (0.9856 * t) - 3.289

    # Calculate the Sun's true longitude
    l = m + 1.916 * math.sin(math.radians(m)) + 0.020 \
        * math.sin(2 * math.radians(m)) + 282.634
    l = abs(l) % 360

    # Calculate the Sun's right ascension
    ra = math.degrees(math.atan(0.91764 * math.tan(math.radians(l))))

    # Right ascension value needs to be in the same quadrant as L
    l_quandrant = (math.floor(l / 90)) * 90
    ra_quandrant = (math.floor(ra / 90)) * 90
    ra = ra + (l_quandrant - ra_quandrant)

    # Right ascension value needs to be converted into hours
    ra = ra / 15

    # Calculate the Sun's declination
    sin_dec = 0.39782 * math.sin(math.radians(l))
    cos_dec = math.cos(math.asin(sin_dec))

    # Calculate the Sun's local hour angle
    cos_h = (math.radians(zenith) -
             (sin_dec * math.sin(math.radians(latitude)))) \
        / (cos_dec * math.cos(math.radians(latitude)))

    if cos_h > 1:
        # The sun never rises on this location (on the specified date)
        return None
    elif cos_h < -1:
        # The sun never sets on this location (on the specified date)
        return None

    # Finish calculating H and convert into hours
    if mode == 'rise':
        h = 360 - math.degrees(math.acos(cos_h))
    else:
        h = math.degrees(math.acos(cos_h))
    h = h / 15

    # Calculate local mean time of rising/setting
    t = h + ra - (0.06571 * t) - 6.622

    # Adjust back to UTC
    utc = t - lng_hour

    # Convert UT value to local time zone of latitude/longitude
    local_t = utc + timezone / 60
    if local_t < 0:
        local_t += 24
    elif local_t > 23:
        local_t -= 24

    hour = int(local_t)
    if hour == 0:
        minute = int(60 * local_t)
    else:
        minute = int(60 * (local_t % hour))
    if minute < 0:
        minute += 60
    return datetime.time(hour, minute)


def sun_events(latitude, longitude, date, timezone=0, zenith=None):
    """Convenience function for calculating sunrise and sunset.

    Civil twilight starts/ends when the Sun's centre is 6 degrees below
    the horizon.

    Nautical twilight starts/ends when the Sun's centre is 12 degrees
    below the horizon.

    Astronomical twilight starts/ends when the Sun's centre is 18 degrees below
    the horizon.

    :param float latitude: Location's latitude
    :param float longitude: Location's longitude
    :param datetime.date date: Calculate rise or set for given date
    :param int timezone: Offset from UTC in minutes
    :param str zenith: Calculate rise/set events, or twilight times
    :rtype: ``tuple`` of :class:`datetime.time`
    :return: The time for the given events in the specified timezone

    """
    return (sun_rise_set(latitude, longitude, date, 'rise', timezone, zenith),
            sun_rise_set(latitude, longitude, date, 'set', timezone, zenith))

#}


def dump_xearth_markers(markers, name='identifier'):
    """Generate an Xearth compatible marker file.

    ``dump_xearth_markers()`` writes a simple Xearth_ marker file from
    a dictionary of :class:`trigpoints.Trigpoint` objects.

    It expects a dictionary in one of the following formats. For support of
    :class:`Trigpoint` that is::

        {500936: Trigpoint(52.066035, -0.281449, 37.0, "Broom Farm"),
         501097: Trigpoint(52.010585, -0.173443, 97.0, "Bygrave"),
         505392: Trigpoint(51.910886, -0.186462, 136.0, "Sish Lane")}

    And generates output of the form::

        52.066035 -0.281449 "500936" # Broom Farm, alt 37m
        52.010585 -0.173443 "501097" # Bygrave, alt 97m
        51.910886 -0.186462 "205392" # Sish Lane, alt 136m

    Or similar to the following if the ``name`` parameter is set to ``name``::

        52.066035 -0.281449 "Broom Farm" # 500936 alt 37m
        52.010585 -0.173443 "Bygrave" # 501097 alt 97m
        51.910886 -0.186462 "Sish Lane" # 205392 alt 136m

    Point objects should be provided in the following format::

        {"Broom Farm": Point(52.066035, -0.281449),
         "Bygrave": Point(52.010585, -0.173443),
         "Sish Lane": Point(51.910886, -0.186462)}

    And generates output of the form::

        52.066035 -0.281449 "Broom Farm"
        52.010585 -0.173443 "Bygrave"
        51.910886 -0.186462 "Sish Lane"

    .. note:
       xplanet_ also supports xearth marker files, and as such can use the
       output from this function.

    .. seealso:

       :func:`upoints.xearth.Xearths.import_locations`

    :param dict markers: Dictionary of identifier keys, with :class:`Trigpoint`
        values
    :param str name: Value to use as Xearth display string
    :rtype: ``list``
    :return: List of strings representing an Xearth marker file
    :raise ValueError: Unsupported value for ``name``

    .. _xearth: http://hewgill.com/xearth/original/
    .. _xplanet: http://xplanet.sourceforge.net/

    """
    output = []
    for identifier, point in markers.items():
        line = ['%f %f ' % (point.latitude, point.longitude), ]
        if hasattr(point, 'name') and point.name:
            if name == 'identifier':
                line.append('"%s" # %s' % (identifier, point.name))
            elif name == 'name':
                line.append('"%s" # %s' % (point.name, identifier))
            elif name == 'comment':
                line.append('"%s" # %s' % (identifier, point.comment))
            else:
                raise ValueError('Unknown name type %r' % name)
            if hasattr(point, 'altitude') and point.altitude:
                line.append(', alt %im' % point.altitude)
        else:
            line.append('"%s"' % identifier)
        output.append(''.join(line))
    # Return the list sorted on the marker name
    return sorted(output, key=lambda x: x.split()[2])


def calc_radius(latitude, ellipsoid='WGS84'):
    """Calculate earth radius for a given latitude.

    This function is most useful when dealing with datasets that are very
    localised and require the accuracy of an ellipsoid model without the
    complexity of code necessary to actually use one.  The results are meant to
    be used as a :data:`BODY_RADIUS` replacement when the simple geocentric
    value is not good enough.

    The original use for ``calc_radius`` is to set a more accurate radius value
    for use with trigpointing databases that are keyed on the OSGB36 datum, but
    it has been expanded to cover other ellipsoids.

    :param float latitude: Latitude to calculate earth radius for
    :type ellipsoid: ``tuple`` of ``float`` objects
    :param ellipsoid: Ellipsoid model to use for calculation
    :rtype: ``float``
    :return: Approximated Earth radius at the given latitude

    """

    ellipsoids = {
        'Airy (1830)': (6377.563, 6356.257),  # Ordnance Survey default
        'Bessel': (6377.397, 6356.079),
        'Clarke (1880)': (6378.249145, 6356.51486955),
        'FAI sphere': (6371, 6371),  # Idealised
        'GRS-67': (6378.160, 6356.775),
        'International': (6378.388, 6356.912),
        'Krasovsky': (6378.245, 6356.863),
        'NAD27': (6378.206, 6356.584),
        'WGS66': (6378.145, 6356.758),
        'WGS72': (6378.135, 6356.751),
        'WGS84': (6378.137, 6356.752),  # GPS default
    }

    # Equatorial radius, polar radius
    major, minor = ellipsoids[ellipsoid]
    # eccentricity of the ellipsoid
    eccentricity = 1 - (minor ** 2 / major ** 2)

    sl = math.sin(math.radians(latitude))
    return (major * (1 - eccentricity)) / (1 - eccentricity * sl ** 2) ** 1.5
