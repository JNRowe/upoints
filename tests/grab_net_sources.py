#! /usr/bin/env python3
"""grab_net_sources - Fetch sources for tests."""
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

import bz2
import gzip
import os
import tempfile
try:
    from urllib.request import (urlopen, urlretrieve)
except ImportError:
    from urllib import (urlopen, urlretrieve)

import click


SOURCES = {
    'cities.dat': 'http://cvs.savannah.gnu.org/viewvc/*checkout*/miscfiles/cities.dat?root=miscfiles',
    'nsd_bbsss.txt': 'http://weather.noaa.gov/data/nsd_bbsss.txt',
    'nsd_cccc': 'http://weather.noaa.gov/data/nsd_cccc.txt',
    'alltrigs-wgs84.txt': 'http://www.haroldstreet.org.uk/download.php?file=waypoints/files/alltrigs-wgs84.txt',
    'cells.txt': 'http://myapp.fr/cellsIdData/cells.txt.gz',
    'earth-markers-schaumann': 'http://xplanet.sourceforge.net/Extras/earth-markers-schaumann',
}


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-f', '--force/--no-force', help='Re-download files')
def main(force):
    """Fetch non-free data files."""
    click.secho('WARNING', nl=False, fg='red', bold=True, blink=True)
    click.echo(""":
  This script will fetch some data files that can not be distributed
  legally!  In some jurisdictions you may not even be entitled to
  personal use of the data it fetches without express consent of the
  copyright holders.'
    """)
    cached = 0
    for filename, url in SOURCES.items():
        filename = os.path.join(os.path.dirname(__file__), 'data', filename)
        if not force and os.path.exists(filename):
            print('%r already downloaded.' % filename)
            cached += 1
        else:
            print('Fetching %r...' % url)
            if url.endswith('.gz'):
                temp = tempfile.mkstemp()[1]
                try:
                    urlretrieve(url, temp)
                    data = gzip.GzipFile(temp).read()
                finally:
                    os.unlink(temp)
                with click.open_file(filename, 'w') as f:
                    f.write(data)
            elif url.endswith('.bz2'):
                data = bz2.decompress(urlopen(url).read())
                with click.open_file(filename, 'w') as f:
                    f.write(data)
            else:
                urlretrieve(url, filename)
    if cached > 1:
        click.secho(
            "You can force download with the `-f' option to this script.",
            fg='yellow'
        )


if __name__ == '__main__':
    main()
