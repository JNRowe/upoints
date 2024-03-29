#
"""nmea - Imports GPS NMEA-formatted data files."""
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

import datetime
import logging

from functools import reduce
from operator import xor

from . import point, utils


def calc_checksum(sentence):
    """Calculate a NMEA 0183 checksum for the given sentence.

    NMEA checksums are a simple XOR of all the characters in the sentence
    between the leading ``$`` symbol, and the ``*`` checksum separator.

    Args:
        sentence (str): NMEA 0183 formatted sentence
    """
    if sentence.startswith('$'):
        sentence = sentence[1:]
    sentence = sentence.split('*')[0]
    return reduce(xor, map(ord, sentence))


def nmea_latitude(latitude):
    """Generate a NMEA-formatted latitude pair.

    Args:
        latitude (float): Latitude to convert

    Returns:
        tuple: NMEA-formatted latitude values
    """
    return (
        '%02i%07.4f' % utils.to_dms(abs(latitude), 'dm'),
        'N' if latitude >= 0 else 'S',
    )


def nmea_longitude(longitude):
    """Generate a NMEA-formatted longitude pair.

    Args:
        longitude (float): Longitude to convert

    Returns:
        tuple: NMEA-formatted longitude values
    """
    return (
        '%03i%07.4f' % utils.to_dms(abs(longitude), 'dm'),
        'E' if longitude >= 0 else 'W',
    )


def parse_latitude(latitude, hemisphere):
    """Parse a NMEA-formatted latitude pair.

    Args:
        latitude (str): Latitude in DDMM.MMMM
        hemisphere (str): North or South

    Returns:
        float: Decimal representation of latitude
    """
    latitude = int(latitude[:2]) + float(latitude[2:]) / 60
    if hemisphere == 'S':
        latitude = -latitude
    elif not hemisphere == 'N':
        raise ValueError(f'Incorrect North/South value {hemisphere!r}')
    return latitude


def parse_longitude(longitude, hemisphere):
    """Parse a NMEA-formatted longitude pair.

    Args:
        longitude (str): Longitude in DDDMM.MMMM
        hemisphere (str): East or West

    Returns:
        float: Decimal representation of longitude
    """
    longitude = int(longitude[:3]) + float(longitude[3:]) / 60
    if hemisphere == 'W':
        longitude = -longitude
    elif not hemisphere == 'E':
        raise ValueError(f'Incorrect North/South value {hemisphere!r}')
    return longitude


#: NMEA’s mapping of code to reading type
MODE_INDICATOR = {
    'A': 'Autonomous',
    'D': 'Differential',
    'E': 'Estimated',
    'M': 'Manual',
    'S': 'Simulated',
    'N': 'Invalid',
}


class LoranPosition(point.Point):
    """Class for representing a GPS NMEA-formatted Loran-C position."""

    def __init__(self, latitude, longitude, time, status, mode=None):
        """Initialise a new ``LoranPosition`` object.

        Args:
            latitude (float): Fix’s latitude
            longitude (float): Fix’s longitude
            time (datetime.time): Time the fix was taken
            status (bool): Whether the data is active
            mode (str): Type of reading
        """
        super(LoranPosition, self).__init__(latitude, longitude)
        self.time = time
        self.status = status
        self.mode = mode

    def __str__(self, talker='GP'):
        """Pretty printed position string.

        Args:
            talker (str): Talker ID

        Returns:
            str: Human readable string representation of ``Position`` object
        """
        if not len(talker) == 2:
            raise ValueError(f'Talker ID must be two characters {talker!r}')
        data = [f'{talker}GLL']
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append(
            '%s.%02i'
            % (self.time.strftime('%H%M%S'), self.time.microsecond / 1000000)
        )
        data.append('A' if self.status else 'V')
        if self.mode:
            data.append(self.mode)
        data = ','.join(data)
        return '$%s*%02X\r' % (data, calc_checksum(data))

    def mode_string(self):
        """Return a string version of the reading mode information.

        Returns:
            str: Quality information as string
        """
        return MODE_INDICATOR.get(self.mode, 'Unknown')

    @staticmethod
    def parse_elements(elements):
        """Parse position data elements.

        Args:
            elements (list): Data values for fix

        Returns:
            Fix: Fix object representing data
        """
        if not len(elements) in (6, 7):
            raise ValueError('Invalid GLL position data')
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[0], elements[1])
        longitude = parse_longitude(elements[2], elements[3])
        hour, minute, second = [
            int(elements[4][i : i + 2]) for i in range(0, 6, 2)
        ]
        usecond = int(elements[4][6:8]) * 10000
        time = datetime.time(hour, minute, second, usecond)
        active = True if elements[5] == 'A' else False
        mode = elements[6] if len(elements) == 7 else None
        return LoranPosition(latitude, longitude, time, active, mode)


class Position(point.Point):
    """Class for representing a GPS NMEA-formatted position.

    .. versionadded:: 0.8.0
    """

    def __init__(
        self,
        time,
        status,
        latitude,
        longitude,
        speed,
        track,
        date,
        variation,
        mode=None,
    ):
        """Initialise a new ``Position`` object.

        Args:
            time (datetime.time): Time the fix was taken
            status (bool): Whether the data is active
            latitude (float): Fix’s latitude
            longitude (float): Fix’s longitude
            speed (float): Ground speed
            track (float): Track angle
            date (datetime.date): Date when position was taken
            variation (float): Magnetic variation
            mode (str): Type of reading
        """
        super(Position, self).__init__(latitude, longitude)
        self.time = time
        self.status = status
        self.speed = speed
        self.track = track
        self.date = date
        self.variation = variation
        self.mode = mode

    def __str__(self):
        """Pretty printed position string.

        Returns:
            str: Human readable string representation of ``Position`` object
        """
        data = ['GPRMC']
        data.append(self.time.strftime('%H%M%S'))
        data.append('A' if self.status else 'V')
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append('%.1f' % self.speed)
        data.append('%.1f' % self.track)
        data.append(self.date.strftime('%d%m%y'))
        if self.variation == int(self.variation):
            data.append('%i' % abs(self.variation))
        else:
            data.append('%.1f' % abs(self.variation))
        data.append('E' if self.variation >= 0 else 'W')
        if self.mode:
            data.append(self.mode)
        data = ','.join(data)
        return '$%s*%02X\r' % (data, calc_checksum(data))

    def mode_string(self):
        """Return a string version of the reading mode information.

        Returns:
            str: Quality information as string
        """
        return MODE_INDICATOR.get(self.mode, 'Unknown')

    @staticmethod
    def parse_elements(elements):
        """Parse position data elements.

        Args:
            elements (list): Data values for position

        Returns:
            Position: Position object representing data
        """
        if not len(elements) in (11, 12):
            raise ValueError('Invalid RMC position data')
        time = datetime.time(
            *[int(elements[0][i : i + 2]) for i in range(0, 6, 2)]
        )
        active = True if elements[1] == 'A' else False
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[2], elements[3])
        longitude = parse_longitude(elements[4], elements[5])
        speed = float(elements[6])
        track = float(elements[7])
        date = datetime.date(
            2000 + int(elements[8][4:6]),
            int(elements[8][2:4]),
            int(elements[8][:2]),
        )
        variation = float(elements[9]) if not elements[9] == '' else None
        if elements[10] == 'W':
            variation = -variation
        elif variation and not elements[10] == 'E':
            raise ValueError(f'Incorrect variation value {elements[10]!r}')
        mode = elements[11] if len(elements) == 12 else None
        return Position(
            time,
            active,
            latitude,
            longitude,
            speed,
            track,
            date,
            variation,
            mode,
        )


class Fix(point.Point):
    """Class for representing a GPS NMEA-formatted system fix.

    .. versionadded:: 0.8.0
    """

    fix_quality = [
        'Invalid',
        'GPS',
        'DGPS',
        'PPS',
        'Real Time Kinematic' 'Float RTK',
        'Estimated',
        'Manual',
        'Simulation',
    ]

    def __init__(
        self,
        time,
        latitude,
        longitude,
        quality,
        satellites,
        dilution,
        altitude,
        geoid_delta,
        dgps_delta=None,
        dgps_station=None,
        mode=None,
    ):
        """Initialise a new ``Fix`` object.

        Args:
            time (datetime.time): Time the fix was taken
            latitude (float): Fix’s latitude
            longitude (float): Fix’s longitude
            quality (int): Mode under which the fix was taken
            satellites (int): Number of tracked satellites
            dilution (float): Horizontal dilution at reported position
            altitude (float): Altitude above MSL
            geoid_delta (float): Height of geoid’s MSL above WGS84 ellipsoid
            dgps_delta (float): Number of seconds since last DGPS sync
            dgps_station (int): Identifier of the last synced DGPS station
            mode (str): Type of reading
        """
        super(Fix, self).__init__(latitude, longitude)
        self.time = time
        self.quality = quality
        self.satellites = satellites
        self.dilution = dilution
        self.altitude = altitude
        self.geoid_delta = geoid_delta
        self.dgps_delta = dgps_delta
        self.dgps_station = dgps_station
        self.mode = mode

    def __str__(self):
        """Pretty printed location string.

        Returns:
            str: Human readable string representation of ``Fix`` object
        """
        data = ['GPGGA']
        data.append(self.time.strftime('%H%M%S'))
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append(str(self.quality))
        data.append('%02i' % self.satellites)
        data.append('%.1f' % self.dilution)
        data.append('%.1f' % self.altitude)
        data.append('M')
        data.append('-' if not self.geoid_delta else '%.1f' % self.geoid_delta)
        data.append('M')
        data.append('%.1f' % self.dgps_delta if self.dgps_delta else '')
        data.append('%04i' % self.dgps_station if self.dgps_station else '')
        data = ','.join(data)
        return '$%s*%02X\r' % (data, calc_checksum(data))

    def quality_string(self):
        """Return a string version of the quality information.

        Returns::
            str: Quality information as string
        """
        return self.fix_quality[self.quality]

    @staticmethod
    def parse_elements(elements):
        """Parse essential fix’s data elements.

        Args:
            elements (list): Data values for fix

        Returns:
            Fix: Fix object representing data
        """
        if not len(elements) in (14, 15):
            raise ValueError('Invalid GGA fix data')
        time = datetime.time(
            *[int(elements[0][i : i + 2]) for i in range(0, 6, 2)]
        )
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[1], elements[2])
        longitude = parse_longitude(elements[3], elements[4])
        quality = int(elements[5])
        if not 0 <= quality <= 9:
            raise ValueError(f'Invalid quality value {quality!r}')
        satellites = int(elements[6])
        if not 0 <= satellites <= 12:
            raise ValueError(f'Invalid number of satellites {satellites!r}')
        dilution = float(elements[7])
        altitude = float(elements[8])
        if elements[9] == 'F':
            altitude = altitude * 3.2808399
        elif not elements[9] == 'M':
            raise ValueError(f'Unknown altitude unit {elements[9]!r}')
        if elements[10] in ('-', ''):
            geoid_delta = False
            logging.warning(
                'Altitude data could be incorrect, as the geoid '
                'difference has not been provided'
            )
        else:
            geoid_delta = float(elements[10])
        if elements[11] == 'F':
            geoid_delta = geoid_delta * 3.2808399
        elif geoid_delta and not elements[11] == 'M':
            raise ValueError(f'Unknown geoid delta unit {elements[11]!r}')
        dgps_delta = float(elements[12]) if elements[12] else None
        dgps_station = int(elements[13]) if elements[13] else None
        mode = elements[14] if len(elements) == 15 else None
        return Fix(
            time,
            latitude,
            longitude,
            quality,
            satellites,
            dilution,
            altitude,
            geoid_delta,
            dgps_delta,
            dgps_station,
            mode,
        )


class Waypoint(point.Point):
    """Class for representing a NMEA-formatted waypoint.

    .. versionadded:: 0.8.0
    """

    def __init__(self, latitude, longitude, name):
        """Initialise a new ``Waypoint`` object.

        Args:
            latitude (float): Waypoint’s latitude
            longitude (float): Waypoint’s longitude
            name (str): Comment for waypoint
        """
        super(Waypoint, self).__init__(latitude, longitude)
        self.name = name.upper()

    def __str__(self):
        """Pretty printed location string.

        Returns:
            str: Human readable string representation of ``Waypoint`` object
        """
        data = ['GPWPL']
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append(self.name)
        data = ','.join(data)
        text = '$%s*%02X\r' % (data, calc_checksum(data))
        if len(text) > 81:
            raise ValueError(
                'All NMEA sentences must be less than 82 bytes '
                'including line endings'
            )
        return text

    @staticmethod
    def parse_elements(elements):
        """Parse waypoint data elements.

        Args:
            elements (list): Data values for fix

        Returns:
            nmea.Waypoint: Object representing data
        """
        if not len(elements) == 5:
            raise ValueError('Invalid WPL waypoint data')
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[0], elements[1])
        longitude = parse_longitude(elements[2], elements[3])
        name = elements[4]
        return Waypoint(latitude, longitude, name)


class Locations(point.Points):
    """Class for representing a group of GPS location objects.

    .. versionadded:: 0.8.0
    """

    def __init__(self, gpsdata_file=None):
        """Initialise a new ``Locations`` object."""
        super(Locations, self).__init__()
        self._gpsdata_file = gpsdata_file
        if gpsdata_file:
            self.import_locations(gpsdata_file)

    def import_locations(self, gpsdata_file, checksum=True):
        r"""Import GPS NMEA-formatted data files.

        ``import_locations()`` returns a list of `Fix` objects representing the
        fix sentences found in the GPS data.

        It expects data files in NMEA 0183 format, as specified in `the
        official documentation`_, which is ASCII text such as::

            $GPGSV,6,6,21,32,65,170,35*48
            $GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,*6B
            $GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E,A*2C
            $GPGSV,6,1,21,02,76,044,43,03,84,156,49,06,89,116,51,08,60,184,30*7C
            $GPGSV,6,2,21,09,87,321,50,10,77,243,44,11,85,016,49,12,89,100,52*7A
            $GPGSV,6,3,21,13,70,319,39,14,90,094,52,16,85,130,49,17,88,136,51*7E
            $GPGSV,6,4,21,18,57,052,27,24,65,007,34,25,62,142,32,26,88,031,51*73
            $GPGSV,6,5,21,27,64,343,33,28,45,231,16,30,84,198,49,31,90,015,52*7C
            $GPGSV,6,6,21,32,65,170,34*49
            $GPWPL,5200.9000,N,00013.2600,W,HOME*5E
            $GPGGA,142100,5200.9000,N,00316.6600,W,1,04,5.6,1000.0,M,34.5,M,,*68
            $GPRMC,142100,A,5200.9000,N,00316.6600,W,123142.7,188.1,191107,5,E,A*21

        The reader only imports the GGA, or GPS fix, sentences currently but
        future versions will probably support tracks and waypoints.  Other than
        that the data is out of scope for ``upoints``.

        The above file when processed by ``import_locations()`` will return the
        following ``list`` object::

            [Fix(datetime.time(14, 20, 58), 53.1440233333, -3.01542833333, 1,
                 4, 5.6, 1374.6, 34.5, None, None),
             Position(datetime.time(14, 20, 58), True, 53.1440233333,
                      -3.01542833333, 109394.7, 202.9,
                      datetime.date(2007, 11, 19), 5.0, 'A'),
             Waypoint(52.015, -0.221, 'Home'),
             Fix(datetime.time(14, 21), 52.015, -3.27766666667, 1, 4, 5.6,
                 1000.0, 34.5, None, None),
             Position(datetime.time(14, 21), True, 52.015, -3.27766666667,
                      123142.7, 188.1, datetime.date(2007, 11, 19), 5.0, 'A')]

        Note:
            The standard is quite specific in that sentences *must* be less
            than 82 bytes, while it would be nice to add yet another validity
            check it isn't all that uncommon for devices to break this
            requirement in their “extensions” to the standard.

        .. todo:: Add optional check for message length, on by default

        Args:
            gpsdata_file (iter): NMEA data to read
            checksum (bool): Whether checksums should be tested

        Returns:
            list: Series of locations taken from the data

        .. _the official documentation: http://en.wikipedia.org/wiki/NMEA_0183
        """
        self._gpsdata_file = gpsdata_file
        data = utils.prepare_read(gpsdata_file)

        parsers = {
            'GPGGA': Fix,
            'GPRMC': Position,
            'GPWPL': Waypoint,
            'GPGLL': LoranPosition,
            'LCGLL': LoranPosition,
        }

        if not checksum:
            logging.warning(
                'Disabling the checksum tests should only be used'
                'when the device is incapable of emitting the '
                'correct values!'
            )
        for line in data:
            # The standard tells us lines should end in \r\n even though some
            # devices break this, but Python’s standard file object solves this
            # for us anyway.  However, be careful if you implement your own
            # opener.
            if not line[1:6] in parsers:
                continue
            if checksum:
                values, checksum = line[1:].split('*')
                if not calc_checksum(values) == int(checksum, 16):
                    raise ValueError('Sentence has invalid checksum')
            else:
                values = line[1:].split('*')[0]
            elements = values.split(',')
            parser = parsers[elements[0]].parse_elements
            self.append(parser(elements[1:]))
