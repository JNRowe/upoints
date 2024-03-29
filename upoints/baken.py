#
"""baken - Imports baken data files."""
# Copyright © 2007-2021  James Rowe <jnrowe@gmail.com>
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

import logging
import re

from configparser import ConfigParser

from . import point, utils


class Baken(point.Point):
    """Class for representing location from baken_ data files.

    .. versionadded:: 0.4.0

    .. _baken: http://www.qsl.net:80/g4klx/
    """

    def __init__(
        self,
        latitude,
        longitude,
        antenna=None,
        direction=None,
        frequency=None,
        height=None,
        locator=None,
        mode=None,
        operator=None,
        power=None,
        qth=None,
    ):
        """Initialise a new ``Baken`` object.

        Args:
            latitude (float): Location’s latitude
            longitude (float): Location’s longitude
            antenna (str): Location’s antenna type
            direction (tuple of int): Antenna’s direction
            frequency (float): Transmitter’s frequency
            height (float): Antenna’s height
            locator (str): Location’s Maidenhead locator string
            mode (str): Transmitter’s mode
            operator (tuple of str): Transmitter’s operator
            power (float): Transmitter’s power
            qth (str): Location’s qth

        Raises:
            LookupError: No position data to use
        """
        if latitude is not None:
            super(Baken, self).__init__(latitude, longitude)
        elif locator is not None:
            latitude, longitude = utils.from_grid_locator(locator)
            super(Baken, self).__init__(latitude, longitude)
        else:
            raise LookupError(
                'Unable to instantiate baken object, no '
                'latitude or locator string'
            )

        self.antenna = antenna
        self.direction = direction
        self.frequency = frequency
        self.height = height
        self._locator = locator
        self.mode = mode
        self.operator = operator
        self.power = power
        self.qth = qth

    @property
    def locator(self):
        return self._locator

    @locator.setter
    def locator(self, value):
        """Update the locator, and trigger a latitude and longitude update.

        Args:
            value (str): New Maidenhead locator string
        """
        self._locator = value
        self._latitude, self._longitude = utils.from_grid_locator(value)

    def __str__(self):
        """Pretty printed location string.

        Args:
            mode (str): Coordinate formatting system to use

        Returns:
            str: Human readable string representation of ``Baken`` object
        """
        text = super(Baken, self).__format__('dms')
        if self._locator:
            text = f'{self._locator} ({text})'
        return text


class Bakens(point.KeyedPoints):
    """Class for representing a group of :class:`Baken` objects.

    .. versionadded:: 0.5.1
    """

    def __init__(self, baken_file=None):
        """Initialise a new `Bakens` object."""
        super(Bakens, self).__init__()
        if baken_file:
            self.import_locations(baken_file)

    def import_locations(self, baken_file):
        """Import baken data files.

        ``import_locations()`` returns a dictionary with keys containing the
        section title, and values consisting of a collection :class:`Baken`
        objects.

        It expects data files in the format used by the baken_ amateur radio
        package, which is Windows INI style files such as:

        .. code-block:: ini

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

        The reader uses the :mod:`configparser` module, so should be reasonably
        robust against encodings and such.  The above file processed by
        ``import_locations()`` will return the following ``dict`` object::

            {'Abeche, Chad': Baken(14.460, 20.680, None, None, None, 0.000,
                                   None, None, None, None, None),
             'GB3BUX': : Baken(None, None, '2 x Turnstile', None, 50.000,
                               460.000, 'IO93BF', 'A1A', None, 25, None)}

        Args::
            baken_file (iter): Baken data to read

        Returns:
            dict: Named locations and their associated values

        .. _baken: http://www.qsl.net:80/g4klx/
        """
        self._baken_file = baken_file
        data = ConfigParser()
        if hasattr(baken_file, 'readlines'):
            data.read_file(baken_file)
        elif isinstance(baken_file, list):
            data.read(baken_file)
        elif isinstance(baken_file, str):
            with open(baken_file) as f:
                data.readfp(f)
        else:
            raise TypeError(
                'Unable to handle data of type %r' % type(baken_file)
            )
        valid_locator = re.compile(r'[A-Z]{2}\d{2}[A-Z]{2}')
        for name in data.sections():
            elements = {}
            for item in (
                'latitude',
                'longitude',
                'antenna',
                'direction',
                'frequency',
                'height',
                'locator',
                'mode',
                'operator',
                'power',
                'qth',
            ):
                if data.has_option(name, item):
                    if item in ('antenna', 'locator', 'mode', 'power', 'qth'):
                        elements[item] = data.get(name, item)
                    elif item == 'operator':
                        elements[item] = elements[item].split(',')
                    elif item == 'direction':
                        elements[item] = data.get(name, item).split(',')
                    else:
                        try:
                            elements[item] = data.getfloat(name, item)
                        except ValueError:
                            logging.debug(
                                'Multiple frequency workaround for '
                                '%r entry',
                                name,
                            )
                            elements[item] = map(
                                float, data.get(name, item).split(',')
                            )
                else:
                    elements[item] = None
            if elements['latitude'] is None and not valid_locator.match(
                elements['locator']
            ):
                logging.info(
                    'Skipping %r entry, as it contains no location ' 'data',
                    name,
                )
                continue

            self[name] = Baken(**elements)
