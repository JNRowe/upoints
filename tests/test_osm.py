#
"""test_osm - Test osm support"""
# Copyright © 2012-2021  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

from pytest import fixture, mark

from upoints import point, utils
from upoints.osm import Node, Osm, Way, etree, get_area_url

from tests.utils import xml_compare, xml_str_compare


@mark.parametrize(
    "size, results",
    [
        (
            3,
            (
                -0.26486443825283734,
                51.98800340214556,
                -0.17713556174716266,
                52.04199659785444,
            ),
        ),
        (
            12,
            (
                -0.3964574335910109,
                51.907013608582226,
                -0.04554256640898919,
                52.12298639141776,
            ),
        ),
    ],
)
def test_get_area_url(size, results):
    assert (
        get_area_url(point.Point(52.015, -0.221), size)
        == "http://api.openstreetmap.org/api/0.5/map?bbox=%s,%s,%s,%s" % results
    )


@fixture
def sample_Node():
    yield {
        "bare": Node(0, 52, 0),
        "named": Node(0, 52, 0, True, "jnrowe", utils.Timestamp(2008, 1, 25)),
        "tagged": Node(0, 52, 0, tags={"key": "value"}),
    }


@mark.parametrize(
    "node, result",
    [
        ("bare", "Node(0, 52.0, 0.0, False, None, None, None)"),
        (
            "named",
            "Node(0, 52.0, 0.0, True, 'jnrowe', "
            "Timestamp(2008, 1, 25, 0, 0), None)",
        ),
        (
            "tagged",
            "Node(0, 52.0, 0.0, False, None, None, {'key': 'value'})",
        ),
    ],
)
def test_Node___repr__(sample_Node, node, result):
    assert repr(sample_Node[node]) == result


@mark.parametrize(
    "node, result",
    [
        ("bare", """Node 0 (52°00′00″N, 000°00′00″E)"""),
        (
            "named",
            """Node 0 (52°00′00″N, 000°00′00″E) [visible, user: jnrowe, """
            "timestamp: 2008-01-25T00:00:00+00:00]",
        ),
        ("tagged", """Node 0 (52°00′00″N, 000°00′00″E) [key: value]"""),
    ],
)
def test_Node___str__(sample_Node, node, result):
    assert str(sample_Node[node]) == result


@mark.parametrize(
    "node, result",
    [
        ("bare", '<node id="0" lat="52.0" lon="0.0" visible="false"/>'),
        (
            "named",
            '<node id="0" lat="52.0" lon="0.0" '
            'timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" '
            'visible="true"/>',
        ),
        (
            "tagged",
            '<node id="0" lat="52.0" lon="0.0" visible="false">'
            '<tag k="key" v="value"/>'
            "</node>",
        ),
    ],
)
def test_Node_toosm(sample_Node, node, result):
    xml_str_compare(result, etree.tostring(sample_Node[node].toosm()))


@mark.parametrize(
    "size, results",
    [
        (
            3,
            (
                -0.04384973831146972,
                51.97300340214557,
                0.04384973831146972,
                52.02699659785445,
            ),
        ),
        (
            12,
            (
                -0.1753986342770412,
                51.892013608582225,
                0.1753986342770412,
                52.10798639141778,
            ),
        ),
    ],
)
def test_Node_get_area_url(sample_Node, size, results):
    assert (
        sample_Node["bare"].get_area_url(size)
        == "http://api.openstreetmap.org/api/0.5/map?bbox=%s,%s,%s,%s" % results
    )


def test_Node_fetch_area_osm():
    # FIXME: The following test is skipped, because the Osm object doesn't
    # support a reliable way __repr__ method.
    # assert Home.fetch_area_osm(3)
    pass


@fixture
def sample_Way():
    yield {
        "bare": Way(0, (0, 1, 2)),
        "named": Way(
            0, (0, 1, 2), True, "jnrowe", utils.Timestamp(2008, 1, 25)
        ),
        "tagged": Way(0, (0, 1, 2), tags={"key": "value"}),
    }


@mark.parametrize(
    "node, result",
    [
        ("bare", "Way(0, [0, 1, 2], False, None, None, None)"),
        (
            "named",
            "Way(0, [0, 1, 2], True, 'jnrowe', Timestamp(2008, 1, 25, 0, 0), "
            "None)",
        ),
        (
            "tagged",
            "Way(0, [0, 1, 2], False, None, None, {'key': 'value'})",
        ),
    ],
)
def test___repr__(sample_Way, node, result):
    assert repr(sample_Way[node]) == result


@mark.parametrize(
    "node, result",
    [
        ("bare", "Way 0 (nodes: 0, 1, 2)"),
        (
            "named",
            "Way 0 (nodes: 0, 1, 2) [visible, user: jnrowe, timestamp: "
            "2008-01-25T00:00:00+00:00]",
        ),
        ("tagged", "Way 0 (nodes: 0, 1, 2) [key: value]"),
    ],
)
def test___str__(sample_Way, node, result):
    assert str(sample_Way[node]) == result


def test___str___list(sample_Way):
    nodes = [
        Node(
            0,
            52.015749,
            -0.221765,
            True,
            "jnrowe",
            utils.Timestamp(2008, 1, 25, 12, 52, 11),
            None,
        ),
        Node(
            1,
            52.015761,
            -0.221767,
            True,
            None,
            utils.Timestamp(2008, 1, 25, 12, 53, 14),
            {"created_by": "hand", "highway": "crossing"},
        ),
        Node(
            2,
            52.015754,
            -0.221766,
            True,
            "jnrowe",
            utils.Timestamp(2008, 1, 25, 12, 52, 30),
            {"amenity": "pub"},
        ),
    ]
    assert sample_Way["tagged"].__str__(nodes).splitlines() == [
        "Way 0 [key: value]",
        """    Node 0 (52°00′56″N, 000°13′18″W) [visible, user: """
        "jnrowe, timestamp: 2008-01-25T12:52:11+00:00]",
        """    Node 1 (52°00′56″N, 000°13′18″W) [visible, timestamp: """
        "2008-01-25T12:53:14+00:00, created_by: hand, highway: crossing]",
        """    Node 2 (52°00′56″N, 000°13′18″W) [visible, user: """
        "jnrowe, timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]",
    ]


@mark.parametrize(
    "node, result",
    [
        (
            "bare",
            '<way id="0" visible="false">'
            '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
            "</way>",
        ),
        (
            "named",
            '<way id="0" timestamp="2008-01-25T00:00:00+00:00" user="jnrowe" '
            'visible="true">'
            '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
            "</way>",
        ),
        (
            "tagged",
            '<way id="0" visible="false">'
            '<tag k="key" v="value"/>'
            '<nd ref="0"/><nd ref="1"/><nd ref="2"/>'
            "</way>",
        ),
    ],
)
def test_toosm(sample_Way, node, result):
    xml_str_compare(result, etree.tostring(sample_Way[node].toosm()))


@fixture
def sample_Osm():
    with open("tests/data/osm") as f:
        yield Osm(f)


def test_Osm_import_locations(sample_Osm):
    assert [
        str(x)
        for x in sorted(
            (x for x in sample_Osm if isinstance(x, Node)),
            key=attrgetter("ident"),
        )
    ] == [
        """Node 0 (52°00′56″N, 000°13′18″W) [visible, user: jnrowe, """
        "timestamp: 2008-01-25T12:52:11+00:00]",
        """Node 1 (52°00′56″N, 000°13′18″W) [visible, timestamp: """
        "2008-01-25T12:53:00+00:00, created_by: hand, highway: crossing]",
        """Node 2 (52°00′56″N, 000°13′18″W) [visible, user: jnrowe, """
        "timestamp: 2008-01-25T12:52:30+00:00, amenity: pub]",
    ]


def test_Osm_export_osm_file(sample_Osm):
    export = sample_Osm.export_osm_file()
    osm_xml = etree.parse("tests/data/osm")
    for e1, e2 in zip(export.getiterator(), osm_xml.getiterator()):
        xml_compare(e1, e2)
