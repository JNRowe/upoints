#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""geonames - Imports geonames.org data files"""
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

try:
    from dateutil import tz
except ImportError:
    tz = None

from earth_distance import (trigpoints, utils)

class Location(trigpoints.Trigpoint):
    """
    Class for representing a location from a geonames.org data file

    All country codes are specified with their two letter ISO-3166 country code.

    @ivar geonameid: ID of record in geonames database
    @ivar name: Name of geographical location
    @ivar asciiname: Name of geographical location in ASCII encoding
    @ivar alt_names: Alternate names for the location
    @ivar latitude: Location's latitude
    @ivar longitude: Location's longitude
    @ivar feature_class: Location's type
    @ivar feature_code: Location's code
    @ivar country: Location's country
    @ivar alt_country: Alternate country codes for location
    @ivar admin1: FIPS code (subject to change to ISO code), ISO code for the US
        and CH
    @ivar admin2: Code for the second administrative division, a county in the
        US
    @ivar admin3: Code for third level administrative division
    @ivar admin4: Code for fourth level administrative division
    @ivar population: Location's population, if applicable
    @ivar altitude: Location's elevation
    @ivar gtopo30: Average elevation of 900 square metre region, if available
    @ivar tzname: The timezone identifier using POSIX timezone names
    @ivar timezone: The non-DST UTC timezone offset in minutes
    @ivar modified_date: Location's last modification date in the geonames
        databases
    @cvar __TIMEZONES: C{dateutil.gettz} cache to speed up generation
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
        """
        Initialise a new C{Location} object

        @type geonameid: C{int}
        @param geonameid: ID of record in geonames database
        @type name: Unicode C{str}
        @param name: Name of geographical location
        @type asciiname: C{str}
        @param asciiname: Name of geographical location in ASCII encoding
        @type alt_names: C{list} of Unicode C{str}
        @param alt_names: Alternate names for the location
        @type latitude: C{float}
        @param latitude: Location's latitude
        @type longitude: C{float}
        @param longitude: Location's longitude
        @type feature_class: C{str}
        @param feature_class: Location's type
        @type feature_code: C{str}
        @param feature_code: Location's code
        @type country: C{str}
        @param country: Location's country
        @type alt_country: C{str}
        @param alt_country: Alternate country codes for location
        @type admin1: C{str}
        @param admin1: FIPS code (subject to change to ISO code), ISO code for
            the US and CH
        @type admin2: C{str}
        @param admin2: Code for the second administrative division, a county in
            the US
        @param admin3: Code for third level administrative division
        @type admin4: C{str}
        @param admin4: Code for fourth level administrative division
        @type population: C{int}
        @param population: Location's population, if applicable
        @type altitude: C{int}
        @param altitude: Location's elevation
        @type gtopo30: C{int}
        @param gtopo30: Average elevation of 900 square metre region, if
            available
        @type tzname: C{str}
        @param tzname: The timezone identifier using POSIX timezone names
        @type modified_date: C{datetime.date}
        @param modified_date: Location's last modification date in the geonames
            databases
        @type timezone: C{int}
        @param timezone: The non-DST timezone offset from UTC in minutes
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

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Location(2636782, "Stotfold", "Stotfold", None, 52.0, -0.2166667,
        ...          "P", "PPL", "GB", None, "F8", None, None, None, 6245,
        ...          None, 77, "Europe/London", datetime.date(2007, 6, 15), 0)
        Location(2636782, 'Stotfold', 'Stotfold', None, 52.0, -0.2166667, 'P',
                 'PPL', 'GB', None, 'F8', None, None, None, 6245, None, 77,
                 'Europe/London', datetime.date(2007, 6, 15), 0)

        @rtype: C{str}
        @return: String to recreate C{Location} object
        """
        data = utils.repr_assist(self.geonameid, self.name, self.asciiname,
                                 self.alt_names,self.latitude, self.longitude,
                                 self.feature_class, self.feature_code,
                                 self.country, self.alt_country, self.admin1,
                                 self.admin2, self.admin3, self.admin4,
                                 self.population, self.altitude, self.gtopo30,
                                 self.tzname, self.modified_date,
                                 self.timezone)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        @see: C{trigpoints.point.Point}

        >>> Stotfold = Location(2636782, "Stotfold", "Stotfold", None, 52.0,
        ...                     -0.2166667, "P", "PPL", "GB", None, "F8", None,
        ...                     None, None, 6245, None, 77, "Europe/London",
        ...                     datetime.date(2007, 6, 15))
        >>> print(Stotfold)
        Stotfold (N52.000°; W000.217°)
        >>> print(Stotfold.__str__(mode="dms"))
        Stotfold (52°00'00"N, 000°13'00"W)
        >>> print(Stotfold.__str__(mode="dm"))
        Stotfold (52°00.00'N, 000°13.00'W)
        >>> Stotfold.alt_names = ["Home", "Target"]
        >>> print(Stotfold)
        Stotfold (Home, Target - N52.000°; W000.217°)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Location} object
        """
        text = super(Location.__base__, self).__str__(mode)

        if self.alt_names:
            return "%s (%s - %s)" % (self.name, ", ".join(self.alt_names), text)
        else:
            return "%s (%s)" % (self.name, text)

class Locations(dict):
    """
    Class for representing a group of C{Location} objects
    """

    def __init__(self, data=None, tzfile=None):
        """
        Initialise a new C{Locations} object
        """
        dict.__init__(self)
        if tzfile:
            self.import_timezones_file(tzfile)
        else:
            self.timezones = {}

        if data:
            self.import_geonames_file(data)

    def import_geonames_file(self, data):
        """
        Parse geonames.org country database exports

        C{import_geonames_file()} returns a dictionary with keys containing the
        geonames identifier, and values consisting of a C{trigpoints.Trigpoint}
        object and a large variety of other information available in the data
        exported by U{geonames <http://geonames.org/>}.

        It expects data files in the following tab separated format::

            2633441	Afon Wyre	Afon Wyre	River Wayrai,River Wyrai,Wyre	52.3166667	-4.1666667	H	STM	GB	GB	00				0		-9999	Europe/London	1994-01-13
            2633442	Wyre	Wyre	Viera	59.1166667	-2.9666667	T	ISL	GB	GB	V9				0		1	Europe/London	2004-09-24
            2633443	Wraysbury	Wraysbury	Wyrardisbury	51.45	-0.55	P	PPL	GB		P9				0		28	Europe/London	2006-08-21

        Files containing the data in this format can be downloaded from the
        geonames site in their U{database export page
        <http://download.geonames.org/export/dump/>}.

        Files downloaded from the geonames site when processed by
        C{import_geonames_file()} will return C{dict} object of the following
        style::

            {2633441: Location(2633441, "Afon Wyre", "Afon Wyre",
                               ['River Wayrai', 'River Wyrai', 'Wyre'],
                               52.3166667, -4.1666667, "H", "STM", "GB",
                               ['GB'], "00", None, None, None, 0, None, -9999,
                               "Europe/London", datetime.date(1994, 1, 13)),
             2633442: Location(2633442, "Wyre", "Wyre", ['Viera'], 59.1166667,
                               -2.9666667, "T", "ISL", "GB", ['GB'], "V9",
                               None, None, None, 0, None, 1, "Europe/London",
                               datetime.date(2004, 9, 24)),
             2633443: Location(2633443, "Wraysbury", "Wraysbury",
                               ['Wyrardisbury'], 51.45, -0.55, "P", "PPL",
                               "GB", None, "P9", None, None, None, 0, None, 28,
                               "Europe/London", datetime.date(2006, 8, 21))}

        >>> locations = Locations(open("geonames"))
        >>> for key, value in sorted(locations.items()):
        ...     print("%s - %s" % (key, value))
        2633441 - Afon Wyre (River Wayrai, River Wyrai, Wyre - N52.317°;
        W004.167°)
        2633442 - Wyre (Viera - N59.117°; W002.967°)
        2633443 - Wraysbury (Wyrardisbury - N51.450°; W000.550°)
        >>> broken_locations = Locations(open("broken_geonames"))
        Traceback (most recent call last):
            ...
        FileFormatError: Incorrect data format, if you're using a file
        downloaded from geonames.org please report this to James Rowe
        <jnrowe@ukfsn.org>

        @type data: C{file}, C{list} or C{str}
        @param data: geonames locations data to read
        @rtype: C{dict}
        @return: geonames identifiers with C{Location} objects
        @raise FileFormatError: Unknown file format
        """
        data = utils.prepare_read(data)
        for line in data:
            timezone = None
            chunk = line.strip().split("	")
            if not len(chunk) == 19:
                raise utils.FileFormatError("geonames.org")
            for pos, elem in zip(range(19), chunk):
                if pos in [0, 14, 15, 16]:
                    elem = None if elem == "" else int(elem)
                elif pos in [4, 5]:
                    elem = None if elem == "" else float(elem)
                elif pos in [3, 9]:
                    elem = None if elem == "" else elem.split(",")
                elif pos == 17 and not elem == "" and self.timezones:
                    timezone = self.timezones[elem][0]
                elif pos == 18:
                    elem = datetime.date(*[int(i) for i in elem.split("-")])
                elif elem == "":
                    elem = None
                else:
                    continue
                chunk[pos] = elem
            chunk.append(timezone)
            self[chunk[0]] = Location(*chunk)

    def import_timezones_file(self, data):
        """
        Parse geonames.org timezone exports

        C{import_timezone_file()} returns a dictionary with keys containing the
        timezone identifier, and values consisting of a UTC offset and UTC
        offset during daylight savings time in minutes.

        It expects data files in the following format::

            Europe/Andorra	1.0	2.0
            Asia/Dubai	4.0	4.0
            Asia/Kabul	4.5	4.5

        Files containing the data in this format can be downloaded from the
        geonames site in their U{database export page
        <http://download.geonames.org/export/dump/timeZones.txt>}.

        Files downloaded from the geonames site when processed by
        C{import_timezones_file()} will return C{dict} object of the following
        style::

            {"Europe/Andorra": (60, 120),
             "Asia/Dubai": (240, 240),
             "Asia/Kabul": (270, 270)}

        >>> timezones = Locations(None, open("geonames_timezones")).timezones
        >>> for key, value in sorted(timezones.items()):
        ...     print("%s - %s" % (key, value))
        Asia/Dubai - (240, 240)
        Asia/Kabul - (270, 270)
        Europe/Andorra - (60, 120)
        >>> header_skip_check = Locations(None,
        ...                               open("geonames_timezones_header"))
        >>> print(header_skip_check)
        {}
        >>> broken_file_check = Locations(None,
        ...                               open("geonames_timezones_broken"))
        Traceback (most recent call last):
            ...
        FileFormatError: Incorrect data format, if you're using a file
        downloaded from geonames.org please report this to James Rowe
        <jnrowe@ukfsn.org>

        @type data: C{file}, C{list} or C{str}
        @param data: geonames timezones data to read
        @rtype: C{dict}
        @return: geonames timezone identifiers with their UTC offsets
        @raise FileFormatError: Unknown file format
        """
        data = utils.prepare_read(data)

        self.timezones = {}
        for line in data:
            chunk = line.strip().split("	")
            if chunk[0] == "TimeZoneId":
                continue
            elif not len(chunk) == 3:
                raise utils.FileFormatError("geonames.org")
            else:
                delta = tuple([int(float(x) * 60) for x in chunk[1:]])
            self.timezones[chunk[0]] = delta

