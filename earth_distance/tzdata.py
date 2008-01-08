#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""tzdata - Imports timezone data files from UNIX zoneinfo"""
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

from earth_distance import (point, utils)

class Zone(point.Point):
    """
    Class for representing timezone descriptions from zoneinfo data

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar country: Location's ISO 3166 country code
    @ivar zone: Location's zone name as used in zoneinfo database
    @ivar comments: Location comments
    """

    __slots__ = ('country', 'zone', 'comments')

    def __init__(self, location, country, zone, comments=None):
        """
        Initialise a new C{Zone} object

        >>> Zone("+513030-0000731", 'GB', "Europe/London")
        Zone('+513030-0000730', 'GB', 'Europe/London', None)

        @type location: C{str}
        @param location: Primary location in ISO 6709 format
        @type country: C{str}
        @param country: Location's ISO 3166 country code
        @type zone: C{str}
        @param zone: Location's zone name as used in zoneinfo databse
        @type comments: C{list}
        @param comments: Location's alternate names
        """
        latitude, longitude = utils.from_iso6709(location + "/")[:2]
        super(Zone, self).__init__(latitude, longitude)

        self.country = country
        self.zone = zone
        self.comments = comments

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Zone("+513030-0000731", 'GB', "Europe/London")
        Zone('+513030-0000730', 'GB', 'Europe/London', None)

        @rtype: C{str}
        @return: String to recreate C{Zone} object
        """
        data = utils.repr_assist(self.country, self.zone, self.comments)
        data.insert(0, repr(utils.to_iso6709(self.latitude, self.longitude,
                                             format="dms")[:-1]))
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Zone("+513030-0000731", 'GB', "Europe/London"))
        Europe/London (GB: 51°30'30"N, 000°07'30"W)
        >>> print(Zone("+0658-15813", "FM", "Pacific/Ponape",
        ...            ["Ponape (Pohnpei)", ]))
        Pacific/Ponape (FM: 06°58'00"N, 158°13'00"W also Ponape (Pohnpei))

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Zone} object
        """
        text = "%s (%s: %s" % (self.zone, self.country,
                               super(Zone, self).__str__(mode))
        if self.comments:
            text += " also " + ", ".join(self.comments)
        text += ")"
        return text

class Zones(dict):
    """
    Class for representing a group of C{Zone} objects
    """

    def __init__(self, zone_file=None):
        """
        Initialise a new Zones object
        """
        dict.__init__(self)
        if zone_file:
            self.import_zone_file(zone_file)

    def import_zone_file(self, data):
        """
        Parse zoneinfo zone description data files

        C{import_zone_file()} returns a dictionary with keys containing the zone
        name, and values that are C{Zone} objects.

        It expects data files in one of the following formats::

            AN	+1211-06900	America/Curacao
            AO	-0848+01314	Africa/Luanda
            AQ	-7750+16636	Antarctica/McMurdo	McMurdo Station, Ross Island

        Files containing the data in this format can be found in C{zone.tab}
        file that is normally found in C{/usr/share/zoneinfo} on UNIX-like
        systems, or from the U{standard distribution site
        <ftp://elsie.nci.nih.gov/pub/>}.

        When processed by C{import_zone_file()} a C{dict} object of the
        following style will be returned::

            {"America/Curacao": Zone(None, None, "AN", "America/Curacao", None),
             "Africa/Luanda": Zone(None, None, "AO", "Africa/Luanda", None),
             "Antartica/McMurdo": Zone(None, None, "AO", "Antartica/McMurdo",
                                       ["McMurdo Station", "Ross Island"])}

        >>> zones = Zones(open("timezones"))
        >>> for value in sorted(zones.values(),
        ...                     lambda x, y: cmp(x.zone, y.zone)):
        ...     print(value)
        Africa/Luanda (AO: 08°48'00"S, 013°14'00"E)
        America/Curacao (AN: 12°11'00"N, 069°00'00"W)
        Antarctica/McMurdo (AQ: 77°50'00"S, 166°36'00"E also McMurdo Station,
        Ross Island)

        @type data: C{file}, C{list} or C{str}
        @param data: zone.tab data to read
        @rtype: C{dict}
        @return: Locations with C{Zone} objects
        @raise FileFormatError: Unknown file format
        """
        data = utils.prepare_read(data)

        for line in data:
            if line.startswith("#"):
                continue
            line = line.strip()
            chunk = line.split("	")
            if not len(chunk) in (3, 4):
                raise utils.FileFormatError("ftp://elsie.nci.nih.gov/pub/")
            country, location, zone = chunk[:3]
            comments = chunk[3].split(", ") if len(chunk) == 4 else None
            self[zone] = Zone(location, country, zone, comments)

    def dump_zone_file(self):
        """
        Generate a zoneinfo compatible zone description table

        >>> zones = Zones(open("timezones"))
        >>> Zones.dump_zone_file(zones)
        ['AN\\t+121100-0690000\\tAmerica/Curacao',
         'AO\\t-084800+0131400\\tAfrica/Luanda',
         'AQ\\t-775000+1663600\\tAntarctica/McMurdo\\tMcMurdo Station, Ross Island']

        @rtype: C{list}
        @returns: zoneinfo descriptions
        """

        data = []
        for zone in sorted(self.values(),
                           lambda x, y: cmp(x.country, y.country)):
            text = "%s	%s	%s" % (zone.country,
                                   utils.to_iso6709(zone.latitude,
                                                    zone.longitude,
                                                    format="dms")[:-1],
                                   zone.zone)
            if zone.comments:
                text += "	%s" % ", ".join(zone.comments)
            data.append(text)
        return data

