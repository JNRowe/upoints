#
# coding=utf-8
"""test_gpx - Test gpx support"""
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

from operator import attrgetter

from upoints.gpx import (_GpxElem, _GpxMeta, ET, Routepoint, Routepoints,
                         Trackpoint, Trackpoints, Waypoint, Waypoints)
from upoints import point
from upoints import utils


class Test_GpxElem():
    def test___init__(self):
        """
        >>> _GpxElem(52, 0)
        _GpxElem(52.0, 0.0, None, None, None, None)
        >>> _GpxElem(52, 0, None)
        _GpxElem(52.0, 0.0, None, None, None, None)
        >>> _GpxElem(52, 0, "name", "desc")
        _GpxElem(52.0, 0.0, 'name', 'desc', None, None)

        """

    def test___str__(self):
        """
        >>> print(_GpxElem(52, 0))
        52°00'00"N, 000°00'00"E
        >>> print(_GpxElem(52, 0, "name", "desc", 40))
        name (52°00'00"N, 000°00'00"E @ 40m) [desc]
        >>> print(_GpxElem(52, 0, "name", "desc", 40,
        ...                utils.Timestamp(2008, 7, 25)))
        name (52°00'00"N, 000°00'00"E @ 40m on 2008-07-25T00:00:00+00:00) [desc]

        """

    def test_togpx(self):
        """
        >>> ET.tostring(_GpxElem(52, 0).togpx())
        '<ns0:None xmlns:ns0="http://www.topografix.com/GPX/1/1" lat="52.0" lon="0.0" />'
        >>> ET.tostring(_GpxElem(52, 0, "Cambridge").togpx())
        '<ns0:None xmlns:ns0="http://www.topografix.com/GPX/1/1" lat="52.0" lon="0.0"><ns0:name>Cambridge</ns0:name></ns0:None>'
        >>> ET.tostring(_GpxElem(52, 0, "Cambridge", "in the UK").togpx())
        '<ns0:None xmlns:ns0="http://www.topografix.com/GPX/1/1" lat="52.0" lon="0.0"><ns0:name>Cambridge</ns0:name><ns0:desc>in the UK</ns0:desc></ns0:None>'
        >>> ET.tostring(_GpxElem(52, 0, "Cambridge", "in the UK").togpx())
        '<ns0:None xmlns:ns0="http://www.topografix.com/GPX/1/1" lat="52.0" lon="0.0"><ns0:name>Cambridge</ns0:name><ns0:desc>in the UK</ns0:desc></ns0:None>'
        >>> ET.tostring(_GpxElem(52, 0, "name", "desc", 40,
        ...                      utils.Timestamp(2008, 7, 25)).togpx())
        '<ns0:None xmlns:ns0="http://www.topografix.com/GPX/1/1" lat="52.0" lon="0.0"><ns0:name>name</ns0:name><ns0:desc>desc</ns0:desc><ns0:ele>40</ns0:ele><ns0:time>2008-07-25T00:00:00+00:00</ns0:time></ns0:None>'

        """


class Test_GpxMeta():
    def test_togpx(self):
        """
        >>> meta = _GpxMeta(time=(2008, 6, 3, 16, 12, 43, 1, 155, 0))
        >>> ET.tostring(meta.togpx())
        '<ns0:metadata xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:time>2008-06-03T16:12:43+0000</ns0:time></ns0:metadata>'
        >>> meta.bounds = {"minlat": 52, "maxlat": 54, "minlon": -2,
        ...                "maxlon": 1}
        >>> ET.tostring(meta.togpx())
        '<ns0:metadata xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:time>2008-06-03T16:12:43+0000</ns0:time><ns0:bounds maxlat="54" maxlon="1" minlat="52" minlon="-2" /></ns0:metadata>'
        >>> meta.bounds = [point.Point(52.015, -0.221),
        ...                point.Point(52.167, 0.390)]
        >>> from dtopt import ELLIPSIS
        >>> ET.tostring(meta.togpx())
        '<ns0:metadata xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:time>...</ns0:time><ns0:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221" /></ns0:metadata>'

        """


class TestWaypoint():
    """
    >>> Waypoint(52, 0)
    Waypoint(52.0, 0.0, None, None, None, None)
    >>> Waypoint(52, 0, None)
    Waypoint(52.0, 0.0, None, None, None, None)
    >>> Waypoint(52, 0, "name", "desc")
    Waypoint(52.0, 0.0, 'name', 'desc', None, None)

    """


class TestWaypoints():
    def test_import_locations(self):
        """
        >>> waypoints = Waypoints(open("test/data/gpx"))
        >>> for value in sorted(waypoints, key=attrgetter("name")):
        ...     print(value)
        Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]
        MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]

        """

    def test_export_gpx_file(self):
        """
        >>> from sys import stdout
        >>> locations = Waypoints(open("test/data/gpx"))
        >>> xml = locations.export_gpx_file()
        >>> from dtopt import ELLIPSIS
        >>> xml.write(stdout)
        <ns0:gpx xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:metadata><ns0:time>...</ns0:time><ns0:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221" /></ns0:metadata><ns0:wpt lat="52.015" lon="-0.221"><ns0:name>Home</ns0:name><ns0:desc>My place</ns0:desc><ns0:time>2008-07-26T00:00:00+00:00</ns0:time></ns0:wpt><ns0:wpt lat="52.167" lon="0.39"><ns0:name>MSR</ns0:name><ns0:desc>Microsoft Research, Cambridge</ns0:desc><ns0:time>2008-07-27T00:00:00+00:00</ns0:time></ns0:wpt></ns0:gpx>

        """


class TestTrackpoint():
    """
    >>> Trackpoint(52, 0)
    Trackpoint(52.0, 0.0, None, None, None, None)
    >>> Trackpoint(52, 0, None)
    Trackpoint(52.0, 0.0, None, None, None, None)
    >>> Trackpoint(52, 0, "name", "desc")
    Trackpoint(52.0, 0.0, 'name', 'desc', None, None)

    """


class TestTrackpoints():
    def test_import_locations(self):
        """
        >>> trackpoints = Trackpoints(open("test/data/gpx_tracks"))
        >>> for value in sorted(trackpoints[0],
        ...                     key=attrgetter("name")):
        ...     print(value)
        Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]
        MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]

        """

    def test_export_gpx_file(self):
        """
        >>> from sys import stdout
        >>> locations = Trackpoints(open("test/data/gpx_tracks"))
        >>> xml = locations.export_gpx_file()
        >>> from dtopt import ELLIPSIS
        >>> xml.write(stdout)
        <ns0:gpx xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:metadata><ns0:time>...</ns0:time><ns0:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221" /></ns0:metadata><ns0:trk><ns0:trkseg><ns0:trkpt lat="52.015" lon="-0.221"><ns0:name>Home</ns0:name><ns0:desc>My place</ns0:desc><ns0:time>2008-07-26T00:00:00+00:00</ns0:time></ns0:trkpt><ns0:trkpt lat="52.167" lon="0.39"><ns0:name>MSR</ns0:name><ns0:desc>Microsoft Research, Cambridge</ns0:desc><ns0:time>2008-07-27T00:00:00+00:00</ns0:time></ns0:trkpt></ns0:trkseg></ns0:trk></ns0:gpx>

        """


class TestRoutepoint():
    """
    >>> Routepoint(52, 0)
    Routepoint(52.0, 0.0, None, None, None, None)
    >>> Routepoint(52, 0, None)
    Routepoint(52.0, 0.0, None, None, None, None)
    >>> Routepoint(52, 0, "name", "desc")
    Routepoint(52.0, 0.0, 'name', 'desc', None, None)

    """


class TestRoutepoints():
    def test_import_locations(self):
        """
        >>> routepoints = Routepoints(open("test/data/gpx_routes"))
        >>> for value in sorted(routepoints[0],
        ...                     key=attrgetter("name")):
        ...     print(value)
        Home (52°00'54"N, 000°13'15"W on 2008-07-26T00:00:00+00:00) [My place]
        MSR (52°10'01"N, 000°23'24"E on 2008-07-27T00:00:00+00:00) [Microsoft Research, Cambridge]

        """

    def test_export_gpx_file(self):
        """
        >>> from sys import stdout
        >>> locations = Routepoints(open("test/data/gpx_routes"))
        >>> xml = locations.export_gpx_file()
        >>> from dtopt import ELLIPSIS
        >>> xml.write(stdout)
        <ns0:gpx xmlns:ns0="http://www.topografix.com/GPX/1/1"><ns0:metadata><ns0:time>...</ns0:time><ns0:bounds maxlat="52.167" maxlon="0.39" minlat="52.015" minlon="-0.221" /></ns0:metadata><ns0:rte><ns0:rtept lat="52.015" lon="-0.221"><ns0:name>Home</ns0:name><ns0:desc>My place</ns0:desc><ns0:time>2008-07-26T00:00:00+00:00</ns0:time></ns0:rtept><ns0:rtept lat="52.167" lon="0.39"><ns0:name>MSR</ns0:name><ns0:desc>Microsoft Research, Cambridge</ns0:desc><ns0:time>2008-07-27T00:00:00+00:00</ns0:time></ns0:rtept></ns0:rte></ns0:gpx>

        """
