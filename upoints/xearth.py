#
# coding=utf-8
"""xearth - Imports xearth-style marker files"""
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

from upoints import (point, utils)


class Xearth(point.Point):

    """Class for representing a location from a Xearth marker.

    .. versionadded:: 0.2.0

    """

    __slots__ = ('comment', )

    def __init__(self, latitude, longitude, comment=None):
        """Initialise a new ``Xearth`` object.

        :param float latitude: Location's latitude
        :param float longitude: Location's longitude
        :param str comment: Comment for location

        """
        super(Xearth, self).__init__(latitude, longitude)
        self.comment = comment

    def __str__(self):
        """Pretty printed location string.

        .. seealso:

           :class:`point.Point`

        :rtype: ``str``
        :return: Human readable string representation of ``Xearth`` object

        """
        text = super(Xearth, self).__str__()

        if self.comment:
            return '%s (%s)' % (self.comment, text)
        else:
            return text


class Xearths(point.KeyedPoints):

    """Class for representing a group of :class:`Xearth` objects.

    .. versionadded:: 0.5.1

    """

    def __init__(self, marker_file=None):
        """Initialise a new ``Xearths`` object."""
        super(Xearths, self).__init__()
        self._marker_file = marker_file
        if marker_file:
            self.import_locations(marker_file)

    def __str__(self):
        """``Xearth`` objects rendered for use with Xearth/Xplanet.

        :rtype: ``str``
        :return: Xearth/Xplanet marker file formatted output

        """
        return '\n'.join(utils.dump_xearth_markers(self, 'comment'))

    def import_locations(self, marker_file):
        """Parse Xearth data files.

        ``import_locations()`` returns a dictionary with keys containing the
        xearth_ name, and values consisting of a :class:`Xearth` object and
        a string containing any comment found in the marker file.

        It expects Xearth marker files in the following format::

            # Comment

            52.015     -0.221 "Home"          # James Rowe's home
            52.6333    -2.5   "Telford"

        Any empty line or line starting with a '#' is ignored.  All data lines
        are whitespace-normalised, so actual layout should have no effect.  The
        above file processed by ``import_locations()`` will return the
        following ``dict`` object::

            {'Home': point.Point(52.015, -0.221, "James Rowe's home"),
             'Telford': point.Point(52.6333, -2.5, None)}

        .. note:
           This function also handles the extended xplanet_ marker files whose
           points can optionally contain added xplanet specific keywords for
           defining colours and fonts.

        :type marker_file: ``file``, ``list`` or ``str``
        :param marker_file: Xearth marker data to read
        :rtype: ``dict``
        :return: Named locations with optional comments

        .. _xearth: http://hewgill.com/xearth/original/
        .. _xplanet: http://xplanet.sourceforge.net/

        """
        self._marker_file = marker_file
        data = utils.prepare_read(marker_file)

        for line in data:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            chunk = line.split('#')
            data = chunk[0]
            comment = chunk[1].strip() if len(chunk) == 2 else None
            # Need maximum split of 2, because name may contain whitespace
            latitude, longitude, name = data.split(None, 2)
            name = name.strip()
            # Find matching start and end quote, and keep only the contents
            name = name[1:name.find(name[0], 1)]
            self[name.strip()] = Xearth(latitude, longitude, comment)
