#
# coding=utf-8
"""geonames - Imports geonames.org data files"""
# Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>
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

try:
    from dateutil import tz
except ImportError:
    #: ``dateutil`` module reference if available
    tz = None

from upoints import (point, trigpoints, utils)


class Location(trigpoints.Trigpoint):

    """Class for representing a location from a geonames.org_ data file.

    All country codes are specified with their two letter ISO-3166 country
    code.

    .. versionadded:: 0.3.0

    :cvar __TIMEZONES: ``dateutil.gettz`` cache to speed up generation

    .. _geonames.org: http://www.geonames.org/
    """

    __slots__ = ('geonameid', 'asciiname', 'alt_names', 'feature_class',
                 'feature_code', 'country', 'alt_country', 'admin1', 'admin2',
                 'admin3', 'admin4', 'population', 'altitude', 'gtopo30',
                 'tzname', 'modified_date')

    if tz:
        __TIMEZONES = {}

    def __init__(self, geonameid, name, asciiname, alt_names, latitude,
                 longitude, feature_class, feature_code, country, alt_country,
                 admin1, admin2, admin3, admin4, population, altitude, gtopo30,
                 tzname, modified_date, timezone=None):
        """Initialise a new ``Location`` object.

        Args:
            geonameid (int): ID of record in geonames database
            name (unicode): Name of geographical location
            asciiname (str): Name of geographical location in ASCII encoding
            alt_names (list of unicode): Alternate names for the location
            latitude (float): Location's latitude
            longitude (float): Location's longitude
            feature_class (str): Location's type
            feature_code (str): Location's code
            country (str): Location's country
            alt_country (str): Alternate country codes for location
            admin1 (str): FIPS code (subject to change to ISO code), ISO code
                for the US and CH
            admin2 (str): Code for the second administrative division, a county
                in the US
            admin3 (str): Code for third level administrative division
            admin4 (str): Code for fourth level administrative division
            population (int): Location's population, if applicable
            altitude (int): Location's elevation
            gtopo30 (int): Average elevation of 900 square metre region, if
                available
            tzname (str): The timezone identifier using POSIX timezone names
            modified_date (datetime.date): Location's last modification date
                in the geonames databases
            timezone (int): The non-DST timezone offset from UTC in minutes
        """
        super(Location, self).__init__(latitude, longitude, altitude, name)
        self.geonameid = geonameid
        self.name = name
        self.asciiname = asciiname
        self.alt_names = alt_names
        self.latitude = latitude
        self.longitude = longitude
        self.feature_class = feature_class
        self.feature_code = feature_code
        self.country = country
        self.alt_country = alt_country
        self.admin1 = admin1
        self.admin2 = admin2
        self.admin3 = admin3
        self.admin4 = admin4
        self.population = population
        self.altitude = altitude
        self.gtopo30 = gtopo30
        self.tzname = tzname
        self.modified_date = modified_date
        if timezone is not None:
            self.timezone = timezone
        elif tz:
            if tzname in Location.__TIMEZONES:
                self.timezone = Location.__TIMEZONES[tzname]
            else:
                self.timezone = int(tz.gettz(tzname)._ttinfo_std.offset / 60)
                Location.__TIMEZONES[tzname] = self.timezone
        else:
            self.timezone = None

    def __str__(self):
        """Pretty printed location string.

        See also:
            trigpoints.point.Point

        Returns:
            str: Human readable string representation of ``Location`` object
        """
        return self.__format__()

    def __format__(self, format_spec='dd'):
        """Extended pretty printing for location strings.

        Args:
            format_spec (str): Coordinate formatting system to use

        Returns:
            str: Human readable string representation of ``Point`` object

        Raises:
            ValueError: Unknown value for ``format_spec``
        """
        text = super(Location.__base__, self).__format__(format_spec)

        if self.alt_names:
            return '%s (%s - %s)' % (self.name, ', '.join(self.alt_names),
                                     text)
        else:
            return '%s (%s)' % (self.name, text)


class Locations(point.Points):

    """Class for representing a group of :class:`Location` objects.

    .. versionadded:: 0.5.1
    """

    def __init__(self, data=None, tzfile=None):
        """Initialise a new ``Locations`` object."""
        super(Locations, self).__init__()
        if tzfile:
            self.import_timezones_file(tzfile)
        else:
            self.timezones = {}

        self._data = data
        self._tzfile = tzfile

        if data:
            self.import_locations(data)

    def import_locations(self, data):
        """Parse geonames.org country database exports.

        ``import_locations()`` returns a list of :class:`trigpoints.Trigpoint`
        objects generated from the data exported by geonames.org_.

        It expects data files in the following tab separated format::

            2633441	Afon Wyre	Afon Wyre	River Wayrai,River Wyrai,Wyre	52.3166667	-4.1666667	H	STM	GB	GB	00				0		-9999	Europe/London	1994-01-13
            2633442	Wyre	Wyre	Viera	59.1166667	-2.9666667	T	ISL	GB	GB	V9				0		1	Europe/London	2004-09-24
            2633443	Wraysbury	Wraysbury	Wyrardisbury	51.45	-0.55	P	PPL	GB		P9				0		28	Europe/London	2006-08-21

        Files containing the data in this format can be downloaded from the
        geonames.org_ site in their `database export page`_.

        Files downloaded from the geonames site when processed by
        ``import_locations()`` will return ``list`` objects of the following
        style::

            [Location(2633441, "Afon Wyre", "Afon Wyre",
                      ['River Wayrai', 'River Wyrai', 'Wyre'],
                      52.3166667, -4.1666667, "H", "STM", "GB", ['GB'], "00",
                      None, None, None, 0, None, -9999, "Europe/London",
                      datetime.date(1994, 1, 13)),
             Location(2633442, "Wyre", "Wyre", ['Viera'], 59.1166667,
                      -2.9666667, "T", "ISL", "GB", ['GB'], "V9", None, None,
                      None, 0, None, 1, "Europe/London",
                      datetime.date(2004, 9, 24)),
             Location(2633443, "Wraysbury", "Wraysbury", ['Wyrardisbury'],
                      51.45, -0.55, "P", "PPL", "GB", None, "P9", None, None,
                      None, 0, None, 28, "Europe/London",
                      datetime.date(2006, 8, 21))]

        Args:
            data (iter): geonames.org locations data to read

        Returns:
            list: geonames.org identifiers with :class:`Location` objects

        Raises:
            FileFormatError: Unknown file format

        .. _geonames.org: http://www.geonames.org/
        .. _database export page: http://download.geonames.org/export/dump/
        """
        self._data = data
        field_names = ('geonameid', 'name', 'asciiname', 'alt_names',
                       'latitude', 'longitude', 'feature_class',
                       'feature_code', 'country', 'alt_country', 'admin1',
                       'admin2', 'admin3', 'admin4', 'population', 'altitude',
                       'gtopo30', 'tzname', 'modified_date')
        comma_split = lambda s: s.split(',')
        date_parse = lambda s: datetime.date(*map(int, s.split('-')))
        or_none = lambda x, s: x(s) if s else None
        str_or_none = lambda s: or_none(str, s)
        float_or_none = lambda s: or_none(float, s)
        int_or_none = lambda s: or_none(int, s)
        tz_parse = lambda s: self.timezones[s][0] if self.timezones else None
        field_parsers = (int_or_none, str_or_none, str_or_none, comma_split,
                         float_or_none, float_or_none, str_or_none,
                         str_or_none, str_or_none, comma_split, str_or_none,
                         str_or_none, str_or_none, str_or_none, int_or_none,
                         int_or_none, int_or_none, tz_parse, date_parse)
        data = utils.prepare_csv_read(data, field_names, delimiter=r"	")
        for row in data:
            try:
                for name, parser in zip(field_names, field_parsers):
                    row[name] = parser(row[name])
            except ValueError:
                raise utils.FileFormatError('geonames.org')
            self.append(Location(**row))

    def import_timezones_file(self, data):
        """Parse geonames.org_ timezone exports.

        ``import_timezones_file()`` returns a dictionary with keys containing
        the timezone identifier, and values consisting of a UTC offset and UTC
        offset during daylight savings time in minutes.

        It expects data files in the following format::

            Europe/Andorra	1.0	2.0
            Asia/Dubai	4.0	4.0
            Asia/Kabul	4.5	4.5

        Files containing the data in this format can be downloaded from the
        geonames site in their `database export page`_

        Files downloaded from the geonames site when processed by
        ``import_timezones_file()`` will return ``dict`` object of the
        following style::

            {"Europe/Andorra": (60, 120),
             "Asia/Dubai": (240, 240),
             "Asia/Kabul": (270, 270)}

        Args:
            data (iter): geonames.org timezones data to read

        Returns:
            list: geonames.org timezone identifiers with their UTC offsets

        Raises:
            FileFormatError: Unknown file format

        .. _geonames.org: http://www.geonames.org/
        .. _database export page: http://download.geonames.org/export/dump/
        """
        self._tzfile = data
        field_names = ('ident', 'gmt_offset', 'dst_offset')
        time_parse = lambda n: int(float(n) * 60)
        data = utils.prepare_csv_read(data, field_names, delimiter=r"	")

        self.timezones = {}
        for row in data:
            if row['ident'] == 'TimeZoneId':
                continue
            try:
                delta = list(map(time_parse, (row['gmt_offset'], row['dst_offset'])))
            except ValueError:
                raise utils.FileFormatError('geonames.org')
            self.timezones[row['ident']] = delta
