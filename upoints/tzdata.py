#
# coding=utf-8
"""tzdata - Imports timezone data files from UNIX zoneinfo"""
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

from upoints import (point, utils)
from upoints.compat import mangle_repr_type


@mangle_repr_type
class Zone(point.Point):

    """Class for representing timezone descriptions from zoneinfo data.

    .. versionadded:: 0.6.0

    """

    __slots__ = ('country', 'zone', 'comments')

    def __init__(self, location, country, zone, comments=None):
        """Initialise a new ``Zone`` object.

        :param str location: Primary location in ISO 6709 format
        :param str country: Location's ISO 3166 country code
        :param str zone: Location's zone name as used in zoneinfo database
        :param list comments: Location's alternate names

        """
        latitude, longitude = utils.from_iso6709(location + '/')[:2]
        super(Zone, self).__init__(latitude, longitude)

        self.country = country
        self.zone = zone
        self.comments = comments

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: ``str``
        :return: String to recreate ``Zone`` object

        """
        location = utils.to_iso6709(self.latitude, self.longitude,
                                    format='dms')[:-1]
        return utils.repr_assist(self, {'location': location})

    def __str__(self):
        """Pretty printed location string.

        :param str mode: Coordinate formatting system to use
        :rtype: ``str``
        :return: Human readable string representation of ``Zone`` object

        """
        text = ['%s (%s: %s' % (self.zone, self.country,
                                super(Zone, self).__format__('dms')), ]
        if self.comments:
            text.append(' also ' + ', '.join(self.comments))
        text.append(')')
        return ''.join(text)


class Zones(point.Points):

    """Class for representing a group of :class:`Zone` objects.

    .. versionadded:: 0.6.0

    """

    def __init__(self, zone_file=None):
        """Initialise a new Zones object."""
        super(Zones, self).__init__()
        self._zone_file = zone_file
        if zone_file:
            self.import_locations(zone_file)

    def import_locations(self, zone_file):
        """Parse zoneinfo zone description data files.

        ``import_locations()`` returns a list of :class:`Zone` objects.

        It expects data files in one of the following formats::

            AN	+1211-06900	America/Curacao
            AO	-0848+01314	Africa/Luanda
            AQ	-7750+16636	Antarctica/McMurdo	McMurdo Station, Ross Island

        Files containing the data in this format can be found in the
        :file:`zone.tab` file that is normally found in
        :file:`/usr/share/zoneinfo` on UNIX-like systems, or from the `standard
        distribution site`_.

        When processed by ``import_locations()`` a ``list`` object of the
        following style will be returned::

            [Zone(None, None, "AN", "America/Curacao", None),
             Zone(None, None, "AO", "Africa/Luanda", None),
             Zone(None, None, "AO", "Antartica/McMurdo",
                  ["McMurdo Station", "Ross Island"])]

        :type zone_file: ``file``, ``list`` or ``str``
        :param zone_file: ``zone.tab`` data to read
        :rtype: ``list``
        :return: Locations as :class:`Zone` objects
        :raise FileFormatError: Unknown file format

        .. _standard distribution site: ftp://elsie.nci.nih.gov/pub/

        """
        self._zone_file = zone_file
        field_names = ('country', 'location', 'zone', 'comments')

        data = utils.prepare_csv_read(zone_file, field_names, delimiter=r"	")

        for row in (x for x in data if not x['country'].startswith('#')):
            if row['comments']:
                row['comments'] = row['comments'].split(', ')
            self.append(Zone(**row))

    def dump_zone_file(self):
        """Generate a zoneinfo compatible zone description table.

        :rtype: ``list``
        :return: zoneinfo descriptions

        """
        data = []
        for zone in sorted(self, key=attrgetter('country')):
            text = ['%s	%s	%s'
                    % (zone.country,
                       utils.to_iso6709(zone.latitude, zone.longitude,
                                        format='dms')[:-1],
                       zone.zone), ]
            if zone.comments:
                text.append('	%s' % ', '.join(zone.comments))
            data.append(''.join(text))
        return data
