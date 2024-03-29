#
"""mock - Mock objects for doctest code snippets"""
# Copyright © 2007-2021  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

import builtins
import os
import StringIO
import urllib

from types import ModuleType

from tests import grab_net_sources


SOURCES = {os.path.basename(s): s for s in grab_net_sources.SOURCES}
BASEDIR = os.path.dirname(__file__)


def isfile(path):
    """Mock ``isfile`` to check existence of test files.

    Args:
        path (str): File to check for existence

    Returns:
        bool: `True` if file exists
    """
    filename = os.path.basename(path)
    try:
        builtins.open(os.path.join(BASEDIR, 'data', filename))
    except IOError:
        return False
    return True


def _get_test_file(filename):
    """Open a test data file.

    Args:
        filename (str): Basename of the test data to open

    Returns:
        file: Test data

    Raises:
        IOError: When the file can't be opened for reading
    """
    if isfile(filename):
        return builtins.open(os.path.join(BASEDIR, 'data', filename))
    else:
        if filename in SOURCES:
            raise IOError(
                f'{filename!r} missing.  It can be downloaded from '
                f'{SOURCES[filename]!r} or alternatively by running '
                'the ‘grab_net_sources’ script.'
            )
        else:
            raise IOError(f'Can not open {filename!r}')


def open(filename, mode='rb'):
    """Mock ``open`` function to open test data files.

    Args:
        filename (str): File to simulate, basename is used as local file name
        mode (str): Valid `file` mode string

    Returns::
        file: File object opened from test data directory, or
            ``StringIO.StringIO`` object if a writable file is expected

    Raises:
        NotImplementedError: When attempting to use an unhandled file mode
    """
    if 'r' in mode:
        return _get_test_file(os.path.basename(filename))
    elif 'w' in mode:
        return StringIO.StringIO()
    else:
        raise NotImplementedError


def urlopen(url, data=None, proxies=None):
    """Mock ``urlopen`` to open test data files.

    Args:
        url (str): URL to simulate, basename is used as local file name
        data (any): Ignored, just for compatibility with `urlopen` callers
        proxies (any): Ignored, just for compatibility with `urlopen` callers

    Returns:
        file: File object from test data directory
    """
    return _get_test_file(os.path.basename(url))


urllib.urlopen = urlopen


class pymetar(ModuleType):
    """Mock ``pymetar`` infrastructure for tests.

    .. versionadded:: 0.6.0

    See also:
        `pymetar <http://www.schwarzvogel.de/software-pymetar.shtml>`__
    """

    class ReportFetcher:
        def __init__(self, StationCode=None):
            """Mock `ReportFetcher` initialisation for tests.

            Args:
                StationCode (any): Ignored, just for compatibility with
                    `ReportFetcher` callers
            """
            super(pymetar.ReportFetcher, self).__init__()

        @staticmethod
        def FetchReport():
            """Mock ``FetchReport`` function to pass tests."""
            pass

    class ReportParser:
        class ParseReport:
            def __init__(self, MetarReport=None):
                """Mock ``ParseReport`` object to return test data.

                Args:
                    MetarReport (any): Ignored, just for compatibility with
                        ``FetchReport`` callers
                """
                super(pymetar.ReportParser.ParseReport, self).__init__()

            @staticmethod
            def getTemperatureCelsius():
                """Mock `getTemperatureCelsius`.

                Returns:
                    float: Sample temperature data for tests
                """
                return 10.3

            @staticmethod
            def getISOTime():
                """Mock `getISOTime`.

                Returns:
                    str: Sample |ISO|-8601 time string
                """
                return '2007-11-28 19:20:00Z'
