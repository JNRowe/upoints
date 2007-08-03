#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""
utils - Support code for earth_distance
"""
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

from __future__ import division

import datetime
import math

BODIES = {
    # Body radii in kilometres
    'Sun': 696000,

    # Terrestrial inner planets
    'Mercury': 2440,
    'Venus': 6052,
    'Earth': 6372,
    'Mars': 3390,

    # Gas giant outer planets
    'Jupiter': 69911,
    'Saturn': 58232,
    'Uranus': 25362,
    'Neptune': 24622,

    # only satellite to be added
    'Moon': 1738,

    # dwarf planets may be added
    'Pluto': 1153,
    'Ceres': 475,
    'Eris': 1200,
}

BODY_RADIUS = BODIES['Earth']
NAUTICAL_MILE = 1.852 #kM
STATUTE_MILE = 1.609 #kM

def to_dms(angle, style="dms"):
    """
    Convert decimal angle to degrees, minutes and possibly seconds

    >>> to_dms(52.015)
    (52, 0, 54)
    >>> to_dms(-0.221)
    (0, -13, -15)
    >>> to_dms(-0.221, style="dm")
    (0, -13.25)

    @type angle: C{float} or coercible to C{float}
    @param angle: Angle to convert
    @type style: C{str}
    @param style: Return fractional or whole minutes values
    @rtype: C{tuple} of C{int}s for values
    @return: Angle converted to degrees, minutes and possibly seconds
    @raise ValueError: Unknown value for C{style}
    """
    sign = int(angle / abs(angle))
    angle = abs(angle) * 3600
    minutes, seconds = divmod(angle, 60)
    degrees, minutes = divmod(minutes, 60)
    if style == "dms":
        return sign * int(degrees), sign * int(minutes), sign * int(seconds)
    elif style == "dm":
        return sign * int(degrees), sign * (int(minutes) + int(seconds) / 60)
    else:
        raise ValueError("Unknown style type `%s'" % style)

def to_dd(degrees, minutes, seconds=0):
    """
    Convert degrees, minutes and optionally seconds to decimal angle

    >>> "%.3f" % to_dd(52, 0, 54)
    '52.015'
    >>> "%.3f" % to_dd(0, -13, -15)
    '-0.221'
    >>> "%.3f" % to_dd(0, -13.25)
    '-0.221'

    @type degrees: C{float} or coercible to C{float}
    @param degrees: Number of degrees
    @type minutes: C{float} or coercible to C{float}
    @param minutes: Number of minutes
    @type seconds: C{float} or coercible to C{float}
    @param seconds: Number of seconds
    @rtype: C{float}
    @return: Angle converted to decimal degrees
    """
    return degrees + minutes / 60 + seconds / 3600

def angle_to_distance(angle, format="metric"):
    """
    Convert angle in to distance along a meridian

    >>> "%.3f" % angle_to_distance(1)
    '111.212'
    >>> "%i" % angle_to_distance(360, "imperial")
    '24882'
    >>> "%i" % angle_to_distance(1.0/60, "nautical")
    '1'

    @type angle: C{float} or coercible to C{float}
    @param angle: Angle in degrees to convert to distance
    @type format: C{str}
    @param format: Unit type to be used for distances
    @rtype: C{float}
    @return: Distance in kilometres
    @raise ValueError: Unknown value for C{format}
    """
    distance = math.radians(angle) * BODY_RADIUS

    if format == "metric":
        return distance
    elif format in ("imperial", "US customary"):
        return distance / STATUTE_MILE
    elif format == "nautical":
        return distance / NAUTICAL_MILE
    else:
        raise ValueError("Unknown unit type `%s'" % format)

def distance_to_angle(distance, format="metric"):
    """
    Convert a distance in to an angle along a meridian

    >>> "%.3f" % round(distance_to_angle(111.212))
    '1.000'
    >>> "%i" % round(distance_to_angle(24882, "imperial"))
    '360'
    >>> "%i" % round(distance_to_angle(60, "nautical"))
    '1'

    @type distance: C{float} or coercible to C{float}
    @param distance: Distance to convert to degrees
    @type format: C{str}
    @param format: Unit type to be used for distances
    @rtype: C{float}
    @return: Angle in degrees
    @raise ValueError: Unknown value for C{format}
    """

    if format == "metric":
        pass
    elif format in ("imperial", "US customary"):
        distance *= STATUTE_MILE
    elif format == "nautical":
        distance *= NAUTICAL_MILE
    else:
        raise ValueError("Unknown unit type `%s'" % format)

    return math.degrees(distance / BODY_RADIUS)

ZENITH = {
    # All values are specified in degrees!

    # Sunrise/sunset is defined as the moment the upper limb becomes visible,
    # taking in to account atmospheric refraction.  That is 34' for atmospheric
    # refraction and 16' for angle between the Sun's centre and it's upper limb,
    # resulting in a combined 50' below the horizon.
    #
    # We're totally ignoring how temperature and pressure change the amount of
    # atmospheric refraction, because their effects are drowned out by rounding
    # errors in the equation.
    None: -50/60,

    # Twilight definitions specify the angle in degrees of the Sun below the
    # horizon
    "civil": -6,
    "nautical": -12,
    "astronomical": -18,
}

def sun_rise_set(latitude, longitude, date, mode="rise", timezone=0,
                 zenith=None):
    """
    Calculate sunrise or sunset for a specific location

    This function calculates the time sunrise or sunset, or optionally the
    beginning or end of a specified twilight period.

    Source::

        Almanac for Computers, 1990
        published by Nautical Almanac Office
        United States Naval Observatory
        Washington, DC 20392

    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15))
    datetime.time(3, 40)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), "set")
    datetime.time(20, 23)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), timezone=60)
    datetime.time(4, 40)
    >>> sun_rise_set(52.015, -0.221, datetime.date(2007, 6, 15), "set", 60)
    datetime.time(21, 23)
    >>> sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11))
    datetime.time(7, 58)
    >>> sun_rise_set(52.015, -0.221, datetime.date(1993, 12, 11), "set")
    datetime.time(15, 50)

    @type latitude: C{float} or coercible to C{float}
    @param latitude: Location's latitude
    @type longitude: C{float} or coercible to C{float}
    @param longitude: Location's longitude
    @type date: C{datetime.date}
    @param date: Calculate rise or set for given date
    @type mode: C{str}
    @param mode: Which time to calculate
    @type timezone: C{int}
    @param timezone: Offset from UTC in minutes
    @type zenith: C{None} or C{str}
    @param zenith: Calculate rise/set events, or twilight times
    @rtype: C{datetime.time}
    @return: The time for the given event in the specified timezone
    @raise ValueError: Unknown value for C{mode}
    """
    zenith = ZENITH[zenith]

    # First calculate the day of the year
    # Thanks, datetime this would have been ugly without you!!!
    n = (date - datetime.date(date.year-1, 12, 31)).days

    # Convert the longitude to hour value and calculate an approximate time
    lngHour = longitude / 15

    if mode == "rise":
        t = n + ((6 - lngHour) / 24)
    elif mode == "set":
        t = n + ((18 - lngHour) / 24)
    else:
        raise ValueError("Unknown mode value `%s'" % mode)

    # Calculate the Sun's mean anomaly
    m = (0.9856 * t) - 3.289

    # Calculate the Sun's true longitude
    l = m + 1.916 * math.sin(math.radians(m)) + 0.020 * \
        math.sin(2 * math.radians(m)) + 282.634
    l = abs(l) % 360

    # Calculate the Sun's right ascension
    ra = math.degrees(math.atan(0.91764 * math.tan(math.radians(l))))

    # Right ascension value needs to be in the same quadrant as L
    lQuandrant = (math.floor(l / 90)) * 90
    raQuandrant = (math.floor(ra / 90)) * 90
    ra = ra + (lQuandrant - raQuandrant)

    # Right ascension value needs to be converted into hours
    ra = ra / 15

    # Calculate the Sun's declination
    sinDec = 0.39782 * math.sin(math.radians(l))
    cosDec = math.cos(math.asin(sinDec))

    # Calculate the Sun's local hour angle
    cosH = (math.radians(zenith) - 
            (sinDec * math.sin(math.radians(latitude)))) / \
           (cosDec * math.cos(math.radians(latitude)))

    if cosH > 1:
        # The sun never rises on this location (on the specified date)
        return None
    if cosH < -1:
        # The sun never sets on this location (on the specified date)
        return None

    # Finish calculating H and convert into hours
    if mode == "rise":
        h = 360 - math.degrees(math.acos(cosH))
    else:
        h = math.degrees(math.acos(cosH))
    h = h / 15

    # Calculate local mean time of rising/setting
    T = h + ra - (0.06571 * t) - 6.622

    # Adjust back to UTC
    UT = T - lngHour

    # Convert UT value to local time zone of latitude/longitude
    localT = UT + timezone/60

    hour = int(localT)
    if hour == 0:
        minute = int(60 * localT)
    else:
        minute = int(60 * (localT % hour))
    if hour < 0:
        hour += 23
    if minute < 0:
        minute += 60
    return datetime.time(hour, minute)


def sun_events(latitude, longitude, date, timezone=0, zenith=None):
    """
    Convenience function for calculating sunrise and sunset

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15))
    (datetime.time(3, 40), datetime.time(20, 23))
    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15), 60)
    (datetime.time(4, 40), datetime.time(21, 23))
    >>> sun_events(52.015, -0.221, datetime.date(1993, 12, 11))
    (datetime.time(7, 58), datetime.time(15, 50))
    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15))
    (datetime.time(3, 40), datetime.time(20, 23))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15)) # JFK
    (datetime.time(9, 23), datetime.time(0, 27))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15)) # CDG
    (datetime.time(4, 5), datetime.time(20, 16))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15)) # TIA
    (datetime.time(19, 25), datetime.time(9, 58))

    Civil twilight starts/ends when the Sun's center is 6 degrees below
    the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15), zenith="civil")
    (datetime.time(2, 51), datetime.time(21, 12))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="civil") # JFK
    (datetime.time(8, 50), datetime.time(1, 0))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="civil") # CDG
    (datetime.time(3, 22), datetime.time(20, 59))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="civil") # TIA
    (datetime.time(18, 55), datetime.time(10, 28))

    Nautical twilight starts/ends when the Sun's center is 12 degrees
    below the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
    ...            zenith="nautical")
    (datetime.time(1, 32), datetime.time(22, 31))
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # JFK
    (datetime.time(8, 7), datetime.time(1, 44))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # CDG
    (datetime.time(2, 20), datetime.time(22, 1))
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="nautical") # TIA
    (datetime.time(18, 18), datetime.time(11, 6))

    Astronomical twilight starts/ends when the Sun's center is 18
    degrees below the horizon.

    >>> sun_events(52.015, -0.221, datetime.date(2007, 6, 15),
    ...            zenith="astronomical")
    (None, None)
    >>> sun_events(40.638611, -73.762222, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # JFK
    (datetime.time(7, 14), datetime.time(2, 36))
    >>> sun_events(49.016666, -2.5333333, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # CDG
    (None, None)
    >>> sun_events(35.549999, 139.78333333, datetime.date(2007, 6, 15),
    ...            zenith="astronomical") # TIA
    (datetime.time(17, 35), datetime.time(11, 49))

    @type latitude: C{float} or coercible to C{float}
    @param latitude: Location's latitude
    @type longitude: C{float} or coercible to C{float}
    @param longitude: Location's longitude
    @type date: C{datetime.date}
    @param date: Calculate rise or set for given date
    @type timezone: C{int}
    @param timezone: Offset from UTC in minutes
    @type zenith: C{None} or C{str}
    @param zenith: Calculate rise/set events, or twilight times
    @rtype: C{tuple} of C{datetime.time}
    @return: The time for the given events in the specified timezone
    """
    return (sun_rise_set(latitude, longitude, date, "rise", timezone, zenith),
            sun_rise_set(latitude, longitude, date, "set", timezone, zenith))

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod(optionflags=doctest.REPORT_UDIFF)[0])

