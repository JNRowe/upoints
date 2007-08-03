#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""marker_file - Imports xearth-style marker files"""
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

import os

import point

class Xearth(point.Point):
    """
    Class for representing a location from a xearth marker file

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar comment: Location's comment
    """

    __slots__ = ('comment', )

    def __init__(self, latitude, longitude, comment=None, format="metric",
                 angle="degrees"):
        """
        Initialise a new Xearth object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Location's longitude
        @type comment: C{string}
        @param comment: Comment for location
        """
        point.Point.__init__(self, latitude, longitude, format, angle)
        self.comment = comment

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Xearth(52.015, -0.221, "James Rowe's house")
        Xearth(52.015000, -0.221000, "James Rowe's house")

        @rtype: C{str}
        @return: String to recreate Xearth object
        """
        return 'Xearth(%f, %f, "%s")' % (self.latitude, self.longitude,
                                         self.comment)

    def __str__(self, mode="dd"):
        """
        Pretty printed location string

        @see: C{point.Point}

        >>> print Xearth(52.015, -0.221)
        N52.015°; W000.221°
        >>> print Xearth(52.015, -0.221).__str__(mode="dms")
        52°00'54"N, 000°13'15"W
        >>> print Xearth(52.015, -0.221).__str__(mode="dm")
        52°00.90'N, 000°13.25'W
        >>> print Xearth(52.015, -0.221, "James Rowe's house")
        James Rowe's house (N52.015°; W000.221°)

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of Point object
        """
        text = super(Xearth, self).__str__(mode)

        if self.comment:
            return "%s (%s)" % (self.comment, text)
        else:
            return text

def import_marker_file(marker_file):
    """
    C{import_marker_file()} returns a dictionary with keys containing the
    U{xearth <http://www.cs.colorado.edu/~tuna/xearth/>} name, and values
    consisting of a C{point.Point} object and a string containing any comment
    found in the marker file.

    It expects xearth marker files in the following format::

        # Comment

        52.015     -0.221 "Home"          # James Rowe's home
        52.6333    -2.5   "Telford"

    Any empty line or line starting with a '#' is ignored.  All data lines are
    whitespace-normalised, so actual layout should have no effect.  The above
    file processed by C{import_marker_file()} will return the following C{dict}
    object::

        'Home': (point.Point(52.015, -0.221, "James Rowe's home"),
        'Telford': (point.Point(52.6333, -2.5, None)

    @note: This function also handles the extended U{xplanet
    <http://xplanet.sourceforge.net/>} marker files whose points can optionally
    contain added xplanet specific keywords for defining colours and fonts.

    >>> import StringIO
    >>> marker_file = StringIO.StringIO("\\n".join([
    ...     '# Comment',
    ...     '',
    ...     '52.015     -0.221 "Home" font=11  # James Rowe\\'s home',
    ...     '52.6333    -2.5   "Telford" font=11 color=blue']))
    >>> markers = import_marker_file(marker_file)
    >>> for key, value in sorted(markers.items()):
    ...     print key, '-', value
    Home - James Rowe's home (N52.015°; W000.221°)
    Telford - N52.633°; W002.500°

    @type marker_file: C{file}, C{list} or C{str}
    @param marker_file: xearth marker data to read
    @rtype: C{dict}
    @return: Named locations with optional comments
    """
    if hasattr(marker_file, "readlines"):
        data = marker_file.readlines()
    elif isinstance(marker_file, list):
        data = marker_file
    elif isinstance(marker_file, str):
        if os.path.isfile(marker_file):
            data = open(marker_file).readlines()
    else:
        raise ValueError("Unable to handle data of type `%s`"
                         % type(marker_file))

    markers = {}
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
        markers[name.strip()] = Xearth(latitude, longitude, comment)
    return markers

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod(optionflags=doctest.REPORT_UDIFF)[0])

