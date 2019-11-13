#
"""edist - Simple command line coordinate processing.

edist operates on one, or more, locations specified in the following format
``[+-]DD.DD;[+-]DDD.DD``.  For example, a location string of ``52.015;-0.221``
would be interpreted as 52.015 degrees North by 0.221 degrees West.  Positive
values can be specified with a ``+`` prefix, but it isn't required.

For example::

    \b
    $ ./edist.py --location '52.015;-0.221' sunrise
    $ ./edist.py --location '52.015;0.221' destination 20 45

Note:
    In most shells the locations must be quoted because of the special nature
    of the semicolon.

"""
# Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>
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

import logging
import os
import sys

from operator import itemgetter

import click

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from . import (_version, point, utils)


class LocationsError(ValueError):
    """Error object for data parsing error.

    .. versionadded:: 0.6.0

    Attributes:
        function: Function where error is raised.
        data: Location number and data
    """

    def __init__(self, function=None, data=None):
        """Initialise a new ``LocationsError`` object.

        Args:
            function (str): Function where error is raised
            data (tuple): Location number and data
        """
        super(LocationsError, self).__init__()
        self.function = function
        self.data = data

    def __str__(self):
        """Pretty printed error string.

        Returns:
            str: Human readable error string
        """
        if self.function:
            return 'More than one location is required for %s.' % self.function
        elif self.data:
            return 'Location parsing failure in location %i %r.' % self.data
        else:
            return 'Invalid location data.'


class NumberedPoint(point.Point):
    """Class for representing locations from command line.

    See also:
       upoints.point.Point

    .. versionadded:: 0.6.0

    Attributes:
        name: A name for location, or its position on the command line
        units: Unit type to be used for distances
    """

    __slots__ = ('name', )

    def __init__(self, latitude, longitude, name, units='km'):
        """Initialise a new ``NumberedPoint`` object.

        Args:
            latitude (float): Location's latitude
            longitude (float): Location's longitude
            name (str): Location's name or command line position
            units (str): Unit type to be used for distances
        """
        super(NumberedPoint, self).__init__(latitude, longitude, units)

        self.name = name

    def __format__(self, format_spec='dd'):
        """Extended pretty printing for location strings.

        Args:
            format_spec (str): Coordinate formatting system to use

        Returns:
            str: Human readable string representation of ``NumberedPoint``
                object

        Raises:
            ValueError: Unknown value for ``format_spec``
        """
        return super(NumberedPoint, self).__format__('dm')


class NumberedPoints(point.Points):
    """Class for representing a group of :class:`NumberedPoint` objects.

    .. versionadded:: 0.6.0
    """

    def __init__(self, locations=None, format='dd', verbose=True,
                 config_locations=None, units='km'):
        """Initialise a new ``NumberedPoints`` object.

        Args:
            locations (list of str): Location identifiers
            format (str): Coordinate formatting system to use
            verbose (bool): Whether to generate verbose output
            config_locations (dict): Locations imported from user's config
                file
            units (str): Unit type to be used for distances
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

        Returns:
            str: String to recreate ``NumberedPoints`` object
        """
        return utils.repr_assist(self, {'locations': self[:]})

    def import_locations(self, locations, config_locations):
        """Import locations from arguments.

        Args:
            locations (list of str): Location identifiers
            config_locations (dict): Locations imported from user's config
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

        Args:
            locator (str): Accuracy of Maidenhead locator output
        """
        for location in self:
            if locator:
                output = location.to_grid_locator(locator)
            else:
                output = format(location, self.format)
            if self.verbose:
                click.echo('Location %s is %s' % (location.name, output))
            else:
                click.echo(output)

    def distance(self):
        """Calculate distances between locations."""
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
                click.echo(' '.join(leg_msg)
                           % (self[number].name, self[number + 1].name,
                              distance))
            if len(distances) > 1:
                click.echo(' '.join(total_msg) % sum(distances))
        else:
            click.echo(sum(distances))

    def bearing(self, mode, string):
        """Calculate bearing/final bearing between locations.

        Args:
            mode (str): Type of bearing to calculate
            string (bool): Use named directions
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
                click.echo(verbose_fmt % (self[number].name,
                                          self[number + 1].name,
                                          bearing))
            else:
                click.echo(bearing)

    def range(self, distance):
        """Test whether locations are within a given range of the first.

        Args:
            distance (float): Distance to test location is within
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
                click.echo(' '.join(text) % (location.name, distance,
                                             self[0].name))
            else:
                click.echo(in_range)

    def destination(self, distance, bearing, locator):
        """Calculate destination locations for given distance and bearings.

        Args:
            distance (float): Distance to travel
            bearing (float): Direction of travel
            locator (str): Accuracy of Maidenhead locator output
        """
        destinations = super(NumberedPoints, self).destination(bearing,
                                                               distance)
        for location, destination in zip(self, destinations):
            if locator:
                output = destination.to_grid_locator(locator)
            else:
                output = format(location, self.format)
            if self.verbose:
                click.echo('Destination from location %s is %s'
                           % (location.name, output))
            else:
                click.echo(output)

    def sun_events(self, mode):
        """Calculate sunrise/sunset times for locations.

        Args:
            mode (str): Sun event to display
        """
        mode_str = mode.capitalize()
        times = getattr(super(NumberedPoints, self), mode)()
        for location, time in zip(self, times):
            if self.verbose:
                if time:
                    click.echo('%s at %s UTC in location %s'
                               % (mode_str, time, location.name))
                else:
                    click.echo("The sun doesn't %s at location %s on this date"
                               % (mode_str[3:], location.name))
            else:
                click.echo(time)

    def flight_plan(self, speed, time):
        """Output the flight plan corresponding to the given locations.

        .. todo:: Description

        Args:
            speed (float): Speed to use for elapsed time calculation
            time (str): Time unit to use for output
        """
        if len(self) == 1:
            raise LocationsError('flight_plan')
        if self.verbose:
            click.echo('WAYPOINT,BEARING[°],DISTANCE[%s],ELAPSED_TIME[%s],'
                       'LATITUDE[d.dd],LONGITUDE[d.dd]' % (self.units, time))
        legs = [(0, 0), ] + list(self.inverse())
        for leg, loc in zip(legs, self):
            if leg == (0, 0):
                click.echo('%s,,,,%f,%f' % (loc.name, loc.latitude,
                                            loc.longitude))
            else:
                leg_speed = '%.1f' % (leg[1] / speed) if speed != 0 else ''
                click.echo('%s,%i,%.1f,%s,%f,%f'
                           % (loc.name, leg[0], leg[1], leg_speed,
                              loc.latitude, loc.longitude))
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
            click.echo('-- OVERALL --%s,,%.1f,%s,,'
                       % (speed_marker, overall_distance, overall_speed))
            click.echo('-- DIRECT --%s,%i,%.1f,%s,,'
                       % (speed_marker, self[0].bearing(self[-1]),
                          direct_distance, direct_speed))


@click.group(help=__doc__[__doc__.find('\n\n')+2:__doc__.rfind('\n\n')],
             epilog='Please report bugs at '
                    'https://github.com/JNRowe/upoints/issues',
             context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(_version.dotted)
@click.option('-v', '--verbose/--quiet',
              help='Change verbosity level of output.')
@click.option('--config',
              type=click.Path(dir_okay=False, resolve_path=True,
                              allow_dash=True),
              metavar='~/.edist.conf',
              default=os.path.expanduser('~/.edist.conf'),
              help='Config file to read custom locations from.')
@click.option('--csv-file',
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              help='CSV file (gpsbabel format) to read route/locations from.')
@click.option('-o', '--format',
              type=click.Choice(['dms', 'dm', 'dd']),
              default='dms',
              help='Produce output in dms, dm or dd format.')
@click.option('-u', '--units',
              type=click.Choice(['km', 'sm', 'nm']), metavar='km',
              default='km',
              help='Display distances in kilometres, statute miles or '
                   'nautical miles.')
@click.option('-l', '--location', multiple=True,
              help='Location to operate on.')
@click.pass_context
def cli(ctx, verbose, config, csv_file, format, units, location):
    if csv_file:
        config_locations, location = read_csv(csv_file)
    else:
        config_locations = read_locations(config)

    try:
        locations = NumberedPoints(location, format, verbose, config_locations,
                                   units)
    except LocationsError as error:
        raise click.BadParameter(str(error))

    class Obj:
        pass
    ctx.obj = Obj()
    ctx.obj.locations = locations


@cli.command()
@click.option('-g', '--string', is_flag=True, help='Display named bearings.')
@click.pass_obj
def bearing(globs, string):
    """Calculate initial bearing between locations."""
    globs.locations.bearing('bearing', string)


@cli.command()
@click.option('-l', '--locator',
              type=click.Choice(['square', 'subsquare', 'extsquare']),
              default='subsquare',
              help='Accuracy of Maidenhead locator output.')
@click.argument('distance', type=float)
@click.argument('bearing', type=float)
@click.pass_obj
def destination(globs, locator, distance, bearing):
    """Calculate destination from locations."""
    globs.locations.destination(distance, bearing, locator)


@cli.command()
@click.option('-l', '--locator',
              type=click.Choice(['square', 'subsquare', 'extsquare']),
              help='Accuracy of Maidenhead locator output.')
@click.pass_obj
def display(globs, locator):
    """Pretty print the locations."""
    globs.locations.display(locator)


@cli.command()
@click.pass_obj
def distance(globs):
    """Calculate distance between locations."""
    globs.locations.distance()


@cli.command()
@click.option('-g', '--string', is_flag=True,
              help='Display named bearings.')
@click.pass_obj
def final_bearing(globs, string):
    """Calculate final bearing between locations."""
    globs.locations.bearing('final_bearing', string)


@cli.command()
@click.option('-s', '--speed', default=0, type=float,
              help='Speed to calculate elapsed time.')
@click.option('-t', '--time', type=click.Choice(['h', 'm', 's']),
              help='Display time in hours, minutes or seconds.')
@click.pass_obj
def flight_plan(globs, speed, time):
    """Calculate flight plan for locations."""
    globs.locations.flight_plan(speed, time)


@cli.command()
@click.argument('distance', type=float)
@click.pass_obj
def range(globs, distance):
    """Check locations are within a given range."""
    globs.locations.range(distance)


@cli.command()
@click.pass_obj
def sunrise(globs):
    """Calculate the sunrise time for locations."""
    globs.locations.sun_events('sunrise')


@cli.command()
@click.pass_obj
def sunset(globs):
    """Calculate the sunset time for locations."""
    globs.locations.sun_events('sunset')


def read_locations(filename):
    """Pull locations from a user's config file.

    Args:
        filename (str): Config file to parse

    Returns:
        dict: List of locations from config file
    """
    data = ConfigParser()
    if filename == '-':
        data.read_file(sys.stdin)
    else:
        data.read(filename)
    if not data.sections():
        logging.debug('Config file is empty')

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

    Args:
        filename (str): CSV file to parse

    Returns:
        tuple of dict and list: List of locations as ``str`` objects
    """
    field_names = ('latitude', 'longitude', 'name')
    data = utils.prepare_csv_read(filename, field_names, skipinitialspace=True)
    locations = {}
    args = []
    for index, row in enumerate(data, 1):
        name = '%02i:%s' % (index, row['name'])
        locations[name] = (row['latitude'], row['longitude'])
        args.append(name)
    return locations, args


def main():
    """Main script handler.

    Returns:
        int: 0 for success, >1 error code
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')

    try:
        cli()
        return 0
    except LocationsError as error:
        print(error)
        return 2
    except RuntimeError as error:
        print(error)
        return 255
    except OSError as error:
        return error.errno
