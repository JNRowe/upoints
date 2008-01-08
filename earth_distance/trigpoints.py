#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""trigpoints - Imports trigpoint marker files"""
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

import csv
import logging
import os

from earth_distance import (point, utils)

class Trigpoint(point.Point):
    """
    Class for representing a location from a trigpoint marker file

    @warning: Although this class stores and presents the representation of
    altitude it doesn't take it in to account when making calculations.  For
    example, consider a point at the base of Mount Everest and a point at the
    peak of Mount Everest the actual distance travelled between the two would be
    larger than the reported value calculated at ground level.

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar altitude: Location's altitude
    @ivar name: Location's name
    """

    __slots__ = ('altitude', 'name')

    def __init__(self, latitude, longitude, altitude, name=None):
        """
        Initialise a new C{Trigpoint} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Location's longitude
        @type altitude: C{float} or coercible to C{float}
        @param altitude: Location's altitude
        @type name: C{string}
        @param name: Name for location
        """
        super(Trigpoint, self).__init__(latitude, longitude)
        self.altitude = altitude
        self.name = name

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Trigpoint(52.010585, -0.173443, 97.0, "Bygrave")
        Trigpoint(52.010585, -0.173443, 97.0, 'Bygrave')

        @rtype: C{str}
        @return: String to recreate C{Trigpoint} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.altitude,
                                 self.name)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Trigpoint(52.010585, -0.173443, 97.0))
        52°00'38"N, 000°10'24"W alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0).__str__(mode="dd"))
        N52.011°; W000.173° alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0).__str__(mode="dm"))
        52°00.64'N, 000°10.41'W alt 97m
        >>> print(Trigpoint(52.010585, -0.173443, 97.0, "Bygrave"))
        Bygrave (52°00'38"N, 000°10'24"W alt 97m)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Trigpoint} object
        """
        text = super(Trigpoint, self).__str__(mode)
        if self.altitude:
            text += " alt %im" % self.altitude

        if self.name:
            return "%s (%s)" % (self.name, text)
        else:
            return text

class Trigpoints(dict):
    """
    Class for representing a group of C{Trigpoint} objects
    """

    def __init__(self, marker_file=None):
        """
        Initialise a new C{Trigpoints} object
        """
        dict.__init__(self)
        if marker_file:
            self.import_marker_file(marker_file)

    def import_marker_file(self, marker_file):
        """
        Import trigpoint database files

        C{import_marker_file()} returns a dictionary with keys containing the
        trigpoint identifier, and values that are C{Trigpoint} objects.

        It expects trigpoint marker files in the format provided at
        U{alltrigs-wgs84.txt http://www.haroldstreet.org.uk/trigpoints.php},
        which is the following format::

            H  SOFTWARE NAME & VERSION
            I  GPSU 4.04,
            S SymbolSet=0
            ...
            W,500936,N52.066035,W000.281449,    37.0,Broom Farm
            W,501097,N52.010585,W000.173443,    97.0,Bygrave
            W,505392,N51.910886,W000.186462,   136.0,Sish Lane

        Any line not consisting of 6 comma separated fields will be ignored.
        The reader uses U{Python <http://www.python.org/>}'s C{csv} module, so
        alternative whitespace formatting should have no effect.  The above file
        processed by C{import_marker_file()} will return the following C{dict}
        object::

            {500936: point.Point(52.066035, -0.281449, 37.0, "Broom Farm"),
             501097: point.Point(52.010585, -0.173443, 97.0, "Bygrave"),
             505392: point.Point(51.910886, -0.186462, 136.0, "Sish Lane")}

        >>> marker_file = open("trigpoints")
        >>> markers = Trigpoints(marker_file)
        >>> for key, value in sorted(markers.items()):
        ...     print("%s - %s" % (key, value))
        500936 - Broom Farm (52°03'57"N, 000°16'53"W alt 37m)
        501097 - Bygrave (52°00'38"N, 000°10'24"W alt 97m)
        505392 - Sish Lane (51°54'39"N, 000°11'11"W alt 136m)
        >>> marker_file.seek(0)
        >>> markers = Trigpoints(marker_file.readlines())
        >>> markers = Trigpoints(open("southern_trigpoints"))
        >>> print(markers[1])
        FakeLand (48°07'23"S, 000°07'23"W alt 12m)
        >>> markers = Trigpoints(open("broken_trigpoints"))
        >>> for key, value in sorted(markers.items()):
        ...     print("%s - %s" % (key, value))
        500968 - Brown Hill Nm  See The Heights (53°38'23"N, 001°39'34"W)
        501414 - Cheriton Hill Nm  See Paddlesworth (51°06'03"N, 001°08'33"E)

        @type marker_file: C{file}, C{list} or C{str}
        @param marker_file: Trigpoint marker data to read
        @rtype: C{dict}
        @return: Named locations with C{Trigpoint} objects
        @raise ValueError: Invalid value for C{marker_file}
        """
        if hasattr(marker_file, "readlines"):
            data = csv.reader(marker_file)
        elif isinstance(marker_file, list):
            data = csv.reader(marker_file)
        elif isinstance(marker_file, basestring):
            data = csv.reader(open(marker_file))
        else:
            raise TypeError("Unable to handle data of type `%s'"
                            % type(marker_file))

        for row in data:
            if not len(row) == 6 or row[0] == "F":
                continue
            identity, latitude, longitude, altitude, name = row[1:]
            identity = int(identity)
            if latitude[0] == "N":
                latitude = float(latitude[1:])
            else:
                latitude = 0 - float(latitude[1:])
            if longitude[0] == "E":
                longitude = float(longitude[1:])
            else:
                longitude = 0 - float(longitude[1:])
            altitude = float(altitude)
            # A value of 8888 denotes unavailable data
            if altitude == 8888:
                logging.debug("Ignoring `8888' value for altitude in `%s' entry"
                              % row)
                altitude = None
            self[identity] = Trigpoint(latitude, longitude, altitude, name)

