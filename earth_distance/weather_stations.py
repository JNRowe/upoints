#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""weather_stations - Imports weather station data files"""
# Copyright (C) 2007 James Rowe;
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111, USA.
#

__bug_report__ = "James Rowe <jnrowe@ukfsn.org>"

import os
import sys

import trigpoints

class Station(trigpoints.Trigpoint):
    """
    Class for representing a weather station from a NOAA data file

    @ivar alt_id: Alternate location identifier(either ICAO or WMO)
    @ivar name: Station's name
    @ivar state: State name, if station is in the US
    @ivar country: Country name
    @ivar WMO: WMO region code
    @ivar latitude: Station's latitude
    @ivar longitude: Station's longitude
    @ivar ua_latitude: Station's upper air latitude
    @ivar ua_longitude: Station's upper air longitude
    @ivar altitude: Station's elevation
    @ivar ua_altitude: Station's upper air elevation
    @ivar RBSN: True if station belongs to RSBN
    """

    __slots__ = ('alt_id', 'state', 'country', 'WMO', 'ua_latitude',
                 'ua_longitude', 'ua_altitude', 'RBSN')

    def __init__(self, alt_id, name, state, country, WMO, latitude, longitude,
                 ua_latitude, ua_longitude, altitude, ua_altitude, RBSN):
        """
        Initialise a new Station object

        @type alt_id: C{str} or C{None}
        @param alt_id: Alternate location identifier
        @type name: C{str}
        @param name: Station's name
        @type state: C{str} or C{None}
        @param state: State name, if station is in the US
        @type country: C{str}
        @param country: Country name
        @type WMO: C{int}
        @param WMO: WMO region code
        @type latitude: C{float}
        @param latitude: Station's latitude
        @type longitude: C{float}
        @param longitude: Station's longitude
        @type ua_latitude: C{float} or C{None}
        @param ua_latitude: Station's upper air latitude
        @type ua_longitude: C{float} or C{None}
        @param ua_longitude: Station's upper air longitude
        @type altitude: C{int} or C{None}
        @param altitude: Station's elevation
        @type ua_altitude: C{int} or C{None}
        @param ua_altitude: Station's upper air elevation
        @type RBSN: C{bool}
        @param RBSN: True if station belongs to RSBN
        """
        trigpoints.Trigpoint.__init__(self, latitude, longitude, altitude, name)
        self.alt_id = alt_id
        self.state = state
        self.country = country
        self.WMO = WMO
        self.ua_latitude = ua_latitude
        self.ua_longitude = ua_longitude
        self.ua_altitude = ua_altitude
        self.RBSN = RBSN

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Station('EGLL', 'London / Heathrow Airport', None, 'United Kingdom', 6, 51.4833333333, -0.45, None, None, 24, 0, True)
        Station("EGLL", "London / Heathrow Airport", None, "United Kingdom", 6, 51.4833333333, -0.45, None, None, 24, 0, True)

        @rtype: C{str}
        @return: String to recreate Station object
        """
        data = []
        for i in (self.alt_id, self.name, self.state, self.country, self.WMO,
                  self.latitude, self.longitude, self.ua_latitude,
                  self.ua_longitude, self.altitude, self.ua_altitude,
                  self.RBSN):
            if i is None:
                data.append("None")
            elif isinstance(i, str):
                data.append('"%s"' % str(i))
            else:
                data.append(str(i))
        return "Station(" + ", ".join(data) + ")"

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        @see: C{trigpoints.point.Point}

        >>> Heathrow = Station("EGLL", "London / Heathrow Airport", None, "United Kingdom", 6, 51.048333, -0.450000, None, None, 24, 0, True)
        >>> print Heathrow
        London / Heathrow Airport (EGLL - N51.048°; W000.450°)
        >>> print Heathrow.__str__(mode="dms")
        London / Heathrow Airport (EGLL - 51°02'53"N, 000°27'00"W)
        >>> print Heathrow.__str__(mode="dm")
        London / Heathrow Airport (EGLL - 51°02.88'N, 000°27.00'W)
        >>> Heathrow.alt_id = None
        >>> print Heathrow
        London / Heathrow Airport (N51.048°; W000.450°)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of Point object
        """
        text = super(Station.__base__, self).__str__(mode)

        if self.alt_id:
            return "%s (%s - %s)" % (self.name, self.alt_id, text)
        else:
            return "%s (%s)" % (self.name, text)

def import_NOAA_file(data, index="WMO"):
    """
    C{import_NOAA_file()} returns a dictionary with keys containing the WMO
    identifer, and values consisting of a C{trigpoints.Trigpoint} object and
    a large variety of other information available in the data exported by
    U{NOAA <http://weather.noaa.gov/>}.

    It expects data files in one of the following formats::

        00;000;PABL;Buckland, Buckland Airport;AK;United States;4;65-58-56N;161-09-07W;;;7;;
        01;001;ENJA;Jan Mayen;;Norway;6;70-56N;008-40W;70-56N;008-40W;10;9;P
        01;002;----;Grahuken;;Norway;6;79-47N;014-28E;;;;15;

    or::

        AYMD;94;014;Madang;;Papua New Guinea;5;05-13S;145-47E;05-13S;145-47E;3;5;P
        AYMO;--;---;Manus Island/Momote;;Papua New Guinea;5;02-03-43S;147-25-27E;;;4;;
        AYPY;94;035;Moresby;;Papua New Guinea;5;09-26S;147-13E;09-26S;147-13E;38;49;P

    Files containing the data in this format can be downloaded from NOAA's site
    in their U{station location page <http://weather.noaa.gov/tg/site.shtml>}.

    WMO indexed files downloaded from the NOAA site when processed by
    C{import_NOAA_file()} will return C{dict} object of the following style::

        '00000': ('PABL', 'Buckland, Buckland Airport', 'AK', 'United States', 4, 65.982222. -160.848055, None, None, 7, False),
        '01001'; ('ENJA', Jan Mayen, None, 'Norway', 6, 70.933333, -7.333333, 70.933333, -7.333333, 10, 9, True),
        '01002': (None, 'Grahuken', None, 'Norway', 6, 79.783333, 13.533333, None, None, 15, False),

    And C{dict} objects such as the following will be created when ICAO indexed
    data files are processed::

        'AYMD': ("94", "014", "Madang", None, "Papua New Guinea", 5, -5.216666, 145.783333, -5.216666, 145.78333333333333, 3, 5, True,
        'AYMO': (None, None, "Manus Island/Momote", None, "Papua New Guinea", 5, -2.061944, 147.424166, None, None, 4, False,
        'AYPY': ("94", "035", "Moresby", None, "Papua New Guinea", 5, -9.433333, 147.216667, -9.433333, 147.216667, 38, 49, True,

    >>> import StringIO
    >>> stations_file = StringIO.StringIO("\\n".join([
    ...     '00;000;PABL;Buckland, Buckland Airport;AK;United States;4;65-58-56N;161-09-07W;;;7;;',
    ...     '01;001;ENJA;Jan Mayen;;Norway;6;70-56N;008-40W;70-56N;008-40W;10;9;P',
    ...     '01;002;----;Grahuken;;Norway;6;79-47N;014-28E;;;;15;']))
    >>> stations = import_NOAA_file(stations_file)
    >>> for key, value in sorted(stations.items()):
    ...     print key, '-', value
    00000 - Buckland, Buckland Airport (PABL - N65.982°; W161.152°)
    01001 - Jan Mayen (ENJA - N70.933°; W008.667°)
    01002 - Grahuken (N79.783°; E014.467°)
    >>> stations_file = StringIO.StringIO("\\n".join([
    ...     'AYMD;94;014;Madang;;Papua New Guinea;5;05-13S;145-47E;05-13S;145-47E;3;5;P',
    ...     'AYMO;--;---;Manus Island/Momote;;Papua New Guinea;5;02-03-43S;147-25-27E;;;4;;',
    ...     'AYPY;94;035;Moresby;;Papua New Guinea;5;09-26S;147-13E;09-26S;147-13E;38;49;P']))
    >>> stations = import_NOAA_file(stations_file, "ICAO")
    >>> for key, value in sorted(stations.items()):
    ...     print key, '-', value
    AYMD - Madang (94014 - S05.217°; E145.783°)
    AYMO - Manus Island/Momote (S02.062°; E147.424°)
    AYPY - Moresby (94035 - S09.433°; E147.217°)

    @type data: C{file}, C{list} or C{str}
    @param data: NOAA station data to read
    @rtype: C{dict}
    @return: WMO locations with C{Point} objects and associated data
    @raise ValueError: Invalid value for data
    @raise ValueError: Unknown file format
    """
    if hasattr(data, "readlines"):
        data = data.readlines()
    elif isinstance(data, list):
        pass
    elif isinstance(data, str):
        if os.path.isfile(data):
            data = open(data).readlines()
    else:
        raise ValueError("Unable to handle data of type `%s`" % type(data))
    stations = {}
    for line in data:
        line = line.strip()
        chunk = line.split(";")
        if not len(chunk) == 14:
            if index == "ICAO":
                # Some entries only have 12 or 13 elements, so we assume 13 and
                # 14 are None.  Of the entries I've hand checked this assumption
                # would be correct.
                chunk.extend(["", ""])
            elif index == "WMO" and len(chunk) == 13:
                # A few of the WMO indexed entries are missing their RBSN
                # fields, hand checking the entries for 71046 and 71899 shows
                # that they are correct if we just assume RBSN is false.
                chunk.append("")
            else:
                raise ValueError("Incorrect data format, if you're using a "
                                 "file downloaded from NOAA please report this "
                                 "to %s." % __bug_report__)
        if index == "WMO":
            identifier = "".join(chunk[:2])
            alt_id = chunk[2] if not chunk[2] == "----" else None
        elif index == "ICAO":
            identifier = chunk[0]
            alt_id = "".join(chunk[1:3])
            if alt_id == "-----":
                alt_id = None
        else:
            raise ValueError("Unknown format `%s'" % index)
        name = chunk[3]
        state = chunk[4] if not chunk[4] == "" else None 
        country = chunk[5]
        WMO = int(chunk[6]) if not chunk[6] == "" else None
        point_data = []
        for i in chunk[7:11]:
            if i == "":
                point_data.append(None)
                continue
            if ' ' in i:
                # Some entries in nsd_cccc.txt are of the format "DD-MM-  N",
                # so we just take the spaces to mean 0 seconds.
                i = i.replace(" ", "0")
            values = [int(x) for x in i[:-1].split("-")]
            if i[-1] in ("S", "W"):
                values = [-i for i in values]
            point_data.append(trigpoints.point.utils.to_dd(*values))
        latitude, longitude, ua_latitude, ua_longitude = point_data
        altitude = int(chunk[11]) if not chunk[11] == "" else None
        ua_altitude = int(chunk[12]) if not chunk[12] == "" else None
        RBSN = False if chunk[13] == "" else True
        stations[identifier] = Station(alt_id, name, state, country, WMO,
                                       latitude, longitude, ua_latitude,
                                       ua_longitude, altitude, ua_altitude,
                                       RBSN)
    return stations

if __name__ == '__main__':
    import doctest
    sys.exit(doctest.testmod(optionflags=doctest.REPORT_UDIFF)[0])

