#
# coding=utf-8
"""gpx - Imports GPS eXchange format data files"""
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

import time

from operator import attrgetter

from lxml import etree

from upoints import (point, utils)
from upoints._version import web as ua_string


GPX_NS = 'http://www.topografix.com/GPX/1/1'
etree.register_namespace('gpx', GPX_NS)

create_elem = utils.element_creator(GPX_NS)

GPX_ELEM_ATTRIB = {
    'creator': ua_string,
    'version': '1.1',
    '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': '%s http://www.topografix.com/GPX/1/1/gpx.xsd' % GPX_NS,
}

class _GpxElem(point.TimedPoint):

    """Abstract class for representing an element from GPX data files.

    .. versionadded:: 0.11.0

    """

    __slots__ = ('name', 'description', 'elevation', 'time', )

    _elem_name = None

    def __init__(self, latitude, longitude, name=None, description=None,
                 elevation=None, time=None):
        """Initialise a new ``_GpxElem`` object.

        :param float latitude: Element's latitude
        :param float longitude: Element's longitude
        :param str name: Name for Element
        :param str description: Element's description
        :param float elevation: Element's elevation
        :param utils.Timestamp time: Time the data was generated

        """
        super(_GpxElem, self).__init__(latitude, longitude, time=time)
        self.name = name
        self.description = description
        self.elevation = elevation

    def __str__(self):
        """Pretty printed location string.

        :rtype: ``str``
        :return: Human readable string representation of :class:`_GpxElem`
            object

        """
        location = super(_GpxElem, self).__format__('dms')
        if self.elevation:
            location += ' @ %sm' % self.elevation
        if self.time:
            location += ' on %s' % self.time.isoformat()
        if self.name:
            text = ['%s (%s)' % (self.name, location), ]
        else:
            text = [location, ]
        if self.description:
            text.append('[%s]' % self.description)
        return ' '.join(text)

    def togpx(self):
        """Generate a GPX waypoint element subtree.

        :rtype: :class:`etree.Element`
        :return: GPX element

        """
        element = create_elem(self.__class__._elem_name,
                              {'lat': str(self.latitude),
                               'lon': str(self.longitude)})
        if self.name:
            element.append(create_elem('name', text=self.name))
        if self.description:
            element.append(create_elem('desc', text=self.description))
        if self.elevation:
            element.append(create_elem('ele', text=str(self.elevation)))
        if self.time:
            element.append(create_elem('time', text=self.time.isoformat()))
        return element


class _SegWrap(list):

    """Abstract class for representing segmented elements from GPX data files.

    .. versionadded:: 0.12.0

    """

    def __init__(self, gpx_file=None, metadata=None):
        """Initialise a new ``_SegWrap`` object."""
        super(_SegWrap, self).__init__()
        self.metadata = metadata if metadata else _GpxMeta()
        self._gpx_file = gpx_file
        if gpx_file:
            self.import_locations(gpx_file)

    def distance(self, method='haversine'):
        """Calculate distances between locations in segments.

        :Parameters:
            method : ``str``
                Method used to calculate distance

        :rtype: ``list`` of ``list`` of ``float``
        :return: Groups of distance between points in segments

        """
        distances = []
        for segment in self:
            if len(segment) < 2:
                distances.append([])
            else:
                distances.append(segment.distance(method))
        return distances

    def bearing(self, format='numeric'):
        """Calculate bearing between locations in segments.

        :param str format: Format of the bearing string to return
        :rtype: ``list`` of ``list`` of ``float``
        :return: Groups of bearings between points in segments

        """
        bearings = []
        for segment in self:
            if len(segment) < 2:
                bearings.append([])
            else:
                bearings.append(segment.bearing(format))
        return bearings

    def final_bearing(self, format='numeric'):
        """Calculate final bearing between locations in segments.

        :param str format: Format of the bearing string to return
        :rtype: ``list`` of ``list`` of ``float``
        :return: Groups of bearings between points in segments

        """
        bearings = []
        for segment in self:
            if len(segment) < 2:
                bearings.append([])
            else:
                bearings.append(segment.final_bearing(format))
        return bearings

    def inverse(self):
        """Calculate the inverse geodesic between locations in segments.

        :rtype: ``list`` of 2 ``tuple`` of ``float``
        :return: Groups in bearing and distance between points in segments

        """
        inverses = []
        for segment in self:
            if len(segment) < 2:
                inverses.append([])
            else:
                inverses.append(segment.inverse())
        return inverses

    def midpoint(self):
        """Calculate the midpoint between locations in segments.

        :rtype: ``list`` of ``Point`` instance
        :return: Groups of midpoint between points in segments

        """
        midpoints = []
        for segment in self:
            if len(segment) < 2:
                midpoints.append([])
            else:
                midpoints.append(segment.midpoint())
        return midpoints

    def range(self, location, distance):
        """Test whether locations are within a given range of ``location``.

        :param Point location: Location to test range against
        :param float distance: Distance to test location is within
        :rtype: ``list`` of ``list`` of ``Point`` objects within specified
            range
        :return: Groups of points in range per segment

        """
        return (segment.range(location, distance) for segment in self)

    def destination(self, bearing, distance):
        """Calculate destination locations for given distance and bearings.

        :param float bearing: Bearing to move on in degrees
        :param float distance: Distance in kilometres
        :rtype: ``list`` of ``list`` of ``Point``
        :return: Groups of points shifted by ``distance`` and ``bearing``

        """
        return (segment.destination(bearing, distance) for segment in self)
    forward = destination

    def sunrise(self, date=None, zenith=None):
        """Calculate sunrise times for locations.

        :param datetime.date date: Calculate rise or set for given date
        :param str zenith: Calculate sunrise events, or end of twilight
        :rtype: ``list`` of ``list`` of :class:`datetime.datetime`
        :return: The time for the sunrise for each point in each segment

        """
        return (segment.sunrise(date, zenith) for segment in self)

    def sunset(self, date=None, zenith=None):
        """Calculate sunset times for locations.

        :param datetime.date date: Calculate rise or set for given date
        :param str zenith: Calculate sunset events, or start of twilight times
        :rtype: ``list`` of ``list`` of :class:`datetime.datetime`
        :return: The time for the sunset for each point in each segment

        """
        return (segment.sunset(date, zenith) for segment in self)

    def sun_events(self, date=None, zenith=None):
        """Calculate sunrise/sunset times for locations.

        :param datetime.date date: Calculate rise or set for given date
        :param str zenith: Calculate rise/set events, or twilight times
        :rtype: ``list`` of ``list`` of 2 ``tuple`` of
            :class:`datetime.datetime`
        :return: The time for the sunrise and sunset events for each point in
            each segment

        """
        return (segment.sun_events(date, zenith) for segment in self)

    def to_grid_locator(self, precision='square'):
        """Calculate Maidenhead locator for locations.

        :param str precision: Precision with which generate locator string
        :rtype: ``list`` of ``list`` of ``str``
        :return: Groups of Maidenhead locator for each point in segments

        """
        return (segment.to_grid_locator(precision) for segment in self)

    def speed(self):
        """Calculate speed between locations per segment.

        :rtype: ``list`` of ``list`` of ``float``
        :return: Speed between points in each segment in km/h

        """
        return (segment.speed() for segment in self)


class _GpxMeta(object):

    """Class for representing GPX global metadata.

    .. versionadded:: 0.12.0

    """

    __slots__ = ('name', 'desc', 'author', 'copyright', 'link', 'time',
                 'keywords', 'bounds', 'extensions')

    def __init__(self, name=None, desc=None, author=None, copyright=None,
                 link=None, time=None, keywords=None, bounds=None,
                 extensions=None):
        """Initialise a new `_GpxMeta` object.

        :param str name: Name for the export
        :param str desc: Description for the GPX export
        :param dict author: Author of the entire GPX data
        :param dict copyright: Copyright data for the exported data
        :type link: ``list`` of ``str`` or ``dict``
        :param link: Links associated with the data
        :param utils.Timestamp time:Time the data was generated
        :param str keywords: Keywords associated with the data
        :type bounds: ``dict`` or ``list`` of ``Point`` objects
        :param bounds: Area used in the data
        :type extensions: ``list`` of :class:`etree.Element` objects
        :param extensions: Any external data associated with the export

        """
        super(_GpxMeta, self).__init__()
        self.name = name
        self.desc = desc
        self.author = author if author else {}
        self.copyright = copyright if copyright else {}
        self.link = link if link else []
        self.time = time
        self.keywords = keywords
        self.bounds = bounds
        self.extensions = extensions

    def togpx(self):
        """Generate a GPX metadata element subtree.

        :rtype: :class:`etree.Element`
        :return: GPX metadata element

        """
        metadata = create_elem('metadata')
        if self.name:
            metadata.append(create_elem('name', text=self.name))
        if self.desc:
            metadata.append(create_elem('desc', text=self.desc))
        if self.author:
            element = create_elem('author')
            if self.author['name']:
                element.append(create_elem('name', text=self.author['name']))
            if self.author['email']:
                attr = dict(zip(self.author['email'].split('@'),
                                ('id', 'domain')))
                element.append(create_elem('email', attr))
            if self.author['link']:
                element.append(create_elem('link', text=self.author['link']))
            metadata.append(element)
        if self.copyright:
            if self.copyright['name']:
                author = {'author': self.copyright['name']}
            else:
                author = None
            element = create_elem('copyright', author)
            if self.copyright['year']:
                element.append(create_elem('year', text=self.copyright['year']))
            if self.copyright['license']:
                license = create_elem('license')
                element.append(license)
            metadata.append(element)
        if self.link:
            for link in self.link:
                if isinstance(link, basestring):
                    element = create_elem('link', {'href': link})
                else:
                    element = create_elem('link', {'href': link['href']})
                    if link['text']:
                        element.append(create_elem('text', text=link['text']))
                    if link['type']:
                        element.append(create_elem('type', text=link['type']))
                metadata.append(element)
        if isinstance(self.time, (time.struct_time, tuple)):
            text = time.strftime('%Y-%m-%dT%H:%M:%S%z', self.time)
        elif isinstance(self.time, utils.Timestamp):
            text = self.time.isoformat()
        else:
            text = time.strftime('%Y-%m-%dT%H:%M:%S%z')
        metadata.append(create_elem('time', text=text))
        if self.keywords:
            metadata.append(create_elem('keywords', text=self.keywords))
        if self.bounds:
            if not isinstance(self.bounds, dict):
                latitudes = list(map(attrgetter('latitude'), self.bounds))
                longitudes = list(map(attrgetter('longitude'), self.bounds))
                bounds = {
                    'minlat': str(min(latitudes)),
                    'maxlat': str(max(latitudes)),
                    'minlon': str(min(longitudes)),
                    'maxlon': str(max(longitudes)),
                }
            else:
                bounds = dict((k, str(v)) for k, v in self.bounds.items())
            metadata.append(create_elem('bounds', bounds))
        if self.extensions:
            element = create_elem('extensions')
            for i in self.extensions:
                element.append(i)
            metadata.append(self.extensions)
        return metadata

    def import_metadata(self, elements):
        """Import information from GPX metadata.

        :param etree.Element elements: GPX metadata subtree

        """
        metadata_elem = lambda name: etree.QName(GPX_NS, name)

        for child in elements.getchildren():
            tag_ns, tag_name = child.tag[1:].split('}')
            if not tag_ns == GPX_NS:
                continue
            if tag_name in ('name', 'desc', 'keywords'):
                setattr(self, tag_name, child.text)
            elif tag_name == 'time':
                self.time = utils.Timestamp.parse_isoformat(child.text)
            elif tag_name == 'author':
                self.author['name'] = child.findtext(metadata_elem('name'))
                aemail = child.find(metadata_elem('email'))
                if aemail:
                    self.author['email'] = '%s@%s' % (aemail.get('id'),
                                                      aemail.get('domain'))
                self.author['link'] = child.findtext(metadata_elem('link'))
            elif tag_name == 'bounds':
                self.bounds = {
                    'minlat': child.get('minlat'),
                    'maxlat': child.get('maxlat'),
                    'minlon': child.get('minlon'),
                    'maxlon': child.get('maxlon'),
                }
            elif tag_name == 'extensions':
                self.extensions = child.getchildren()
            elif tag_name == 'copyright':
                if child.get('author'):
                    self.copyright['name'] = child.get('author')
                self.copyright['year'] = child.findtext(metadata_elem('year'))
                self.copyright['license'] = child.findtext(metadata_elem('license'))
            elif tag_name == 'link':
                link = {
                    'href': child.get('href'),
                    'type': child.findtext(metadata_elem('type')),
                    'text': child.findtext(metadata_elem('text')),
                }
                self.link.append(link)


class Waypoint(_GpxElem):

    """Class for representing a waypoint element from GPX data files.

    .. versionadded:: 0.8.0

    .. seealso::

        :class:`_GpxElem`

    """

    __slots__ = ('name', 'description', )

    _elem_name = 'wpt'


class Waypoints(point.TimedPoints):

    """Class for representing a group of :class:`Waypoint` objects.

    .. versionadded:: 0.8.0

    """

    def __init__(self, gpx_file=None, metadata=None):
        """Initialise a new ``Waypoints`` object."""
        super(Waypoints, self).__init__()
        self.metadata = metadata if metadata else _GpxMeta()
        self._gpx_file = gpx_file
        if gpx_file:
            self.import_locations(gpx_file)

    def import_locations(self, gpx_file):
        """Import GPX data files.

        ``import_locations()`` returns a list with :class:`Waypoint` objects.

        It expects data files in GPX format, as specified in `GPX 1.1 Schema
        Documentation`_, which is XML such as::

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

        The reader uses the :mod:`ElementTree` module, so should be very fast
        when importing data.  The above file processed by ``import_locations()``
        will return the following ``list`` object::

            [Waypoint(52.015, -0.221, "Home", "My place"),
             Waypoint(52.167, 0.390, "MSR", "Microsoft Research, Cambridge")]

        :type gpx_file: ``file``, ``list`` or ``str``
        :param gpx_file: GPX data to read
        :rtype: ``list``
        :return: Locations with optional comments

        .. _GPX 1.1 Schema Documentation: http://www.topografix.com/GPX/1/1/

        """
        self._gpx_file = gpx_file
        data = utils.prepare_xml_read(gpx_file, objectify=True)

        try:
            self.metadata.import_metadata(data.metadata)
        except AttributeError:
            pass

        for waypoint in data.wpt:
            latitude = waypoint.get('lat')
            longitude = waypoint.get('lon')
            try:
                name = waypoint.name.text
            except AttributeError:
                name = None
            try:
                description = waypoint.desc.text
            except AttributeError:
                description = None
            try:
                elevation = float(waypoint.ele.text)
            except AttributeError:
                elevation = None
            try:
                time = utils.Timestamp.parse_isoformat(waypoint.time.text)
            except AttributeError:
                time = None
            self.append(Waypoint(latitude, longitude, name, description,
                                 elevation, time))

    def export_gpx_file(self):
        """Generate GPX element tree from ``Waypoints`` object.

        :rtype: :class:`etree.ElementTree`
        :return: GPX element tree depicting ``Waypoints`` object

        """
        gpx = create_elem('gpx', GPX_ELEM_ATTRIB)
        if not self.metadata.bounds:
            self.metadata.bounds = self[:]
        gpx.append(self.metadata.togpx())
        for place in self:
            gpx.append(place.togpx())

        return etree.ElementTree(gpx)


class Trackpoint(_GpxElem):

    """Class for representing a trackpoint element from GPX data files.

    .. versionadded:: 0.10.0

    .. seealso::

        :class:`_GpxElem`

    """

    __slots__ = ('name', 'description', )

    _elem_name = 'trkpt'


class Trackpoints(_SegWrap):

    """Class for representing a group of :class:`Trackpoint` objects.

    .. versionadded:: 0.10.0

    """

    def import_locations(self, gpx_file):
        """Import GPX data files.

        ``import_locations()`` returns a series of lists representing track
        segments with :class:`Trackpoint` objects as contents.

        It expects data files in GPX format, as specified in `GPX 1.1 Schema
        Documentation`_, which is XML such as::

            <?xml version="1.0" encoding="utf-8" standalone="no"?>
            <gpx version="1.1" creator="upoints/0.12.0"
            xmlns="http://www.topografix.com/GPX/1/1"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
              <trk>
                <trkseg>
                  <trkpt lat="52.015" lon="-0.221">
                    <name>Home</name>
                    <desc>My place</desc>
                  </trkpt>
                  <trkpt lat="52.167" lon="0.390">
                    <name>MSR</name>
                    <desc>Microsoft Research, Cambridge</desc>
                  </trkpt>
                </trkseg>
              </trk>
            </gpx>

        The reader uses the :mod:`ElementTree` module, so should be very fast
        when importing data.  The above file processed by ``import_locations()``
        will return the following ``list`` object::

            [[Trackpoint(52.015, -0.221, "Home", "My place"),
              Trackpoint(52.167, 0.390, "MSR", "Microsoft Research, Cambridge")], ]

        :type gpx_file: ``file``, ``list`` or ``str``
        :param gpx_file: GPX data to read
        :rtype: ``list``
        :return: Locations with optional comments

        .. _GPX 1.1 Schema Documentation: http://www.topografix.com/GPX/1/1/

        """
        self._gpx_file = gpx_file
        data = utils.prepare_xml_read(gpx_file, objectify=True)

        try:
            self.metadata.import_metadata(data.metadata)
        except AttributeError:
            pass

        for segment in data.trk.trkseg:
            points = point.TimedPoints()
            for trackpoint in segment.trkpt:
                latitude = trackpoint.get('lat')
                longitude = trackpoint.get('lon')
                try:
                    name = trackpoint.name.text
                except AttributeError:
                    name = None
                try:
                    description = trackpoint.desc.text
                except AttributeError:
                    description = None
                try:
                    elevation = float(trackpoint.ele.text)
                except AttributeError:
                    elevation = None
                try:
                    time = utils.Timestamp.parse_isoformat(trackpoint.time.text)
                except AttributeError:
                    time = None
                points.append(Trackpoint(latitude, longitude, name,
                                         description, elevation, time))
            self.append(points)

    def export_gpx_file(self):
        """Generate GPX element tree from ``Trackpoints``.

        :rtype: :class:`etree.ElementTree`
        :return: GPX element tree depicting ``Trackpoints`` objects

        """
        gpx = create_elem('gpx', GPX_ELEM_ATTRIB)
        if not self.metadata.bounds:
            self.metadata.bounds = [j for i in self for j in i]
        gpx.append(self.metadata.togpx())
        track = create_elem('trk')
        gpx.append(track)
        for segment in self:
            chunk = create_elem('trkseg')
            track.append(chunk)
            for place in segment:
                chunk.append(place.togpx())

        return etree.ElementTree(gpx)


class Routepoint(_GpxElem):

    """Class for representing a ``rtepoint`` element from GPX data files.

    .. versionadded:: 0.10.0

    .. seealso:

         :class:`_GpxElem`

    """

    __slots__ = ('name', 'description', )

    _elem_name = 'rtept'


class Routepoints(_SegWrap):

    """Class for representing a group of :class:`Routepoint` objects.

    .. versionadded:: 0.10.0

    """

    def import_locations(self, gpx_file):
        """Import GPX data files.

        ``import_locations()`` returns a series of lists representing track
        segments with :class:`Routepoint` objects as contents.

        It expects data files in GPX format, as specified in `GPX 1.1 Schema
        Documentation`_, which is XML such as::

            <?xml version="1.0" encoding="utf-8" standalone="no"?>
            <gpx version="1.1" creator="upoints/0.12.0"
            xmlns="http://www.topografix.com/GPX/1/1"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
              <rte>
                <rtept lat="52.015" lon="-0.221">
                  <name>Home</name>
                  <desc>My place</desc>
                </rtept>
                <rtept lat="52.167" lon="0.390">
                  <name>MSR</name>
                  <desc>Microsoft Research, Cambridge</desc>
                </rtept>
              </rte>
            </gpx>

        The reader uses the :mod:`ElementTree` module, so should be very fast
        when importing data.  The above file processed by ``import_locations()``
        will return the following ``list`` object::

            [[Routepoint(52.015, -0.221, "Home", "My place"),
              Routepoint(52.167, 0.390, "MSR", "Microsoft Research, Cambridge")], ]

        :type gpx_file: ``file``, ``list`` or ``str``
        :param gpx_file: GPX data to read
        :rtype: ``list``
        :return: Locations with optional comments

        .. _GPX 1.1 Schema Documentation: http://www.topografix.com/GPX/1/1/

        """
        self._gpx_file = gpx_file
        data = utils.prepare_xml_read(gpx_file, objectify=True)

        try:
            self.metadata.import_metadata(data.metadata)
        except AttributeError:
            pass

        for route in data.rte:
            points = point.TimedPoints()
            for routepoint in route.rtept:
                latitude = routepoint.get('lat')
                longitude = routepoint.get('lon')
                try:
                    name = routepoint.name.text
                except AttributeError:
                    name = None
                try:
                    description = routepoint.desc.text
                except AttributeError:
                    description = None
                try:
                    elevation = float(routepoint.ele.text)
                except AttributeError:
                    elevation = None
                try:
                    time = utils.Timestamp.parse_isoformat(routepoint.time.text)
                except AttributeError:
                    time = None
                points.append(Routepoint(latitude, longitude, name,
                                         description, elevation, time))
            self.append(points)

    def export_gpx_file(self):
        """Generate GPX element tree from :class:`Routepoints`

        :rtype: :class:`etree.ElementTree`
        :return: GPX element tree depicting :class:`Routepoints` objects

        """
        gpx = create_elem('gpx', GPX_ELEM_ATTRIB)
        if not self.metadata.bounds:
            self.metadata.bounds = [j for i in self for j in i]
        gpx.append(self.metadata.togpx())
        for rte in self:
            chunk = create_elem('rte')
            gpx.append(chunk)
            for place in rte:
                chunk.append(place.togpx())

        return etree.ElementTree(gpx)
