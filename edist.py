#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""edist - Simple command line coordinate conversion"""
# Copyright (C) 2007 James Rowe;
# All rights reserved.
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

from __future__ import division
from email.utils import parseaddr

from earth_distance import (__version__, __date__, __author__, __copyright__,
                            __license__, __credits__)

__doc__ += """
edist operates on one, or more, locations specified in the following format
"[+-]DD.DD;[+-]DDD.DD".  For example, a location string of "52.015;-0.221" would
be interpreted as 52.015 degrees North by 0.221 degrees West.  Positive values
can be specified with a "+" prefix, but it isn't required.

Note that in most shells the locations must be quoted because of the special
nature of the semicolon.

@version: %s
@author: U{%s <mailto:%s>}
@copyright: %s
@status: WIP
@license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

# Scrub the main header, and epydoc footer
__description__ = "\n".join(__doc__[:__doc__.find("@")-2].splitlines()[1:])
# Replace script name, with optparse's substitution var
__description__ = __description__.replace("edist", "%prog")

import logging
import optparse
import os
import sys

from earth_distance import (point, utils)

class LocationsError(ValueError):
    """
    Error object for data parsing error

    >>> raise LocationsError
    Traceback (most recent call last):
        ...
    LocationsError: Invalid location data.
    >>> raise LocationsError("distance")
    Traceback (most recent call last):
        ...
    LocationsError: More than one location is required for distance.

    @ivar function: Function where error is raised.
    """
    def __init__(self, function=None, data=None):
        """
        Initialise a new C{LocationsError} object

        @type function: C{str}
        @param function: Function where error is raised
        @type data: C{tuple}
        @param data: Location number and data
        """
        ValueError.__init__(self)
        self.function = function
        self.data = data

    def __str__(self):
        """
        Pretty printed error string

        @rtype: C{str}
        @return: Human readable error string
        """
        if self.function:
            return "More than one location is required for %s." % self.function
        elif self.data:
            return "Location parsing failure in location %i `%s'." % self.data
        else:
            return "Invalid location data."

class NumberedPoint(point.Point):
    """
    Class for representing locations from command line

    @ivar number: Location's position on command line
    """

    __slots__ = ("number", )

    def __init__(self, latitude, longitude, number):
        """
        Initialise a new C{NumberedPoint} object

        @type latitude: C{float} or coercible to C{float}
        @param latitude: Location's latitude
        @type longitude: C{float} or coercible to C{float}
        @param longitude: Location's longitude
        @type number: C{int}
        @param number: Location's position
        """
        super(NumberedPoint, self).__init__(latitude, longitude)
        self.number = number

    def __repr__(self):
        """
        Self-documenting string representation

        >>> NumberedPoint(52.015, -0.221, 4)
        NumberedPoint(52.015, -0.221, 4)

        @rtype: C{str}
        @return: String to recreate C{NumberedPoint} object
        """
        data = utils.repr_assist(self.latitude, self.longitude, self.number)
        return self.__class__.__name__ + '(' + ", ".join(data) + ')'

    def destination(self, bearing, distance):
        """
        Calculate the destination from self given bearing and distance

        @see: C{point.Point.destination}

        >>> NumberedPoint(52.015, -0.221, 1).destination(294, 169)
        NumberedPoint(52.6111880522, -2.50755435332, 1)

        @type bearing: C{float} or coercible to C{float}
        @param bearing: Bearing from self
        @type distance: C{float} or coercible to C{float}
        @param distance: Distance from self in C{self.format} type units
        @rtype: C{Point}
        @return: Location after travelling C{distance} along C{bearing}
        """
        dest = super(NumberedPoint, self).destination(bearing, distance)
        return NumberedPoint(dest.latitude, dest.longitude, self.number)

class NumberedPoints(list):
    """
    Class for representing a group of C{NumberedPoint} objects
    """

    def __init__(self, locations=None, format="dd", unistr=True,
                 verbose=True):
        """
        Initialise a new C{NumberedPoints} object

        >>> locations = ["0;0"] * 4
        >>> NumberedPoints(locations)
        [NumberedPoint(0.0, 0.0, 1), NumberedPoint(0.0, 0.0, 2),
         NumberedPoint(0.0, 0.0, 3), NumberedPoint(0.0, 0.0, 4)]

        @type locations: C{list} of C{str}
        @param locations: Location identifiers
        @type format: C{str}
        @param format: Coordinate formatting system to use
        @type unistr: C{bool}
        @param unistr: Whether to output Unicode results
        @type verbose: C{bool}
        @param verbose: Whether to generate verbose output
        """
        list.__init__(self)
        if locations:
            self.import_locations(locations)
        self.format = format
        if unistr:
            self.stringify = lambda p: p.__unicode__(format)
        else:
            self.stringify = lambda p: p.__str__(format)
        self.verbose = verbose

    def import_locations(self, locations):
        """
        Import locations from arguments

        @type locations: C{list} of C{str}
        @param locations: Location identifiers
        """
        for number, location in enumerate(locations):
            try:
                latitude, longitude = location.split(";")
                self.append(NumberedPoint(latitude, longitude, number+1))
            except ValueError:
                raise LocationsError(data=(number, location))

    def display(self, locator):
        """
        Pretty print locations

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.display(None)
        Location 1 is N52.015°; W000.221°
        Location 2 is N52.168°; E000.040°
        >>> locations.format = "locator"
        >>> locations.display("extsquare")
        Location 1 is IO92va33
        Location 2 is JO02ae40
        >>> locations.verbose = False
        >>> locations.display("extsquare")
        IO92va33
        JO02ae40

        @type locator: C{str}
        @param locator: Accuracy of Maidenhead locator output
        """
        for location in self:
            if self.format == "locator":
                output = location.to_grid_locator(locator)
            else:
                output = self.stringify(location)
            if self.verbose:
                print("Location %i is %s" % (location.number, output))
            else:
                print(output)

    def distance(self, unit):
        """
        Calculate distances between locations

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.distance("km")
        Location 1 to 2 is 24 kilometres
        Total distance is 24 kilometres
        >>> locations.distance("mile")
        Location 1 to 2 is 15 miles
        Total distance is 15 miles
        >>> locations.verbose = False
        >>> locations.distance("nautical")
        13.3094010923

        @type unit: C{str}
        @param unit: Distance unit to use for output
        """
        if len(self) == 1:
            raise LocationsError("distance")
        distances = [self[i].distance(self[i+1]) for i in range(len(self)-1)]
        leg_msg = "Location %i to %i is %i "
        total_msg = "Total distance is %i "
        if unit == "mile":
            distances = [i / utils.STATUTE_MILE for i in distances]
            leg_msg += "miles"
            total_msg += "miles"
        elif unit == "nautical":
            distances = [i / utils.NAUTICAL_MILE for i in distances]
            leg_msg += "nautical miles"
            total_msg += "nautical miles"
        else:
            leg_msg += "kilometres"
            total_msg += "kilometres"
        if self.verbose:
            for number, distance in enumerate(distances):
                print(leg_msg % (number+1, number+2, distance))
            print(total_msg % sum(distances))
        else:
            print(sum(distances))

    def bearing(self, mode, string):
        """
        Calculate bearing/final bearing between locations

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.bearing("bearing", False)
        Location 1 to 2 is 46°
        >>> locations.bearing("bearing", True)
        Location 1 to 2 is North-east
        >>> locations.bearing("final_bearing", False)
        Final bearing from location 1 to 2 is 46°
        >>> locations.bearing("final_bearing", True)
        Final bearing from location 1 to 2 is North-east
        >>> locations.verbose = False
        >>> locations.bearing("bearing", True)
        North-east
        >>> locations.verbose = False
        >>> locations.bearing("final_bearing", True)
        North-east

        @type mode: C{str}
        @param mode: Type of bearing to calculate
        @type string: C{bool}
        @param string: Use named directions
        """
        if len(self) == 1:
            raise LocationsError(mode)
        bearing_calc = lambda x: getattr(self[x], mode)(self[x+1])
        bearings = [bearing_calc(i) for i in range(len(self)-1)]
        if string:
            bearings = [utils.angle_to_name(bearing) for bearing in bearings]
        else:
            bearings = ["%i°" % bearing for bearing in bearings]
        if mode == "bearing":
            verbose_fmt = "Location %i to %i is %s"
        else:
            verbose_fmt = "Final bearing from location %i to %i is %s"
        for number, bearing in enumerate(bearings):
            if self.verbose:
                print(verbose_fmt % (number+1, number+2, bearing))
            else:
                print(bearing)

    def range(self, distance):
        """
        Test whether locations are within a given range of the first

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.range(20)
        Location 2 is not within 20 kilometres of location 3
        >>> locations.range(30)
        Location 2 is within 30 kilometres of location 3
        >>> locations.verbose = False
        >>> locations.range(30)
        True

        @type distance: C{float}
        @param distance: Distance to test location is within
        """
        if len(self) == 1:
            raise LocationsError("range")
        test_location = self[0]
        for location in self[1:]:
            in_range = test_location.__eq__(location, distance)
            if self.verbose:
                text = "Location %i is "
                if not in_range:
                    text += "not "
                text += "within %i kilometres of location %s"
                print(text % (location.number, distance, location.number+1))
            else:
                print(in_range)

    def destination(self, options, locator):
        """
        Calculate destination locations for given distance and bearings

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.destination((42, 240), False)
        Destination from location 1 is N51.825°; W000.750°
        Destination from location 2 is N51.978°; W000.491°
        >>> locations.format = "locator"
        >>> locations.destination((42, 240), "subsquare")
        Destination from location 1 is IO91ot
        Destination from location 2 is IO91sx
        >>> locations.verbose = False
        >>> locations.destination((42, 240), "extsquare")
        IO91ot97
        IO91sx14

        @type options: C{tuple}
        @param options: Distance and bearing
        @type locator: C{str}
        @param locator: Accuracy of Maidenhead locator output
        """
        distance, bearing = options
        dest_calc = lambda location: location.destination(bearing, distance)
        for location in [dest_calc(location) for location in self]:
            if self.format == "locator":
                output = location.to_grid_locator(locator)
            else:
                output = self.stringify(location)
            if self.verbose:
                print("Destination from location %i is %s" % (location.number,
                                                              output))
            else:
                print(output)

    def sun_events(self, mode):
        """
        Calculate sunrise/sunset times for locations

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.sun_events("sunrise") # doctest: +ELLIPSIS
        Sunrise at ... in location 1
        Sunrise at ... in location 2
        >>> locations.sun_events("sunset") # doctest: +ELLIPSIS
        Sunset at ... in location 1
        Sunset at ... in location 2

        @type mode: C{str}
        @param mode: Sun event to display
        """
        mode_str = mode.capitalize()
        for location in self:
            time = getattr(location, mode)()
            if self.verbose:
                print("%s at %s UTC in location %i" % (mode_str, time,
                                                       location.number))
            else:
                print(time)

def process_command_line():
    """
    Main command line interface

    >>> sys.argv[1:] = ["-p", "52.015;-0.221"]
    >>> modes, opts, args = process_command_line()
    >>> modes, args
    (['display'], ['52.015;-0.221'])
    >>> sys.argv[1:] = ["-d", "-b", "52.015;-0.221", "52.168;0.040"]
    >>> modes, opts, args = process_command_line()
    >>> modes, args
    (['distance', 'bearing'], ['52.015;-0.221', '52.168;0.040'])

    @rtype: C{tuple} of C{list}, C{dict} and C{list}
    @return: Modes, options, list of locations as C{str} objects
    """
    parser = optparse.OptionParser(usage="%prog [options...] <location>...",
                                   version="%prog v" + __version__,
                                   description=__description__)

    parser.set_defaults(format="dms", locator="subsquare", verbose=True,
                        units="km")
    mode_opts = optparse.OptionGroup(parser, "Calculation modes")
    parser.add_option_group(mode_opts)
    mode_opts.add_option("-p", "--print", action="store_true", dest="display",
                         help="pretty print the location(s)")
    mode_opts.add_option("-d", "--distance", action="store_true",
                         help="calculate the distance between locations")
    mode_opts.add_option("-b", "--bearing", action="store_true",
                         help="calculate the initial bearing between locations")
    mode_opts.add_option("-f", "--final-bearing", action="store_true",
                         help="calculate the final bearing between locations")
    mode_opts.add_option("-r", "--range", type="float", metavar="range",
                         help="calculate whether locations are within a " \
                              "given range")
    mode_opts.add_option("-s", "--destination", metavar="distance@bearing",
                         help="calculate the destination for a given " \
                              "distance and bearing")
    mode_opts.add_option("-y", "--sunrise", action="store_true",
                         help="calculate the sunrise time for a given "
                              "location")
    mode_opts.add_option("-z", "--sunset", action="store_true",
                         help="calculate the sunset time for a given location")

    output_opts = optparse.OptionGroup(parser, "Output options")
    output_opts.add_option("--unicode", action="store_true",
                           help="produce Unicode output")
    output_opts.add_option("--ascii", action="store_true",
                           help="produce ASCII output")
    output_opts.add_option("-o", "--format",
                           choices=("dms", "dm", "dd", "locator"),
                           help="produce output in dms, dm, d format or " \
                                "Maidenhead locator")
    output_opts.add_option("-l", "--locator",
                           choices=("square", "subsquare", "extsquare"),
                           help="accuracy of Maidenhead locator output")
    output_opts.add_option("-g", "--string", action="store_true",
                           help="display named bearings")
    output_opts.add_option("-v", "--verbose", action="store_true",
                           dest="verbose", help="produce verbose output")
    output_opts.add_option("-q", "--quiet", action="store_false",
                           dest="verbose",
                           help="output only results and errors")
    output_opts.add_option("-u", "--units",
                           choices=("km", "mile", "nm"), metavar="km",
                           help="display distances in km(default), mile or nm")

    parser.add_option_group(output_opts)
    options, args = parser.parse_args()

    # This could be done with a new Option subclass directly, but the cost
    # outweighs the benefit significantly
    if options.destination:
        try:
            distance, bearing = options.destination.split("@")
            distance = float(distance)
            bearing = float(bearing)
        except ValueError:
            parser.error("Invalid format for destination option!")
        options.destination = distance, bearing

    if not len(args) >= 1:
        parser.error("No locations specified!")

    modes = []
    for mode in ("display", "distance", "bearing", "final_bearing", "range",
                 "destination", "sunrise", "sunset"):
        if getattr(options, mode):
            modes.append(mode)

    return modes, options, args

def main():
    """
    Main script handler

    @rtype: C{int}
    @return: 0 for success, >1 error code
    """

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    modes, options, args = process_command_line()

    if not options.unicode and not options.ascii:
        logging.debug("Neither ASCII nor Unicode is set, guessing")
        if "utf8" in os.getenv("LC_ALL", "").lower().replace("-", ""):
            options.unicode = True
            logging.debug("Setting output to Unicode")
        else:
            options.unicode = False
            logging.debug("Setting output to ASCII")

    locations = NumberedPoints(args, options.format, options.unicode,
                               options.verbose)

    if len(modes) > 1:
        logging.warning("Output order for multiple modes is not guaranteed "
                        "to remain stable across future versions")

    for mode in modes:
        if mode == "display":
            locations.display(options.locator)
        if mode == "distance":
            locations.distance(options.units)
        if mode in ("bearing", "final_bearing"):
            locations.bearing(mode, options.string)
        if mode == "range":
            locations.range(options.range)
        if mode == "destination":
            locations.destination(options.destination, options.locator)
        if mode in ("sunrise", "sunset"):
            locations.sun_events(mode)

if __name__ == '__main__':
    sys.exit(main())

