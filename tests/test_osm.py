#
# coding=utf-8
"""test_osm - Test osm support"""
# Copyright (C) 2006-2011  James Rowe <jnrowe@gmail.com>
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

from upoints import utils
from upoints.osm import (ET, Node, Osm, Way, get_area_url)


def test_get_area_url():
    """
    >>> from upoints import point
    >>> get_area_url(point.Point(52.015, -0.221), 3)
    'http://api.openstreetmap.org/api/0.5/map?bbox=-0.264864438253,51.9880034021,-0.177135561747,52.0419965979'
    >>> get_area_url(point.Point(52.015, -0.221), 12)
    'http://api.openstreetmap.org/api/0.5/map?bbox=-0.396457433591,51.9070136086,-0.045542566409,52.1229863914'

    """


class TestNode():
    def test___init__(self):
        """
        >>> Node(0, 52, 0)
        Node(0, 52.0, 0.0, False, None, None, None)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Node(0, 52, 0, True, "jnrowe", utils.Timestamp(2008, 1, 25))
        Node(0, 52.0, 0.0, True, 'jnrowe',
             Timestamp(2008, 1, 25, 0, 0), None)
        >>> Node(0, 52, 0, tags={"key": "value"})
        Node(0, 52.0, 0.0, False, None, None, {'key': 'value'})

        """

    def test___str__(self):
        """
        >>> print(Node(0, 52, 0))
        Node 0 (52°00'00"N, 000°00'00"E)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> print(Node(0, 52, 0, True, "jnrowe",
        ...            utils.Timestamp(2008, 1, 25)))
        Node 0 (52°00'00"N, 000°00'00"E) [visible, user: jnrowe, timestamp:
        2008-01-25T00:00:00+00:00]
        >>> print(Node(0, 52, 0, tags={"key": "value"}))
        Node 0 (52°00'00"N, 000°00'00"E) [key: value]

        """

    def test_toosm(self):
        """
        >>> ET.tostring(Node(0, 52, 0).toosm())
        '<node id="0" lat="52.0" lon="0.0" visible="false" />'
        >>> ET.tostring(Node(0, 52, 0, True, "jnrowe",
        ...                  utils.Timestamp(2008, 1, 25)).toosm())
        '<node id="0" lat="52.0" lon="0.0" timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" visible="true" />'
        >>> ET.tostring(Node(0, 52, 0, tags={"key": "value"}).toosm())
        '<node id="0" lat="52.0" lon="0.0" visible="false"><tag k="key" v="value" /></node>'

        """

    def test_get_area_url(self):
        """
        >>> Home = Node(0, 52, 0)
        >>> Home.get_area_url(3)
        'http://api.openstreetmap.org/api/0.5/map?bbox=-0.0438497383115,51.9730034021,0.0438497383115,52.0269965979'
        >>> Home.get_area_url(12)
        'http://api.openstreetmap.org/api/0.5/map?bbox=-0.175398634277,51.8920136086,0.175398634277,52.1079863914'

        """

    def test_fetch_area_osm(self):
        """
        >>> Home = Node(0, 52, 0)
        >>> # The following test is skipped, because the Osm object doesn't
        >>> # support a reliable way __repr__ method.
        >>> Home.fetch_area_osm(3) # doctest: +SKIP

        """


class TestWay():
    def test___repr__():
        """
        >>> Way(0, (0, 1, 2))
        Way(0, [0, 1, 2], False, None, None, None)
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> Way(0, (0, 1, 2), True, "jnrowe", utils.Timestamp(2008, 1, 25))
        Way(0, [0, 1, 2], True, 'jnrowe', Timestamp(2008, 1, 25, 0, 0),
            None)
        >>> Way(0, (0, 1, 2), tags={"key": "value"})
        Way(0, [0, 1, 2], False, None, None, {'key': 'value'})

        """

    def test___str__(self):
        """
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> print(Way(0, (0, 1, 2)))
        Way 0 (nodes: 0, 1, 2)
        >>> print(Way(0, (0, 1, 2), True, "jnrowe",
        ...           utils.Timestamp(2008, 1, 25)))
        Way 0 (nodes: 0, 1, 2)
              [visible, user: jnrowe, timestamp: 2008-01-25T00:00:00+00:00]
        >>> print(Way(0, (0, 1, 2), tags={"key": "value"}))
        Way 0 (nodes: 0, 1, 2) [key: value]
        >>> nodes = [
        ...     Node(0, 52.015749, -0.221765, True, "jnrowe",
        ...          utils.Timestamp(2008, 1, 25, 12, 52, 11), None),
        ...     Node(1, 52.015761, -0.221767, True, None,
        ...          utils.Timestamp(2008, 1, 25, 12, 53, 14),
        ...          {"created_by": "hand", "highway": "crossing"}),
        ...     Node(2, 52.015754, -0.221766, True, "jnrowe",
        ...          utils.Timestamp(2008, 1, 25, 12, 52, 30),
        ...          {"amenity": "pub"}),
        ... ]
        >>> print(Way(0, (0, 1, 2), tags={"key": "value"}).__str__(nodes))
        Way 0 [key: value]
            Node 0 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:11+00:00]
            Node 1 (52°00'56"N, 000°13'18"W) [visible, timestamp: 2008-01-25T12:53:14+00:00, highway: crossing, created_by: hand]
            Node 2 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]

        """

    def test_toosm(self):
        """
        >>> ET.tostring(Way(0, (0, 1, 2)).toosm())
        '<way id="0" visible="false"><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'
        >>> ET.tostring(Way(0, (0, 1, 2), True, "jnrowe",
        ...                 utils.Timestamp(2008, 1, 25)).toosm())
        '<way id="0" timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" visible="true"><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'
        >>> ET.tostring(Way(0, (0, 1, 2), tags={"key": "value"}).toosm())
        '<way id="0" visible="false"><tag k="key" v="value" /><nd ref="0" /><nd ref="1" /><nd ref="2" /></way>'

        """

class TestOsm():
    def test_import_locations(self):
        """
        >>> from operator import attrgetter
        >>> from dtopt import NORMALIZE_WHITESPACE
        >>> region = Osm(open("test/data/osm"))
        >>> for node in sorted([x for x in region if isinstance(x, Node)],
        ...                    key=attrgetter("ident")):
        ...     print(node)
        Node 0 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:11+00:00]
        Node 1 (52°00'56"N, 000°13'18"W) [visible, timestamp: 2008-01-25T12:53:00+00:00, highway: crossing, created_by: hand]
        Node 2 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]

        """

    def test_export_osm_file(self):
        """
        >>> from sys import stdout
        >>> region = Osm(open("test/data/osm"))
        >>> xml = region.export_osm_file()
        >>> xml.write(stdout)
        <osm generator="upoints/0.11.0" version="0.5"><node id="0" lat="52.015749" lon="-0.221765" timestamp="2008-01-25T12:52:11+00:00" user="jnrowe" visible="true" /><node id="1" lat="52.015761" lon="-0.221767" timestamp="2008-01-25T12:53:00+00:00" visible="true"><tag k="highway" v="crossing" /><tag k="created_by" v="hand" /></node><node id="2" lat="52.015754" lon="-0.221766" timestamp="2008-01-25T12:52:30+00:00" user="jnrowe" visible="true"><tag k="amenity" v="pub" /></node><way id="0" timestamp="2008-01-25T13:00:00+00:00" visible="true"><tag k="highway" v="primary" /><tag k="ref" v="My Way" /><nd ref="0" /><nd ref="1" /><nd ref="2" /></way></osm>

        """
