#
"""test_cellid - Test cellid support"""
# Copyright © 2012-2021  James Rowe <jnrowe@gmail.com>
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

from upoints.cellid import Cell, Cells


class TestCell:
    def test___repr__(self):
        assert repr(
            Cell(
                4,
                52.015,
                -0.221,
                21,
                46,
                40000,
                10,
                0,
                1,
                datetime.datetime(2008, 4, 15, 15, 21, 35),
                datetime.datetime(2008, 4, 15, 15, 28, 49),
            )
        ) == (
            'Cell(4, 52.015, -0.221, 21, 46, 40000, 10, 0, 1, '
            'datetime.datetime(2008, 4, 15, 15, 21, 35), '
            'datetime.datetime(2008, 4, 15, 15, 28, 49))'
        )

    def test___str__(self):
        assert str(
            Cell(
                4,
                52.015,
                -0.221,
                21,
                46,
                40000,
                10,
                0,
                1,
                datetime.datetime(2008, 4, 15, 15, 21, 35),
                datetime.datetime(2008, 4, 15, 15, 28, 49),
            )
        ) == (
            '4,52.0150000000000,-0.2210000000000,21,46,40000,10,0,1,'
            '2008-04-15 15:21:35,2008-04-15 15:28:49'
        )


class TestCells:
    def setup(self):
        with open('tests/data/cells') as f:
            self.cells = Cells(f)

    def test___str__(self):
        assert sorted(str(x) for x in self.cells.values()) == [
            (
                '22747,52.0438995361328,-0.2246370017529,234,33,2319,647,0,1,'
                '2008-04-05 21:32:40,2008-04-05 21:32:40'
            ),
            (
                '22995,52.3305015563965,-0.2255620062351,234,10,20566,4068,0,1,'
                '2008-04-05 21:32:59,2008-04-05 21:32:59'
            ),
            (
                '23008,52.3506011962891,-0.2234109938145,234,10,10566,4068,0,1,'
                '2008-04-05 21:32:59,2008-04-05 21:32:59'
            ),
        ]

    def test_import_locations(self):
        assert self.cells['22747'] == Cell(
            22747,
            52.0438995361328,
            -0.224637001752853,
            234,
            33,
            2319,
            647,
            0,
            1,
            datetime.datetime(2008, 4, 5, 21, 32, 40),
            datetime.datetime(2008, 4, 5, 21, 32, 40),
        )
