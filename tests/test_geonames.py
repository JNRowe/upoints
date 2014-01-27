#
# coding=utf-8
"""test_geonames - Test geonames support"""
# Copyright © 2007-2014  James Rowe <jnrowe@gmail.com>
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

from unittest import TestCase

from expecter import expect

from upoints.geonames import (Location, Locations)
from upoints.utils import FileFormatError


class TestLocation(TestCase):
    def setUp(self):
        self.x = Location(2636782, 'Stotfold', 'Stotfold', None, 52.0,
                          -0.2166667, 'P', 'PPL', 'GB', None, 'F8', None, None,
                          None, 6245, None, 77, 'Europe/London',
                          datetime.date(2007, 6, 15), 0)

    def test___repr__(self):
        expect(repr(self.x)) == \
            ("Location(2636782, 'Stotfold', 'Stotfold', None, 52.0, "
             "-0.2166667, 'P', 'PPL', 'GB', None, 'F8', None, None, None, "
             "6245, None, 77, 'Europe/London', datetime.date(2007, 6, 15), 0)")

    def test___str__(self):
        expect(str(self.x)) == 'Stotfold (N52.000°; W000.217°)'
        self.x.alt_names = ['Home', 'Target']
        expect(str(self.x)) == 'Stotfold (Home, Target - N52.000°; W000.217°)'
        self.x.alt_names = None

    def test___format__(self):
        expect(format(self.x, 'dms')) == \
            """Stotfold (52°00'00"N, 000°13'00"W)"""
        expect(format(self.x, 'dm')) == \
            "Stotfold (52°00.00'N, 000°13.00'W)"


class TestLocations(TestCase):
    def test_import_locations(self):
        locations = Locations(open('tests/data/geonames'))
        expect(str(locations[0])) == \
            'Afon Wyre (River Wayrai, River Wyrai, Wyre - N52.317°; W004.167°)'
        expect(str(locations[1])) == \
            'Wyre (Viera - N59.117°; W002.967°)'
        expect(str(locations[2])) == \
            'Wraysbury (Wyrardisbury - N51.450°; W000.550°)'

        with expect.raises(FileFormatError,
                           "Incorrect data format, if you're using a file "
                           'downloaded from geonames.org please report this '
                           'to James Rowe <jnrowe@gmail.com>'):
            Locations(open('tests/data/broken_geonames'))

    def test_import_timezones_file(self):
        locations = Locations(None, open('tests/data/geonames_timezones'))
        timezones = locations.timezones
        expect(timezones['Asia/Dubai']) == [240, 240]
        expect(timezones['Asia/Kabul']) == [270, 270]
        expect(timezones['Europe/Andorra']) == [60, 120]

        header_skip_check = Locations(None,
                                      open('tests/data/geonames_timezones_header'))
        expect(header_skip_check) == Locations()

        with expect.raises(FileFormatError,
                           "Incorrect data format, if you're using a file "
                           'downloaded from geonames.org please report this '
                           'to James Rowe <jnrowe@gmail.com>'):
            Locations(None, open('tests/data/geonames_timezones_broken'))
