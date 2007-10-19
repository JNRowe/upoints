#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""baken - Imports baken data files"""
# Copyright (C) 2007  James Rowe
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

import ConfigParser
import os
import re

from earth_distance import point
import utils

class Baken(point.Point):
    """
    Class for representing location from baken data files

    @ivar latitude: Location's latitude
    @ivar longitude: Locations's longitude
    @ivar antenna: Location's antenna type
    @ivar direction: Antenna's direction
    @ivar frequency: Transmitter's frequency
    @ivar height: Antenna's height
    @ivar locator: Location's locator string
    @ivar mode: Transmitter's mode
    @ivar operator: Transmitter's operator
    @ivar power: Transmitter's power
    @ivar qth: Location's qth
    """

    __slots__ = ('antenna', 'direction', 'frequency', 'height', 'locator',
                 'mode', 'operator', 'power', 'qth')

    def __init__(self, latitude, longitude, antenna, direction, frequency,
                 height, locator, mode, operator, power, qth):
        """
        Initialise a new Baken object

        >>> obj = Baken(*(None, ) * 11)
        Traceback (most recent call last):
        ...
        LookupError: Unable to instantiate baken object, no latitude or locator string

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Location's longitude
        @type antenna: C{str}
        @param antenna Location's antenna type
        @type direction: C{tuple} of C{int}
        @param direction Antenna's direction
        @type frequency: C{float}
        @param frequency Transmitter's frequency
        @type height: C{float}
        @param height Antenna's height
        @type locator: C{str}
        @param locator Location's Maidenhead locator string
        @type mode: C{str}
        @param mode Transmitter's mode
        @type operator: C{tuple} of C{str}
        @param operator Transmitter's operator
        @type power: C{float}
        @param power Transmitter's power
        @type qth: C{str}
        @param qth Location's qth
        @raise LookupError: No position data to use
        """
        if not latitude is None:
            super(Baken, self).__init__(latitude, longitude)
        elif not locator is None:
            super(Baken, self).__init__(*utils.from_grid_locator(locator))
        else:
            raise LookupError("Unable to instantiate baken object, no latitude"
                              " or locator string")

        self.antenna = antenna
        self.direction = direction
        self.frequency = frequency
        self.height = height
        self.locator = locator
        self.mode = mode
        self.operator = operator
        self.power = power
        self.qth = qth

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Baken(14.460, 20.680, None, None, None, 0.000, None, None, None,
        ...       None, None)
        Baken(14.46, 20.68, None, None, None, 0.0, None, None, None, None, None)
        >>> Baken(None, None, "2 x Turnstile", None, 50.000, 460.000, "IO93BF",
        ...       "A1A", None, 25, None)
        Baken(53.2291666667, -1.875, '2 x Turnstile', None, 50.0, 460.0, 'IO93BF', 'A1A', None, 25, None)

        @rtype: C{str}
        @return: String to recreate Baken object
        """
        data = []
        for i in (self.latitude, self.longitude, self.antenna, self.direction,
                   self.frequency, self.height, self.locator, self.mode,
                   self.operator, self.power, self.qth):
            if isinstance(i, (type(None), list, str)):
                data.append(repr(i))
            else:
                data.append(str(i))
        return 'Baken(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Baken(14.460, 20.680, None, None, None, 0.000, None, None, None,
        ...             None, None))
        14°27'36"N, 020°40'48"E
        >>> print(Baken(None, None, "2 x Turnstile", None, 50.000, 460.000, "IO93BF",
        ...             "A1A", None, 25, None))
        IO93BF (53°13'45"N, 001°52'30"W)

        @rtype: C{str}
        @return: Human readable string representation of Point object
        """
        text = super(Baken, self).__str__(mode)
        if self.locator:
            text = "%s (%s)" % (self.locator, text)
        return text

def import_baken_file(baken_file):
    """
    Import baken data files

    C{import_baken_file()} returns a dictionary with keys containing the section
    title, and values consisting of a C{point.Point} object, and all the
    associated data from the baken data file.

    It expects data files in the format used by the baken amateur radio package,
    which is Windows INI style files such as::

        [Abeche, Chad]
        latitude=14.460000
        longitude=20.680000
        height=0.000000

        [GB3BUX]
        frequency=50.000
        locator=IO93BF
        power=25 TX
        antenna=2 x Turnstile
        height=460
        mode=A1A

    The reader uses U{Python <http://www.python.org/>}'s C{ConfigParser} module,
    so should be reasonably robust against encodings and such.  The above file
    processed by C{import_baken_file()} will return the following C{dict}
    object::

        {"Abeche, Chad": (Baken(14.460, 20.680, None, None, None, 0.000, None,
                                None, None, None, None),
         "GB3BUX": : (Baken(None, None, "2 x Turnstile", None, 50.000, 460.000,
                            "IO93BF", "A1A", None, 25, None)}

    >>> try:
    ...     from io import StringIO
    ... except ImportError:
    ...     from StringIO import StringIO
    >>> baken_file = StringIO("\\n".join([
    ...     '[Abeche, Chad]',
    ...     'latitude=14.460000',
    ...     'longitude=20.680000',
    ...     'height=0.000000',
    ...     '',
    ...     '[GB3BUX]',
    ...     'frequency=50.000',
    ...     'locator=IO93BF',
    ...     'power=25 TX',
    ...     'antenna=2 x Turnstile',
    ...     'height=460',
    ...     'mode=A1A',
    ...     '',
    ...     '[IW1RCT]',
    ...     'frequency=50.001',
    ...     'locator=JN44FH',
    ...     'power=2 TX',
    ...     'antenna=3 ele Yagi',
    ...     'direction=90',
    ...     'mode=A1A']))
    >>> locations = import_baken_file(baken_file)
    >>> for key, value in sorted(locations.items()):
    ...     print("%s - %s" % (key, value))
    Abeche, Chad - 14°27'36"N, 020°40'48"E
    GB3BUX - IO93BF (53°13'45"N, 001°52'30"W)
    IW1RCT - JN44FH (44°18'45"N, 008°27'29"E)
    >>> no_valid_locations_file = StringIO("\\n".join([
    ...     '[SV1UY-12]',
    ...     'frequency=144.625',
    ...     'locator=TCP/IP',
    ...     'qth=Athen 1200 ']))
    >>> locations = import_baken_file(no_valid_locations_file)
    >>> len(locations)
    0

    @type baken_file: C{file}, C{list} or C{str}
    @param baken_file: Baken data to read
    @rtype: C{dict}
    @return: Named locations with optional comments
    """
    data = ConfigParser.ConfigParser()
    if hasattr(baken_file, "readlines"):
        data.readfp(baken_file)
    elif isinstance(baken_file, list):
        data.read(baken_file)
    elif isinstance(baken_file, str):
        if os.path.isfile(baken_file):
            data.readfp(open(baken_file))
    else:
        raise ValueError("Unable to handle data of type `%s`"
                         % type(baken_file))
    locations = {}
    valid_locator = re.compile("[A-Z]{2}[0-9]{2}[A-Z]{2}")
    for name in data.sections():
        elements = {}
        for item in ("latitude", "longitude", "antenna", "direction",
                     "frequency", "height", "locator", "mode", "operator",
                     "power", "qth"):
            if data.has_option(name, item):
                if item in ("antenna", "locator", "mode", "operator", "power",
                            "qth"):
                    elements[item] = data.get(name, item)
                    if item == "operator":
                        elements[item] = elements[item].split(",")
                elif item == "direction":
                    elements[item] = data.get(name, item).split(",")
                else:
                    try:
                        elements[item] = data.getfloat(name, item)
                    except ValueError:
                        # Work around stations with multiple frequencies
                        # TODO: Maybe it is better to ignore these
                        elements[item] = data.get(name, item).split(",")
            else:
                elements[item] = None
        # Some locations in the "nodefile" data do not contain any location
        # information, and are therefore not useful for our purposes.
        if elements["latitude"] is None \
           and not valid_locator.match(elements["locator"]):
            continue

        locations[name] = Baken(**elements)
    return locations

