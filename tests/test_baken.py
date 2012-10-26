#
# coding=utf-8
"""test_baken - Test baken support"""
# Copyright (C) 2006-2011  James Rowe <jnrowe@gmail.com>
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


from upoints.baken import (Baken, Bakens)


class TestBaken():
    def test___init__(test):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Baken(14.460, 20.680, None, None, None, 0.000, None, None, None,
        ...       None, None)
        Baken(14.46, 20.68, None, None, None, 0.0, None, None, None, None,
              None)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Baken(None, None, "2 x Turnstile", None, 50.000, 460.000, "IO93BF",
        ...       "A1A", None, 25, None)
        Baken(53.2291666667, -1.875, '2 x Turnstile', None, 50.0, 460.0,
              'IO93BF', 'A1A', None, 25, None)
        >>> obj = Baken(None, None)
        Traceback (most recent call last):
        ...
        LookupError: Unable to instantiate baken object, no latitude or
        locator string

        """

    def test__set_locator(self):
        """
        >>> test = Baken(None, None, "2 x Turnstile", None, 50.000, 460.000,
        ...              "IO93BF", "A1A", None, 25, None)
        >>> test.locator = "JN44FH"
        >>> test
        Baken(44.3125, 8.45833333333, '2 x Turnstile', None, 50.0, 460.0,
              'JN44FH', 'A1A', None, 25, None)

        """

    def test___str__(self):
        """
        >>> print(Baken(14.460, 20.680, None, None, None, 0.000, None, None,
        ...             None, None, None))
        14°27'36"N, 020°40'48"E
        >>> print(Baken(None, None, "2 x Turnstile", None, 50.000, 460.000,
        ...             "IO93BF", "A1A", None, 25, None))
        IO93BF (53°13'45"N, 001°52'30"W)

        """


class TestBakens():
    def test_import_locations(self):
        """
        >>> locations = Bakens(open("test/data/baken_data"))
        >>> for key, value in sorted(locations.items()):
        ...     print("%s - %s" % (key, value))
        Abeche, Chad - 14°27'36"N, 020°40'48"E
        GB3BUX - IO93BF (53°13'45"N, 001°52'30"W)
        IW1RCT - JN44FH (44°18'45"N, 008°27'29"E)
        >>> locations = Bakens(open("test/data/no_valid_baken"))
        >>> len(locations)
        0

        """
