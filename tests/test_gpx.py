#
# coding=utf-8
"""test_gpx - Test gpx support"""
# Copyright © 2007-2013  James Rowe <jnrowe@gmail.com>
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

from StringIO import StringIO
from unittest import TestCase

from expecter import expect

from upoints.gpx import (_GpxElem, _GpxMeta, Routepoint, Routepoints,
                         Trackpoint, Trackpoints, Waypoint, Waypoints, etree)
from upoints import point
from upoints import utils

from utils import xml_str_compare


class Test_GpxElem(TestCase):
    def test___repr__(self):
        expect(repr(_GpxElem(52, 0))) == \
            '_GpxElem(52.0, 0.0, None, None, None, None)'
        expect(repr(_GpxElem(52, 0, None))) == \
            '_GpxElem(52.0, 0.0, None, None, None, None)'
        expect(_GpxElem(52, 0, 'name', 'desc')) == \
            "_GpxElem(52.0, 0.0, 'name', 'desc', None, None)"

    def test___str__(self):
        expect(str(_GpxElem(52, 0))) == """52°00'00"N, 000°00'00"E"""
        expect(str(_GpxElem(52, 0, 'name', 'desc', 40))) == \
            """name (52°00'00"N, 000°00'00"E @ 40m) [desc]"""
        expect(str(_GpxElem(52, 0, 'name', 'desc', 40,
                   utils.Timestamp(2008, 7, 25)))) == \
            ("""name (52°00'00"N, 000°00'00"E @ 40m on """
             '2008-07-25T00:00:00+00:00) [desc]')


class Test_GpxMeta(TestCase):
    def test_togpx(self):
        meta = _GpxMeta(time=(2008, 6, 3, 16, 12, 43, 1, 155, 0))
        expect(etree.tostring(meta.togpx())) == \
            ('<gpx:metadata xmlns:gpx="http://www.topografix.com/GPX/1/1">'
             '<gpx:time>2008-06-03T16:12:43+0000</gpx:time>'
             '</gpx:metadata>')
        meta.bounds = {'minlat': 52, 'maxlat': 54, 'minlon': -2, 'maxlon': 1}
        expect(etree.tostring(meta.togpx())) == \
            ('<gpx:metadata xmlns:gpx="http://www.topografix.com/GPX/1/1">'
             '<gpx:time>2008-06-03T16:12:43+0000</gpx:time><gpx:bounds maxlat="54" maxlon="1" minlat="52" minlon="-2"/>'
             '</gpx:metadata>')
        meta.bounds = [point.Point(52.015, -0.221), point.Point(52.167, 0.390)]
        expect(etree.tostring(meta.togpx())) == \
            ('<gpx:metadata xmlns:gpx="http://www.topografix.com/GPX/1/1">'
                    '<gpx:time>2008-06-03T16:12:43+0000</gpx:time><gpx:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221"/>'
             '</gpx:metadata>')


class TestWaypoint(TestCase):
    expect(repr(Waypoint(52, 0))) == \
        'Waypoint(52.0, 0.0, None, None, None, None)'
    expect(repr(Waypoint(52, 0, None))) == \
        'Waypoint(52.0, 0.0, None, None, None, None)'
    expect(repr(Waypoint(52, 0, 'name', 'desc'))) == \
        "Waypoint(52.0, 0.0, 'name', 'desc', None, None)"


class TestWaypoints(TestCase):
    def test_import_locations(self):
        waypoints = Waypoints(open('tests/data/gpx'))
        data = map(str, sorted(waypoints, key=lambda x: x.name))
        expect(data[0]) == \
            """Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]"""
        expect(data[1]) == \
            """MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]"""

    def test_export_gpx_file(self):
        locations = Waypoints(open('tests/data/gpx'))
        xml = locations.export_gpx_file()
        f = StringIO()
        xml.write(f)
        f.seek(0)
        xml_str_compare(
            ('<gpx:gpx xmlns:gpx="http://www.topografix.com/GPX/1/1">'
             '<gpx:metadata>'
             '<gpx:time>...</gpx:time>'
             '<gpx:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221"/>'
             '</gpx:metadata>'
             '<gpx:wpt lat="52.015" lon="-0.221">'
             '<gpx:name>Home</gpx:name><gpx:desc>My place</gpx:desc><gpx:time>2008-07-26T00:00:00+00:00</gpx:time>'
             '</gpx:wpt>'
             '<gpx:wpt lat="52.167" lon="0.39">'
             '<gpx:name>MSR</gpx:name><gpx:desc>Microsoft Research, Cambridge</gpx:desc>'
             '<gpx:time>2008-07-27T00:00:00+00:00</gpx:time>'
             '</gpx:wpt>'
             '</gpx:gpx>'),
            f.read(),
            ellipsis=True)


class TestTrackpoint(TestCase):
    def test___repr__(self):
        expect(Trackpoint(52, 0)) == \
            'Trackpoint(52.0, 0.0, None, None, None, None)'
        expect(Trackpoint(52, 0, None)) == \
            'Trackpoint(52.0, 0.0, None, None, None, None)'
        expect(Trackpoint(52, 0, 'name', 'desc')) == \
            "Trackpoint(52.0, 0.0, 'name', 'desc', None, None)"


class TestTrackpoints(TestCase):
    def test_import_locations(self):
        trackpoints = Trackpoints(open('tests/data/gpx_tracks'))
        data = map(str, sorted(trackpoints[0], key=lambda x: x.name))
        expect(data[0]) == \
            """Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]"""
        expect(data[1]) == \
            """MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]"""

    def test_export_gpx_file(self):
        locations = Trackpoints(open('tests/data/gpx_tracks'))
        xml = locations.export_gpx_file()
        f = StringIO()
        xml.write(f)
        f.seek(0)
        xml_str_compare(
            ('<gpx:gpx xmlns:gpx="http://www.topografix.com/GPX/1/1">'
             '<gpx:metadata>'
             '<gpx:time>...</gpx:time><gpx:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221"/>'
             '</gpx:metadata>'
             '<gpx:trk>'
             '<gpx:trkseg>'
             '<gpx:trkpt lat="52.015" lon="-0.221">'
             '<gpx:name>Home</gpx:name><gpx:desc>My place</gpx:desc><gpx:time>2008-07-26T00:00:00+00:00</gpx:time>'
             '</gpx:trkpt>'
             '<gpx:trkpt lat="52.167" lon="0.39">'
             '<gpx:name>MSR</gpx:name><gpx:desc>Microsoft Research, Cambridge</gpx:desc>'
             '<gpx:time>2008-07-27T00:00:00+00:00</gpx:time>'
             '</gpx:trkpt>'
             '</gpx:trkseg>'
             '</gpx:trk>'
             '</gpx:gpx>'),
            f.read(),
            ellipsis=True)


class TestRoutepoint(TestCase):
    def test___repr__(self):
        expect(Routepoint(52, 0)) == \
            'Routepoint(52.0, 0.0, None, None, None, None)'
        expect(Routepoint(52, 0, None)) == \
            'Routepoint(52.0, 0.0, None, None, None, None)'
        expect(Routepoint(52, 0, 'name', 'desc')) == \
            "Routepoint(52.0, 0.0, 'name', 'desc', None, None)"


class TestRoutepoints(TestCase):
    def test_import_locations(self):
        routepoints = Routepoints(open('tests/data/gpx_routes'))
        data = map(str, sorted(routepoints[0], key=lambda x: x.name))
        expect(data[0]) == \
            """Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]"""
        expect(data[1]) == \
            """MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]"""

    def test_export_gpx_file(self):
        locations = Routepoints(open('tests/data/gpx_routes'))
        xml = locations.export_gpx_file()
        f = StringIO()
        xml.write(f)
        f.seek(0)
        xml_str_compare(
            ('<gpx:gpx xmlns:gpx="http://www.topografix.com/GPX/1/1">'
             '<gpx:metadata>'
             '<gpx:time>...</gpx:time>'
             '<gpx:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221"/>'
             '</gpx:metadata>'
             '<gpx:rte>'
             '<gpx:rtept lat="52.015" lon="-0.221">'
             '<gpx:name>Home</gpx:name><gpx:desc>My place</gpx:desc><gpx:time>2008-07-26T00:00:00+00:00</gpx:time>'
             '</gpx:rtept>'
             '<gpx:rtept lat="52.167" lon="0.39">'
             '<gpx:name>MSR</gpx:name><gpx:desc>Microsoft Research, Cambridge</gpx:desc>'
             '<gpx:time>2008-07-27T00:00:00+00:00</gpx:time>'
             '</gpx:rtept>'
             '</gpx:rte>'
             '</gpx:gpx>'),
            f.read(),
            ellipsis=True)
