#
# coding=utf-8
"""test_cities - Test cities support"""
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

from unittest import TestCase

from expecter import expect

from upoints.cities import (City, Cities)


class TestCity(TestCase):
    def setUp(self):
        self.t = City(498, 'Zwickau', 'City', 'Sachsen', 'DE', 'Earth', 108835,
                      None, 12.5, 50.72, None,
                      (1997, 4, 10, 0, 0, 0, 3, 100, -1),
                      'M.Dowling@tu-bs.de')

    def test___repr__(self):
        expect(repr(self.t)) == \
            ("City(498, 'Zwickau', 'City', 'Sachsen', 'DE', 'Earth', 108835, "
             'None, 12.5, 50.72, None, (1997, 4, 10, 0, 0, 0, 3, 100, -1), '
             "'M.Dowling@tu-bs.de')")

    def test___str__(self):
        data = str(self.t).splitlines()
        expect(data[0]) == 'ID          : 498'
        expect(data[1]) == 'Type        : City'
        expect(data[2]) == 'Population  : 108835'
        expect(data[3]) == 'Size        : '
        expect(data[4]) == 'Name        : Zwickau'
        expect(data[5]) == ' Country    : DE'
        expect(data[6]) == ' Region     : Sachsen'
        expect(data[7]) == 'Location    : Earth'
        expect(data[8]) == ' Longitude  : 12.5'
        expect(data[9]) == ' Latitude   : 50.72'
        expect(data[10]) == ' Elevation  : '
        expect(data[11]) == 'Date        : 19970410'
        expect(data[12]) == 'Entered-By  : M.Dowling@tu-bs.de'


class TestCities(TestCase):
    def test_import_locations(self):
        cities_file = open('tests/data/city_data')
        cities = Cities(cities_file)
        data = [('%i - %s (%s;%s)' % (city.identifier, city.name,
                                      city.latitude, city.longitude))
                for city in sorted(cities, key=lambda x: x.identifier)]
        expect(data[0]) == '126 - London (51.5;-0.083)'
        expect(data[1]) == '127 - Luxembourg (49.617;6.117)'
        expect(data[2]) == '128 - Lyon (45.767;4.867)'
        cities_file.seek(0)
        manual_list = cities_file.read().split('//\\n')
        cities = Cities(manual_list)
        expect(len(cities)) == 1
