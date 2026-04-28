#
"""test_nmea - Test NMEA support"""
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

from pytest import fixture, mark

from upoints.nmea import (
    Fix,
    Locations,
    LoranPosition,
    Position,
    Waypoint,
    calc_checksum,
    nmea_latitude,
    nmea_longitude,
    parse_latitude,
    parse_longitude,
)


@mark.parametrize(
    "start, end",
    [
        ("$", "*6B"),
        ("", "*6B"),
        ("$", ""),
        ("", ""),
    ],
)
def test_calc_checksum(start, end):
    s = "GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,"
    assert calc_checksum(start + s + end) == 107


def test_nmea_latitude():
    assert nmea_latitude(53.144023333333337) == ("5308.6414", "N")


def test_nmea_longitude():
    assert nmea_longitude(-3.0154283333333334) == ("00300.9257", "W")


def test_parse_latitude():
    assert parse_latitude("5308.6414", "N") == 53.14402333333334


def test_parse_longitude():
    assert parse_longitude("00300.9257", "W") == -3.0154283333333334


@mark.parametrize(
    "args, result",
    [
        (
            (
                53.1440233333,
                -3.01542833333,
                datetime.time(14, 20, 58, 14),
                True,
                None,
            ),
            "LoranPosition(53.1440233333, -3.01542833333, "
            "datetime.time(14, 20, 58, 14), True, None)",
        ),
        (
            (
                53.1440233333,
                -3.01542833333,
                datetime.time(14, 20, 58, 14),
                True,
                "A",
            ),
            "LoranPosition(53.1440233333, -3.01542833333, "
            "datetime.time(14, 20, 58, 14), True, 'A')",
        ),
    ],
)
def test_LoranPosition___repr__(args, result):
    assert repr(LoranPosition(*args)) == result


@mark.parametrize(
    "args, result",
    [
        (
            (
                53.1440233333,
                -3.01542833333,
                datetime.time(14, 20, 58, 14),
                True,
                None,
            ),
            "$GPGLL,5308.6414,N,00300.9257,W,142058.00,A*1F\r",
        ),
        (
            (
                53.1440233333,
                -3.01542833333,
                datetime.time(14, 20, 58, 14),
                True,
                "A",
            ),
            "$GPGLL,5308.6414,N,00300.9257,W,142058.00,A,A*72\r",
        ),
    ],
)
def test_LoranPosition___str__(args, result):
    assert str(LoranPosition(*args)) == result


def test_LoranPosition_mode_string():
    position = LoranPosition(
        53.1440233333,
        -3.01542833333,
        datetime.time(14, 20, 58),
        True,
        None,
    )
    assert str(position.mode_string()) == "Unknown"
    position.mode = "A"
    assert str(position.mode_string()) == "Autonomous"


def test_LoranPosition_parse_elements():
    assert LoranPosition.parse_elements([
        "52.32144",
        "N",
        "00300.9257",
        "W",
        "14205914",
        "A",
    ]) == LoranPosition(
        52.005357333333336,
        -3.0154283333333334,
        datetime.time(14, 20, 59, 140000),
        True,
        None,
    )


@fixture
def sample_Position():
    yield Position(
        datetime.time(14, 20, 58),
        True,
        53.1440233333,
        -3.01542833333,
        109394.7,
        202.9,
        datetime.date(2007, 11, 19),
        5.0,
    )


def test_Position___repr__(sample_Position):
    assert repr(sample_Position) == (
        "Position(datetime.time(14, 20, 58), True, 53.1440233333, "
        "-3.01542833333, 109394.7, 202.9, datetime.date(2007, 11, 19), "
        "5.0, None)"
    )


def test_Position___str__(sample_Position):
    assert (
        str(sample_Position)
        == "$GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E*41\r"
    )


def test_Position_mode_string(sample_Position):
    assert str(sample_Position.mode_string()) == "Unknown"
    sample_Position.mode = "A"
    assert str(sample_Position.mode_string()) == "Autonomous"


def test_Position_parse_elements():
    assert repr(
        Position.parse_elements([
            "142058",
            "A",
            "5308.6414",
            "N",
            "00300.9257",
            "W",
            "109394.7",
            "202.9",
            "191107",
            "5",
            "E",
            "A",
        ])
    ) == (
        "Position(datetime.time(14, 20, 58), True, 53.14402333333334, "
        "-3.0154283333333334, 109394.7, 202.9, "
        "datetime.date(2007, 11, 19), 5.0, 'A')"
    )
    assert repr(
        Position.parse_elements([
            "142100",
            "A",
            "5200.9000",
            "N",
            "00316.6600",
            "W",
            "123142.7",
            "188.1",
            "191107",
            "5",
            "E",
            "A",
        ])
    ) == (
        "Position(datetime.time(14, 21), True, 52.015, "
        "-3.2776666666666667, 123142.7, "
        "188.1, datetime.date(2007, 11, 19), 5.0, 'A')"
    )


@fixture
def sample_Fix():
    yield Fix(
        datetime.time(14, 20, 27),
        52.1380333333,
        -2.56861166667,
        1,
        4,
        5.6,
        1052.3,
        34.5,
    )


def test_Fix___repr__(sample_Fix):
    assert repr(sample_Fix) == (
        "Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, "
        "1, 4, 5.6, 1052.3, 34.5, None, None, None)"
    )
    sample_Fix.dgps_delta = 12
    sample_Fix.dgps_station = 4
    assert repr(sample_Fix) == (
        "Fix(datetime.time(14, 20, 27), 52.1380333333, -2.56861166667, "
        "1, 4, 5.6, 1052.3, 34.5, 12, 4, None)"
    )


def test___str__(sample_Fix):
    assert (
        str(sample_Fix)
        == "$GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,,*61\r"
    )
    sample_Fix.dgps_delta = 12
    sample_Fix.dgps_station = 4
    assert (
        str(sample_Fix)
        == "$GPGGA,142027,5208.2820,N,00234.1167,W,1,04,5.6,1052.3,M,34.5,M,12.0,0004*78\r"
    )


def test_quality_string(sample_Fix):
    assert str(sample_Fix.quality_string()) == "GPS"


@mark.parametrize(
    "elements, result",
    [
        (
            [
                "142058",
                "5308.6414",
                "N",
                "00300.9257",
                "W",
                "1",
                "04",
                "5.6",
                "1374.6",
                "M",
                "34.5",
                "M",
                "",
                "",
            ],
            "Fix(datetime.time(14, 20, 58), 53.14402333333334, "
            "-3.0154283333333334, 1, 4, 5.6, 1374.6, 34.5, None, None, None)",
        ),
        (
            [
                "142100",
                "5200.9000",
                "N",
                "00316.6600",
                "W",
                "1",
                "04",
                "5.6",
                "1000.0",
                "M",
                "34.5",
                "M",
                "",
                "",
            ],
            "Fix(datetime.time(14, 21), 52.015, -3.2776666666666667, 1, 4, 5.6, "
            "1000.0, 34.5, None, None, None)",
        ),
    ],
)
def test_parse_elements(elements, result):
    assert repr(Fix.parse_elements(elements)) == result


def test_Waypoint___repr__():
    assert (
        repr(Waypoint(52.015, -0.221, "Home"))
        == "Waypoint(52.015, -0.221, 'HOME')"
    )


def test_Waypoint___str__():
    assert (
        str(Waypoint(52.015, -0.221, "Home"))
        == "$GPWPL,5200.9000,N,00013.2600,W,HOME*5E\r"
    )


def test_Waypoint_parse_elements():
    assert (
        repr(
            Waypoint.parse_elements([
                "5200.9000",
                "N",
                "00013.2600",
                "W",
                "HOME",
            ])
        )
        == "Waypoint(52.015, -0.221, 'HOME')"
    )


def test_Locations_import_locations():
    with open("tests/data/gpsdata") as f:
        locations = Locations(f)
    assert [str(x) for x in locations] == [
        "$GPGGA,142058,5308.6414,N,00300.9257,W,1,04,5.6,1374.6,M,34.5,M,,*6B\r",
        "$GPRMC,142058,A,5308.6414,N,00300.9257,W,109394.7,202.9,191107,5,E,A*2C\r",
        "$GPWPL,5200.9000,N,00013.2600,W,HOME*5E\r",
        "$GPGGA,142100,5200.9000,N,00316.6600,W,1,04,5.6,1000.0,M,34.5,M,,*68\r",
        "$GPRMC,142100,A,5200.9000,N,00316.6600,W,123142.7,188.1,191107,5,E,A*21\r",
    ]
