#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""cities - Imports GNU miscfiles cities data files"""
# Copyright (C) 2007  James Rowe
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

import logging
import os
import time

from earth_distance import (trigpoints, utils)

TEMPLATE = """\
ID          : %s
Type        : %s
Population  : %s
Size        : %s
Name        : %s
 Country    : %s
 Region     : %s
Location    : %s
 Longitude  : %s
 Latitude   : %s
 Elevation  : %s
Date        : %s
Entered-By  : %s"""

class City(trigpoints.Trigpoint):
    """
    Class for representing an entry from the GNU miscfiles cities data file

    @ivar ptype: Place type
    @ivar population: Place population, if known
    @ivar size: Place Size
    @ivar name: Place name
    @ivar country: Country the place is in
    @ivar region: Region the place is in
    @ivar location: Body, always Earth in miscfiles 1.4.2
    @ivar latitude: Place's latitude
    @ivar longitude: Place's longitude
    @ivar altitude: Place's elevation
    @ivar date: Entry date
    @ivar entered: Entry's author
    """

    __slots__ = ('identifier', 'ptype', 'population', 'size', 'country',
                 'region', 'location', 'date', 'entered')

    def __init__(self, identifier, name, ptype, region, country, location,
                 population, size, latitude, longitude, altitude, date,
                 entered):
        """
        Initialise a new C{City} object

        @type identifier: C{int}
        @param identifier: Numeric identifier for object
        @type name: C{str}
        @param name: Place name
        @type ptype: C{str}
        @param ptype: Type of place
        @type region: C{str} or C{None}
        @param region: Region place can be found
        @type country: C{str} or C{None}
        @param country: Country name place can be found
        @type location: C{str}
        @param location: Body place can be found
        @type population: C{int} or C{None}
        @param population: Place's population
        @type size: C{int} or C{None}
        @param size: Place's area
        @type latitude: C{float}
        @param latitude: Station's latitude
        @type longitude: C{float}
        @param longitude: Station's longitude
        @type altitude: C{int} or C{None}
        @param altitude: Station's elevation
        @type date: C{time.struct_time}
        @param date: Date the entry was added
        @type entered: C{str} or C{None}
        @param entered: Entry's author
        """
        super(City, self).__init__(latitude, longitude, altitude, name)
        self.identifier = identifier
        self.ptype = ptype
        self.region = region
        self.country = country
        self.location = location
        self.population = population
        self.size = size
        self.date = date
        self.entered = entered

    def __repr__(self):
        """
        Self-documenting string representation

        >>> City(498, "Zwickau", "City", "Sachsen", "DE", "Earth", 108835,
        ...      None, 12.5, 50.72, None, (1997, 4, 10, 0, 0, 0, 3, 100, -1),
        ...      "M.Dowling@tu-bs.de")
        City(498, 'Zwickau', 'City', 'Sachsen', 'DE', 'Earth', 108835, None,
             12.5, 50.72, None, (1997, 4, 10, 0, 0, 0, 3, 100, -1),
             'M.Dowling@tu-bs.de')

        @rtype: C{str}
        @return: String to recreate C{City} object
        """
        data = utils.repr_assist(self.identifier, self.name, self.ptype,
                                 self.region, self.country, self.location,
                                 self.population, self.size, self.latitude,
                                 self.longitude, self.altitude, self.date,
                                 self.entered)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def __str__(self, mode=None):
        """
        Pretty printed location string

        @see: C{trigpoints.point.Point}

        >>> t = City(498, "Zwickau", "City", "Sachsen", "DE", "Earth", 108835,
        ...          None, 50.72, 12.5, None,
        ...          (1997, 4, 10, 0, 0, 0, 3, 100, -1), "M.Dowling@tu-bs.de")
        >>> print(t)
        ID          : 498
        Type        : City
        Population  : 108835
        Size        : 
        Name        : Zwickau
         Country    : DE
         Region     : Sachsen
        Location    : Earth
         Longitude  : 12.5
         Latitude   : 50.72
         Elevation  : 
        Date        : 19970410
        Entered-By  : M.Dowling@tu-bs.de

        @type mode: C{None}
        @param mode: Dummy parameter to maintain signature of
            C{Trigpoint.__str__}
        @rtype: C{str}
        @return: Human readable string representation of C{City} object
        """
        values = map(utils.value_or_empty,
                     (self.identifier, self.ptype,
                      self.population, self.size,
                      self.name, self.country,
                      self.region, self.location,
                      self.longitude, self.latitude,
                      self.altitude,
                      time.strftime("%Y%m%d", self.date) if self.date else "",
                      self.entered))
        return TEMPLATE % tuple(values)

class Cities(dict):
    """
    Class for representing a group of C{City} objects
    """

    def __init__(self, data=None):
        """
        Initialise a new C{Cities} object
        """
        dict.__init__(self)
        if data:
            self.import_cities_file(data)

    def import_cities_file(self, data):
        """
        Parse GNU miscfiles cities data files

        C{import_cities_file()} returns a dictionary with keys containing the
        WMO numeric identifer, and values consisting of
        a C{trigpoints.Trigpoint} object and a heap of other data from the U{GNU
        miscfiles <http://www.gnu.org/directory/miscfiles.html>} cities data
        file.

        It expects data files in the same format that GNU miscfiles provided,
        that is::

            ID          : 1
            Type        : City
            Population  : 210700
            Size        :
            Name        : Aberdeen
             Country    : UK
             Region     : Scotland
            Location    : Earth
             Longitude  : -2.083
             Latitude   :   57.150
             Elevation  :
            Date        : 19961206
            Entered-By  : Rob.Hooft@EMBL-Heidelberg.DE
            //
            ID          : 2
            Type        : City
            Population  : 1950000
            Size        :
            Name        : Abidjan
             Country    : Ivory Coast
             Region     :
            Location    : Earth
             Longitude  : -3.867
             Latitude   :    5.333
             Elevation  :
            Date        : 19961206
            Entered-By  : Rob.Hooft@EMBL-Heidelberg.DE

        When processed by C{import_cities_file()} will return C{dict} object in
        the following style::

            1: City(1, "City", 210700, None, "Aberdeen", "UK", "Scotland",
                    "Earth", -2.083, 57.15, None, (1996, 12, 6, 0, 0, 0, 4,
                    341, -1), "Rob.Hooft@EMBL-Heidelberg.DE")
            2: City(2, "City", 1950000, None, "Abidjan", "Ivory Coast", "",
                    "Earth", -3.867, 5.333, None, (1996, 12, 6, 0, 0, 0, 4,
                    341, -1), "Rob.Hooft@EMBL-Heidelberg.DE")

        >>> cities_file = open("city_data")
        >>> cities = Cities(cities_file)
        >>> for key, value in sorted(cities.items()):
        ...     print("%i - %s (%s;%s)" % (key, value.name, value.latitude,
        ...                                value.longitude))
        126 - London (51.5;-0.083)
        127 - Luxembourg (49.617;6.117)
        128 - Lyon (45.767;4.867)
        >>> cities_file.seek(0)
        >>> manual_list = cities_file.read().split("//\\n")
        >>> cities = Cities(manual_list)

        @type data: C{file}, C{list} or C{str}
        @param data: NOAA station data to read
        @rtype: C{dict}
        @return: Places with identifier and their associated C{City} objects
        @raise TypeError: Invalid value for data
        """
        if hasattr(data, "read"):
            data = data.read().split("//\n")
        elif isinstance(data, list):
            pass
        elif isinstance(data, basestring):
            data = open(data).read().split("//\n")
        else:
            raise TypeError("Unable to handle data of type `%s'" % type(data))

        for record in data:
            # We truncate after splitting because the v1.4.2 datafile contains
            # a broken separator between 229 and 230 that would otherwise break
            # the import
            entry = [i.split(":")[1].strip() for i in record.splitlines()[:13]]
            for i in (0, 2, 3, 10):
                # Entry for Utrecht has the incorrect value of 0.000 for
                # elevation.
                if i == 10 and entry[i] == "0.000":
                    logging.debug("Ignoring `0.000' value for elevation in "
                                  "`%s' entry" % record)
                    entry[i] = ""
                entry[i] = int(entry[i]) if not entry[i] == "" else None
            for i in (8, 9):
                entry[i] = float(entry[i]) if not entry[i] == "" else None
            entry[11] = time.strptime(entry[11], "%Y%m%d")
            # Reorder elements to match required format
            entry = [entry[i] for i in (0, 4, 1, 6, 5, 7, 2, 3, 9, 8, 10, 11, 12)]
            self[entry[0]] = City(*entry)

