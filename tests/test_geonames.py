#
# coding=utf-8
"""test_geonames - Test geonames support"""
# Copyright (C) 2006-2011  James Rowe <jnrowe@gmail.com>
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

from upoints.geonames import (Location, Locations)

class TestLocation():
    def test___init__(self):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Location(2636782, "Stotfold", "Stotfold", None, 52.0, -0.2166667,
        ...          "P", "PPL", "GB", None, "F8", None, None, None, 6245,
        ...          None, 77, "Europe/London", datetime.date(2007, 6, 15), 0)
        Location(2636782, 'Stotfold', 'Stotfold', None, 52.0, -0.2166667, 'P',
                 'PPL', 'GB', None, 'F8', None, None, None, 6245, None, 77,
                 'Europe/London', datetime.date(2007, 6, 15), 0)

        """

    def test___str__(self):
        """
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

        """


class TestLocations():
    def test_import_locations(self):
        """
        >>> from operator import attrgetter
        >>> locations = Locations(open("test/data/geonames"))
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> for location in sorted(locations, key=attrgetter("geonameid")):
        ...     print("%i - %s" % (location.geonameid, location))
        2633441 - Afon Wyre (River Wayrai, River Wyrai, Wyre - N52.317°;
        W004.167°)
        2633442 - Wyre (Viera - N59.117°; W002.967°)
        2633443 - Wraysbury (Wyrardisbury - N51.450°; W000.550°)
        >>> broken_locations = Locations(open("test/data/broken_geonames"))
        Traceback (most recent call last):
            ...
        FileFormatError: Incorrect data format, if you're using a file
        downloaded from geonames.org please report this to James Rowe
        <jnrowe@gmail.com>

        """

    def test_import_timezones_file(self):
        """
        >>> timezones = Locations(None, open("test/data/geonames_timezones")).timezones
        >>> for key, value in sorted(timezones.items()):
        ...     print("%s - %s" % (key, value))
        Asia/Dubai - [240, 240]
        Asia/Kabul - [270, 270]
        Europe/Andorra - [60, 120]
        >>> header_skip_check = Locations(None,
        ...                               open("test/data/geonames_timezones_header"))
        >>> from dtopt import ELLIPSIS
        >>> print(header_skip_check)
        Locations(None, <open file ...>)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> broken_file_check = Locations(None,
        ...                               open("test/data/geonames_timezones_broken"))
        Traceback (most recent call last):
            ...
        FileFormatError: Incorrect data format, if you're using a file
        downloaded from geonames.org please report this to James Rowe
        <jnrowe@gmail.com>

        """
