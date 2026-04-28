#
"""test_cities - Test cities support"""
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

from operator import attrgetter

from pytest import fixture

from upoints.cities import City, Cities


@fixture
def sample_City():
    yield City(
        498,
        "Zwickau",
        "City",
        "Sachsen",
        "DE",
        "Earth",
        108835,
        None,
        12.5,
        50.72,
        None,
        (1997, 4, 10, 0, 0, 0, 3, 100, -1),
        "M.Dowling@tu-bs.de",
    )


def test_City___repr__(sample_City):
    assert repr(sample_City) == (
        "City(498, 'Zwickau', 'City', 'Sachsen', 'DE', 'Earth', 108835, "
        "None, 12.5, 50.72, None, (1997, 4, 10, 0, 0, 0, 3, 100, -1), "
        "'M.Dowling@tu-bs.de')"
    )


def test_City___str__(sample_City):
    data = str(sample_City).splitlines()
    assert data == [
        "ID          : 498",
        "Type        : City",
        "Population  : 108835",
        "Size        : ",
        "Name        : Zwickau",
        " Country    : DE",
        " Region     : Sachsen",
        "Location    : Earth",
        " Longitude  : 12.5",
        " Latitude   : 50.72",
        " Elevation  : ",
        "Date        : 19970410",
        "Entered-By  : M.Dowling@tu-bs.de",
    ]


def test_Cities_import_locations():
    with open("tests/data/city_data") as f:
        cities = Cities(f)
    data = [
        (
            "%i - %s (%s;%s)"
            % (city.identifier, city.name, city.latitude, city.longitude)
        )
        for city in sorted(cities, key=attrgetter("identifier"))
    ]
    assert data == [
        "126 - London (51.5;-0.083)",
        "127 - Luxembourg (49.617;6.117)",
        "128 - Lyon (45.767;4.867)",
    ]
    with open("tests/data/city_data") as f:
        manual_list = f.read().split("//\\n")
    cities = Cities(manual_list)
    assert len(cities) == 1
