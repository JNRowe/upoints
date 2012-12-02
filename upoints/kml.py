#
# coding=utf-8
"""kml - Imports KML data files"""
# Copyright © 2008, 2010, 2011, 2012  James Rowe <jnrowe@gmail.com>
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

from functools import partial

from lxml import etree as ET

from upoints import (point, trigpoints, utils)

KML_NS = "http://earth.google.com/kml/2.2"
ET.register_namespace('kml', KML_NS)


def create_elem(tag, attr=None, text=None):
    """Create a partial :class:`ET.Element` wrapper with namespace defined.

    :param str tag: Tag name
    :param dict attr: Default attributes for tag
    :param str text: Text content for the tag
    :rtype: ``function``
    :return: :class:`ET.Element` wrapper with predefined namespace

    """
    if not attr:
        attr = {}
    element = ET.Element("{%s}%s" % (KML_NS, tag), attr)
    if text:
        element.text = text
    return element


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

    def __str__(self, mode="dms"):
        """Pretty printed location string.

        :param str mode: Coordinate formatting system to use
        :rtype: ``str``
        :return: Human readable string representation of ``Placemark`` object

        """
        location = super(Placemark, self).__str__(mode)
        if self.description:
            return "%s [%s]" % (location, self.description)
        else:
            return location

    def tokml(self):
        """Generate a KML Placemark element subtree.

        :rtype: :class:`ET.Element`
        :return: KML Placemark element

        """
        element = partial(create_elem)
        placemark = element("Placemark")
        if self.name:
            placemark.set("id", self.name)
            nametag = element("name", None, self.name)
        if self.description:
            desctag = element("description", None, self.description)
        tpoint = element("Point")
        coords = element("coordinates")

        data = [str(self.longitude), str(self.latitude)]
        if self.altitude:
            if int(self.altitude) == self.altitude:
                data.append("%i" % self.altitude)
            else:
                data.append(str(self.altitude))
        coords.text = ",".join(data)

        if self.name:
            placemark.append(nametag)
        if self.description:
            placemark.append(desctag)
        placemark.append(tpoint)
        tpoint.append(coords)

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
        data = utils.prepare_xml_read(kml_file)

        kml_elem = lambda name: ET.QName(KML_NS, name).text
        placemark_elem = ".//" + kml_elem("Placemark")
        name_elem = kml_elem("name")
        coords_elem = kml_elem("Point") + "/" + kml_elem("coordinates")
        desc_elem = kml_elem("description")

        for place in data.findall(placemark_elem):
            name = place.findtext(name_elem)
            coords = place.findtext(coords_elem)
            if coords is None:
                logging.info("No coordinates found for `%s' entry" % name)
                continue
            coords = coords.split(",")
            if len(coords) == 2:
                longitude, latitude = coords
                altitude = None
            elif len(coords) == 3:
                longitude, latitude, altitude = coords
            else:
                raise ValueError("Unable to handle coordinates value `%s'"
                                    % coords)
            description = place.findtext(desc_elem)
            self[name] = Placemark(latitude, longitude, altitude, name,
                                    description)

    def export_kml_file(self):
        """Generate KML element tree from ``Placemarks``.

        :rtype: :class:`ET.ElementTree`
        :return: KML element tree depicting ``Placemarks``

        """
        element = partial(create_elem)
        kml = element('kml')
        doc = element('Document')
        for place in self.values():
            doc.append(place.tokml())
        kml.append(doc)

        return ET.ElementTree(kml)
