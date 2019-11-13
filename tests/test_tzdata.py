#
"""test_tzdata - Test tzdata support"""
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

from operator import attrgetter

from pytest import mark

from upoints.tzdata import (Zone, Zones)


class TestZone:
    def test___repr__(self):
        assert repr(Zone('+513030-0000731', 'GB', 'Europe/London')) == \
            "Zone('+513030-0000730', 'GB', 'Europe/London', None)"

    @mark.parametrize('args, result', [
        (('+513030-0000731', 'GB', 'Europe/London'),
         """Europe/London (GB: 51°30'30"N, 000°07'30"W)"""),
        (('+0658-15813', 'FM', 'Pacific/Ponape', ['Ponape (Pohnpei)', ]),
         """Pacific/Ponape (FM: 06°58'00"N, 158°13'00"W also Ponape (Pohnpei))"""),
    ])
    def test___str__(self, args, result):
        assert str(Zone(*args)) == result


class TestZones:
    def setup(self):
        self.zones = Zones(open('tests/data/timezones'))

    def test_import_locations(self):
        data = [str(v) for v in sorted(self.zones, key=attrgetter('zone'))]
        assert data == [
            """Africa/Luanda (AO: 08°48'00"S, 013°14'00"E)""",
            """America/Curacao (AN: 12°11'00"N, 069°00'00"W)""",
            """Antarctica/McMurdo (AQ: 77°50'00"S, 166°36'00"E also McMurdo Station, Ross Island)""",
        ]

    def test_dump_zone_file(self):
        assert Zones.dump_zone_file(self.zones) == \
            ['AN\t+121100-0690000\tAmerica/Curacao',
             'AO\t-084800+0131400\tAfrica/Luanda',
             'AQ\t-775000+1663600\tAntarctica/McMurdo\tMcMurdo Station, Ross Island']
