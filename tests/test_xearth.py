#
"""test_xearth - Test xearth support"""
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

from pytest import fixture, mark

from upoints.xearth import Xearth, Xearths


def test_Xearth__repr__():
    assert (
        repr(Xearth(52.015, -0.221, "James Rowe’s house"))
        == "Xearth(52.015, -0.221, 'James Rowe’s house')"
    )


def test_Xearth__str__():
    assert str(Xearth(52.015, -0.221)) == "N52.015°; W000.221°"
    assert (
        str(Xearth(52.015, -0.221, "James Rowe’s house"))
        == "James Rowe’s house (N52.015°; W000.221°)"
    )


@mark.parametrize(
    "style, result",
    [
        ("dms", "52°00′54″N, 000°13′15″W"),
        ("dm", "52°00.90′N, 000°13.26′W"),
    ],
)
def test_Xearth__format__(style, result):
    assert format(Xearth(52.015, -0.221), style) == result


@fixture
def sample_data():
    with open("tests/data/xearth") as f:
        yield Xearths(f)


def test_Xearths___str__(sample_data):
    assert sample_data.__str__().splitlines() == [
        '52.015000 -0.221000 "Home"',
        '52.633300 -2.500000 "Telford"',
    ]


@mark.parametrize(
    "marker, result",
    [
        ("Home", "James Rowe’s home (N52.015°; W000.221°)"),
        ("Telford", "N52.633°; W002.500°"),
    ],
)
def test_Xearths_import_locations(sample_data, marker, result):
    assert str(sample_data[marker]) == result
