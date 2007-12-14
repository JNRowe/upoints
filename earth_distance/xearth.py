#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""xearth - Imports xearth-style marker files"""
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

class Xearth(point.Point):
    """
    Class for representing a location from a Xearth marker

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar comment: Location's comment
    """

    __slots__ = ('comment', )

    def __init__(self, latitude, longitude, comment=None, format="metric",
                 angle="degrees"):
        """
        Initialise a new C{Xearth} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Location's longitude
        @type comment: C{string}
        @param comment: Comment for location
        """
        super(Xearth, self).__init__(latitude, longitude, format, angle)
        self.comment = comment

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Xearth(52.015, -0.221, "James Rowe's house")
        Xearth(52.015, -0.221, "James Rowe's house")

        @rtype: C{str}
        @return: String to recreate C{Xearth} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.comment)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        @see: C{point.Point}

        >>> print(Xearth(52.015, -0.221))
        N52.015°; W000.221°
        >>> print(Xearth(52.015, -0.221).__str__(mode="dms"))
        52°00'54"N, 000°13'15"W
        >>> print(Xearth(52.015, -0.221).__str__(mode="dm"))
        52°00.90'N, 000°13.26'W
        >>> print(Xearth(52.015, -0.221, "James Rowe's house"))
        James Rowe's house (N52.015°; W000.221°)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Xearth} object
        """
        text = super(Xearth, self).__str__(mode)

        if self.comment:
            return "%s (%s)" % (self.comment, text)
        else:
            return text

class Xearths(dict):
    """
    Class for representing a group of C{Xearth} objects
    """

    def __init__(self, marker_file=None):
        """
        Initialise a new C{Xearths} object
        """
        dict.__init__(self)
        if marker_file:
            self.import_marker_file(marker_file)

    def __str__(self):
        """
        C{Xearth} objects rendered for use with Xearth/Xplanet

        >>> markers = Xearths(open("xearth"))
        >>> print markers
        52.015000 -0.221000 "Home"
        52.633300 -2.500000 "Telford"

        @rtype: C{str}
        @return: Xearth/Xplanet marker file formatted output
        """
        return "\n".join(utils.dump_xearth_markers(self, "comment"))

    def import_marker_file(self, marker_file):
        """
        Parse Xearth data files

        C{import_marker_file()} returns a dictionary with keys containing the
        U{xearth <http://www.cs.colorado.edu/~tuna/xearth/>} name, and values
        consisting of a C{Xearth} object and a string containing any comment
        found in the marker file.

        It expects Xearth marker files in the following format::

            # Comment

            52.015     -0.221 "Home"          # James Rowe's home
            52.6333    -2.5   "Telford"

        Any empty line or line starting with a '#' is ignored.  All data lines
        are whitespace-normalised, so actual layout should have no effect.  The
        above file processed by C{import_marker_file()} will return the
        following C{dict} object::

            {'Home': point.Point(52.015, -0.221, "James Rowe's home"),
             'Telford': point.Point(52.6333, -2.5, None)}

        @note: This function also handles the extended U{xplanet
        <http://xplanet.sourceforge.net/>} marker files whose points can
        optionally contain added xplanet specific keywords for defining colours
        and fonts.

        >>> markers = Xearths(open("xearth"))
        >>> for key, value in sorted(markers.items()):
        ...     print("%s - %s" % (key, value))
        Home - James Rowe's home (N52.015°; W000.221°)
        Telford - N52.633°; W002.500°

        @type marker_file: C{file}, C{list} or C{str}
        @param marker_file: Xearth marker data to read
        @rtype: C{dict}
        @return: Named locations with optional comments
        """
        data = utils.prepare_read(marker_file)

        for line in data:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            chunk = line.split("#")
            data = chunk[0]
            if len(chunk) == 2:
                comment = chunk[1].strip()
            else:
                comment = None
            # Need maximum split of 2, because name may contain whitespace
            latitude, longitude, name = data.split(None, 2)
            name = name.strip()
            # Find matching start and end quote, and keep only the contents
            name = name[1:name.find(name[0], 1)]
            self[name.strip()] = Xearth(latitude, longitude, comment)

