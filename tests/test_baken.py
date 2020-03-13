#
"""test_baken - Test baken support"""
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

from pytest import raises

from upoints.baken import (Baken, Bakens)


class TestBaken:
    def test___repr__(self):
        assert repr(Baken(14.460, 20.680, None, None, None, 0.000, None, None,
                          None, None, None)) == \
            'Baken(14.46, 20.68, None, None, None, 0.0, None, None, None, None, None)'
        assert repr(Baken(None, None, '2 x Turnstile', None, 50.000, 460.000,
                          'IO93BF', 'A1A', None, 25, None)) == \
            ("Baken(%s, -1.875, '2 x Turnstile', None, 50.0, "
             "460.0, 'IO93BF', 'A1A', None, 25, None)" % 53.229166666666686)

        with raises(LookupError,
                    match=('Unable to instantiate baken object, no latitude '
                           'or locator string')):
            Baken(None, None)

    def test__set_locator(self):
        test = Baken(None, None, '2 x Turnstile', None, 50.000, 460.000,
                     'IO93BF', 'A1A', None, 25, None)
        test.locator = 'JN44FH'
        assert test.latitude == 44.3125
        assert test.longitude == 8.458333333333314

    def test___str__(self):
        assert str(Baken(14.460, 20.680, None, None, None, 0.000, None, None,
                         None, None, None)) == \
            '14°27′36″N, 020°40′48″E'
        assert str(Baken(None, None, '2 x Turnstile', None, 50.000, 460.000,
                         'IO93BF', 'A1A', None, 25, None)) == \
            'IO93BF (53°13′45″N, 001°52′30″W)'


class TestBakens:
    def test_import_locations(self):
        with open('tests/data/baken_data') as f:
            locations = Bakens(f)
        data = ['%s - %s' % (k, v) for k, v in sorted(locations.items())]

        assert data == [
            'Abeche, Chad - 14°27′36″N, 020°40′48″E',
            'GB3BUX - IO93BF (53°13′45″N, 001°52′30″W)',
            'IW1RCT - JN44FH (44°18′45″N, 008°27′29″E)',
        ]

    def test_import_locations2(self):
        with open('tests/data/no_valid_baken') as f:
            locations = Bakens(f)
        assert len(locations) == 0
