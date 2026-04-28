#
"""test_weather_stations - Test weather stations support"""
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

from upoints.weather_stations import Station, Stations


@fixture
def sample_station():
    yield Station(
        "EGLL",
        "London / Heathrow Airport",
        None,
        "United Kingdom",
        6,
        51.4833333333,
        -0.45,
        None,
        None,
        24,
        0,
        True,
    )


def test_Station___repr__(sample_station):
    assert repr(sample_station) == (
        "Station('EGLL', 'London / Heathrow Airport', None, "
        "'United Kingdom', 6, 51.4833333333, -0.45, None, None, 24, 0, "
        "True)"
    )


def test_Station___str__(sample_station):
    assert (
        str(sample_station)
        == "London / Heathrow Airport (EGLL - N51.483°; W000.450°)"
    )
    sample_station.alt_id = None
    assert (
        str(sample_station) == "London / Heathrow Airport (N51.483°; W000.450°)"
    )
    sample_station.alt_id = "EGLL"


@mark.parametrize(
    "style, result",
    [
        (
            "dms",
            "London / Heathrow Airport (EGLL - 51°28′59″N, 000°27′00″W)",
        ),
        (
            "dm",
            "London / Heathrow Airport (EGLL - 51°29.00′N, 000°27.00′W)",
        ),
    ],
)
def test_Station___format__(sample_station, style, result):
    assert format(sample_station, style) == result


def test_Stations_import_locations_wmo():
    with open("tests/data/WMO_stations") as f:
        stations = Stations(f)
    data = sorted(stations.items())
    assert (
        "%s - %s" % data[0]
        == "00000 - Buckland, Buckland Airport (PABL - N65.982°; W161.152°)"
    )
    assert (
        "%s - %s" % data[1] == "01001 - Jan Mayen (ENJA - N70.933°; W008.667°)"
    )
    assert "%s - %s" % data[2] == "01002 - Grahuken (N79.783°; E014.467°)"


def test_Stations_import_locations_icao():
    with open("tests/data/ICAO_stations") as f:
        stations = Stations(f, "ICAO")
    data = sorted(stations.items())
    assert "%s - %s" % data[0] == "AYMD - Madang (94014 - S05.217°; E145.783°)"
    assert (
        "%s - %s" % data[1]
        == "AYMO - Manus Island/Momote (S02.062°; E147.424°)"
    )
    assert "%s - %s" % data[2] == "AYPY - Moresby (94035 - S09.433°; E147.217°)"


def test_Stations_import_locations_broken_wmo():
    with open("tests/data/broken_WMO_stations") as f:
        stations = Stations(f)
    data = sorted(stations.items())
    assert (
        "%s - %s" % data[0]
        == "71046 - Komakuk Beach, Y. T. (CWKM - N69.617°; W140.200°)"
    )
    assert (
        "%s - %s" % data[1]
        == "71899 - Langara, B. C. (CWLA - N54.250°; W133.133°)"
    )


def test_Stations_import_locations_broken_icao():
    with open("tests/data/broken_ICAO_stations") as f:
        stations = Stations(f, "ICAO")
    data = sorted(stations.items())
    assert "%s - %s" % data[0] == "KBRX - Bordeaux (N41.933°; W104.950°)"
    assert (
        "%s - %s" % data[1]
        == "KCQB - Chandler, Chandler Municipal Airport (N35.724°; W096.820°)"
    )
    assert (
        "%s - %s" % data[2]
        == "KTYR - Tyler, Tyler Pounds Field (N32.359°; W095.404°)"
    )
