#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""
grab_net_sources - Fetch sources for tests
"""
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

__version__ = "0.1.0"
__date__ = "2007-11-29"
__author__ = "James Rowe <jnrowe@ukfsn.org>"
__copyright__ = "Copyright (C) 2007 James Rowe"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See Mercurial repository"

__doc__ += """

@version: %s
@author: U{%s%s}
@copyright: %s
@status: WIP
@license: %s
""" % (__version__, __author__[0:__author__.rfind(" ")],
       __author__[__author__.rfind(" "):], __copyright__, __license__)

import os
import sys
import urllib
from urlparse import urlparse

SOURCES = [
    "http://cvs.savannah.gnu.org/viewvc/*checkout*/miscfiles/cities.dat?root=miscfiles",
    "http://weather.noaa.gov/data/nsd_bbsss.txt",
    "http://weather.noaa.gov/data/nsd_cccc.txt",
    "http://www.haroldstreet.org.uk/waypoints/alltrigs-wgs84.txt",
    "http://xplanet.sourceforge.net/Extras/earth-markers-schaumann",
]

data_file = lambda name: os.path.join(os.path.dirname(__file__), "data",
                                      os.path.basename(urlparse(name).path))
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ("-f" or "--force"):
        FORCE = True
    else:
        FORCE = False
    cached = 0
    for resource in SOURCES:
        filename = data_file(resource)
        if not FORCE and os.path.exists(filename):
            print("`%s' already downloaded." % resource)
            cached += 1
        else:
            print("Fetching `%s'..." % resource)
            urllib.urlretrieve(resource, filename)
    if cached > 1:
        print("You can force download with the `-f' option to this script.")