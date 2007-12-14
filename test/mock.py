#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""
mock - Mock objects for doctest code snippets
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
__date__ = "2007-11-21"
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

import __builtin__
import os
import urllib

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from types import ModuleType

import grab_net_sources
SOURCES = dict([(os.path.basename(i), i) for i in grab_net_sources.SOURCES])

BASEDIR = os.path.dirname(__file__)

def isfile(path):
    """
    Mock C{isfile} to check existance of test files

    @type path: C{str}
    @param path: File to check for existance
    @rtype: C{bool}
    @return: True if file exists, False otherwise
    """
    filename = os.path.basename(path)
    try:
        __builtin__.open(os.path.join(BASEDIR, "data", filename))
    except IOError:
        return False
    return True

def _get_test_file(filename):
    """
    Open a test data file

    @type filename: C{str}
    @param filename: Basename of the test data to open
    @rtype: C{file}
    @return: Test data
    @raise IOError: When the file can't be opened for reading
    """
    if isfile(filename):
        return __builtin__.open(os.path.join(BASEDIR, "data", filename))
    else:
        if filename in SOURCES:
            raise IOError("`%s' missing.  It can be downloaded from `%s', or "
                          "alternatively by running the `grab_net_sources'"
                          "script." % (filename, SOURCES[filename]))
        else:
            raise IOError("Can not open `%s'" % filename)

def open(filename, mode="rb"):
    """
    Mock C{open} function to open test data files

    @type filename: C{str}
    @param filename: File to simulate, basename is used as local file name
    @type mode: C{str}
    @param mode: Valid C{file} mode string
    @rtype: C{file}
    @return: File object opened from test data directory, or C{StringIO.StringIO}
        object if a writable file is expected
    @raise NotImplementedError: When attempting to use an unhandled file mode
    """
    if "r" in mode:
        return _get_test_file(os.path.basename(filename))
    elif "w" in mode:
        return StringIO.StringIO()
    else:
        raise NotImplementedError

def urlopen(url, data=None, proxies=None):
    """
    Mock C{urlopen} to open test data files

    @type url: C{str}
    @param url: URL to simulate, basename is used as local file name
    @type data: any
    @param data: Ignored, just for compatibility with C{urlopen} callers
    @type proxies: any
    @param proxies: Ignored, just for compatibility with C{urlopen} callers
    @rtype: C{file}
    @return: File object from test data directory
    """
    return _get_test_file(os.path.basename(url))
urllib.urlopen = urlopen

class pymetar(ModuleType):
    """
    Mock C{pymetar} infrastructure for tests

    @see: U{pymetar <http://www.schwarzvogel.de/software-pymetar.shtml>}
    """
    class ReportFetcher(object):
        def __init__(self, StationCode=None):
            """
            Mock C{ReportFetcher} initialisation for tests

            @type stationCode: any
            @param stationCode: Ignored, just for compatibility with
                C{ReportFetcher} callers
            """
            pass

        def FetchReport(self):
            """
            Mock C{FetchReport} function to pass tests
            """
            pass

    class ReportParser(object):
        class ParseReport(object):
            def __init__(self, MetarReport=None):
                """
                Mock C{ParseReport} object to return test data

                @type MetarReport: any
                @param MetarReport: Ignored, just for compatibility with
                    C{FetchReport} callers
                """
                pass

            def getTemperatureCelsius(self):
                """
                Mock C{getTemperatureCelsius}

                @rtype: C{float}
                @return: Sample temperature data for tests
                """
                return 10.3

            def getISOTime(self):
                """
                Mock C{getISOTime}

                @rtype: C{str}
                @return: Sample ISO time string
                """
                return "2007-11-28 19:20:00Z"

