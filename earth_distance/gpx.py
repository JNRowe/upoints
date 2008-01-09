#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""gpx - Imports GPS eXchange format data files"""
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

from earth_distance import (point, utils)

GPX_NS = "http://www.topografix.com/GPX/1/1"

def create_elem(tag, attr={}, human_namespace=False):
    """
    Create a partial C{ET.Element} wrapper with namespace defined

    @type tag: C{str}
    @param tag: Tag name
    @type attr: C{dict}
    @param attr: Default attributes for tag
    @type human_namespace: C{bool}
    @param human_namespace: Whether to generate output using human readable
        namespace prefixes
    @rtype: C{function}
    @return: C{ET.Element} wrapper with predefined namespace
    """
    if human_namespace:
        ElementTree._namespace_map[GPX_NS] = "gpx"
        return ElementTree.Element("{%s}%s" % (GPX_NS, tag), attr)
    else:
        return ET.Element("{%s}%s" % (GPX_NS, tag), attr)

class Waypoint(point.Point):
    """
    Class for representing a Waypoint element from GPX data files

    @ivar latitude: Waypoint's latitude
    @ivar longitude: Waypoint's longitude
    @ivar name: Waypoint's name
    @ivar description: Waypoint's description
    """

    __slots__ = ('name', 'description', )

    def __init__(self, latitude, longitude, name=None, description=None):
        """
        Initialise a new C{Waypoint} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Waypoints's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Waypoint's longitude
        @type name: C{string}
        @param name: Name for Waypoint
        @type description: C{string}
        @param description: Waypoint's description
        """
        super(Waypoint, self).__init__(latitude, longitude)

        self.name = name
        self.description = description

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Waypoint(52, 0)
        Waypoint(52.0, 0.0, None, None)
        >>> Waypoint(52, 0, None)
        Waypoint(52.0, 0.0, None, None)
        >>> Waypoint(52, 0, "name", "desc")
        Waypoint(52.0, 0.0, 'name', 'desc')

        @rtype: C{str}
        @return: String to recreate C{Waypoint} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.name,
                                 self.description)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Waypoint(52, 0))
        52°00'00"N, 000°00'00"E
        >>> print(Waypoint(52, 0, "name", "desc"))
        name (52°00'00"N, 000°00'00"E) [desc]

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Waypoint} object
        """
        text = super(Waypoint, self).__str__(mode)
        if self.name:
            text = "%s (%s)" % (self.name, text)
        if self.description:
            text += " [%s]" % self.description
        return text

    def togpx(self, human_namespace=False):
        """
        Generate a GPX Waypoint element subtree

        >>> ET.tostring(Waypoint(52, 0).togpx())
        '<ns0:wpt lat="52.0" lon="0.0" xmlns:ns0="http://www.topografix.com/GPX/1/1" />'
        >>> ET.tostring(Waypoint(52, 0, "Cambridge").togpx())
        '<ns0:wpt lat="52.0" lon="0.0" xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:name>Cambridge</ns0:name></ns0:wpt>'
        >>> ET.tostring(Waypoint(52, 0, "Cambridge", "in the UK").togpx())
        '<ns0:wpt lat="52.0" lon="0.0" xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:name>Cambridge</ns0:name><ns0:desc>in the UK</ns0:desc></ns0:wpt>'

        @type human_namespace: C{bool}
        @param human_namespace: Whether to generate output using human readable
            namespace prefixes
        @rtype: C{ET.Element}
        @return: GPX Waypoint element
        """
        Waypoint = create_elem("wpt", {"lat": str(self.latitude),
                                          "lon": str(self.longitude)})
        if self.name:
            nametag = create_elem("name")
            nametag.text = self.name
            Waypoint.append(nametag)
        if self.description:
            desctag = create_elem("desc")
            desctag.text = self.description
            Waypoint.append(desctag)
        return Waypoint

class Waypoints(list):
    """
    Class for representing a group of C{Track}, C{Waypoint} and C{Route} objects
    """

    def __init__(self, gpx_file=None):
        """
        Initialise a new C{Gpx} object
        """
        list.__init__(self)
        if gpx_file:
            self.import_gpx_file(gpx_file)

    def import_gpx_file(self, gpx_file):
        """
        Import GPX data files

        C{import_GPX_file()} returns a list with C{Waypoint}s.

        It expects data files in GPX format, as specified in U{GPX 1.1 Schema
        Documentation <http://www.topografix.com/GPX/1/1/>}, which is XML such
        as::

            <?xml version="1.0" encoding="utf-8" standalone="no"?>
            <gpx version="1.1" creator="PocketGPSWorld.com"
            xmlns="http://www.topografix.com/GPX/1/1"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">

              <wpt lat="52.015" lon="-0.221">
                <name>Home</name>
                <desc>My place</desc>
              </wpt>
              <wpt lat="52.167" lon="0.390">
                <name>MSR</name>
                <desc>Microsoft Research, Cambridge</desc>
              </wpt>
            </gpx>

        The reader uses U{Python <http://www.python.org/>}'s C{ElementTree}
        module, so should be very fast when importing data.  The above file
        processed by C{import_gpx_file()} will return the following C{dict}
        object::

            [Waypoint(52.015, -0.221, "Home", "My place"),
             Waypoint(52.167, 0.390, "MSR", "Microsoft Research, Cambridge")]

        >>> waypoints = Waypoints(open("gpx"))
        >>> for value in sorted(waypoints,
        ...                     lambda x,y: cmp(x.name.lower(),
        ...                                     y.name.lower())):
        ...     print(value)
        Home (52°00'54"N, 000°13'15"W) [My place]
        MSR (52°10'01"N, 000°23'24"E) [Microsoft Research, Cambridge]

        @type gpx_file: C{file}, C{list} or C{str}
        @param gpx_file: GPX data to read
        @rtype: C{list}
        @return: Locations with optional comments
        """
        if hasattr(gpx_file, "readlines"):
            data = ET.parse(gpx_file)
        elif isinstance(gpx_file, list):
            data = ET.fromstring("".join(gpx_file))
        elif isinstance(gpx_file, basestring):
            data = ET.parse(open(gpx_file))
        else:
            raise TypeError("Unable to handle data of type `%s`"
                            % type(gpx_file))

        gpx_elem = lambda name: ET.QName(GPX_NS, name).text
        waypoint_elem = "//" + gpx_elem("wpt")
        name_elem = gpx_elem("name")
        desc_elem = gpx_elem("desc")

        for waypoint in data.findall(waypoint_elem):
            latitude = waypoint.get("lat")
            longitude = waypoint.get("lon")
            name = waypoint.findtext(name_elem)
            description = waypoint.findtext(desc_elem)
            self.append(Waypoint(latitude, longitude, name, description))

    def export_gpx_file(self, human_namespace=False):
        """
        Generate GPX element tree from C{Waypoints}

        >>> from sys import stdout
        >>> locations = Waypoints(open("gpx"))
        >>> xml = locations.export_gpx_file()
        >>> xml.write(stdout)
        <ns0:gpx xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:wpt lat="52.015" lon="-0.221"><ns0:name>Home</ns0:name><ns0:desc>My place</ns0:desc></ns0:wpt><ns0:wpt lat="52.167" lon="0.39"><ns0:name>MSR</ns0:name><ns0:desc>Microsoft Research, Cambridge</ns0:desc></ns0:wpt></ns0:gpx>
        
        @type human_namespace: C{bool}
        @param human_namespace: Whether to generate output using human readable
            namespace prefixes
        @rtype: C{ET.ElementTree}
        @return: GPX element tree depicting C{Waypoint}s
        """
        gpx = create_elem('gpx')
        for place in self:
            gpx.append(place.togpx(human_namespace))

        return ET.ElementTree(gpx)
