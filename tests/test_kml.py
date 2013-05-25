#
# coding=utf-8
"""test_kml - Test kml support"""
# Copyright © 2012  James Rowe <jnrowe@gmail.com>
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

from upoints.kml import (Placemark, Placemarks, etree)


class TestPlacemark(TestCase):
    def test___repr__(self):
        expect(Placemark(52, 0, 4)) == \
            'Placemark(52.0, 0.0, 4.0, None, None)'
        expect(Placemark(52, 0, None)) == \
            'Placemark(52.0, 0.0, None, None, None)'
        expect(Placemark(52, 0, None, "name", "desc")) == \
            "Placemark(52.0, 0.0, None, 'name', 'desc')"

    def test___str__(self):
        expect(str(Placemark(52, 0, 4))) == \
            """52°00'00"N, 000°00'00"E alt 4m"""
        expect(str(Placemark(52, 0, None))) == \
            """52°00'00"N, 000°00'00"E"""
        expect(str(Placemark(52, 0, None, "name", "desc"))) == \
            """name (52°00'00"N, 000°00'00"E) [desc]"""
        expect(str(Placemark(52, 0, 42, "name", "desc"))) == \
            """name (52°00'00"N, 000°00'00"E alt 42m) [desc]"""

    def test_tokml(self):
        expect(etree.tostring(Placemark(52, 0, 4).tokml())) == \
            ('<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.2">'
             '<ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>')
        expect(etree.tostring(Placemark(52, 0, 4, "Cambridge").tokml())) == \
            ('<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.2" id="Cambridge">'
             '<ns0:name>Cambridge</ns0:name><ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>')
        expect(etree.tostring(Placemark(52, 0, 4).tokml(kml_version="2.0"))) == \
            ('<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.0">'
             '<ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point></ns0:Placemark>')
        expect(etree.tostring(Placemark(52, 0, 4, "Cambridge", "in the UK").tokml())) == \
            ('<ns0:Placemark xmlns:ns0="http://earth.google.com/kml/2.2" id="Cambridge">'
             '<ns0:name>Cambridge</ns0:name><ns0:description>in the UK</ns0:description>'
             '<ns0:Point><ns0:coordinates>0.0,52.0,4</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>')


class TestPlacemarks(TestCase):
    def test_import_locations(self):
        locations = Placemarks(open("test/data/kml"))
        expect(str(locations['Cambridge'])) ==  \
            """Cambridge (52°10'01"N, 000°23'24"E)"""
        expect(str(locations['Home'])) == \
            """Home (52°00'54"N, 000°13'15"W alt 60m)"""

    def test_export_kml_file(self):
        locations = Placemarks(open("test/data/kml"))
        xml = locations.export_kml_file()
        f = StringIO()
        xml.write(f)
        f.seek(0)
        expect(f.read()) == \
            ('<ns0:kml xmlns:ns0="http://earth.google.com/kml/2.2">'
             '<ns0:Document>'
             '<ns0:Placemark id="Home"><ns0:name>Home</ns0:name>'
             '<ns0:Point><ns0:coordinates>-0.221,52.015,60</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>'
             '<ns0:Placemark id="Cambridge"><ns0:name>Cambridge</ns0:name>'
             '<ns0:Point><ns0:coordinates>0.39,52.167</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>'
             '</ns0:Document>'
             '</ns0:kml>')
        xml = locations.export_kml_file("2.0")
        f = StringIO()
        xml.write(f)
        f.seek(0)
        expect(f.read()) == \
            ('<ns0:kml xmlns:ns0="http://earth.google.com/kml/2.0">'
             '<ns0:Document>'
             '<ns0:Placemark id="Home"><ns0:name>Home</ns0:name>'
             '<ns0:Point><ns0:coordinates>-0.221,52.015,60</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>'
             '<ns0:Placemark id="Cambridge"><ns0:name>Cambridge</ns0:name>'
             '<ns0:Point><ns0:coordinates>0.39,52.167</ns0:coordinates></ns0:Point>'
             '</ns0:Placemark>'
             '</ns0:Document>'
             '</ns0:kml>')
