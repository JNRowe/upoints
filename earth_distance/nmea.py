#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""nmea - Imports GPS NMEA-formatted data files"""
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

import datetime
import logging

from earth_distance import (point, utils)

def calc_checksum(sentence):
    """
    Calculate a NMEA 0183 checksum for the given sentence

    NMEA checksums are a simple XOR of all the characters in the sentence
    between the leading "$" symbol, and the "*" checksum separator.

    @type sentence: C{str}
    @param sentence: NMEA 0183 formatted sentence
    """
    if sentence.startswith("$"):
        sentence = sentence[1:]
    if "*" in sentence:
        sentence = sentence.split("*")[0]
    return reduce(lambda x, y: x^y, [ord(i) for i in sentence])

def nmea_latitude(latitude):
    """
    Generate a NMEA-formatted latitude pair

    >>> nmea_latitude(53.144023333333337)
    ('5308.6414', 'N')

    @type latitude: C{float} or coercible to C{float}
    @param latitude: Latitude to convert
    @rtype: C{tuple}
    @return: NMEA-formatted latitude values
    """
    return ("%02i%07.4f" % utils.to_dms(abs(latitude), "dm"),
            "N" if latitude >= 0 else "S")

def nmea_longitude(longitude):
    """
    Generate a NMEA-formatted longitude pair

    >>> nmea_longitude(-3.0154283333333334)
    ('00300.9257', 'W')

    @type longitude: C{float} or coercible to C{float}
    @param longitude: Longitude to convert
    @rtype: C{tuple}
    @return: NMEA-formatted longitude values
    """
    return ("%03i%07.4f" % utils.to_dms(abs(longitude), "dm"),
            "E" if longitude >= 0 else "W")

def parse_latitude(latitude, hemisphere):
    """
    Parse a NMEA-formatted latitude pair

    >>> parse_latitude("5308.6414", "N")
    53.144023333333337

    @type latitude: C{str}
    @param latitude: Latitude in DDMM.MMMM
    @type hemisphere: C{str}
    @param hemisphere: North or South
    @rtype: C{float}
    @return: Decimal representation of latitude
    """
    latitude = int(latitude[:2]) + float(latitude[2:]) / 60
    if hemisphere == "S":
        latitude = -latitude
    elif not hemisphere == "N":
        raise ValueError("Incorrect North/South value `%s'" % hemisphere)
    return latitude

def parse_longitude(longitude, hemisphere):
    """
    Parse a NMEA-formatted longitude pair

    >>> parse_longitude("00300.9257", "W")
    -3.0154283333333334

    @type longitude: C{str}
    @param longitude: Longitude in DDDMM.MMMM
    @type hemisphere: C{str}
    @param hemisphere: East or West
    @rtype: C{float}
    @return: Decimal representation of longitude
    """
    longitude = int(longitude[:3]) + float(longitude[3:]) / 60
    if hemisphere == "W":
        longitude = -longitude
    elif not hemisphere == "E":
        raise ValueError("Incorrect North/South value `%s'" % hemisphere)
    return longitude

MODE_INDICATOR = {
    "A": "Autonomous",
    "D": "Differential",
    "E": "Estimated",
    "M": "Manual",
    "S": "Simulated",
    "N": "Invalid",
}

class Position(point.Point):
    """
    Class for representing a GPS NMEA-formatted position

    @ivar time: Time the position was taken
    @ivar status: GPS status
    @ivar latitude: Unit's latitude
    @ivar longitude: Unit's longitude
    @ivar speed: Unit's speed in knots
    @ivar track: Track angle
    @ivar date: Date when position was taken
    @ivar variation: Magnetic variation
    @ivar mode: Type of reading
    """

    __slots__ = ('time', 'status', 'speed', 'track', 'date', 'variation',
                 'mode')

    def __init__(self, time, status, latitude, longitude, speed, track, date,
                 variation, mode=None):
        """
        Initialise a new C{Position} object

        @type time: C{datetime.time}
        @param time: Time the fix was taken
        @type status: C{bool}
        @param status: Whether the data is active
        @type latitude: C{float} or coercible to C{float}
        @param latitude: Fix's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Fix's longitude
        @type speed: C{float} or coercible to C{float}
        @param speed: Ground speed
        @type track: C{float} or coercible to C{float}
        @param track: Track angle
        @type date: C{datetime.date}
        @param date: Date when position was taken
        @type variation: C{float} or coercible to C{float}
        @param variation: Magnetic variation
        @type mode: C{str}
        @param mode: Type of reading
        """
        super(Position, self).__init__(latitude, longitude)
        self.time = time
        self.status = status
        self.speed = speed
        self.track = track
        self.date = date
        self.variation = variation
        self.mode = mode

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Position(datetime.time(14, 20, 58), True, 53.1440233333, -3.01542833333,
        ...          109394.7, 202.9, datetime.date(2007, 11, 19), 5.0)
        Position(datetime.time(14, 20, 58), True, 53.1440233333, -3.01542833333,
                 109394.7, 202.9, datetime.date(2007, 11, 19), 5.0, None)

        @rtype: C{str}
        @return: String to recreate C{Position} object
        """
        data = [repr(self.time)]
        data.extend(utils.repr_assist(self.status, self.latitude,
                                      self.longitude, self.speed, self.track))
        data.extend([repr(self.date), str(self.variation), repr(self.mode)])
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self):
        """
        Pretty printed position string

        >>> print(Position(datetime.time(14, 20, 58), True, 53.1440233333,
        ...                -3.01542833333, 109394.7, 202.9,
        ...                datetime.date(2007, 11, 19), 5.0))
        $GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E*41

        @rtype: C{str}
        @return: Human readable string representation of C{Position} object
        """
        data = ["GPRMC"]
        data.append(self.time.strftime("%H%M%S"))
        data.append("A" if self.status else "V")
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append("%.1f" % self.speed)
        data.append("%.1f" % self.track)
        data.append(self.date.strftime("%d%m%y"))
        if abs(self.variation) == int(abs(self.variation)):
            data.append("%i" % abs(self.variation))
        else:
            data.append("%.1f" % abs(self.variation))
        data.append("E" if self.variation >= 0 else "W")
        if self.mode:
            data.append(self.mode)
        data = ",".join(data)
        return "$%s*%X\r" % (data, calc_checksum(data))

    def mode_string(self):
        """
        Return a string version of the reading mode information

        >>> position = Position(datetime.time(14, 20, 58), True, 53.1440233333,
        ...                     -3.01542833333, 109394.7, 202.9,
        ...                     datetime.date(2007, 11, 19), 5.0)
        >>> print(position.mode_string())
        Unknown
        >>> position.mode = "A"
        >>> print(position.mode_string())
        Autonomous

        @rtype: C{str}
        @return: Quality information as string
        """
        return MODE_INDICATOR.get(self.mode, "Unknown")

    @staticmethod
    def parse_elements(elements):
        """
        Parse position data elements

        >>> Position.parse_elements(["142058", "A", "5308.6414", "N",
        ...                          "00300.9257", "W", "109394.7", "202.9",
        ...                          "191107", "5", "E", "A"])
        Position(datetime.time(14, 20, 58), True, 53.1440233333, -3.01542833333,
                 109394.7, 202.9, datetime.date(2007, 11, 19), 5.0, 'A')
        >>> Position.parse_elements(["142100", "A", "5200.9000", "N",
        ...                          "00316.6600", "W", "123142.7", "188.1",
        ...                          "191107", "5", "E", "A"])
        Position(datetime.time(14, 21), True, 52.015, -3.27766666667, 123142.7,
                 188.1, datetime.date(2007, 11, 19), 5.0, 'A')

        @type elements: C{list}
        @param elements: Data values for fix
        @rtype: C{Fix}
        @return: Fix object representing data
        """
        if not len(elements) in (11, 12):
            raise ValueError("Invalid RMC position data")
        time = datetime.time(*[int(elements[0][i:i+2]) for i in range(0, 6, 2)])
        active = True if elements[1] == "A" else False
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[2], elements[3])
        longitude = parse_longitude(elements[4], elements[5])
        speed = float(elements[6])
        track = float(elements[7])
        date = datetime.date(2000+int(elements[8][4:6]), int(elements[8][2:4]),
                             int(elements[8][:2]))
        variation = float(elements[9]) if not elements[9] == "" else None
        if elements[10] == "W":
            variation = -variation
        elif variation and not elements[10] == "E":
            raise ValueError("Incorrect variation value `%s'"
                             % elements[10])
        if len(elements) == 12:
            mode = elements[11]
        else:
            mode = None
        return Position(time, active, latitude, longitude, speed, track, date,
                        variation, mode)

class Fix(point.Point):
    """
    Class for representing a GPS NMEA-formatted system fix

    @ivar time: Time the fix was taken
    @ivar latitude: Fix's latitude
    @ivar longitude: Fix's longitude
    @ivar quality: Mode under which the fix was taken
    @ivar satellites: Number of tracked satellites
    @ivar dilution: Horizontal dilution at reported position
    @ivar altitude: Altitude above MSL
    @ivar geoid_delta: Height of geoid's MSL above WGS84 ellipsoid
    @ivar dgps_delta: Number of seconds since last DGPS sync
    @ivar dgps_station: Identifier of the last synced DGPS station
    @ivar mode: Type of reading
    @cvar fix_quality: List of fix quality integer to string representations
    """

    __slots__ = ('time', 'quality', 'satellites', 'dilution', 'altitude',
                 'geoid_delta', 'dgps_delta', 'dgps_station', 'mode')

    fix_quality = [
        "Invalid",
        "GPS",
        "DGPS",
        "PPS",
        "Real Time Kinematic"
        "Float RTK",
        "Estimated",
        "Manual",
        "Simulation",
    ]

    def __init__(self, time, latitude, longitude, quality, satellites, dilution,
                 altitude, geoid_delta, dgps_delta=None, dgps_station=None,
                 mode=None):
        """
        Initialise a new C{Fix} object

        @type time: C{datetime.time}
        @param time: Time the fix was taken
        @type latitude: C{float} or coercible to C{float}
        @param latitude: Fix's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Fix's longitude
        @type quality: C{int}
        @param quality: Mode under which the fix was taken
        @type satellites: C{int}
        @param satellites: Number of tracked satellites
        @type dilution: C{float}
        @param dilution: Horizontal dilution at reported position
        @type altitude: C{float} or coercible to C{float}
        @param altitude: Altitude above MSL
        @type geoid_delta: C{float} or coercible to C{float}
        @param geoid_delta: Height of geoid's MSL above WGS84 ellipsoid
        @type dgps_delta: C{float} or coercible to C{float}
        @param dgps_delta: Number of seconds since last DGPS sync
        @type dgps_station: C{int}
        @param dgps_station: Identifier of the last synced DGPS station
        @type mode: C{str}
        @param mode: Type of reading
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

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, 1, 4,
        ...     5.6, 1052.3, 34.5)
        Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, 1, 4, 5.6,
            1052.3, 34.5, None, None)
        >>> Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, 1, 4,
        ...     5.6, 1052.3, 34.5, 12, 4)
        Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, 1, 4,
            5.6, 1052.3, 34.5, 12, 4)

        @rtype: C{str}
        @return: String to recreate C{Fix} object
        """
        data = [repr(self.time)]
        data.extend(utils.repr_assist(self.latitude, self.longitude,
                                      self.quality, self.satellites,
                                      self.dilution, self.altitude,
                                      self.geoid_delta, self.dgps_delta,
                                      self.dgps_station))
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self):
        """
        Pretty printed location string

        >>> print(Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667,
        ...           1, 4, 5.6, 1052.3, 34.5))
        $GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,,*61
        >>> print(Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667,
        ...           1, 4, 5.6, 1052.3, 34.5, 12, 4))
        $GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,12.0,0004*78

        @rtype: C{str}
        @return: Human readable string representation of C{Fix} object
        """
        data = ["GPGGA"]
        data.append(self.time.strftime("%H%M%S"))
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append(str(self.quality))
        data.append("%02i" % self.satellites)
        data.append("%.1f" % self.dilution)
        data.append("%.1f" % self.altitude)
        data.append("M")
        if self.geoid_delta is False:
            data.append("-")
        else:
            data.append("%.1f" % self.geoid_delta)
        data.append("M")
        data.append("%.1f" % self.dgps_delta if self.dgps_delta else "")
        data.append("%04i" % self.dgps_station if self.dgps_station else "")
        data = ",".join(data)
        return "$%s*%X\r" % (data, calc_checksum(data))

    def quality_string(self):
        """
        Return a string version of the quality information

        >>> fix = Fix(datetime.time(14, 20, 58), 53.1440233333, -3.01542833333,
        ...           1, 4, 5.6, 1374.6, 34.5, None, None)
        >>> print(fix.quality_string())
        GPS

        @rtype: C{str}
        @return: Quality information as string
        """
        return self.fix_quality[self.quality]

    @staticmethod
    def parse_elements(elements):
        """
        Parse essential fix's data elements

        >>> Fix.parse_elements(["142058", "5308.6414", "N", "00300.9257", "W", "1",
        ...                     "04", "5.6", "1374.6", "M", "34.5", "M", "", ""])
        Fix(datetime.time(14, 20, 58), 53.1440233333, -3.01542833333, 1, 4, 5.6,
            1374.6, 34.5, None, None)
        >>> Fix.parse_elements(["142100", "5200.9000", "N", "00316.6600", "W", "1",
        ...                     "04", "5.6", "1000.0", "M", "34.5", "M", "", ""])
        Fix(datetime.time(14, 21), 52.015, -3.27766666667, 1, 4, 5.6, 1000.0, 34.5,
            None, None)

        @type elements: C{list}
        @param elements: Data values for fix
        @rtype: C{Fix}
        @return: Fix object representing data
        """
        if not len(elements) in (14, 15):
            raise ValueError("Invalid GGA fix data")
        time = datetime.time(*[int(elements[0][i:i+2]) for i in range(0, 6, 2)])
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[1], elements[2])
        longitude = parse_longitude(elements[3], elements[4])
        quality = int(elements[5])
        if not 0 <= quality <= 9:
            raise ValueError("Invalid quality value `%i'" % quality)
        satellites = int(elements[6])
        if not 0 <= satellites <= 12:
            raise ValueError("Invalid number of satellites `%i'"
                             % satellites)
        dilution = float(elements[7])
        altitude = float(elements[8])
        if elements[9] == "F":
            altitude = altitude * 3.2808399
        elif not elements[9] == "M":
            raise ValueError("Unknown altitude unit `%s'" % elements[9])
        if elements[10] in ("-", ""):
            geoid_delta = False
            logging.warning("Altitude data could be incorrect, as the geoid "
                            "difference has not been provided")
        else:
            geoid_delta = float(elements[10])
        if elements[11] == "F":
            geoid_delta = geoid_delta * 3.2808399
        elif geoid_delta and not elements[11] == "M":
            raise ValueError("Unknown geoid delta unit `%s'" % elements[11])
        dgps_delta = float(elements[12]) if elements[12] else None
        dgps_station = int(elements[13]) if elements[13] else None
        if len(elements) == 15:
            mode = elements[14]
        else:
            mode = None
        return Fix(time, latitude, longitude, quality, satellites, dilution,
                   altitude, geoid_delta, dgps_delta, dgps_station, mode)

class Waypoint(point.Point):
    """
    Class for representing a NMEA-formatted waypoint

    @ivar latitude: Waypoint's latitude
    @ivar longitude: Waypoint's longitude
    @ivar name: Waypoint's name
    """

    __slots__ = ('name', )

    def __init__(self, latitude, longitude, name):
        """
        Initialise a new C{Waypoint} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Waypoint's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Waypoint's longitude
        @type name: C{string}
        @param name: Comment for waypoint
        """
        super(Waypoint, self).__init__(latitude, longitude)
        self.name = name.upper()

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Waypoint(52.015, -0.221, "Home")
        Waypoint(52.015, -0.221, 'HOME')

        @rtype: C{str}
        @return: String to recreate C{Waypoint} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.name)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self):
        """
        Pretty printed location string

        >>> print Waypoint(52.015, -0.221, "Home")
        $GPWPL,5200.9000,N,00013.2600,W,HOME*5E

        @rtype: C{str}
        @return: Human readable string representation of C{Waypoint} object
        """
        data = ["GPWPL"]
        data.extend(nmea_latitude(self.latitude))
        data.extend(nmea_longitude(self.longitude))
        data.append(self.name)
        data = ",".join(data)
        text = "$%s*%X\r" % (data, calc_checksum(data))
        if len(text) > 81:
            raise ValueError("All NMEA sentences must be less than 82 bytes "
                             "including line endings")
        return text

    @staticmethod
    def parse_elements(elements):
        """
        Parse waypoint data elements

        >>> Waypoint.parse_elements(["5200.9000", "N", "00013.2600", "W",
        ...                          "HOME"])
        Waypoint(52.015, -0.221, 'HOME')

        @type elements: C{list}
        @param elements: Data values for fix
        @rtype: C{Fix}
        @return: Fix object representing data
        """
        if not len(elements) == 5:
            raise ValueError("Invalid WPL waypoint data")
        # Latitude and longitude are checked for validity during Fix
        # instantiation
        latitude = parse_latitude(elements[0], elements[1])
        longitude = parse_longitude(elements[2], elements[3])
        name = elements[4]
        return Waypoint(latitude, longitude, name)

class Locations(list):
    """
    Class for representing a group of GPS location objects
    """

    def __init__(self, gpsdata_file=None):
        """
        Initialise a new C{Locations} object
        """
        list.__init__(self)
        if gpsdata_file:
            self.import_gpsdata_file(gpsdata_file)

    def import_gpsdata_file(self, gpsdata_file):
        """
        Import GPS NMEA-formatted data files

        C{import_gpsdata_file()} returns a list of C{Fix} objects representing
        the fix sentences found in the GPS data.

        It expects data files in NMEA 0183 format, as specified in U{the
        official documentation <http://www.nmea.org/pub/0183/>}, which is ASCII
        text such as::

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
        that the data is out of scope for ``earth_distance``.

        The above file when processed by C{import_gpsdata_file()} will return
        the following C{list} object::

            [Fix(datetime.time(14, 20, 58), 53.1440233333, -3.01542833333, 1, 4,
                 5.6, 1374.6, 34.5, None, None),
             Position(datetime.time(14, 20, 58), True, 53.1440233333,
                      -3.01542833333, 109394.7, 202.9,
                      datetime.date(2007, 11, 19), 5.0, 'A'),
             Waypoint(52.015, -0.221, 'Home'),
             Fix(datetime.time(14, 21), 52.015, -3.27766666667, 1, 4, 5.6,
                 1000.0, 34.5, None, None),
             Position(datetime.time(14, 21), True, 52.015, -3.27766666667,
                      123142.7, 188.1, datetime.date(2007, 11, 19), 5.0, 'A')]

        >>> locations = Locations(open("gpsdata"))
        >>> for value in locations:
        ...     print(value)
        $GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,*6B
        $GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E,A*2C
        $GPWPL,5200.9000,N,00013.2600,W,HOME*5E
        $GPGGA,142100,5200.9000,N,00316.6600,W,1,04,5.6,1000.0,M,34.5,M,,*68
        $GPRMC,142100,A,5200.9000,N,00316.6600,W,123142.7,188.1,191107,5,E,A*21

        @note: The standard is quite specific in that sentences must be less
               than 82 bytes, while it would be nice to add yet another validity
               check it isn't all that uncommon for devices to break this
               requirement in their "extensions" to the standard.  If this check
               is enabled it should only be active for processed data.

        @type gpsdata_file: C{file}, C{list} or C{str}
        @param gpsdata_file: NMEA data to read
        @rtype: C{list}
        @return: Series of locations taken from the data
        """
        data = utils.prepare_read(gpsdata_file)

        PARSERS = {
            "GPGGA": Fix,
            "GPRMC": Position,
            "GPWPL": Waypoint,
        }

        for line in data:
            # The standard tells us lines should end in \r\n, even though some
            # devices break this, but Python's standard file object solves this
            # for us anyway.  However, be careful if you implement your own
            # opener.
            if not line[1:6] in PARSERS:
                continue
            values, checksum = line[1:].split("*")
            if not calc_checksum(values) == int(checksum, 16):
                raise ValueError("Sentence has invalid checksum")
            elements = values.split(",")
            parser = getattr(PARSERS[elements[0]], "parse_elements")
            self.append(parser(elements[1:]))
