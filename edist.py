#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""edist - Simple command line coordinate processing"""
# Copyright (C) 2007-2008  James Rowe;
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

from email.utils import parseaddr

from earth_distance import (__version__, __author__, __copyright__, __license__)

__doc__ += """.

edist operates on one, or more, locations specified in the following format
``[+-]DD.DD;[+-]DDD.DD``.  For example, a location string of ``52.015;-0.221``
would be interpreted as 52.015 degrees North by 0.221 degrees West.  Positive
values can be specified with a ``+`` prefix, but it isn't required.

For example::

    $ ./edist.py --sunrise --sunset --ascii '52.015;-0.221'
    $ ./edist.py --destination 20@45 -- '-52.015;0.221'

In the second example the locations are separated by '--', which stops
processing options and allows you to specify locations beginning with
a hyphen(such as anywhere in the Southern hemisphere).

:note: In most shells the locations must be quoted because of the special
    nature of the semicolon.

:version: %s
:author: `%s <mailto:%s>`__
:copyright: %s
:status: WIP
:license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("edist", "%prog")

import ConfigParser
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
    >>> raise LocationsError(data=(4, "52;None"))
    Traceback (most recent call last):
        ...
    LocationsError: Location parsing failure in location 4 `52;None'.

    :since: 0.6.0

    :Ivariables:
        function
            Function where error is raised.
    """
    def __init__(self, function=None, data=None):
        """
        Initialise a new `LocationsError` object

        :Parameters:
            function : `str`
                Function where error is raised
            data : `tuple`
                Location number and data
        """
        super(LocationsError, self).__init__()
        self.function = function
        self.data = data

    def __str__(self):
        """
        Pretty printed error string

        :rtype: `str`
        :return: Human readable error string
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

    :since: 0.6.0

    :Ivariables:
        name
            A name for location, or its position on the command line
    """

    __slots__ = ("name")

    def __init__(self, latitude, longitude, name):
        """
        Initialise a new `NumberedPoint` object

        >>> NumberedPoint(52.015, -0.221, 4)
        NumberedPoint(52.015, -0.221, 4)
        >>> NumberedPoint(52.015, -0.221, "Home")
        NumberedPoint(52.015, -0.221, 'Home')

        :Parameters:
            latitude : `float` or coercible to `float`
                Location's latitude
            longitude : `float` or coercible to `float`
                Location's longitude
            name : `str`
                Location's name or command line position
        """
        super(NumberedPoint, self).__init__(latitude, longitude)

        self.name = name

    def destination(self, bearing, distance):
        """
        Calculate the destination from self given bearing and distance

        :see: `point.Point.destination`

        >>> NumberedPoint(52.015, -0.221, 1).destination(294, 169)
        Point(52.6116387502, -2.50937408195, 'metric', 'degrees', 0)

        :Parameters:
            bearing : `float` or coercible to `float`
                Bearing from self
            distance : `float` or coercible to `float`
                Distance from self in `self.format` type units
        :rtype: `Point`
        :return: Location after travelling `distance` along `bearing`
        """
        dest = super(NumberedPoint, self).destination(bearing, distance)
        return point.Point(dest.latitude, dest.longitude)


class NumberedPoints(list):
    """
    Class for representing a group of `NumberedPoint` objects

    :since: 2008-01-08
    """

    def __init__(self, locations=None, format="dd", unistr=True,
                 verbose=True, config_locations=None):
        """
        Initialise a new `NumberedPoints` object

        :Parameters:
            locations : `list` of `str` objects
                Location identifiers
            format : `str`
                Coordinate formatting system to use
            unistr : `bool`
                Whether to output Unicode results
            verbose : `bool`
                Whether to generate verbose output
            config_locations : `dict`
                Locations imported from user's config file
        """
        super(NumberedPoints, self).__init__()
        if locations:
            self.import_locations(locations, config_locations)
        self.format = format
        self._unistr = unistr
        if unistr:
            self.stringify = lambda p: p.__unicode__(format)
        else:
            self.stringify = lambda p: p.__str__(format)
        self.verbose = verbose
        self._config_locations = config_locations

    def __repr__(self):
        """
        Self-documenting string representation

        >>> locations = ["0;0"] * 4
        >>> NumberedPoints(locations)
        NumberedPoints([NumberedPoint(0.0, 0.0, 1), NumberedPoint(0.0, 0.0, 2),
                        NumberedPoint(0.0, 0.0, 3), NumberedPoint(0.0, 0.0, 4)],
                       'dd', True, True, None)

        :rtype: `str`
        :return: String to recreate `NumberedPoints` object
        """
        return utils.repr_assist(self, {"locations": self[:]})

    def import_locations(self, locations, config_locations):
        """
        Import locations from arguments

        >>> NumberedPoints(["0;0", "Home", "0;0"],
        ...                config_locations={"Home": (52.015, -0.221)})
        NumberedPoints([NumberedPoint(0.0, 0.0, 1), NumberedPoint(52.015, -0.221, 'Home'),
                        NumberedPoint(0.0, 0.0, 3)],
                       'dd', True, True, {'Home': (52.015000000000001, -0.221)})

        :Parameters:
            locations : `list` of `str`
                Location identifiers
            config_locations : `dict`
                Locations imported from user's config file
        """
        for number, location in enumerate(locations):
            if config_locations and location in config_locations:
                latitude, longitude = config_locations[location]
                self.append(NumberedPoint(latitude, longitude, location))
            else:
                try:
                    data = utils.parse_location(location)
                    if data:
                        latitude, longitude = data
                    else:
                        latitude, longitude = utils.from_grid_locator(location)
                    self.append(NumberedPoint(latitude, longitude, number+1))
                except ValueError:
                    raise LocationsError(data=(number, location))

    def display(self, locator):
        """
        Pretty print locations

        >>> locations = NumberedPoints(["Home", "52.168;0.040"],
        ...                            config_locations={"Home": (52.015, -0.221)})
        >>> locations.display(None)
        Location Home is N52.015°; W000.221°
        Location 2 is N52.168°; E000.040°
        >>> locations.format = "locator"
        >>> locations.display("extsquare")
        Location Home is IO92va33
        Location 2 is JO02ae40
        >>> locations.verbose = False
        >>> locations.display("extsquare")
        IO92va33
        JO02ae40

        :Parameters:
            locator : `str`
                Accuracy of Maidenhead locator output
        """
        for location in self:
            if self.format == "locator":
                output = location.to_grid_locator(locator)
            else:
                output = self.stringify(location)
            if self.verbose:
                print("Location %s is %s" % (location.name, output))
            else:
                print(output)

    def distance(self, unit):
        """
        Calculate distances between locations

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.distance("km")
        Location 1 to 2 is 24 kilometres
        >>> locations.distance("mile")
        Location 1 to 2 is 15 miles
        >>> locations.verbose = False
        >>> locations.distance("nautical")
        13.2989574317
        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040",
        ...                             "51.420;-1.500"])
        >>> locations.distance("km")
        Location 1 to 2 is 24 kilometres
        Location 2 to 3 is 134 kilometres
        Total distance is 159 kilometres

        :Parameters:
            unit : `str`
                Distance unit to use for output
        """
        if len(self) == 1:
            raise LocationsError("distance")
        distances = [self[i].distance(self[i+1]) for i in range(len(self)-1)]
        leg_msg = ["Location %s to %s is %i", ]
        total_msg = ["Total distance is %i", ]
        if unit == "mile":
            distances = [i / utils.STATUTE_MILE for i in distances]
            leg_msg.append("miles")
            total_msg.append("miles")
        elif unit == "nautical":
            distances = [i / utils.NAUTICAL_MILE for i in distances]
            leg_msg.append("nautical miles")
            total_msg.append("nautical miles")
        else:
            leg_msg.append("kilometres")
            total_msg.append("kilometres")
        if self.verbose:
            for number, distance in enumerate(distances):
                print(" ".join(leg_msg) % (self[number].name,
                                           self[number+1].name,
                                           distance))
            if len(distances) > 1:
                print(" ".join(total_msg) % sum(distances))
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

        :Parameters:
            mode : `str`
                Type of bearing to calculate
            string : `bool`
                Use named directions
        """
        if len(self) == 1:
            raise LocationsError(mode)
        bearing_calc = lambda x: getattr(self[x], mode)(self[x+1])
        bearings = map(bearing_calc, range(len(self)-1))
        if string:
            bearings = map(utils.angle_to_name, bearings)
        else:
            bearings = ["%i°" % bearing for bearing in bearings]
        if mode == "bearing":
            verbose_fmt = "Location %s to %s is %s"
        else:
            verbose_fmt = "Final bearing from location %s to %s is %s"
        for number, bearing in enumerate(bearings):
            if self.verbose:
                print(verbose_fmt % (self[number].name, self[number+1].name,
                                     bearing))
            else:
                print(bearing)

    def range(self, distance):
        """
        Test whether locations are within a given range of the first

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.range(20)
        Location 2 is not within 20 kilometres of location 1
        >>> locations.range(30)
        Location 2 is within 30 kilometres of location 1
        >>> locations.verbose = False
        >>> locations.range(30)
        True

        :Parameters:
            distance : `float`
                Distance to test location is within
        """
        if len(self) == 1:
            raise LocationsError("range")
        test_location = self[0]
        for location in self[1:]:
            in_range = test_location.__eq__(location, distance)
            if self.verbose:
                text = ["Location %s is", ]
                if not in_range:
                    text.append("not")
                text.append("within %i kilometres of location %s")
                print(" ".join(text) % (location.name, distance, self[0].name))
            else:
                print(in_range)

    def destination(self, options, locator):
        """
        Calculate destination locations for given distance and bearings

        >>> locations = NumberedPoints(["52.015;-0.221", "52.168;0.040"])
        >>> locations.destination((42, 240), False)
        Destination from location 1 is N51.825°; W000.751°
        Destination from location 2 is N51.978°; W000.491°
        >>> locations.format = "locator"
        >>> locations.destination((42, 240), "subsquare")
        Destination from location 1 is IO91ot
        Destination from location 2 is IO91sx
        >>> locations.verbose = False
        >>> locations.destination((42, 240), "extsquare")
        IO91ot97
        IO91sx14

        :Parameters:
            options : `tuple`
                Distance and bearing
            locator : `str`
                Accuracy of Maidenhead locator output
        """
        distance, bearing = options
        dest_calc = lambda location: location.destination(bearing, distance)
        for location, destination in [(i, dest_calc(i)) for i in self]:
            if self.format == "locator":
                output = destination.to_grid_locator(locator)
            else:
                output = self.stringify(destination)
            if self.verbose:
                print("Destination from location %s is %s" % (location.name, output))
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

        :Parameters:
            mode : `str`
                Sun event to display
        """
        mode_str = mode.capitalize()
        for location in self:
            time = getattr(location, mode)()
            if self.verbose:
                if time:
                    print("%s at %s UTC in location %s" % (mode_str, time, location.name))
                else:
                    print("The sun doesn't %s at location %s on this date"
                          % (mode_str[3:], location.name))
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

    :rtype: `tuple` of `list`, `dict` and `list`
    :return: Modes, options, list of locations as `str` objects
    """
    parser = optparse.OptionParser(usage="%prog [options...] <location>...",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(config_file=os.path.expanduser("~/.edist.conf"),
                        format="dms", locator="subsquare", verbose=True,
                        units="km")

    parser.add_option("--config-file", action="store",
                      metavar=os.path.expanduser("~/.edist.conf"),
                      help="Config file to read custom locations from")

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

def read_locations(filename):
    """
    Pull locations from a user's config file

    :Parameters:
        filename : `str`
            Config file to parse
    :rtype: `dict`
    :return: List of locations from config file
    """
    data = ConfigParser.ConfigParser()
    data.read(filename)
    if not data.sections():
        logging.debug("Config file `%s' is empty" % filename)
        return {}

    locations = {}
    for name in data.sections():
        if data.has_option(name, "locator"):
            latitude, longitude = utils.from_grid_locator(data.get(name,
                                                                   "locator"))
        else:
            latitude = data.getfloat(name, "latitude")
            longitude = data.getfloat(name, "longitude")
        locations[name] = (latitude, longitude)
    return locations

def main():
    """
    Main script handler

    :rtype: `int`
    :return: 0 for success, >1 error code
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

    config_locations = read_locations(options.config_file)

    locations = NumberedPoints(args, options.format, options.unicode,
                               options.verbose, config_locations)

    if len(modes) > 1:
        logging.warning("Output order for multiple modes is not guaranteed "
                        "to remain stable across future versions")

    for mode in modes:
        if mode == "display":
            locations.display(options.locator)
        elif mode == "distance":
            locations.distance(options.units)
        elif mode in ("bearing", "final_bearing"):
            locations.bearing(mode, options.string)
        elif mode == "range":
            locations.range(options.range)
        elif mode == "destination":
            locations.destination(options.destination, options.locator)
        elif mode in ("sunrise", "sunset"):
            locations.sun_events(mode)

if __name__ == '__main__':
    sys.exit(main())

