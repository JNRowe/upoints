#
# coding=utf-8
"""kml - Imports KML data files"""
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

import logging

from lxml import etree

from upoints import (point, trigpoints, utils)

KML_NS = 'http://earth.google.com/kml/2.2'
etree.register_namespace('kml', KML_NS)

create_elem = utils.element_creator(KML_NS)


class Placemark(trigpoints.Trigpoint):

    """Class for representing a Placemark element from KML data files.

    .. versionadded:: 0.6.0

    """

    __slots__ = ('description', )

    def __init__(self, latitude, longitude, altitude=None, name=None,
                 description=None):
        """Initialise a new ``Placemark`` object.

        :param float latitude: Placemarks's latitude
        :param float longitude: Placemark's longitude
        :param float altitude: Placemark's altitude
        :param str name: Name for placemark
        :param str description: Placemark's description

        """
        super(Placemark, self).__init__(latitude, longitude, altitude, name)

        if altitude:
            self.altitude = float(altitude)
        self.description = description

    def __str__(self):
        """Pretty printed location string.

        :rtype: ``str``
        :return: Human readable string representation of ``Placemark`` object

        """
        location = super(Placemark, self).__format__('dms')
        if self.description:
            return '%s [%s]' % (location, self.description)
        else:
            return location

    def tokml(self):
        """Generate a KML Placemark element subtree.

        :rtype: :class:`etree.Element`
        :return: KML Placemark element

        """
        placemark = create_elem('Placemark')
        if self.name:
            placemark.set('id', self.name)
            placemark.name = create_elem('name', text=self.name)
        if self.description:
            placemark.description = create_elem('description',
                                                text=self.description)
        placemark.Point = create_elem('Point')

        data = [str(self.longitude), str(self.latitude)]
        if self.altitude:
            if int(self.altitude) == self.altitude:
                data.append('%i' % self.altitude)
            else:
                data.append(str(self.altitude))
        placemark.Point.coordinates = create_elem('coordinates',
                                                  text=','.join(data))

        return placemark


class Placemarks(point.KeyedPoints):

    """Class for representing a group of :class:`Placemark` objects.

    .. versionadded:: 0.6.0

    """

    def __init__(self, kml_file=None):
        """Initialise a new ``Placemarks`` object."""
        super(Placemarks, self).__init__()
        self._kml_file = kml_file
        if kml_file:
            self.import_locations(kml_file)

    def import_locations(self, kml_file):
        """Import KML data files.

        ``import_locations()`` returns a dictionary with keys containing the
        section title, and values consisting of :class:`Placemark` objects.

        It expects data files in KML format, as specified in `KML Reference`_,
        which is XML such as::

            <?xml version="1.0" encoding="utf-8"?>
            <kml xmlns="http://earth.google.com/kml/2.1">
                <Document>
                    <Placemark id="Home">
                        <name>Home</name>
                        <Point>
                            <coordinates>-0.221,52.015,60</coordinates>
                        </Point>
                    </Placemark>
                    <Placemark id="Cambridge">
                        <name>Cambridge</name>
                        <Point>
                            <coordinates>0.390,52.167</coordinates>
                        </Point>
                    </Placemark>
                </Document>
            </kml>

        The reader uses the :mod:`ElementTree` module, so should be very fast
        when importing data.  The above file processed by
        ``import_locations()`` will return the following ``dict`` object::

            {"Home": Placemark(52.015, -0.221, 60),
             "Cambridge": Placemark(52.167, 0.390, None)}

        :type kml_file: ``file``, ``list`` or ``str``
        :param kml_file: KML data to read
        :rtype: ``dict``
        :return: Named locations with optional comments

        .. _KML Reference:
           http://code.google.com/apis/kml/documentation/kmlreference.html

        """
        self._kml_file = kml_file
        data = utils.prepare_xml_read(kml_file, objectify=True)

        for place in data.Document.Placemark:
            name = place.name.text
            coords = place.Point.coordinates.text
            if coords is None:
                logging.info('No coordinates found for %r entry' % name)
                continue
            coords = coords.split(',')
            if len(coords) == 2:
                longitude, latitude = coords
                altitude = None
            elif len(coords) == 3:
                longitude, latitude, altitude = coords
            else:
                raise ValueError('Unable to handle coordinates value %r'
                                 % coords)
            try:
                description = place.description
            except AttributeError:
                description = None
            self[name] = Placemark(latitude, longitude, altitude, name,
                                   description)

    def export_kml_file(self):
        """Generate KML element tree from ``Placemarks``.

        :rtype: :class:`etree.ElementTree`
        :return: KML element tree depicting ``Placemarks``

        """
        kml = create_elem('kml')
        kml.Document = create_elem('Document')
        for place in sorted(self.values(), key=lambda x: x.name):
            kml.Document.append(place.tokml())

        return etree.ElementTree(kml)
