#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""weather_stations - Imports weather station data files"""
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

import logging

from earth_distance import (trigpoints, utils)

class Station(trigpoints.Trigpoint):
    """
    Class for representing a weather station from a NOAA data file

    @since: 0.2.0

    @ivar alt_id: Alternate location identifier(either ICAO or WMO)
    @ivar name: Station's name
    @ivar state: State name, if station is in the US
    @ivar country: Country name
    @ivar wmo: WMO region code
    @ivar latitude: Station's latitude
    @ivar longitude: Station's longitude
    @ivar ua_latitude: Station's upper air latitude
    @ivar ua_longitude: Station's upper air longitude
    @ivar altitude: Station's elevation
    @ivar ua_altitude: Station's upper air elevation
    @ivar rbsn: True if station belongs to RSBN
    """

    __slots__ = ('alt_id', 'state', 'country', 'wmo', 'ua_latitude',
                 'ua_longitude', 'ua_altitude', 'rbsn')

    def __init__(self, alt_id, name, state, country, wmo, latitude, longitude,
                 ua_latitude, ua_longitude, altitude, ua_altitude, rbsn):
        """
        Initialise a new C{Station} object

        @type alt_id: C{str} or C{None}
        @param alt_id: Alternate location identifier
        @type name: C{str}
        @param name: Station's name
        @type state: C{str} or C{None}
        @param state: State name, if station is in the US
        @type country: C{str}
        @param country: Country name
        @type wmo: C{int}
        @param wmo: WMO region code
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
        @type rbsn: C{bool}
        @param rbsn: True if station belongs to RSBN
        """
        super(Station, self).__init__(latitude, longitude, altitude, name)
        self.alt_id = alt_id
        self.state = state
        self.country = country
        self.wmo = wmo
        self.ua_latitude = ua_latitude
        self.ua_longitude = ua_longitude
        self.ua_altitude = ua_altitude
        self.rbsn = rbsn

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Station('EGLL', 'London / Heathrow Airport', None,
        ...         'United Kingdom', 6, 51.4833333333, -0.45, None, None, 24,
        ...         0, True)
        Station('EGLL', 'London / Heathrow Airport', None, 'United Kingdom', 6,
                51.4833333333, -0.45, None, None, 24, 0, True)

        @rtype: C{str}
        @return: String to recreate C{Station} object
        """
        data = utils.repr_assist(self.alt_id, self.name, self.state,
                                 self.country, self.wmo, self.latitude,
                                 self.longitude, self.ua_latitude,
                                 self.ua_longitude, self.altitude,
                                 self.ua_altitude, self.rbsn)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        @see: C{trigpoints.point.Point}

        >>> Heathrow = Station("EGLL", "London / Heathrow Airport", None,
        ...                    "United Kingdom", 6, 51.048333, -0.450000, None,
        ...                    None, 24, 0, True)
        >>> print(Heathrow)
        London / Heathrow Airport (EGLL - N51.048°; W000.450°)
        >>> print(Heathrow.__str__(mode="dms"))
        London / Heathrow Airport (EGLL - 51°02'53"N, 000°27'00"W)
        >>> print(Heathrow.__str__(mode="dm"))
        London / Heathrow Airport (EGLL - 51°02.90'N, 000°27.00'W)
        >>> Heathrow.alt_id = None
        >>> print(Heathrow)
        London / Heathrow Airport (N51.048°; W000.450°)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Station} object
        """
        text = super(Station.__base__, self).__str__(mode)

        if self.alt_id:
            return "%s (%s - %s)" % (self.name, self.alt_id, text)
        else:
            return "%s (%s)" % (self.name, text)

class Stations(dict):
    """
    Class for representing a group of C{Station} objects

    @since: 0.5.1
    """

    def __init__(self, data=None, index="WMO"):
        """
        Initialise a new C{Stations} object
        """
        dict.__init__(self)
        if data:
            self.import_noaa_file(data, index)

    def import_noaa_file(self, data, index="WMO"):
        """
        Parse NOAA weather station data files

        C{import_noaa_file()} returns a dictionary with keys containing either
        the WMO or ICAO identifier, and values that are C{Station} objects that
        describes the large variety of data exported by U{NOAA
        <http://weather.noaa.gov/>}.

        It expects data files in one of the following formats::

            00;000;PABL;Buckland, Buckland Airport;AK;United States;4;65-58-56N;161-09-07W;;;7;;
            01;001;ENJA;Jan Mayen;;Norway;6;70-56N;008-40W;70-56N;008-40W;10;9;P
            01;002;----;Grahuken;;Norway;6;79-47N;014-28E;;;;15;

        or::

            AYMD;94;014;Madang;;Papua New Guinea;5;05-13S;145-47E;05-13S;145-47E;3;5;P
            AYMO;--;---;Manus Island/Momote;;Papua New Guinea;5;02-03-43S;147-25-27E;;;4;;
            AYPY;94;035;Moresby;;Papua New Guinea;5;09-26S;147-13E;09-26S;147-13E;38;49;P

        Files containing the data in this format can be downloaded from NOAA's
        site in their U{station location page
        <http://weather.noaa.gov/tg/site.shtml>}.

        WMO indexed files downloaded from the NOAA site when processed by
        C{import_noaa_file()} will return C{dict} object of the following
        style::

            {'00000': Station('PABL', 'Buckland, Buckland Airport', 'AK',
                              'United States', 4, 65.982222. -160.848055, None,
                              None, 7, False),
             '01001'; Station('ENJA', Jan Mayen, None, 'Norway', 6, 70.933333,
                              -7.333333, 70.933333, -7.333333, 10, 9, True),
             '01002': Station(None, 'Grahuken', None, 'Norway', 6, 79.783333,
                              13.533333, None, None, 15, False)}

        And C{dict} objects such as the following will be created when ICAO
        indexed data files are processed::

            {'AYMD': Station("94", "014", "Madang", None, "Papua New Guinea",
                             5, -5.216666, 145.783333, -5.216666,
                             145.78333333333333, 3, 5, True,
             'AYMO': Station(None, None, "Manus Island/Momote", None,
                             "Papua New Guinea", 5, -2.061944, 147.424166,
                             None, None, 4, False,
             'AYPY': Station("94", "035", "Moresby", None, "Papua New Guinea",
                             5, -9.433333, 147.216667, -9.433333, 147.216667,
                             38, 49, True}

        >>> stations = Stations(open("WMO_stations"))
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        00000 - Buckland, Buckland Airport (PABL - N65.982°; W161.152°)
        01001 - Jan Mayen (ENJA - N70.933°; W008.667°)
        01002 - Grahuken (N79.783°; E014.467°)
        >>> stations = Stations(open("ICAO_stations"), "ICAO")
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        AYMD - Madang (94014 - S05.217°; E145.783°)
        AYMO - Manus Island/Momote (S02.062°; E147.424°)
        AYPY - Moresby (94035 - S09.433°; E147.217°)
        >>> stations = Stations(open("broken_WMO_stations"))
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        71046 - Komakuk Beach, Y. T. (CWKM - N69.617°; W140.200°)
        71899 - Langara, B. C. (CWLA - N54.250°; W133.133°)
        >>> stations = Stations(open("broken_ICAO_stations"), "ICAO")
        >>> for key, value in sorted(stations.items()):
        ...     print("%s - %s" % (key, value))
        KBRX - Bordeaux (N41.933°; W104.950°)
        KCQB - Chandler, Chandler Municipal Airport (N35.724°; W096.820°)

        @type data: C{file}, C{list} or C{str}
        @param data: NOAA station data to read
        @type index: C{str}
        @param index: The identifier type used in the file
        @rtype: C{dict}
        @return: WMO locations with C{Station} objects
        @raise FileFormatError: Unknown file format
        """
        data = utils.prepare_read(data)

        for line in data:
            line = line.strip()
            chunk = line.split(";")
            if not len(chunk) == 14:
                if index == "ICAO":
                    # Some entries only have 12 or 13 elements, so we assume 13
                    # and 14 are None.  Of the entries I've hand checked this
                    # assumption would be correct.
                    logging.debug("Extending ICAO `%s' entry, because it is "
                                  "too short to process" % line)
                    chunk.extend(["", ""])
                elif index == "WMO" and len(chunk) == 13:
                    # A few of the WMO indexed entries are missing their RBSN
                    # fields, hand checking the entries for 71046 and 71899
                    # shows that they are correct if we just assume RBSN is
                    # false.
                    logging.debug("Extending WMO `%s' entry, because it is "
                                  "too short to process" % line)
                    chunk.append("")
                else:
                    raise utils.FileFormatError("NOAA")
            if index == "WMO":
                identifier = "".join(chunk[:2])
                alt_id = chunk[2]
            elif index == "ICAO":
                identifier = chunk[0]
                alt_id = "".join(chunk[1:3])
            else:
                raise ValueError("Unknown format `%s'" % index)
            if alt_id in ("----", "-----"):
                alt_id = None
            name = chunk[3]
            state = chunk[4] if not chunk[4] == "" else None
            country = chunk[5]
            wmo = int(chunk[6]) if not chunk[6] == "" else None
            point_data = []
            for i in chunk[7:11]:
                if i == "":
                    point_data.append(None)
                    continue
                # Some entries in nsd_cccc.txt are of the format "DD-MM-
                # N", so we just take the spaces to mean 0 seconds.
                if " " in i:
                    logging.debug("Fixing unpadded location data in `%s' entry"
                                  % line)
                    i = i.replace(" ", "0")
                values = [int(x) for x in i[:-1].split("-")]
                if i[-1] in ("S", "W"):
                    values = [-i for i in values]
                point_data.append(trigpoints.point.utils.to_dd(*values))
            latitude, longitude, ua_latitude, ua_longitude = point_data
            altitude = int(chunk[11]) if not chunk[11] == "" else None
            ua_altitude = int(chunk[12]) if not chunk[12] == "" else None
            rbsn = False if chunk[13] == "" else True
            self[identifier] = Station(alt_id, name, state, country, wmo,
                                       latitude, longitude, ua_latitude,
                                       ua_longitude, altitude, ua_altitude,
                                       rbsn)

