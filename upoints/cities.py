#
# coding=utf-8
"""cities - Imports GNU miscfiles cities data files"""
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

__doc__ += """.

.. moduleauthor:: James Rowe <jnrowe@gmail.com>
.. versionadded:: 0.2.0
"""

import logging
import time

from upoints import (point, trigpoints, utils)

#: GNU miscfiles cities.dat template
TEMPLATE = """\
ID          : %s
Type        : %s
Population  : %s
Size        : %s
Name        : %s
 Country    : %s
 Region     : %s
Location    : %s
 Longitude  : %s
 Latitude   : %s
 Elevation  : %s
Date        : %s
Entered-By  : %s"""


class City(trigpoints.Trigpoint):

    """Class for representing an entry from the `GNU miscfiles`_ cities data file.

    .. versionadded:: 0.2.0

    .. _GNU miscfiles: http://directory.fsf.org/project/miscfiles/

    """

    __slots__ = ('identifier', 'ptype', 'population', 'size', 'country',
                 'region', 'location', 'date', 'entered')

    def __init__(self, identifier, name, ptype, region, country, location,
                 population, size, latitude, longitude, altitude, date,
                 entered):
        """Initialise a new ``City`` object.

        :param int identifier: Numeric identifier for object
        :param str name: Place name
        :param str ptype: Type of place
        :param str region: Region place can be found
        :param str country: Country name place can be found
        :param str location: Body place can be found
        :param int population: Place's population
        :param int size: Place's area
        :param float latitude: Station's latitude
        :param float longitude: Station's longitude
        :param int altitude: Station's elevation
        :param time.struct_time date: Date the entry was added
        :param str entered: Entry's author

        """
        super(City, self).__init__(latitude, longitude, altitude, name)
        self.identifier = identifier
        self.ptype = ptype
        self.region = region
        self.country = country
        self.location = location
        self.population = population
        self.size = size
        self.date = date
        self.entered = entered

    def __str__(self):
        """Pretty printed location string.

        :rtype: ``str``
        :return: Human readable string representation of ``City`` object

        """
        values = map(utils.value_or_empty,
                     (self.identifier, self.ptype,
                      self.population, self.size,
                      self.name, self.country,
                      self.region, self.location,
                      self.latitude, self.longitude,
                      self.altitude,
                      time.strftime('%Y%m%d', self.date) if self.date else '',
                      self.entered))
        return TEMPLATE % tuple(values)


class Cities(point.Points):

    """Class for representing a group of :class:`City` objects.

    .. versionadded:: 0.5.1

    """

    def __init__(self, data=None):
        """Initialise a new ``Cities`` object."""
        super(Cities, self).__init__()
        self._data = data
        if data:
            self.import_locations(data)

    def import_locations(self, data):
        """Parse `GNU miscfiles`_ cities data files.

        ``import_locations()`` returns a list containing :class:`City` objects.

        It expects data files in the same format that `GNU miscfiles`_
        provides, that is::

            ID          : 1
            Type        : City
            Population  : 210700
            Size        : 
            Name        : Aberdeen
             Country    : UK
             Region     : Scotland
            Location    : Earth
             Longitude  : -2.083
             Latitude   :   57.150
             Elevation  : 
            Date        : 19961206
            Entered-By  : Rob.Hooft@EMBL-Heidelberg.DE
            //
            ID          : 2
            Type        : City
            Population  : 1950000
            Size        : 
            Name        : Abidjan
             Country    : Ivory Coast
             Region     : 
            Location    : Earth
             Longitude  : -3.867
             Latitude   :    5.333
             Elevation  : 
            Date        : 19961206
            Entered-By  : Rob.Hooft@EMBL-Heidelberg.DE

        When processed by ``import_locations()`` will return ``list`` object in
        the following style::

            [City(1, "City", 210700, None, "Aberdeen", "UK", "Scotland",
                  "Earth", -2.083, 57.15, None, (1996, 12, 6, 0, 0, 0, 4,
                  341, -1), "Rob.Hooft@EMBL-Heidelberg.DE"),
             City(2, "City", 1950000, None, "Abidjan", "Ivory Coast", "",
                  "Earth", -3.867, 5.333, None, (1996, 12, 6, 0, 0, 0, 4,
                  341, -1), "Rob.Hooft@EMBL-Heidelberg.DE")])

        :type data: ``file``, ``list`` or ``str``
        :param data:
            :abbr:`NOAA (National Oceanographic and Atmospheric Administration)`
            station data to read
        :rtype: ``list``
        :return: Places as ``City`` objects
        :raise TypeError: Invalid value for data

        .. _GNU miscfiles: http://directory.fsf.org/project/miscfiles/

        """
        self._data = data
        if hasattr(data, 'read'):
            data = data.read().split('//\n')
        elif isinstance(data, list):
            pass
        elif isinstance(data, basestring):
            data = open(data).read().split('//\n')
        else:
            raise TypeError('Unable to handle data of type %r' % type(data))

        keys = ('identifier', 'ptype', 'population', 'size', 'name', 'country',
                'region', 'location', 'longitude', 'latitude', 'altitude',
                'date', 'entered')

        for record in data:
            # We truncate after splitting because the v1.4.2 datafile contains
            # a broken separator between 229 and 230 that would otherwise break
            # the import
            data = [i.split(':')[1].strip() for i in record.splitlines()[:13]]
            entries = dict(zip(keys, data))

            # Entry for Utrecht has the incorrect value of 0.000 for elevation.
            if entries['altitude'] == '0.000':
                logging.debug("Ignoring `0.000' value for elevation in %r "
                              'entry' % record)
                entries['altitude'] = ''
            for i in ('identifier', 'population', 'size', 'altitude'):
                entries[i] = int(entries[i]) if entries[i] else None
            for i in ('longitude', 'latitude'):
                entries[i] = float(entries[i]) if entries[i] else None
            entries['date'] = time.strptime(entries['date'], '%Y%m%d')
            self.append(City(**entries))
