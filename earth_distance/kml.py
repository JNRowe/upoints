#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""kml - Imports KML data files"""
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

import logging
import os

from xml.etree import ElementTree

try:
    from xml.etree import cElementTree as ET
except ImportError:
    ET = ElementTree
    logging.info("cElementTree is unavailable XML processing will be much"
                 "slower with ElementTree")
    logging.warning("You have the fast cElementTree module available, if you "
                    "choose to use the human readable namespace prefixes "
                    "element generation will use the much slower ElementTree "
                    "code.  Slowdown can be in excess of five times.")

from earth_distance import (trigpoints, utils)

# Supported KML versions
KML_VERSIONS = {
  "2.0": "http://earth.google.com/kml/2.0",
  "2.1": "http://earth.google.com/kml/2.1",
  "2.2": "http://earth.google.com/kml/2.2",
}
# This is the default KML version to output, changing this will cause tests to
# fail.
DEF_KML_VERSION = "2.2"

def create_elem(tag, attr={}, kml_version=DEF_KML_VERSION, human_namespace=False):
    """
    Create a partial C{ET.Element} wrapper with namespace defined

    @type tag: C{str}
    @param tag: Tag name
    @type attr: C{dict}
    @param attr: Default attributes for tag
    @type kml_version: C{str}
    @param kml_version: KML version to use
    @type human_namespace: C{bool}
    @param human_namespace: Whether to generate output using human readable
        namespace prefixes
    @rtype: C{function}
    @return: C{ET.Element} wrapper with predefined namespace
    """
    try:
        kml_ns = KML_VERSIONS[kml_version]
    except KeyError:
        raise KeyError("Unknown KML version `%s'" % kml_version)
    if human_namespace:
        ElementTree._namespace_map[kml_ns] = "kml"
        return ElementTree.Element("{%s}%s" % (kml_ns, tag), attr)
    else:
        return ET.Element("{%s}%s" % (kml_ns, tag), attr)

class Placemark(trigpoints.Trigpoint):
    """
    Class for representing a Placemark element from KML data files

    @ivar latitude: Placemark's latitude
    @ivar longitude: Placemark's longitude
    @ivar altitude: Placemark's altitude
    """

    __slots__ = ('description', )

    def __init__(self, latitude, longitude, altitude=None, name=None,
                 description=None):
        """
        Initialise a new C{Placemark} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Placemarks's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Placemark's longitude
        @type altitude: C{float} or coercible to C{float}
        @param altitude Placemark's altitude
        @type name: C{string}
        @param name: Name for placemark
        @type description: C{string}
        @param description: Placemark's description
        """
        super(Placemark, self).__init__(latitude, longitude, altitude, name)

        if altitude:
            self.altitude = float(altitude)
        self.description = description

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Placemark(52, 0, 4)
        Placemark(52.0, 0.0, 4.0, None, None)
        >>> Placemark(52, 0, None)
        Placemark(52.0, 0.0, None, None, None)
        >>> Placemark(52, 0, None, "name", "desc")
        Placemark(52.0, 0.0, None, 'name', 'desc')

        @rtype: C{str}
        @return: String to recreate C{Placemark} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.altitude,
                                 self.name, self.description)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Placemark(52, 0, 4))
        52°00'00"N, 000°00'00"E alt 4m
        >>> print(Placemark(52, 0, None))
        52°00'00"N, 000°00'00"E
        >>> print(Placemark(52, 0, None, "name", "desc"))
        name (52°00'00"N, 000°00'00"E) [desc]
        >>> print(Placemark(52, 0, 42, "name", "desc"))
        name (52°00'00"N, 000°00'00"E alt 42m) [desc]

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Placemark} object
        """
        text = super(Placemark, self).__str__(mode)
        if self.description:
            text += " [%s]" % self.description
        return text

    def tokml(self, kml_version=DEF_KML_VERSION, human_namespace=False):
        """
        Generate a KML Placemark element subtree

        >>> ET.tostring(Placemark(52, 0, 4).tokml())
        '<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.2"><ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point></ns0:Placemark>'
        >>> ET.tostring(Placemark(52, 0, 4, "Cambridge").tokml())
        '<ns0:Placemark id="Cambridge" xmlns:ns0="http://earth.google.com/kml/2.2"><ns0:name>Cambridge</ns0:name><ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point></ns0:Placemark>'
        >>> ET.tostring(Placemark(52, 0, 4).tokml(kml_version="2.0"))
        '<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.0"><ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point></ns0:Placemark>'
        >>> ET.tostring(Placemark(52, 0, 4, "Cambridge", "in the UK").tokml())
        '<ns0:Placemark id="Cambridge" xmlns:ns0="http://earth.google.com/kml/2.2"><ns0:name>Cambridge</ns0:name><ns0:description>in the UK</ns0:description><ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point></ns0:Placemark>'

        @type kml_version: C{str}
        @param kml_version: KML version to generate
        @type human_namespace: C{bool}
        @param human_namespace: Whether to generate output using human readable
            namespace prefixes
        @rtype: C{ET.Element}
        @return: KML Placemark element
        """
        element = lambda tag, attr={}: create_elem(tag, attr, kml_version,
                                                   human_namespace)
        placemark = element("Placemark")
        if self.name:
            placemark.set("id", self.name)
            nametag = element("name")
            nametag.text = self.name
        if self.description:
            desctag = element("description")
            desctag.text = self.description
        point = element("Point")
        coords = element("coordinates")
        coords.text = "%s,%s" % (self.longitude, self.latitude)
        if self.altitude:
            if int(self.altitude) == self.altitude:
                coords.text += ",%i" % self.altitude
            else:
                coords.text += ",%s" % self.altitude

        if self.name:
            placemark.append(nametag)
        if self.description:
            placemark.append(desctag)
        placemark.append(point)
        point.append(coords)

        return placemark

class Placemarks(dict):
    """
    Class for representing a group of C{Placemark} objects
    """

    def __init__(self, kml_file=None):
        """
        Initialise a new C{Placemarks} object
        """
        dict.__init__(self)
        if kml_file:
            self.import_kml_file(kml_file)

    def import_kml_file(self, kml_file, kml_version=None):
        """
        Import KML data files

        C{import_KML_file()} returns a dictionary with keys containing the
        section title, and values consisting of C{Placemark} objects.

        It expects data files in KML format, as specified in U{KML Reference
        <http://code.google.com/apis/kml/documentation/kml_tags_21.html>}, which
        is XML such as::

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

        The reader uses U{Python <http://www.python.org/>}'s C{ElementTree}
        module, so should be very fast when importing data.  The above file
        processed by C{import_kml_file()} will return the following C{dict}
        object::

            {"Home": Placemark(52.015, -0.221, 60),
             "Cambridge": Placemark(52.167, 0.390, None)}

        >>> locations = Placemarks(open("kml"))
        >>> for value in sorted(locations.values(),
        ...                     lambda x,y: cmp(x.name.lower(),
        ...                                     y.name.lower())):
        ...     print(value)
        Cambridge (52°10'01"N, 000°23'24"E)
        Home (52°00'54"N, 000°13'15"W alt 60m)

        The C{kml_version} parameter allows the caller to specify the specific
        KML version that should be processed, this allows the caller to process
        inputs which contain entries in more than one namespace without
        duplicates resulting from entries in being specified with different
        namespaces.

        @type kml_file: C{file}, C{list} or C{str}
        @param kml_file: KML data to read
        @type kml_version: C{str}
        @param kml_version: Specific KML version entities to import
        @rtype: C{dict}
        @return: Named locations with optional comments
        """
        if hasattr(kml_file, "readlines"):
            data = ET.parse(kml_file)
        elif isinstance(kml_file, list):
            data = ET.fromstring("".join(kml_file))
        elif isinstance(kml_file, basestring):
            data = ET.parse(open(kml_file))
        else:
            raise TypeError("Unable to handle data of type `%s`"
                            % type(kml_file))

        if kml_version:
            try:
                accepted_kml = {kml_version: KML_VERSIONS[kml_version]}
            except KeyError:
                raise KeyError("Unknown KML version `%s'" % kml_version)
        else:
            accepted_kml = KML_VERSIONS

        for version, namespace in accepted_kml.items():
            logging.info("Searching for KML v%s entries" % version)
            kml_elem = lambda name: ET.QName(namespace, name).text
            placemark_elem = "//" + kml_elem("Placemark")
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

    def export_kml_file(self, kml_version=DEF_KML_VERSION,
                        human_namespace=False):
        """
        Generate KML element tree from C{Placemarks}

        >>> from sys import stdout
        >>> locations = Placemarks(open("kml"))
        >>> xml = locations.export_kml_file()
        >>> xml.write(stdout)
        <ns0:kml xmlns:ns0="http://earth.google.com/kml/2.2"><ns0:Document><ns0:Placemark id="Home"><ns0:name>Home</ns0:name><ns0:Point><ns0:coordinates>-0.221,52.015,60</ns0:coordinates></ns0:Point></ns0:Placemark><ns0:Placemark id="Cambridge"><ns0:name>Cambridge</ns0:name><ns0:Point><ns0:coordinates>0.39,52.167</ns0:coordinates></ns0:Point></ns0:Placemark></ns0:Document></ns0:kml>
        >>> xml = locations.export_kml_file("2.0")
        >>> xml.write(stdout)
        <ns0:kml xmlns:ns0="http://earth.google.com/kml/2.0"><ns0:Document><ns0:Placemark id="Home"><ns0:name>Home</ns0:name><ns0:Point><ns0:coordinates>-0.221,52.015,60</ns0:coordinates></ns0:Point></ns0:Placemark><ns0:Placemark id="Cambridge"><ns0:name>Cambridge</ns0:name><ns0:Point><ns0:coordinates>0.39,52.167</ns0:coordinates></ns0:Point></ns0:Placemark></ns0:Document></ns0:kml>

        @type kml_version: C{str}
        @param kml_version: KML version to generate
        @type human_namespace: C{bool}
        @param human_namespace: Whether to generate output using human readable
            namespace prefixes
        @rtype: C{ET.ElementTree}
        @return: KML element tree depicting C{Placemarks}
        """
        element = lambda tag, attr={}: create_elem(tag, attr, kml_version,
                                                   human_namespace)
        kml = element('kml')
        doc = element('Document')
        for name, place in self.items():
            doc.append(place.tokml(kml_version, human_namespace))
        kml.append(doc)

        return ET.ElementTree(kml)
