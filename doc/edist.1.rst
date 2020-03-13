:Author: James Rowe <jnrowe@gmail.com>
:Date: 2008-01-22
:Copyright: GPL v3
:Manual section: 1
:Manual group: GIS

edist
=====

Simple command line coordinate processing
-----------------------------------------

SYNOPSIS
--------

    edist [option]... <command> <location...>

DESCRIPTION
-----------

**edist** operates on one, or more, locations specified in various formats.
For example, a location string of “52.015;\-0.221” would be interpreted as
52.015 degrees North by 0.221 degrees West, as would “52d0m54s N 000d13m15s W”.
Positive values can be specified with a “+” prefix, but it isn't required.

It is possible to use Maidenhead locators, such as “IO92” or “IO92va”, for
users who are accustomed to working with them.

Users can maintain a local configuration file that lists locations with
assigned names, and then use the names on the command line.  This makes command
lines much easier to read, and also makes reusing locations at a later date
simpler.  See `CONFIGURATION FILE`_.

OPTIONS
-------

--version
    Show the version and exit.

-v, --verbose / --quiet
    Change verbosity level of output.

--config <file>
    Config file to read custom locations from.

--csv-file <file>
    CSV file (gpsbabel format) to read route/locations from.

-o, --format <format>
    Produce output in dms, dm or dd format.

-u <units>, --units <units>
    Display distances in kilometres, statute miles or nautical miles.

-l, --location <location>
    Location to operate on.

-h, --help
    Show this message and exit.

COMMANDS
--------

``bearing``
'''''''''''

Calculate the initial bearing between locations bearing

g, --string
    Display named bearings.

-h, --help
    Show this message and exit.

``destination``
'''''''''''''''

Calculate destination from locations.

-l <accuracy>, --locator <accuracy>
    Accuracy of Maidenhead locator output.

-h, --help
    Show this message and exit.

``display``
'''''''''''

Pretty print the locations.

-l <accuracy>, --locator <accuracy>
    Accuracy of Maidenhead locator output.

-h, --help
    Show this message and exit.

``distance``
''''''''''''

Calculate distance between locations.

-h, --help
    Show this message and exit.

``final-bearing``
'''''''''''''''''

Calculate final bearing between locations.

-g, --string
    Display named bearings.

-h, --help
    Show this message and exit.

``flight-plan``
'''''''''''''''

Calculate flight plan for locations.

-s <speed>, --speed <speed>
    Speed to calculate elapsed time.

-t <format>, --time <format>
    Display time in hours, minutes or seconds.

-h, --help
    Show this message and exit.

``range``
'''''''''

Check locations are within a given range.

``sunrise``
'''''''''''

Calculate the sunrise time for locations.

-h, --help
    Show this message and exit.

``sunset``
''''''''''

Calculate the sunset time for locations.

-h, --help
    Show this message and exit.

CONFIGURATION FILE
------------------

The configuration file, by default ``~/.edist.conf`, is a simple ``INI`` format
file, with sections headers defining the name of the location and their data
defining the actual position.  You can define locations by either their
latitude and longitude, or with a Maidenhead locator string.  Any options that
aren't handled will simply ignored.  For example::

    [Home]
    latitude = 52.015
    longitude = -0.221

    [Cambridge]
    latitude = 52.200
    longitude = 0.183

    [Pin]
    locator = IO92

With the above configuration file one could find the distance from ``Home`` to
``Cambridge`` using ``edist -l Home -l Cambridge distance``.

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

Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
