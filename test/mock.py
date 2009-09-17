#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""mock - Mock objects for doctest code snippets"""
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

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
import os
import urllib

from test import grab_net_sources
SOURCES = dict([(os.path.basename(i), i) for i in grab_net_sources.SOURCES])

BASEDIR = os.path.dirname(__file__)

def isfile(path):
    """Mock `isfile` to check existence of test files

    :Parameters:
        path : `str`
            File to check for existence
    :rtype: `bool`
    :return: `True` if file exists, `False` otherwise

    """
    filename = os.path.basename(path)
    try:
        __builtin__.open(os.path.join(BASEDIR, "data", filename))
    except IOError:
        return False
    return True

def _get_test_file(filename):
    """Open a test data file

    :Parameters:
        filename : `str`
            Basename of the test data to open
    :rtype: `file`
    :return: Test data
    :raise IOError: When the file can't be opened for reading

    """
    if isfile(filename):
        return __builtin__.open(os.path.join(BASEDIR, "data", filename))
    else:
        if filename in SOURCES:
            raise IOError("`%s' missing.  It can be downloaded from `%s', or "
                          "alternatively by running the `grab_net_sources' "
                          "script." % (filename, SOURCES[filename]))
        else:
            raise IOError("Can not open `%s'" % filename)

def open(filename, mode="rb"):
    """Mock `open` function to open test data files

    :Parameters:
        filename : `str`
            File to simulate, basename is used as local file name
        mode : `str`
            Valid `file` mode string
    :rtype: `file`
    :return: File object opened from test data directory, or ``StringIO.StringIO``
        object if a writable file is expected
    :raise NotImplementedError: When attempting to use an unhandled file mode

    """
    if "r" in mode:
        return _get_test_file(os.path.basename(filename))
    elif "w" in mode:
        return StringIO.StringIO()
    else:
        raise NotImplementedError

def urlopen(url, data=None, proxies=None):
    """Mock `urlopen` to open test data files

    :Parameters:
        url : `str`
            URL to simulate, basename is used as local file name
        data : any
            Ignored, just for compatibility with `urlopen` callers
        proxies : any
            Ignored, just for compatibility with `urlopen` callers
    :rtype: `file`
    :return: File object from test data directory

    """
    return _get_test_file(os.path.basename(url))
urllib.urlopen = urlopen

class pymetar(ModuleType):
    """Mock `pymetar` infrastructure for tests

    :since: 0.6.0

    :see: `pymetar <http://www.schwarzvogel.de/software-pymetar.shtml>`__

    """
    class ReportFetcher(object):
        def __init__(self, StationCode=None):
            """Mock `ReportFetcher` initialisation for tests

            :Parameters:
                StationCode : any
                    Ignored, just for compatibility with `ReportFetcher`
                    callers

            """
            super(pymetar.ReportFetcher, self).__init__()

        @staticmethod
        def FetchReport():
            """Mock ``FetchReport`` function to pass tests"""
            pass


    class ReportParser(object):
        class ParseReport(object):
            def __init__(self, MetarReport=None):
                """Mock ``ParseReport`` object to return test data

                :Parameters:
                    MetarReport : any
                        Ignored, just for compatibility with ``FetchReport``
                        callers

                """
                super(pymetar.ReportParser.ParseReport, self).__init__()

            @staticmethod
            def getTemperatureCelsius():
                """Mock `getTemperatureCelsius`

                :rtype: `float`
                :return: Sample temperature data for tests

                """
                return 10.3

            @staticmethod
            def getISOTime():
                """Mock `getISOTime`

                :rtype: `str`
                :return: Sample ISO time string

                """
                return "2007-11-28 19:20:00Z"

