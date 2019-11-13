#
"""weather_stations - Imports weather station data files."""
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

import logging

from . import (point, trigpoints, utils)


class Station(trigpoints.Trigpoint):
    """Class for representing a weather station from a NOAA data file.

    .. versionadded:: 0.2.0
    """

    __slots__ = ('alt_id', 'state', 'country', 'wmo', 'ua_latitude',
                 'ua_longitude', 'ua_altitude', 'rbsn')

    def __init__(self, alt_id, name, state, country, wmo, latitude, longitude,
                 ua_latitude, ua_longitude, altitude, ua_altitude, rbsn):
        """Initialise a new ``Station`` object.

        Args:
            alt_id (str): Alternate location identifier
            name (str): Station's name
            state (str): State name, if station is in the US
            country (str): Country name
            wmo (int): WMO region code
            latitude (float): Station's latitude
            longitude (float): Station's longitude
            ua_latitude (float): Station's upper air latitude
            ua_longitude (float): Station's upper air longitude
            altitude (int): Station's elevation
            ua_altitude (int): Station's upper air elevation
            rbsn (bool): True if station belongs to RSBN
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

    def __str__(self):
        """Pretty printed location string.

        See also:
           ``trigpoints.point.Point``

        Returns:
            str: Human readable string representation of ``Station`` object
        """
        return self.__format__()

    def __format__(self, format_spec='dd'):
        """Extended pretty printing for location strings.

        Args:
            format_spec str: Coordinate formatting system to use

        Returns:
            Human readable string representation of ``Point`` object

        Raises:
            ValueError: Unknown value for ``format_spec``
        """
        text = super(Station.__base__, self).__format__(format_spec)

        if self.alt_id:
            return '%s (%s - %s)' % (self.name, self.alt_id, text)
        else:
            return '%s (%s)' % (self.name, text)


class Stations(point.KeyedPoints):
    """Class for representing a group of `Station` objects.

    .. versionadded:: 0.5.1
    """

    def __init__(self, data=None, index='WMO'):
        """Initialise a new `Stations` object."""
        super(Stations, self).__init__()
        self._data = data
        self._index = index
        if data:
            self.import_locations(data, index)

    def import_locations(self, data, index='WMO'):
        """Parse NOAA weather station data files.

        ``import_locations()`` returns a dictionary with keys containing either
        the WMO or ICAO identifier, and values that are ``Station`` objects
        that describes the large variety of data exported by NOAA_.

        It expects data files in one of the following formats::

            00;000;PABL;Buckland, Buckland Airport;AK;United States;4;65-58-56N;161-09-07W;;;7;;
            01;001;ENJA;Jan Mayen;;Norway;6;70-56N;008-40W;70-56N;008-40W;10;9;P
            01;002;----;Grahuken;;Norway;6;79-47N;014-28E;;;;15;

        or::

            AYMD;94;014;Madang;;Papua New Guinea;5;05-13S;145-47E;05-13S;145-47E;3;5;P
            AYMO;--;---;Manus Island/Momote;;Papua New Guinea;5;02-03-43S;147-25-27E;;;4;;
            AYPY;94;035;Moresby;;Papua New Guinea;5;09-26S;147-13E;09-26S;147-13E;38;49;P

        Files containing the data in this format can be downloaded from the
        :abbr:`NOAA (National Oceanographic and Atmospheric Administration)`'s
        site in their `station location page`_.

        WMO indexed files downloaded from the :abbr:`NOAA (National
        Oceanographic and Atmospheric Administration)` site when processed by
        ``import_locations()`` will return ``dict`` object of the following
        style::

            {'00000': Station('PABL', 'Buckland, Buckland Airport', 'AK',
                              'United States', 4, 65.982222. -160.848055, None,
                              None, 7, False),
             '01001'; Station('ENJA', Jan Mayen, None, 'Norway', 6, 70.933333,
                              -7.333333, 70.933333, -7.333333, 10, 9, True),
             '01002': Station(None, 'Grahuken', None, 'Norway', 6, 79.783333,
                              13.533333, None, None, 15, False)}

        And ``dict`` objects such as the following will be created when ICAO
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

        Args:
            data (iter): NOAA station data to read
            index (str): The identifier type used in the file

        Returns:
            dict: WMO locations with `Station` objects

        Raises:
            FileFormatError: Unknown file format

        .. _NOAA: http://weather.noaa.gov/
        .. _station location page: http://weather.noaa.gov/tg/site.shtml
        """
        self._data = data
        data = utils.prepare_read(data)

        for line in data:
            line = line.strip()
            chunk = line.split(';')
            if not len(chunk) == 14:
                if index == 'ICAO':
                    # Some entries only have 12 or 13 elements, so we assume 13
                    # and 14 are None.  Of the entries I've hand checked this
                    # assumption would be correct.
                    logging.debug('Extending ICAO %r entry, because it is '
                                  'too short to process' % line)
                    chunk.extend(['', ''])
                elif index == 'WMO' and len(chunk) == 13:
                    # A few of the WMO indexed entries are missing their RBSN
                    # fields, hand checking the entries for 71046 and 71899
                    # shows that they are correct if we just assume RBSN is
                    # false.
                    logging.debug('Extending WMO %r entry, because it is '
                                  'too short to process' % line)
                    chunk.append('')
                else:
                    raise utils.FileFormatError('NOAA')
            if index == 'WMO':
                identifier = ''.join(chunk[:2])
                alt_id = chunk[2]
            elif index == 'ICAO':
                identifier = chunk[0]
                alt_id = ''.join(chunk[1:3])
            else:
                raise ValueError('Unknown format %r' % index)
            if alt_id in ('----', '-----'):
                alt_id = None
            name = chunk[3]
            state = chunk[4] if chunk[4] else None
            country = chunk[5]
            wmo = int(chunk[6]) if chunk[6] else None
            point_data = []
            for i in chunk[7:11]:
                if not i:
                    point_data.append(None)
                    continue
                # Some entries in nsd_cccc.txt are of the format "DD-MM-
                # N", so we just take the spaces to mean 0 seconds.
                if ' ' in i:
                    logging.debug('Fixing unpadded location data in %r entry'
                                  % line)
                    i = i.replace(' ', '0')
                values = map(int, i[:-1].split('-'))
                if i[-1] in ('S', 'W'):
                    values = [-x for x in values]
                point_data.append(point.utils.to_dd(*values))
            latitude, longitude, ua_latitude, ua_longitude = point_data
            altitude = int(chunk[11]) if chunk[11] else None
            ua_altitude = int(chunk[12]) if chunk[12] else None
            rbsn = False if not chunk[13] else True
            self[identifier] = Station(alt_id, name, state, country, wmo,
                                       latitude, longitude, ua_latitude,
                                       ua_longitude, altitude, ua_altitude,
                                       rbsn)
