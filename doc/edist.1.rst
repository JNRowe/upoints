edist
=====

Simple command line coordinate processing
-----------------------------------------

:Author: James Rowe <jnrowe@gmail.com>
:Date: 2008-01-22
:Copyright: GPL v3
:Manual section: 1
:Manual group: GIS

SYNOPSIS
--------

    edist [option]... <command> <location...>

DESCRIPTION
-----------

**edist** operates on one, or more, locations specified in various
formats.  For example, a location string of "52.015;\-0.221" would be
interpreted as 52.015 degrees North by 0.221 degrees West, as would
"52d0m54s N 000d13m15s W".  Positive values can be specified with a "+"
prefix, but it isn't required.

It is possible to use Maidenhead locators, such as "IO92" or "IO92va",
for users who are accustomed to working with them.

Users can maintain a local configuration file that lists locations with
assigned names, and then use the names on the command line.  This makes
command lines much easier to read, and also makes reusing locations at
a later date simpler.  See `CONFIGURATION FILE`_.

OPTIONS
-------

--version
    show program's version number and exit

-h, --help
    show this help message and exit

--config-file = **file**
    Config file to read custom locations from

--csv-file = **csv_file**
    CSV file (gpsbabel format) to read route/locations from

-v, --verbose
    produce verbose output

-q, --quiet
    output only results and errors

-o **FORMAT**, --format **FORMAT**
    produce output in dms, dm, d format or Maidenhead locator

-g, --string
    display named bearings

-u **km**, --units **km**
    display distances in km(default), mile or nm

COMMANDS
--------

``bearing``
'''''''''''

Calculate the initial bearing between locations bearing

g, --string

    display named bearings

``destination``
'''''''''''''''

Calculate the destination for a given distance and

-l {square,subsquare,extsquare}, --locator {square,subsquare,extsquare}

    accuracy of Maidenhead locator output

-d DISTANCE, --distance DISTANCE

    distance from start point

-b BEARING, --bearing BEARING

    bearing from start point

``display``
'''''''''''

Pretty print the location(s)

-l {square,subsquare,extsquare}, --locator {square,subsquare,extsquare}

    accuracy of Maidenhead locator output

``distance``
''''''''''''

Calculate the distance between locations

``final-bearing``
'''''''''''''''''

Calculate the final bearing between locations

g, --string

    display named bearings

``flight-plan``
'''''''''''''''

Calculate the flight plan corresponding to locations

-s SPEED, --speed SPEED

    speed to calculate elapsed time

-t {h,m,s}, --time {h,m,s}

    display time in hours, minutes or seconds

``range``
'''''''''

Calculate whether locations are within a given range

-d DISTANCE, --distance DISTANCE

    range radius

``sunrise``
'''''''''''

Calculate the sunrise time for a given location

``sunset``
''''''''''

Calculate the sunset time for a given location

CONFIGURATION FILE
------------------

The configuration file, by default **~/.edist.conf**, is a simple
**INI** format file, with sections headers defining the name of the
location and their data defining the actual position.  You can define
locations by either their latitude and longitude, or with a Maidenhead
locator string.  Any options that aren't handled will simply ignored.
For example::

    [Home]
    latitude = 52.015
    longitude = -0.221

    [Cambridge]
    latitude = 52.200
    longitude = 0.183

    [Pin]
    locator = IO92

With the above configuration file one could find the distance from
**Home** to **Cambridge** using **edist --distance Home Cambridge**.

BUGS
----

None known.

AUTHOR
------

Written by `James Rowe <mailto:jnrowe@gmail.com>`__

RESOURCES
---------

Home page: https://github.com/JNRowe/upoints

COPYING
-------

Copyright © 2007-2014  James Rowe <jnrowe@gmail.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
