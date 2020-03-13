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

**edist** operates on one, or more, locations specified in various formats.  For
example, a location string of "52.015;\-0.221" would be interpreted as
52.015 degrees North by 0.221 degrees West, as would "52d0m54s N 000d13m15s W".
Positive values can be specified with a "+" prefix, but it isn't required.

It is possible to use Maidenhead locators, such as "IO92" or "IO92va", for users
who are accustomed to working with them.

Users can maintain a local configuration file that lists locations with assigned
names, and then use the names on the command line.  This makes command lines
much easier to read, and also makes reusing locations at a later date simpler.
See `CONFIGURATION FILE`_.

.. click:: upoints.edist:cli
   :prog: edist
   :show-nested:

CONFIGURATION FILE
------------------

The configuration file, by default ``~/.edist.conf``, is a simple ``INI`` format
file, with sections headers defining the name of the location and their data
defining the actual position.  You can define locations by either their latitude
and longitude, or with a Maidenhead locator string.  Any options that aren't
handled will simply ignored.  For example::

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

Full documentation: https://upoints.readthedocs.io/

Issue tracker: https://github.com/JNRowe/upoints/issues/

COPYING
-------

Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>

upoints is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

upoints is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
upoints.  If not, see <http://www.gnu.org/licenses/>.

.. spelling::

    Config
    GIS
    IO
    dd
    dm
    dms
    edist
    gpsbabel
    va
