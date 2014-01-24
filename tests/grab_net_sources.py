#! /usr/bin/python -tt
# coding=utf-8
"""grab_net_sources - Fetch sources for tests"""
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

import bz2
import gzip
import os
import sys
import tempfile
try:
    from urllib.parse import urlparse
    from urllib.request import (urlopen, urlretrieve)
except ImportError:
    from urlparse import urlparse
    from urllib import (urlopen, urlretrieve)


SOURCES = [
    'http://cvs.savannah.gnu.org/viewvc/*checkout*/miscfiles/cities.dat?root=miscfiles',
    'http://weather.noaa.gov/data/nsd_bbsss.txt',
    'http://weather.noaa.gov/data/nsd_cccc.txt',
    'http://www.haroldstreet.org.uk/download.php?file=waypoints/files/alltrigs-wgs84.txt',
    'http://myapp.fr/cellsIdData/cells.txt.gz',
    'http://xplanet.sourceforge.net/Extras/earth-markers-schaumann',
]

def data_file(resource):
    """Generate a local filename for the resource.

    >>> print data_file(SOURCES[0])
    tests/data/cities.dat
    >>> print data_file(SOURCES[4])
    tests/data/cells.txt
    >>> print data_file(SOURCES[3])
    tests/data/alltrigs-wgs84.txt

    :parameters str resource: Source
    :rtype: `str`
    :return: Local filename

    """
    filename = os.path.join(os.path.dirname(__file__), 'data',
                            os.path.basename(urlparse(resource[0]).path))
    if filename.endswith('.gz'):
        return filename[:-3]
    elif filename.endswith('.bz2'):
        return filename[:-4]
    else:
        return filename

def main(argv=None):
    """Main script handler.

    :param list argv: Command line arguments

    """
    print('*WARNING* This script will fetch some data files that can not be '
          'distributed legally!  In some jurisdictions you may not even be '
          'entitled to personal use of the data it fetches without express '
          'consent of the copyright holders.')
    if not argv:
        argv = sys.argv
    if len(argv) == 2 and argv[1] in ('-f' or '--force'):
        force = True
    else:
        force = False
    cached = 0
    for path in SOURCES:
        filename = data_file(path)
        if not force and os.path.exists(filename):
            print('%r already downloaded.' % path)
            cached += 1
        else:
            print('Fetching %r...' % path)
            if path.endswith('.gz'):
                temp = tempfile.mkstemp()[1]
                try:
                    urlretrieve(path, temp)
                    data = gzip.GzipFile(temp).read()
                finally:
                    os.unlink(temp)
                open(filename, 'w').write(data)
            elif path.endswith('.bz2'):
                data = bz2.decompress(urlopen(path).read())
                open(filename, 'w').write(data)
            else:
                urlretrieve(path, filename)
    if cached > 1:
        print("You can force download with the `-f' option to this script.")

if __name__ == '__main__':
    main(sys.argv)
