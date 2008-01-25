#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""osm - Imports OpenStreetMap data files"""
# Copyright (C) 2007-2008  James Rowe
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

import datetime
import logging

from xml.etree import ElementTree

try:
    from xml.etree import cElementTree as ET
except ImportError:
    ET = ElementTree
    logging.info("cElementTree is unavailable XML processing will be much"
                 "slower with ElementTree")

from earth_distance import (__version__, point, utils)

class TzOffset(datetime.tzinfo):
    """
    Time offset from UTC

    @ivar __offset: Number of minutes offset from UTC
    """

    def __init__(self, tzstring):
        """
        Initialise a new C{TzOffset} object

        >>> TzOffset("z").utcoffset()
        datetime.timedelta(0)
        >>> TzOffset("+0530").utcoffset()
        datetime.timedelta(0, 19800)
        >>> TzOffset("-0800").utcoffset()
        datetime.timedelta(-1, 57600)

        @type tzstring: C{str}
        @param tzstring: ISO 8601 style timezone definition
        """
        if tzstring in "zZ":
            hours = 0
            minutes = 0
        else:
            hours = int(tzstring[1:3], 10)
            minutes = int(tzstring[3:], 10)
            if tzstring[0] == "-":
                hours = -1 * hours
                minutes = -1 * minutes
            elif not tzstring[0] == "+":
                raise ValueError("Unable to parse timezone `%s'" % tzstring)

        self.__offset = datetime.timedelta(hours=hours, minutes=minutes)

    def utcoffset(self):
        """
        Return the offset in minutes from UTC
        """
        return self.__offset

class Node(point.Point):
    """
    Class for representing a node element from OSM data files

    @since: 0.9.0

    @ivar ident: Node's unique indentifier
    @ivar latitude: Node's latitude
    @ivar longitude: Node's longitude
    @ivar visible: Whether the node is visible
    @ivar user: User who logged the node
    @ivar timestamp: The date and time a node was logged
    @ivar tags: Tags associated with the node
    """

    __slots__ = ('ident', 'visible', 'user', 'timestamp', 'tags')

    def __init__(self, ident, latitude, longitude, visible=False, user=None,
                 timestamp=None, tags=None):
        """
        Initialise a new C{Node} object

        @type ident: C{int}
        @param ident: Unique identifier for the node
        @type latitude: C{float} or coercible to C{float}
        @param latitude: Nodes's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Node's longitude
        @type visible: C{bool}
        @param visible: Whether the node is visible
        @type user: C{str}
        @param user: User who logged the node
        @type timestamp: C{str}
        @param timestamp: The date and time a node was logged
        @type tags: C{dict}
        @param tags: Tags associated with the node
        """
        super(Node, self).__init__(latitude, longitude)

        self.ident = ident
        self.visible = visible
        self.user = user
        self.timestamp = timestamp
        self.tags = tags

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Node(0, 52, 0)
        Node(0, 52.0, 0.0, False, None, None, None)
        >>> Node(0, 52, 0, True, "jnrowe", datetime.datetime(2008, 1, 25))
        Node(0, 52.0, 0.0, True, 'jnrowe', datetime.datetime(2008, 1, 25, 0, 0), None)
        >>> Node(0, 52, 0, tags={"key": "value"})
        Node(0, 52.0, 0.0, False, None, None, {'key': 'value'})

        @rtype: C{str}
        @return: String to recreate C{Node} object
        """
        data = utils.repr_assist(self.ident, self.latitude, self.longitude,
                                 self.visible, self.user, self.timestamp,
                                 self.tags)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode="dms"):
        """
        Pretty printed location string

        >>> print(Node(0, 52, 0))
        Node 0 (52°00'00"N, 000°00'00"E)
        >>> print(Node(0, 52, 0, True, "jnrowe", datetime.datetime(2008, 1, 25)))
        Node 0 (52°00'00"N, 000°00'00"E) [visible, user: jnrowe, timestamp:
        2008-01-25T00:00:00]
        >>> print(Node(0, 52, 0, tags={"key": "value"}))
        Node 0 (52°00'00"N, 000°00'00"E) [key: value]

        @type mode: C{str}
        @param mode: Coordinate formatting system to use
        @rtype: C{str}
        @return: Human readable string representation of C{Node} object
        """
        text = "Node %i (%s)" % (self.ident, super(Node, self).__str__(mode))
        flags = []
        if self.visible:
            flags.append("visible")
        if self.user:
            flags.append("user: %s" % self.user)
        if self.timestamp:
            flags.append("timestamp: %s" % self.timestamp.isoformat())
        if self.tags:
            flags.append(", ".join(["%s: %s" % (k, v) for k, v in self.tags.items()]))
        if flags:
            text += " [%s]" % ", ".join(flags)
        return text

    def toosm(self):
        """
        Generate a OSM node element subtree

        >>> ET.tostring(Node(0, 52, 0).toosm())
         '<node id="0" lat="52.0" lon="0.0" visible="false" />'
        >>> ET.tostring(Node(0, 52, 0, True, "jnrowe", datetime.datetime(2008, 1, 25)).toosm())
        '<node id="0" lat="52.0" lon="0.0" timestamp="2008-01-25T00:00:00+0000" user="jnrowe" visible="true" />'
        >>> ET.tostring(Node(0, 52, 0, tags={"key": "value"}).toosm())
        '<node id="0" lat="52.0" lon="0.0" visible="false"><tag k="key" v="value" /></node>'

        @rtype: C{ET.Element}
        @return: OSM node element
        """
        node = ET.Element("node", {"id": str(self.ident),
                                   "lat": str(self.latitude),
                                   "lon": str(self.longitude)})
        node.set("visible", "true" if self.visible else "false")
        if self.user:
            node.set("user", self.user)
        if self.timestamp:
            node.set("timestamp", "%s+0000" % self.timestamp.isoformat())
        if self.tags:
            for key, value in self.tags.items():
                tag = ET.Element("tag", {"k": key, "v": value})
                node.append(tag)

        return node

    @staticmethod
    def parse_elem(element):
        """
        Parse a OSM node XML element

        @type element: C{ET.Element}
        @param element: XML Element to parse
        @rtype: C{Node}
        @return: C{Node} object representing parsed element
        """
        ident = int(element.get("id"), 0)
        latitude = element.get("lat")
        longitude = element.get("lon")
        visible = True if element.get("visible") else False
        user = element.get("user")
        timestamp = element.get("timestamp")
        if timestamp:
            zone = TzOffset(timestamp[-5:])
            timestamp = datetime.datetime.strptime(timestamp[:-5],
                                                   "%Y-%m-%dT%H:%M:%S") \
                - zone.utcoffset()
        tags = {}
        for tag in element.findall("tag"):
            key = tag.get("k")
            value = tag.get("v")
            tags[key] = value
        return Node(ident, latitude, longitude, visible, user, timestamp, tags)

class Way(list):
    """
    Class for representing a way element from OSM data files

    @since: 0.9.0

    @ivar ident: Way's unique indentifier
    @ivar visible: Whether the way is visible
    @ivar user: User who logged the way
    @ivar timestamp: The date and time a way was logged
    @ivar tags: Tags associated with the way
    """

    __slots__ = ('ident', 'visible', 'user', 'timestamp', 'tags')

    def __init__(self, ident, nodes, visible=False, user=None, timestamp=None,
                 tags=None):
        """
        Initialise a new C{Way} object

        @type ident: C{int}
        @param ident: Unique identifier for the way
        @type nodes: C{list} of C{str}s
        @param nodes: Identifiers of the nodes that form this way
        @type visible: C{bool}
        @param visible: Whether the way is visible
        @type user: C{str}
        @param user: User who logged the way
        @type timestamp: C{str}
        @param timestamp: The date and time a way was logged
        @type tags: C{dict}
        @param tags: Tags associated with the way
        """
        super(Way, self).__init__()

        for node in nodes:
            self.append(node)

        self.ident = ident
        self.visible = visible
        self.user = user
        self.timestamp = timestamp
        self.tags = tags

    def __repr__(self):
        """
        Self-documenting string representation

        >>> Way(0, (0, 1, 2))
        Way(0, [0, 1, 2], False, None, None, None)
        >>> Way(0, (0, 1, 2), True, "jnrowe", datetime.datetime(2008, 1, 25))
        Way(0, [0, 1, 2], True, 'jnrowe', datetime.datetime(2008, 1, 25, 0, 0), None)
        >>> Way(0, (0, 1, 2), tags={"key": "value"})
        Way(0, [0, 1, 2], False, None, None, {'key': 'value'})

        @rtype: C{str}
        @return: String to recreate C{Way} object
        """
        data = utils.repr_assist(self.ident, self[:], self.visible, self.user,
                                 self.timestamp, self.tags)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, nodes=False):
        """
        Pretty printed location string

        >>> print(Way(0, (0, 1, 2)))
        Way 0 (nodes: 0, 1, 2)
        >>> print(Way(0, (0, 1, 2), True, "jnrowe", datetime.datetime(2008, 1, 25)))
        Way 0 (nodes: 0, 1, 2) [visible, user: jnrowe, timestamp: 2008-01-25T00:00:00]
        >>> print(Way(0, (0, 1, 2), tags={"key": "value"}))
        Way 0 (nodes: 0, 1, 2) [key: value]
        >>> nodes = [
        ...     Node(0, 52.015749, -0.221765, True, "jnrowe",
        ...          datetime.datetime(2008, 1, 25, 12, 52, 11), None),
        ...     Node(1, 52.015761, -0.221767, True,
        ...          datetime.datetime(2008, 1, 25, 12, 53), None,
        ...          {"created_by": "hand", "highway": "crossing"}),
        ...     Node(2, 52.015754, -0.221766, True, "jnrowe",
        ...          datetime.datetime(2008, 1, 25, 12, 52, 30),
        ...          {"amenity": "pub"}),
        ... ]
        >>> print(Way(0, (0, 1, 2), tags={"key": "value"}).__str__(nodes))
        Way 0 [key: value]
            Node 0 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:11]
            Node 1 (52°00'56"N, 000°13'18"W) [visible, user: 2008-01-25 12:53:00, highway: crossing, created_by: hand]
            Node 2 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:30, amenity: pub]

        @type nodes: C{list}
        @param nodes: Nodes to be used in expanding references
        @rtype: C{str}
        @return: Human readable string representation of C{Way} object
        """
        text = "Way %i" % (self.ident)
        if not nodes:
            text += " (nodes: %s)" % str(self[:])[1:-1]
        flags = []
        if self.visible:
            flags.append("visible")
        if self.user:
            flags.append("user: %s" % self.user)
        if self.timestamp:
            flags.append("timestamp: %s" % self.timestamp.isoformat())
        if self.tags:
            flags.append(", ".join(["%s: %s" % (k, v) for k, v in self.tags.items()]))
        if flags:
            text += " [%s]" % ", ".join(flags)
        if nodes:
            text += "\n" + "\n".join(["    %s" % nodes[node] for node in self[:]])

        return text

    def toosm(self):
        """
        Generate a OSM way element subtree

        >>> ET.tostring(Way(0, (0, 1, 2)).toosm())
        '<way id="0" visible="false"><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'
        >>> ET.tostring(Way(0, (0, 1, 2), True, "jnrowe", datetime.datetime(2008, 1, 25)).toosm())
        '<way id="0" timestamp="2008-01-25T00:00:00+0000" user="jnrowe" visible="true"><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'
        >>> ET.tostring(Way(0, (0, 1, 2), tags={"key": "value"}).toosm())
        '<way id="0" visible="false"><tag k="key" v="value" /><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'

        @rtype: C{ET.Element}
        @return: OSM way element
        """
        way = ET.Element("way", {"id": str(self.ident)})
        way.set("visible", "true" if self.visible else "false")
        if self.user:
            way.set("user", self.user)
        if self.timestamp:
            way.set("timestamp", "%s+0000" % self.timestamp.isoformat())
        if self.tags:
            for key, value in self.tags.items():
                tag = ET.Element("tag", {"k": key, "v": value})
                way.append(tag)

        for node in self:
            tag = ET.Element("nd", {"ref": str(node)})
            way.append(tag)

        return way

    @staticmethod
    def parse_elem(element):
        """
        Parse a OSM way XML element

        @type element: C{ET.Element}
        @param element: XML Element to parse
        @rtype: C{Node}
        @return: C{Way} object representing parsed element
        """
        ident = int(element.get("id"), 0)
        visible = True if element.get("visible") else False
        user = element.get("user")
        timestamp = element.get("timestamp")
        if timestamp:
            zone = TzOffset(timestamp[-5:])
            timestamp = datetime.datetime.strptime(timestamp[:-5],
                                                   "%Y-%m-%dT%H:%M:%S") \
                - zone.utcoffset()
        tags = {}
        for tag in element.findall("tag"):
            key = tag.get("k")
            value = tag.get("v")
            tags[key] = value
        nodes = [node.get("ref") for node in element.findall("nd")]
        return Way(ident, nodes, visible, user, timestamp, tags)

class Osm(list):
    """
    Class for representing an OSM region

    @since: 0.9.0
    """

    def __init__(self, osm_file=None):
        """
        Initialise a new C{Osm} object
        """
        super(Osm, self).__init__()
        if osm_file:
            self.import_osm_file(osm_file)

    def __repr__(self):
        """
        Self-documenting string representation

        @rtype: C{str}
        @return: String to recreate C{Osm} object
        """
        data = utils.repr_assist(self, self.generator)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def import_osm_file(self, osm_file):
        """
        Import OSM data files

        C{import_osm_file()} returns a list of C{Node} and C{Way} objects.

        It expects data files conforming to the U{OpenStreetMap 0.5 DTD
        <http://wiki.openstreetmap.org/index.php/OSM_Protocol_Version_0.5/DTD>},
        which is XML such as::

            <?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.5" generator="earth_distance/0.9.0">
              <node id="0" lat="52.015749" lon="-0.221765" user="jnrowe" visible="true" timestamp="2008-01-25T12:52:11+0000" />
              <node id="1" lat="52.015761" lon="-0.221767" visible="true" timestamp="2008-01-25T12:53:00+0000">
                <tag k="created_by" v="hand" />
                <tag k="highway" v="crossing" />
              </node>
              <node id="2" lat="52.015754" lon="-0.221766" user="jnrowe" visible="true" timestamp="2008-01-25T12:52:30+0000">
                <tag k="amenity" v="pub" />
              </node>
              <way id="0" visible="true" timestamp="2008-01-25T13:00:00+0000">
                <nd ref="0" />
                <nd ref="1" />
                <nd ref="2" />
                <tag k="ref" v="My Way" />
                <tag k="highway" v="primary" />
              </way>
            </osm>

        The reader uses U{Python <http://www.python.org/>}'s C{ElementTree}
        module, so should be very fast when importing data.  The above file
        processed by C{import_osm_file()} will return the following C{Osm}
        object::

            Osm([
                Node(0, 52.015749, -0.221765, True, "jnrowe",
                     datetime.datetime(2008, 1, 25, 12, 52, 11), None),
                Node(1, 52.015761, -0.221767, True,
                     datetime.datetime(2008, 1, 25, 12, 53), None,
                     {"created_by": "hand", "highway": "crossing"}),
                Node(2, 52.015754, -0.221766, True, "jnrowe",
                     datetime.datetime(2008, 1, 25, 12, 52, 30),
                     {"amenity": "pub"}),
                Way(0, [0, 1, 2], True, None,
                    datetime.datetime(2008, 1, 25, 13, 00)
                    {"ref": "My Way", "highway": "primary"})],
                generator="earth_distance/0.9.0")

        >>> region = Osm(open("osm"))
        >>> for node in sorted(filter(lambda x: isinstance(x, Node), region),
        ...                    lambda x, y: cmp(x.ident, y.ident)):
        ...     print(node)
        Node 0 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:11]
        Node 1 (52°00'56"N, 000°13'18"W) [visible, timestamp: 2008-01-25T12:53:00, highway: crossing, created_by: hand]
        Node 2 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:30, amenity: pub]

        @type osm_file: C{file}, C{list} or C{str}
        @param osm_file: OpenStreetMap data to read
        @rtype: C{Osm}
        @return: Nodes and ways from the data
        """
        if hasattr(osm_file, "readlines"):
            data = ET.parse(osm_file)
        elif isinstance(osm_file, list):
            data = ET.fromstring("".join(osm_file))
        elif isinstance(osm_file, basestring):
            data = ET.parse(open(osm_file))
        else:
            raise TypeError("Unable to handle data of type `%s`"
                            % type(osm_file))

        # This would be a lot simpler if OSM exports delivered namespace
        # properties
        root = data.getroot()
        if not root.tag == "osm":
            raise ValueError("Root element `%s' is not `osm'" % root.tag)
        version = root.get("version")
        if not version:
            raise ValueError("No specified OSM version")
        elif not version == "0.5":
            raise ValueError("Unsupported OSM version `%s'" % root)

        self.generator = root.get("generator")

        for elem in root.getchildren():
            if elem.tag == "node":
                self.append(Node.parse_elem(elem))
            elif elem.tag == "way":
                self.append(Way.parse_elem(elem))

    def export_osm_file(self):
        """
        Generate OpenStreetMap element tree from C{Osm}

        >>> from sys import stdout
        >>> region = Osm(open("osm"))
        >>> xml = region.export_osm_file()
        >>> xml.write(stdout)
        <osm generator="earth_distance/0.8.0" version="0.5"><node id="0" lat="52.015749" lon="-0.221765" timestamp="2008-01-25T12:52:11+0000" user="jnrowe" visible="true" /><node id="1" lat="52.015761" lon="-0.221767" timestamp="2008-01-25T12:53:00+0000" visible="true"><tag k="highway" v="crossing" /><tag k="created_by" v="hand" /></node><node id="2" lat="52.015754" lon="-0.221766" timestamp="2008-01-25T12:52:30+0000" user="jnrowe" visible="true"><tag k="amenity" v="pub" /></node><way id="0" timestamp="2008-01-25T13:00:00+0000" visible="true"><tag k="ref" v="My Way" /><tag k="highway" v="primary" /><nd ref="0" /><nd ref="1" /><nd ref="2" /></way></osm>
        """
        osm = ET.Element('osm', {"generator": "earth_distance/%s" % __version__,
                                 "version": "0.5"})
        for obj in self:
            osm.append(obj.toosm())

        return ET.ElementTree(osm)

