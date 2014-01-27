#
# coding=utf-8
"""trigpoints - Imports trigpoint marker files"""
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

from functools import partial

from upoints import (point, utils)


class Trigpoint(point.Point):

    """Class for representing a location from a trigpoint marker file.

    .. warning::
       Although this class stores and presents the representation of altitude
       it doesn't take it in to account when making calculations.  For example,
       consider a point at the base of Mount Everest and a point at the peak of
       Mount Everest the actual distance travelled between the two would be
       considerably larger than the reported value calculated at ground level.

    .. versionadded:: 0.2.0

    """

    __slots__ = ('altitude', 'name', 'identity')

    def __init__(self, latitude, longitude, altitude, name=None,
                 identity=None):
        """Initialise a new ``Trigpoint`` object.

        :param float latitude: Location's latitude
        :param float longitude: Location's longitude
        :param float altitude: Location's altitude
        :param str name: Name for location
        :param int identity: Database identifier, if known

        """
        super(Trigpoint, self).__init__(latitude, longitude)
        self.altitude = altitude
        self.name = name
        self.identity = identity

    def __str__(self):
        """Pretty printed location string.

        .. seealso::

           :type :class:`trigpoints.point.Point`

        :rtype: ``str``
        :return: Human readable string representation of ``Station`` object

        """
        return self.__format__()

    def __format__(self, format_spec='dms'):
        """Extended pretty printing for location strings.

        :param str format_spec: Coordinate formatting system to use
        :rtype: ``str``
        :return: Human readable string representation of ``Trigpoint`` object
        :raise ValueError: Unknown value for ``format_spec``

        """
        location = [super(Trigpoint, self).__format__(format_spec), ]
        if self.altitude:
            location.append('alt %im' % self.altitude)

        if self.name:
            return '%s (%s)' % (self.name, ' '.join(location))
        else:
            return ' '.join(location)


class Trigpoints(point.KeyedPoints):

    """Class for representing a group of :class:`Trigpoint` objects.

    .. versionadded:: 0.5.1

    """

    def __init__(self, marker_file=None):
        """Initialise a new ``Trigpoints`` object."""
        super(Trigpoints, self).__init__()
        self._marker_file = marker_file
        if marker_file:
            self.import_locations(marker_file)

    def import_locations(self, marker_file):
        """Import trigpoint database files.

        ``import_locations()`` returns a dictionary with keys containing the
        trigpoint identifier, and values that are :class:`Trigpoint` objects.

        It expects trigpoint marker files in the format provided at
        alltrigs-wgs84.txt_, which is the following format::

            H  SOFTWARE NAME & VERSION
            I  GPSU 4.04,
            S SymbolSet=0
            ...
            W,500936,N52.066035,W000.281449,    37.0,Broom Farm
            W,501097,N52.010585,W000.173443,    97.0,Bygrave
            W,505392,N51.910886,W000.186462,   136.0,Sish Lane

        Any line not consisting of 6 comma separated fields will be ignored.
        The reader uses the :mod:`csv` module, so alternative whitespace
        formatting should have no effect.  The above file processed by
        ``import_locations()`` will return the following ``dict`` object::

            {500936: point.Point(52.066035, -0.281449, 37.0, "Broom Farm"),
             501097: point.Point(52.010585, -0.173443, 97.0, "Bygrave"),
             505392: point.Point(51.910886, -0.186462, 136.0, "Sish Lane")}

        :type marker_file: ``file``, ``list`` or ``str``
        :param marker_file: Trigpoint marker data to read
        :rtype: ``dict``
        :return: Named locations with :class:`Trigpoint` objects
        :raise ValueError: Invalid value for ``marker_file``

        .. _alltrigs-wgs84.txt: http://www.haroldstreet.org.uk/trigpoints/

        """
        self._marker_file = marker_file
        field_names = ('tag', 'identity', 'latitude', 'longitude', 'altitude',
                       'name')
        pos_parse = lambda x, s: float(s[1:]) if s[0] == x else 0 - float(s[1:])
        latitude_parse = partial(pos_parse, 'N')
        longitude_parse = partial(pos_parse, 'E')
        # A value of 8888.0 denotes unavailable data
        altitude_parse = lambda s: None if s.strip() == '8888.0' else float(s)
        field_parsers = (str, int, latitude_parse, longitude_parse,
                         altitude_parse, str)

        data = utils.prepare_csv_read(marker_file, field_names)

        for row in (x for x in data if x['tag'] == 'W'):
            for name, parser in zip(field_names, field_parsers):
                row[name] = parser(row[name])
            del row['tag']
            try:
                self[row['identity']] = Trigpoint(**row)
            except TypeError:
                # Workaround formatting error in 506514 entry that contains
                # spurious comma
                del row[None]
                self[row['identity']] = Trigpoint(**row)
