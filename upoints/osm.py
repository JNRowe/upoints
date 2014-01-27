#
# coding=utf-8
"""osm - Imports OpenStreetMap data files"""
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

import urllib

from operator import attrgetter

from lxml import etree

from upoints import (point, utils)
from upoints._version import web as ua_string
from upoints.compat import mangle_repr_type

create_elem = utils.element_creator()


def _parse_flags(element):
    """Parse OSM XML element for generic data.

    :param etree.Element element: Element to parse
    :rtype: ``tuple``
    :return: Generic OSM data for object instantiation

    """
    visible = True if element.get('visible') else False
    user = element.get('user')
    timestamp = element.get('timestamp')
    if timestamp:
        timestamp = utils.Timestamp.parse_isoformat(timestamp)
    tags = {}
    try:
        for tag in element['tag']:
            key = tag.get('k')
            value = tag.get('v')
            tags[key] = value
    except AttributeError:
        pass

    return visible, user, timestamp, tags


def _get_flags(osm_obj):
    """Create element independent flags output.

    :param Node osm_obj: Object with OSM-style metadata
    :rtype: ``list``
    :return: Human readable flags output

    """
    flags = []
    if osm_obj.visible:
        flags.append('visible')
    if osm_obj.user:
        flags.append('user: %s' % osm_obj.user)
    if osm_obj.timestamp:
        flags.append('timestamp: %s' % osm_obj.timestamp.isoformat())
    if osm_obj.tags:
        flags.append(', '.join('%s: %s' % (k, v)
                               for k, v in sorted(osm_obj.tags.items())))
    return flags


def get_area_url(location, distance):
    """Generate URL for downloading OSM data within a region.

    This function defines a boundary box where the edges touch a circle of
    ``distance`` kilometres in radius.  It is important to note that the box is
    neither a square, nor bounded within the circle.

    The bounding box is strictly a trapezoid whose north and south edges are
    different lengths, which is longer is dependant on whether the box is
    calculated for a location in the Northern or Southern hemisphere.  You will
    get a shorter north edge in the Northern hemisphere, and vice versa.  This
    is simply because we are applying a flat transformation to a spherical
    object, however for all general cases the difference will be negligible.

    :param Point location: Centre of the region
    :param int distance: Boundary distance in kilometres
    :rtype: ``str``
    :return: URL that can be used to fetch the OSM data within ``distance`` of
        ``location``

    """
    locations = [location.destination(i, distance) for i in range(0, 360, 90)]
    latitudes = list(map(attrgetter('latitude'), locations))
    longitudes = list(map(attrgetter('longitude'), locations))

    bounds = (min(longitudes), min(latitudes), max(longitudes), max(latitudes))

    return ('http://api.openstreetmap.org/api/0.5/map?bbox='
            + ','.join(map(str, bounds)))


class Node(point.Point):

    """Class for representing a node element from OSM data files.

    .. versionadded:: 0.9.0

    """

    __slots__ = ('ident', 'visible', 'user', 'timestamp', 'tags')

    def __init__(self, ident, latitude, longitude, visible=False, user=None,
                 timestamp=None, tags=None):
        """Initialise a new ``Node`` object.

        :param int ident: Unique identifier for the node
        :param float latitude: Nodes's latitude
        :param float longitude: Node's longitude
        :param bool visible: Whether the node is visible
        :param str user: User who logged the node
        :param str timestamp: The date and time a node was logged
        :param dict tags: Tags associated with the node

        """
        super(Node, self).__init__(latitude, longitude)

        self.ident = ident
        self.visible = visible
        self.user = user
        self.timestamp = timestamp
        self.tags = tags

    def __str__(self):
        """Pretty printed location string.

        :rtype: ``str``
        :return: Human readable string representation of ``Node`` object

        """
        text = ['Node %i (%s)' % (self.ident,
                                  super(Node, self).__format__('dms')), ]
        flags = _get_flags(self)

        if flags:
            text.append('[%s]' % ', '.join(flags))
        return ' '.join(text)

    def toosm(self):
        """Generate a OSM node element subtree.

        :rtype: :class:`etree.Element`
        :return: OSM node element

        """
        node = create_elem('node', {'id': str(self.ident),
                                    'lat': str(self.latitude),
                                    'lon': str(self.longitude)})
        node.set('visible', 'true' if self.visible else 'false')
        if self.user:
            node.set('user', self.user)
        if self.timestamp:
            node.set('timestamp', self.timestamp.isoformat())
        if self.tags:
            for key, value in sorted(self.tags.items()):
                node.append(create_elem('tag', {'k': key, 'v': value}))

        return node

    def get_area_url(self, distance):
        """Generate URL for downloading OSM data within a region.

        :param int distance: Boundary distance in kilometres
        :rtype: ``str``
        :return: URL that can be used to fetch the OSM data within ``distance``
            of ``location``

        """
        return get_area_url(self, distance)

    def fetch_area_osm(self, distance):
        """Fetch, and import, an OSM region.

        :param int distance: Boundary distance in kilometres
        :rtype: :class:`Osm`
        :return: All the data OSM has on a region imported for use

        """
        return Osm(urllib.urlopen(get_area_url(self, distance)))

    @staticmethod
    def parse_elem(element):
        """Parse a OSM node XML element.

        :param etree.Element element: XML Element to parse
        :rtype: ``Node``
        :return: ``Node`` object representing parsed element

        """
        ident = int(element.get('id'))
        latitude = element.get('lat')
        longitude = element.get('lon')

        flags = _parse_flags(element)

        return Node(ident, latitude, longitude, *flags)


@mangle_repr_type
class Way(point.Points):

    """Class for representing a way element from OSM data files.

    .. versionadded:: 0.9.0

    """

    __slots__ = ('ident', 'visible', 'user', 'timestamp', 'tags')

    def __init__(self, ident, nodes, visible=False, user=None, timestamp=None,
                 tags=None):
        """Initialise a new ``Way`` object.

        :param int ident: Unique identifier for the way
        :type nodes: ``list`` of ``str`` objects
        :param nodes: Identifiers of the nodes that form this way
        :param bool visible: Whether the way is visible
        :param str user: User who logged the way
        :param str timestamp: The date and time a way was logged
        :param dict tags: Tags associated with the way

        """
        super(Way, self).__init__()

        self.extend(nodes)

        self.ident = ident
        self.visible = visible
        self.user = user
        self.timestamp = timestamp
        self.tags = tags

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: ``str``
        :return: String to recreate ``Way`` object

        """
        return utils.repr_assist(self, {'nodes': self[:]})

    def __str__(self, nodes=False):
        """Pretty printed location string.

        :param list nodes: Nodes to be used in expanding references
        :rtype: ``str``
        :return: Human readable string representation of ``Way`` object

        """
        text = ['Way %i' % (self.ident), ]
        if not nodes:
            text.append(' (nodes: %s)' % str(self[:])[1:-1])
        flags = _get_flags(self)

        if flags:
            text.append(' [%s]' % ', '.join(flags))
        if nodes:
            text.append('\n')
            text.append('\n'.join('    %s' % nodes[node] for node in self[:]))

        return ''.join(text)

    def toosm(self):
        """Generate a OSM way element subtree.

        :rtype: :class:`etree.Element`
        :return: OSM way element

        """
        way = create_elem('way', {'id': str(self.ident)})
        way.set('visible', 'true' if self.visible else 'false')
        if self.user:
            way.set('user', self.user)
        if self.timestamp:
            way.set('timestamp', self.timestamp.isoformat())
        if self.tags:
            for key, value in sorted(self.tags.items()):
                way.append(create_elem('tag', {'k': key, 'v': value}))

        for node in self:
            way.append(create_elem('nd', {'ref': str(node)}))

        return way

    @staticmethod
    def parse_elem(element):
        """Parse a OSM way XML element.

        :param etree.Element element: XML Element to parse
        :rtype: ``Way``
        :return: `Way` object representing parsed element

        """
        ident = int(element.get('id'))
        flags = _parse_flags(element)
        nodes = [node.get('ref') for node in element.findall('nd')]
        return Way(ident, nodes, *flags)


class Osm(point.Points):

    """Class for representing an OSM region.

    .. versionadded:: 0.9.0

    """

    def __init__(self, osm_file=None):
        """Initialise a new ``Osm`` object."""
        super(Osm, self).__init__()
        self._osm_file = osm_file
        if osm_file:
            self.import_locations(osm_file)
        self.generator = ua_string
        self.version = '0.5'

    def import_locations(self, osm_file):
        """Import OSM data files.

        ``import_locations()`` returns a list of ``Node`` and ``Way`` objects.

        It expects data files conforming to the `OpenStreetMap 0.5 DTD`_, which
        is XML such as::

            <?xml version="1.0" encoding="UTF-8"?>
            <osm version="0.5" generator="upoints/0.9.0">
              <node id="0" lat="52.015749" lon="-0.221765" user="jnrowe" visible="true" timestamp="2008-01-25T12:52:11+00:00" />
              <node id="1" lat="52.015761" lon="-0.221767" visible="true" timestamp="2008-01-25T12:53:00+00:00">
                <tag k="created_by" v="hand" />
                <tag k="highway" v="crossing" />
              </node>
              <node id="2" lat="52.015754" lon="-0.221766" user="jnrowe" visible="true" timestamp="2008-01-25T12:52:30+00:00">
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

        The reader uses the :mod:`ElementTree` module, so should be very fast
        when importing data.  The above file processed by
        ``import_locations()`` will return the following `Osm` object::

            Osm([
                Node(0, 52.015749, -0.221765, True, "jnrowe",
                     utils.Timestamp(2008, 1, 25, 12, 52, 11), None),
                Node(1, 52.015761, -0.221767, True,
                     utils.Timestamp(2008, 1, 25, 12, 53), None,
                     {"created_by": "hand", "highway": "crossing"}),
                Node(2, 52.015754, -0.221766, True, "jnrowe",
                     utils.Timestamp(2008, 1, 25, 12, 52, 30),
                     {"amenity": "pub"}),
                Way(0, [0, 1, 2], True, None,
                    utils.Timestamp(2008, 1, 25, 13, 00),
                    {"ref": "My Way", "highway": "primary"})],
                generator="upoints/0.9.0")

        :type osm_file: ``file``, ``list`` or ``str``
        :param osm_file: OpenStreetMap data to read
        :rtype: ``Osm``
        :return: Nodes and ways from the data

        .. _OpenStreetMap 0.5 DTD:
            http://wiki.openstreetmap.org/wiki/OSM_Protocol_Version_0.5/DTD

        """
        self._osm_file = osm_file
        data = utils.prepare_xml_read(osm_file, objectify=True)

        # This would be a lot simpler if OSM exports defined a namespace
        if not data.tag == 'osm':
            raise ValueError("Root element %r is not `osm'" % data.tag)
        self.version = data.get('version')
        if not self.version:
            raise ValueError('No specified OSM version')
        elif not self.version == '0.5':
            raise ValueError('Unsupported OSM version %r' % data)

        self.generator = data.get('generator')

        for elem in data.getchildren():
            if elem.tag == 'node':
                self.append(Node.parse_elem(elem))
            elif elem.tag == 'way':
                self.append(Way.parse_elem(elem))

    def export_osm_file(self):
        """Generate OpenStreetMap element tree from `Osm`"""
        osm = create_elem('osm', {'generator': self.generator,
                                  'version': self.version})
        osm.extend(obj.toosm() for obj in self)

        return etree.ElementTree(osm)
