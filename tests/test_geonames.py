#
"""test_geonames - Test geonames support"""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
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

from pytest import mark, raises

from upoints.geonames import Location, Locations
from upoints.utils import FileFormatError


class TestLocation:
    def setup(self):
        self.x = Location(
            2636782,
            'Stotfold',
            'Stotfold',
            None,
            52.0,
            -0.2166667,
            'P',
            'PPL',
            'GB',
            None,
            'F8',
            None,
            None,
            None,
            6245,
            None,
            77,
            'Europe/London',
            datetime.date(2007, 6, 15),
            0,
        )

    def test___repr__(self):
        assert repr(self.x) == (
            "Location(2636782, 'Stotfold', 'Stotfold', None, 52.0, "
            "-0.2166667, 'P', 'PPL', 'GB', None, 'F8', None, None, None, "
            "6245, None, 77, 'Europe/London', datetime.date(2007, 6, 15), 0)"
        )

    @mark.parametrize(
        'names, result',
        [
            (None, 'Stotfold (N52.000°; W000.217°)'),
            (
                ['Home', 'Target'],
                'Stotfold (Home, Target - N52.000°; W000.217°)',
            ),
        ],
    )
    def test___str__(self, names, result):
        self.x.alt_names = names
        assert str(self.x) == result

    @mark.parametrize(
        'style, result',
        [
            ('dms', 'Stotfold (52°00′00″N, 000°13′00″W)'),
            ('dm', 'Stotfold (52°00.00′N, 000°13.00′W)'),
        ],
    )
    def test___format__(self, style, result):
        assert format(self.x, style) == result


class TestLocations:
    def test_import_locations(self):
        with open('tests/data/geonames') as f:
            locs = Locations(f)
        assert [str(l) for l in locs] == [
            'Afon Wyre (River Wayrai, River Wyrai, Wyre - N52.317°; W004.167°)',
            'Wyre (Viera - N59.117°; W002.967°)',
            'Wraysbury (Wyrardisbury - N51.450°; W000.550°)',
        ]

    def test_import_locations_error(self):
        with raises(
            FileFormatError,
            match=(
                'Incorrect data format, if you’re using a file '
                'downloaded from geonames.org please report this '
                'to James Rowe <jnrowe@gmail.com>'
            ),
        ):
            with open('tests/data/broken_geonames') as f:
                Locations(f)

    def test_import_timezones_file(self):
        with open('tests/data/geonames_timezones') as f:
            locations = Locations(None, f)
        assert locations.timezones == {
            'Asia/Dubai': [240, 240],
            'Asia/Kabul': [270, 270],
            'Europe/Andorra': [60, 120],
        }

    def test_import_timezones_file_header(self):
        with open('tests/data/geonames_timezones_header') as f:
            header_skip_check = Locations(None, f)
        assert header_skip_check == Locations()

    def test_import_timezones_file_error(self):
        with raises(
            FileFormatError,
            match=(
                'Incorrect data format, if you’re using a file '
                'downloaded from geonames.org please report this '
                'to James Rowe <jnrowe@gmail.com>'
            ),
        ):
            with open('tests/data/geonames_timezones_broken') as f:
                Locations(None, f)
