#
"""test_kml - Test kml support"""
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

from pytest import mark

from upoints.kml import (Placemark, Placemarks, etree)

from tests.utils import xml_compare


class TestPlacemark:
    @mark.parametrize('args, result', [
        ((52, 0, 4), 'Placemark(52.0, 0.0, 4.0, None, None)'),
        ((52, 0, None), 'Placemark(52.0, 0.0, None, None, None)'),
        ((52, 0, None, 'name', 'desc'),
         "Placemark(52.0, 0.0, None, 'name', 'desc')"),
    ])
    def test___repr__(self, args, result):
        assert Placemark(*args) == result

    @mark.parametrize('args, result', [
        ((52, 0, 4), '52°00′00″N, 000°00′00″E alt 4m'),
        ((52, 0, None), '52°00′00″N, 000°00′00″E'),
        ((52, 0, None, 'name', 'desc'),
         'name (52°00′00″N, 000°00′00″E) [desc]'),
        ((52, 0, 42, 'name', 'desc'),
         'name (52°00′00″N, 000°00′00″E alt 42m) [desc]'),
    ])
    def test___str__(self, args, result):
        assert str(Placemark(*args)) == result

    @mark.parametrize('args, result', [
        ((52, 0, 4),
         b'<kml:Placemark xmlns:kml="http://earth.google.com/kml/2.2">'
         b'<kml:Point><kml:coordinates>0.0,52.0,4</kml:coordinates></kml:Point>'
         b'</kml:Placemark>'),
        ((52, 0, 4, 'Cambridge'),
         b'<kml:Placemark xmlns:kml="http://earth.google.com/kml/2.2" id="Cambridge">'
         b'<kml:name>Cambridge</kml:name><kml:Point><kml:coordinates>0.0,52.0,4</kml:coordinates></kml:Point>'
         b'</kml:Placemark>'),
        ((52, 0, 4),
         b'<kml:Placemark xmlns:kml="http://earth.google.com/kml/2.2">'
         b'<kml:Point><kml:coordinates>0.0,52.0,4</kml:coordinates></kml:Point></kml:Placemark>'),
        ((52, 0, 4, 'Cambridge', 'in the UK'),
         b'<kml:Placemark xmlns:kml="http://earth.google.com/kml/2.2" id="Cambridge">'
         b'<kml:name>Cambridge</kml:name><kml:description>in the UK</kml:description>'
         b'<kml:Point><kml:coordinates>0.0,52.0,4</kml:coordinates></kml:Point>'
         b'</kml:Placemark>'),
    ])
    def test_tokml(self, args, result):
        assert etree.tostring(Placemark(*args).tokml()) == result


class TestPlacemarks:
    @mark.parametrize('name, result', [
        ('Cambridge', 'Cambridge (52°10′01″N, 000°23′24″E)'),
        ('Home', 'Home (52°00′54″N, 000°13′15″W alt 60m)'),
    ])
    def test_import_locations(self, name, result):
        with open('tests/data/kml') as f:
            locations = Placemarks(f)
        assert str(locations[name]) == result

    def test_export_kml_file(self):
        filename = 'tests/data/kml'
        with open(filename) as f:
            locations = Placemarks(f)
        export = locations.export_kml_file()
        kml_xml = etree.parse(filename)
        for e1, e2 in zip(export.getiterator(), kml_xml.getiterator()):
            xml_compare(e1, e2)
