#
"""test_osm - Test osm support"""
# Copyright © 2012-2017  James Rowe <jnrowe@gmail.com>
#
# This file is part of upoints.
#
# upoints is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# upoints is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# upoints.  If not, see <http://www.gnu.org/licenses/>.

from operator import attrgetter

from pytest import mark

from upoints import (point, utils)
from upoints.osm import (Node, Osm, Way, etree, get_area_url)

from tests.utils import (xml_compare, xml_str_compare)


@mark.parametrize('size, results', [
    (3, (-0.26486443825283734, 51.98800340214556, -0.17713556174716266,
         52.04199659785444)),
    (12, (-0.3964574335910109, 51.907013608582226, -0.04554256640898919,
          52.12298639141776)),
])
def test_get_area_url(size, results):
    assert get_area_url(point.Point(52.015, -0.221), size) == \
        'http://api.openstreetmap.org/api/0.5/map?bbox=%s,%s,%s,%s' % results


class TestNode:
    def setup(self):
        self.bare = Node(0, 52, 0)
        self.named = Node(0, 52, 0, True, 'jnrowe',
                          utils.Timestamp(2008, 1, 25))
        self.tagged = Node(0, 52, 0, tags={'key': 'value'})

    @mark.parametrize('node, result', [
        ('bare', 'Node(0, 52.0, 0.0, False, None, None, None)'),
        ('named',
         "Node(0, 52.0, 0.0, True, 'jnrowe', "
         "Timestamp(2008, 1, 25, 0, 0), None)"),
        ('tagged', "Node(0, 52.0, 0.0, False, None, None, {'key': 'value'})"),
    ])
    def test___repr__(self, node, result):
        assert repr(getattr(self, node)) == result

    @mark.parametrize('node, result', [
        ('bare', """Node 0 (52°00'00"N, 000°00'00"E)"""),
        ('named',
         """Node 0 (52°00'00"N, 000°00'00"E) [visible, user: jnrowe, """
         'timestamp: 2008-01-25T00:00:00+00:00]'),
        ('tagged', """Node 0 (52°00'00"N, 000°00'00"E) [key: value]"""),
    ])
    def test___str__(self, node, result):
        assert str(getattr(self, node)) == result

    @mark.parametrize('node, result', [
        ('bare', '<node id="0" lat="52.0" lon="0.0" visible="false"/>'),
        ('named',
         '<node id="0" lat="52.0" lon="0.0" '
         'timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" '
         'visible="true"/>'),
        ('tagged',
         '<node id="0" lat="52.0" lon="0.0" visible="false">'
         '<tag k="key" v="value"/>'
         '</node>'),
    ])
    def test_toosm(self, node, result):
        xml_str_compare(result, etree.tostring(getattr(self, node).toosm()))

    @mark.parametrize('size, results', [
        (3, (-0.04384973831146972, 51.97300340214557, 0.04384973831146972,
             52.02699659785445)),
        (12, (-0.1753986342770412, 51.892013608582225, 0.1753986342770412,
              52.10798639141778)),
    ])
    def test_get_area_url(self, size, results):
        assert self.bare.get_area_url(size) == \
            'http://api.openstreetmap.org/api/0.5/map?bbox=%s,%s,%s,%s' \
            % results

    def test_fetch_area_osm(self):
        # FIXME: The following test is skipped, because the Osm object doesn't
        # support a reliable way __repr__ method.
        # assert Home.fetch_area_osm(3
        pass


class TestWay:
    def setup(self):
        self.bare = Way(0, (0, 1, 2))
        self.named = Way(0, (0, 1, 2), True, 'jnrowe',
                         utils.Timestamp(2008, 1, 25))
        self.tagged = Way(0, (0, 1, 2), tags={'key': 'value'})

    @mark.parametrize('node, result', [
        ('bare', 'Way(0, [0, 1, 2], False, None, None, None)'),
        ('named',
         "Way(0, [0, 1, 2], True, 'jnrowe', Timestamp(2008, 1, 25, 0, 0), "
         "None)"),
        ('tagged', "Way(0, [0, 1, 2], False, None, None, {'key': 'value'})"),
    ])
    def test___repr__(self, node, result):
        assert repr(getattr(self, node)) == result

    @mark.parametrize('node, result', [
        ('bare', 'Way 0 (nodes: 0, 1, 2)'),
        ('named',
         'Way 0 (nodes: 0, 1, 2) [visible, user: jnrowe, timestamp: '
         '2008-01-25T00:00:00+00:00]'),
        ('tagged', 'Way 0 (nodes: 0, 1, 2) [key: value]'),
    ])
    def test___str__(self, node, result):
        assert str(getattr(self, node)) == result

    def test___str___list(self):
        nodes = [
            Node(0, 52.015749, -0.221765, True, 'jnrowe',
                 utils.Timestamp(2008, 1, 25, 12, 52, 11), None),
            Node(1, 52.015761, -0.221767, True, None,
                 utils.Timestamp(2008, 1, 25, 12, 53, 14),
                 {'created_by': 'hand', 'highway': 'crossing'}),
            Node(2, 52.015754, -0.221766, True, 'jnrowe',
                 utils.Timestamp(2008, 1, 25, 12, 52, 30),
                 {'amenity': 'pub'}),
        ]
        assert self.tagged.__str__(nodes).splitlines() == [
            'Way 0 [key: value]',
            """    Node 0 (52°00'56"N, 000°13'18"W) [visible, user: """
            'jnrowe, timestamp: 2008-01-25T12:52:11+00:00]',
            """    Node 1 (52°00'56"N, 000°13'18"W) [visible, timestamp: """
            '2008-01-25T12:53:14+00:00, created_by: hand, highway: crossing]',
            """    Node 2 (52°00'56"N, 000°13'18"W) [visible, user: """
            'jnrowe, timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]',
        ]

    @mark.parametrize('node, result', [
        ('bare',
         '<way id="0" visible="false">'
         '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
         '</way>'),
        ('named',
         '<way id="0" timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" '
         'visible="true">'
         '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
         '</way>'),
        ('tagged',
         '<way id="0" visible="false">'
         '<tag k="key" v="value"/>'
         '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
         '</way>'),
    ])
    def test_toosm(self, node, result):
        xml_str_compare(result, etree.tostring(getattr(self, node).toosm()))


class TestOsm:
    def setup(self):
        with open('tests/data/osm') as f:
            self.region = Osm(f)

    def test_import_locations(self):
        assert [str(x) for x in sorted([x for x in self.region
                                        if isinstance(x, Node)],
                                       key=attrgetter('ident'))] == [
            """Node 0 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, """
            'timestamp: 2008-01-25T12:52:11+00:00]',
            """Node 1 (52°00'56"N, 000°13'18"W) [visible, timestamp: """
            '2008-01-25T12:53:00+00:00, created_by: hand, highway: crossing]',
            """Node 2 (52°00'56"N, 000°13'18"W) [visible, user: jnrowe, """
            'timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]',
        ]

    def test_export_osm_file(self):
        export = self.region.export_osm_file()
        osm_xml = etree.parse('tests/data/osm')
        for e1, e2 in zip(export.getiterator(), osm_xml.getiterator()):
            xml_compare(e1, e2)
