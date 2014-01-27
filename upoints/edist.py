#
# coding=utf-8
"""edist - Simple command line coordinate processing"""
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


from email.utils import parseaddr

from upoints import (__version__, __author__)
from upoints.compat import mangle_repr_type


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
USAGE = '\n'.join(USAGE).replace('edist', '%(prog)s')

import logging
import os
import sys

from operator import itemgetter

import aaargh

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


from upoints import (point, utils)


# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = '\n'.join(USAGE).replace('edist', '%(prog)s')

EPILOG = 'Please report bugs at https://github.com/JNRowe/upoints/'

APP = aaargh.App(description=USAGE, epilog=EPILOG)


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
            return 'More than one location is required for %s.' % self.function
        elif self.data:
            return 'Location parsing failure in location %i %r.' % self.data
        else:
            return 'Invalid location data.'


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

    __slots__ = ('name')

    def __init__(self, latitude, longitude, name, units='km'):
        """Initialise a new ``NumberedPoint`` object.

        :param float latitude: Location's latitude
        :param float longitude: Location's longitude
        :param str name: Location's name or command line position
        :param str units: Unit type to be used for distances

        """
        super(NumberedPoint, self).__init__(latitude, longitude, units)

        self.name = name

    def __format__(self, format_spec='dd'):
        """Extended pretty printing for location strings.

        :param str format_spec: Coordinate formatting system to use
        :rtype: ``str``
        :return: Human readable string representation of ``NumberedPoint``
            object
        :raise ValueError: Unknown value for ``format_spec``

        """
        return super(NumberedPoint, self).__format__('dm')


@mangle_repr_type
class NumberedPoints(point.Points):
    """Class for representing a group of :class:`NumberedPoint` objects.

    .. versionadded:: 0.6.0

    """

    def __init__(self, locations=None, format='dd', verbose=True,
                 config_locations=None, units='km'):
        """Initialise a new ``NumberedPoints`` object.

        :type locations: ``list`` of ``str`` objects
        :param locations: Location identifiers
        :param str format: Coordinate formatting system to use
        :param bool verbose: Whether to generate verbose output
        :param dict config_locations: Locations imported from user's config
            file
        :param str units: Unit type to be used for distances

        """
        super(NumberedPoints, self).__init__()
        self.format = format
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
        return utils.repr_assist(self, {'locations': self[:]})

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
            if self.format == 'locator':
                output = location.to_grid_locator(locator)
            else:
                output = format(location, self.format)
            if self.verbose:
                print('Location %s is %s' % (location.name, output))
            else:
                print(output)

    def distance(self):
        """Calculate distances between locations.

        """
        distances = list(super(NumberedPoints, self).distance())
        leg_msg = ['Location %s to %s is %i', ]
        total_msg = ['Total distance is %i', ]
        if self.units == 'sm':
            leg_msg.append('miles')
            total_msg.append('miles')
        elif self.units == 'nm':
            leg_msg.append('nautical miles')
            total_msg.append('nautical miles')
        else:
            leg_msg.append('kilometres')
            total_msg.append('kilometres')
        if self.verbose:
            for number, distance in enumerate(distances):
                print(' '.join(leg_msg) % (self[number].name,
                                           self[number + 1].name,
                                           distance))
            if len(distances) > 1:
                print(' '.join(total_msg) % sum(distances))
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
            bearings = ['%i°' % bearing for bearing in bearings]
        if mode == 'bearing':
            verbose_fmt = 'Location %s to %s is %s'
        else:
            verbose_fmt = 'Final bearing from location %s to %s is %s'
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
                text = ['Location %s is', ]
                if not in_range:
                    text.append('not')
                text.append('within %i')
                if self.units == 'sm':
                    text.append('miles')
                elif self.units == 'nm':
                    text.append('nautical miles')
                else:
                    text.append('kilometres')
                text.append('of location %s')
                print(' '.join(text) % (location.name, distance, self[0].name))
            else:
                print(in_range)

    def destination(self, distance, bearing, locator):
        """Calculate destination locations for given distance and bearings.

        :param float distance: Distance to travel
        :param float bearing: Direction of travel
        :param str locator: Accuracy of Maidenhead locator output

        """
        destinations = super(NumberedPoints, self).destination(bearing,
                                                               distance)
        for location, destination in zip(self, destinations):
            if self.format == 'locator':
                output = destination.to_grid_locator(locator)
            else:
                output = format(location, self.format)
            if self.verbose:
                print('Destination from location %s is %s' % (location.name,
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
                    print('%s at %s UTC in location %s' % (mode_str, time,
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
            raise LocationsError('flight_plan')
        if self.verbose:
            print('WAYPOINT,BEARING[°],DISTANCE[%s],ELAPSED_TIME[%s],'
                  'LATITUDE[d.dd],LONGITUDE[d.dd]' % (self.units, time))
        legs = [(0, 0), ] + list(self.inverse())
        for leg, loc in zip(legs, self):
            if leg == (0, 0):
                print('%s,,,,%f,%f' % (loc.name, loc.latitude, loc.longitude))
            else:
                leg_speed = '%.1f' % (leg[1] / speed) if speed != 0 else ''
                print('%s,%i,%.1f,%s,%f,%f'
                      % (loc.name, leg[0], leg[1], leg_speed, loc.latitude,
                         loc.longitude))
        if self.verbose:
            overall_distance = sum(map(itemgetter(1), legs))
            direct_distance = self[0].distance(self[-1])
            if speed == 0:
                speed_marker = '#'
                overall_speed = ''
                direct_speed = ''
            else:
                speed_marker = ''
                overall_speed = '%.1f' % (overall_distance / speed)
                direct_speed = '%.1f' % (direct_distance / speed)
            print('-- OVERALL --%s,,%.1f,%s,,'
                  % (speed_marker, overall_distance, overall_speed))
            print('-- DIRECT --%s,%i,%.1f,%s,,'
                  % (speed_marker, self[0].bearing(self[-1]), direct_distance,
                     direct_speed))


@APP.cmd(help='pretty print the location(s)')
@APP.cmd_arg('-l', '--locator', choices=('square', 'subsquare', 'extsquare'),
             default='subsquare',
             help='accuracy of Maidenhead locator output')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def display(args):
    args.locations.display(args.locator)


@APP.cmd(help='calculate the distance between locations')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def distance(args):
    args.locations.distance()


@APP.cmd(help='calculate the initial bearing between locations')
@APP.cmd_arg('-g', '--string', action='store_true',
             help='display named bearings')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def bearing(args):
    args.locations.bearing('bearing', args.string)


@APP.cmd(name='final-bearing',
         help='calculate the final bearing between locations')
@APP.cmd_arg('-g', '--string', action='store_true',
             help='display named bearings')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def final_bearing(args):
    args.locations.bearing('final_bearing', args.string)


@APP.cmd(help='calculate whether locations are within a given range')
@APP.cmd_arg('-d', '--distance', type=float, help='range radius')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def range(args):
    args.locations.range(args.distance)


@APP.cmd(help='calculate the destination for a given distance and bearing')
@APP.cmd_arg('-l', '--locator', choices=('square', 'subsquare', 'extsquare'),
             default='subsquare',
             help='accuracy of Maidenhead locator output')
@APP.cmd_arg('-d', '--distance', required=True, type=float,
             help='distance from start point')
@APP.cmd_arg('-b', '--bearing', required=True, type=float,
             help='bearing from start point')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def destination(args):
    args.locations.destination(args.distance, args.bearing, args.locator)


@APP.cmd(help='calculate the sunrise time for a given location')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def sunrise(args):
    args.locations.sun_events('sunrise')


@APP.cmd(help='calculate the sunset time for a given location')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def sunset(args):
    args.locations.sun_events('sunset')


@APP.cmd(name='flight-plan',
         help='calculate the flight plan corresponding to locations (route)')
@APP.cmd_arg('-s', '--speed', default=0, type=float,
             help='speed to calculate elapsed time')
@APP.cmd_arg('-t', '--time', choices=('h', 'm', 's'),
             help='display time in hours, minutes or seconds')
@APP.cmd_arg('location', nargs='+', help='Locations to operate on')
def flight_plan(args):
    args.locations.flight_plan(args.speed, args.time)


def read_locations(filename):
    """Pull locations from a user's config file.

    :param str filename: Config file to parse
    :rtype: ``dict``
    :return: List of locations from config file

    """
    data = ConfigParser()
    data.read(filename)
    if not data.sections():
        logging.debug('Config file %r is empty' % filename)
        return {}

    locations = {}
    for name in data.sections():
        if data.has_option(name, 'locator'):
            latitude, longitude = utils.from_grid_locator(data.get(name,
                                                                   'locator'))
        else:
            latitude = data.getfloat(name, 'latitude')
            longitude = data.getfloat(name, 'longitude')
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
    if filename == '-':
        filename = sys.stdin
    field_names = ('latitude', 'longitude', 'name')
    data = utils.prepare_csv_read(filename, field_names, skipinitialspace=True)
    index = 0
    locations = {}
    args = []
    for row in data:
        index += 1
        name = '%02i:%s' % (index, row['name'])
        locations[name] = (row['latitude'], row['longitude'])
        args.append(name)
    return locations, args


def main():
    """Main script handler.

    :rtype: ``int``
    :return: 0 for success, >1 error code

    """
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')

    APP.arg('--version', action='version',
            version='%%(prog)s v%s' % __version__)

    APP.arg('-v', '--verbose', action='store_true', dest='verbose',
            default=True,
            help='produce verbose output')
    APP.arg('-q', '--quiet', action='store_false', dest='verbose',
            help='output only results and errors')

    APP.arg('--config-file', metavar='~/.edist.conf',
            default=os.path.expanduser('~/.edist.conf'),
            help='config file to read custom locations from')
    APP.arg('--csv-file',
            help='CSV file (gpsbabel format) to read route/locations from '
                 "('-' for STDIN)")

    APP.arg('-o', '--format', choices=('dms', 'dm', 'dd', 'locator'),
            default='dms',
            help='produce output in dms, dm, d format or Maidenhead locator')
    APP.arg('-g', '--string', action='store_true',
            help='display named bearings')
    APP.arg('-u', '--units', choices=('km', 'sm', 'nm'), metavar='km',
            default='km',
            help='display distances in kilometres(default), statute miles or '
                 'nautical miles')
    APP.arg('-t', '--time', choices=('h', 'm', 's'), metavar='h', default='h',
            help='display time in hours(default), minutes or seconds')

    args = APP._parser.parse_args()
    func = args._func

    if args.csv_file:
        config_locations, args.location = read_csv(args.csv_file)
    else:
        config_locations = read_locations(args.config_file)

    try:
        args.locations = NumberedPoints(args.location, args.format,
                                        args.verbose, config_locations,
                                        args.units)
    except LocationsError as error:
        APP._parser.error(error)

    try:
        return func(args)
    except RuntimeError as error:
        APP._parser.error(error)
