#
# coding=utf-8
"""test_tzdata - Test tzdata support"""
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

from operator import attrgetter
from unittest import TestCase

from expecter import expect

from upoints.tzdata import (Zone, Zones)


class TestZone(TestCase):
    def test___repr__(self):
        expect(repr(Zone('+513030-0000731', 'GB', 'Europe/London'))) == \
            "Zone('+513030-0000730', 'GB', 'Europe/London', None)"

    def test___str__(self):
        expect(str(Zone('+513030-0000731', 'GB', 'Europe/London'))) == \
            """Europe/London (GB: 51°30'30"N, 000°07'30"W)"""
        expect(str(Zone('+0658-15813', 'FM', 'Pacific/Ponape',
                        ['Ponape (Pohnpei)', ]))) == \
            """Pacific/Ponape (FM: 06°58'00"N, 158°13'00"W also Ponape (Pohnpei))"""


class TestZones(TestCase):
    def test_import_locations(self):
        zones = Zones(open('tests/data/timezones'))
        data = [str(v) for v in sorted(zones, key=attrgetter('zone'))]
        expect(data[0]) == """Africa/Luanda (AO: 08°48'00"S, 013°14'00"E)"""
        expect(data[1]) == """America/Curacao (AN: 12°11'00"N, 069°00'00"W)"""
        expect(data[2]) == \
            """Antarctica/McMurdo (AQ: 77°50'00"S, 166°36'00"E also McMurdo Station, Ross Island)"""

    def test_dump_zone_file(self):
        zones = Zones(open('tests/data/timezones'))
        expect(Zones.dump_zone_file(zones)) == \
            ['AN\t+121100-0690000\tAmerica/Curacao',
             'AO\t-084800+0131400\tAfrica/Luanda',
             'AQ\t-775000+1663600\tAntarctica/McMurdo\tMcMurdo Station, Ross Island']
