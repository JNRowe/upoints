#! /usr/bin/python -tt
# coding=utf-8
"""edist - Simple command line coordinate processing"""
# Copyright (C) 2006-2012  James Rowe <jnrowe@gmail.com>
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

from upoints import (__version__, __author__)


__doc__ += """.

edist operates on one, or more, locations specified in the following format
``[+-]DD.DD;[+-]DDD.DD``.  For example, a location string of ``52.015;-0.221``
would be interpreted as 52.015 degrees North by 0.221 degrees West.  Positive
values can be specified with a ``+`` prefix, but it isn't required.

For example::

    $ ./edist.py --sunrise --sunset --ascii '52.015;-0.221'
    $ ./edist.py --destination 20@45 -- '-52.015;0.221'

In the second example the locations are separated by ``--``, which stops
processing options and allows you to specify locations beginning with
a hyphen(such as anywhere in the Southern hemisphere).

.. note::
   In most shells the locations must be quoted because of the special nature of
   the semicolon.

.. currentmodule:: edist
.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].replace('``', "'").splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("edist", "%prog")

import ConfigParser
import logging
import optparse
import os
import sys

from operator import itemgetter

from upoints import (point, utils)


class LocationsError(ValueError):
    """Error object for data parsing error.

    .. versionadded:: 0.6.0

    .. attribute:: function

       Function where error is raised.

    .. attribute:: data

       Location number and data

    """
    def __init__(self, function=None, data=None):
        """Initialise a new ``LocationsError`` object.

        :param str function: Function where error is raised
        :param tuple data: Location number and data

        """
        super(LocationsError, self).__init__()
        self.function = function
        self.data = data

    def __str__(self):
        """Pretty printed error string.

        :rtype: ``str``
        :return: Human readable error string

        """
        if self.function:
            return "More than one location is required for %s." % self.function
        elif self.data:
            return "Location parsing failure in location %i `%s'." % self.data
        else:
            return "Invalid location data."


class NumberedPoint(point.Point):
    """Class for representing locations from command line.

    .. seealso::

       :class:`upoints.point.Point`.

    .. versionadded:: 0.6.0

    .. attribute:: name

       A name for location, or its position on the command line

    .. attribute:: units

       Unit type to be used for distances

    """

    __slots__ = ("name")

    def __init__(self, latitude, longitude, name, units="km"):
        """Initialise a new ``NumberedPoint`` object.

        :param float latitude: Location's latitude
        :param float longitude: Location's longitude
        :param str name: Location's name or command line position
        :param str units: Unit type to be used for distances

        """
        super(NumberedPoint, self).__init__(latitude, longitude, units)

        self.name = name


class NumberedPoints(point.Points):
    """Class for representing a group of :class:`NumberedPoint` objects.

    .. versionadded:: 0.6.0

    """

    def __init__(self, locations=None, format="dd", unistr=True,
                 verbose=True, config_locations=None, units="km"):
        """Initialise a new ``NumberedPoints`` object.

        :type locations: ``list`` of ``str`` objects
        :param locations: Location identifiers
        :param str format: Coordinate formatting system to use
        :param bool unistr: Whether to output Unicode results
        :param bool verbose: Whether to generate verbose output
        :param dict config_locations: Locations imported from user's config
            file
        :param str units: Unit type to be used for distances

        """
        super(NumberedPoints, self).__init__()
        self.format = format
        self._unistr = unistr
        if unistr:
            self.stringify = lambda p: p.__unicode__(format)
        else:
            self.stringify = lambda p: p.__str__(format)
        self.verbose = verbose
        self._config_locations = config_locations
        self.units = units
        if locations:
            self.import_locations(locations, config_locations)

    def __repr__(self):
        """Self-documenting string representation.

        :rtype: ``str``
        :return: String to recreate ``NumberedPoints`` object

        """
        return utils.repr_assist(self, {"locations": self[:]})

    def import_locations(self, locations, config_locations):
        """Import locations from arguments.

        :type locations: ``list`` of ``str``
        :param locations: Location identifiers
        :param dict config_locations: Locations imported from user's config
            file

        """
        for number, location in enumerate(locations):
            if config_locations and location in config_locations:
                latitude, longitude = config_locations[location]
                self.append(NumberedPoint(latitude, longitude, location,
                                          self.units))
            else:
                try:
                    data = utils.parse_location(location)
                    if data:
                        latitude, longitude = data
                    else:
                        latitude, longitude = utils.from_grid_locator(location)
                    self.append(NumberedPoint(latitude, longitude, number + 1,
                                              self.units))
                except ValueError:
                    raise LocationsError(data=(number, location))

    def display(self, locator):
        """Pretty print locations.

        :param str locator: Accuracy of Maidenhead locator output

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

    def distance(self):
        """Calculate distances between locations.

        """
        distances = list(super(NumberedPoints, self).distance())
        leg_msg = ["Location %s to %s is %i", ]
        total_msg = ["Total distance is %i", ]
        if self.units == "sm":
            leg_msg.append("miles")
            total_msg.append("miles")
        elif self.units == "nm":
            leg_msg.append("nautical miles")
            total_msg.append("nautical miles")
        else:
            leg_msg.append("kilometres")
            total_msg.append("kilometres")
        if self.verbose:
            for number, distance in enumerate(distances):
                print(" ".join(leg_msg) % (self[number].name,
                                           self[number + 1].name,
                                           distance))
            if len(distances) > 1:
                print(" ".join(total_msg) % sum(distances))
        else:
            print(sum(distances))

    def bearing(self, mode, string):
        """Calculate bearing/final bearing between locations.

        :param str mode: Type of bearing to calculate
        :param bool string: Use named directions

        """
        bearings = getattr(super(NumberedPoints, self), mode)()
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
                print(verbose_fmt % (self[number].name, self[number + 1].name,
                                     bearing))
            else:
                print(bearing)

    def range(self, distance):
        """Test whether locations are within a given range of the first.

        :param float distance: Distance to test location is within

        """
        test_location = self[0]
        for location in self[1:]:
            in_range = test_location.__eq__(location, distance)
            if self.verbose:
                text = ["Location %s is", ]
                if not in_range:
                    text.append("not")
                text.append("within %i ")
                if self.units == "sm":
                    text.append("miles")
                elif self.units == "nm":
                    text.append("nautical miles")
                else:
                    text.append("kilometres")
                text.append(" of location %s")
                print(" ".join(text) % (location.name, distance, self[0].name))
            else:
                print(in_range)

    def destination(self, options, locator):
        """Calculate destination locations for given distance and bearings.

        :param tuple options: Distance and bearing
        :param str locator: Accuracy of Maidenhead locator output

        """
        distance, bearing = options
        destinations = super(NumberedPoints, self).destination(bearing,
                                                               distance)
        for location, destination in zip(self, destinations):
            if self.format == "locator":
                output = destination.to_grid_locator(locator)
            else:
                output = self.stringify(destination)
            if self.verbose:
                print("Destination from location %s is %s" % (location.name,
                                                              output))
            else:
                print(output)

    def sun_events(self, mode):
        """Calculate sunrise/sunset times for locations.

        :param str mode: Sun event to display

        """
        mode_str = mode.capitalize()
        times = getattr(super(NumberedPoints, self), mode)()
        for location, time in zip(self, times):
            if self.verbose:
                if time:
                    print("%s at %s UTC in location %s" % (mode_str, time,
                                                           location.name))
                else:
                    print("The sun doesn't %s at location %s on this date"
                          % (mode_str[3:], location.name))
            else:
                print(time)

    def flight_plan(self, speed, time):
        """Output the flight plan corresponding to the given locations.

        .. todo:: Description

        :param float speed: Speed to use for elapsed time calculation
        :param str time: Time unit to use for output

        """
        if len(self) == 1:
            raise LocationsError("flight_plan")
        if self.verbose:
            print("WAYPOINT,BEARING[°],DISTANCE[%s],ELAPSED_TIME[%s],"
                  "LATITUDE[d.dd],LONGITUDE[d.dd]" % (self.units, time))
        legs = [(0, 0), ] + list(self.inverse())
        for leg, loc in zip(legs, self):
            if leg == (0, 0):
                print("%s,,,,%f,%f" % (loc.name, loc.latitude, loc.longitude))
            else:
                leg_speed = "%.1f" % (leg[1] / speed) if speed != 0 else ""
                print("%s,%i,%.1f,%s,%f,%f"
                      % (loc.name, leg[0], leg[1], leg_speed, loc.latitude,
                         loc.longitude))
        if self.verbose:
            overall_distance = sum(map(itemgetter(1), legs))
            direct_distance = self[0].distance(self[-1])
            if speed == 0:
                speed_marker = "#"
                overall_speed = ""
                direct_speed = ""
            else:
                speed_marker = ""
                overall_speed = "%.1f" % (overall_distance / speed)
                direct_speed = "%.1f" % (direct_distance / speed)
            print("-- OVERALL --%s,,%.1f,%s,,"
                  % (speed_marker, overall_distance, overall_speed))
            print("-- DIRECT --%s,%i,%.1f,%s,,"
                  % (speed_marker, self[0].bearing(self[-1]), direct_distance,
                     direct_speed))


def process_command_line():
    """Main command line interface.

    :rtype: ``tuple`` of ``list``, ``dict`` and ``list``
    :return: Modes, options, list of locations as ``str`` objects

    """
    parser = optparse.OptionParser(usage="%prog [options...] <location>...",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(config_file=os.path.expanduser("~/.edist.conf"),
                        speed=0, format="dms", locator="subsquare",
                        verbose=True, units="km", time="h")

    parser.add_option("--config-file", action="store",
                      metavar=os.path.expanduser("~/.edist.conf"),
                      help="Config file to read custom locations from")
    parser.add_option("--csv-file", action="store",
                      help="CSV file (gpsbabel format) to read " \
                           "route/locations from ('-' for STDIN)")

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
    mode_opts.add_option("-F", "--flight-plan", action="store_true",
                         help="calculate the flight plan corresponding to " \
                              "locations (route)")
    mode_opts.add_option("-S", "--speed", type="float",
                         help="speed to calculate elapsed time")

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
                           choices=("km", "sm", "nm"), metavar="km",
                           help="display distances in kilometres(default), " \
                                "statute miles or nautical miles")
    output_opts.add_option("-t", "--time",
                           choices=("h", "m", "s"), metavar="h",
                           help="display time in hours(default), minutes or " \
                                "seconds")

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

    modes = []
    for mode in ("display", "distance", "bearing", "final_bearing",
                 "flight_plan", "range", "destination", "sunrise", "sunset"):
        if getattr(options, mode):
            modes.append(mode)

    return modes, options, args


def read_locations(filename):
    """Pull locations from a user's config file.

    :param str filename: Config file to parse
    :rtype: ``dict``
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


def read_csv(filename):
    """Pull locations from a user's CSV file.

    Read gpsbabel_'s CSV output format

    .. _gpsbabel: http://www.gpsbabel.org/

    :param str filename: CSV file to parse (STDIN if '-')
    :rtype: ``tuple`` of ``dict`` and ``list``
    :return: List of locations as ``str`` objects

    """
    if filename == "-":
        filename = sys.stdin
    field_names = ("latitude", "longitude", "name")
    data = utils.prepare_csv_read(filename, field_names, skipinitialspace=True)
    index = 0
    locations = {}
    args = []
    for row in data:
        index += 1
        name = "%02i:%s" % (index, row['name'])
        locations[name] = (row['latitude'], row['longitude'])
        args.append(name)
    return locations, args


def main():
    """Main script handler.

    :rtype: ``int``
    :return: 0 for success, >1 error code

    """
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')

    modes, options, args = process_command_line()

    if not options.unicode and not options.ascii:
        logging.debug("Neither ASCII nor Unicode is set, guessing")
        if "utf8" in os.getenv("LC_ALL", "").lower().replace("-", ""):
            options.unicode = True
            logging.debug("Setting output to Unicode")
        else:
            options.unicode = False
            logging.debug("Setting output to ASCII")

    if options.csv_file:
        config_locations, args = read_csv(options.csv_file)
    else:
        config_locations = read_locations(options.config_file)

    if len(args) == 0:
        print("No locations specified!")
        sys.exit(1)

    locations = NumberedPoints(args, options.format, options.unicode,
                               options.verbose, config_locations,
                               options.units)

    if len(modes) > 1:
        logging.warning("Output order for multiple modes is not guaranteed "
                        "to remain stable across future versions")

    for mode in modes:
        if mode == "display":
            locations.display(options.locator)
        elif mode == "distance":
            locations.distance()
        elif mode in ("bearing", "final_bearing"):
            locations.bearing(mode, options.string)
        elif mode in ("flight_plan"):
            locations.flight_plan(options.speed, options.time)
        elif mode == "range":
            locations.range(options.range)
        elif mode == "destination":
            locations.destination(options.destination, options.locator)
        elif mode in ("sunrise", "sunset"):
            locations.sun_events(mode)

if __name__ == '__main__':
    sys.exit(main())
