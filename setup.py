#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""earth_distance - Modules for working with points on Earth"""
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

import doctest
import os
import shutil
import sys

from distutils.archive_util import make_archive
from distutils.command.clean import clean
from distutils.command.sdist import sdist
from distutils.cmd import Command
from distutils.core import setup
from distutils.dep_util import newer
from distutils.errors import DistutilsModuleError
from distutils.file_util import write_file
from distutils.util import execute
from email.utils import parseaddr
from glob import glob
from re import sub
from subprocess import check_call
from time import strftime

try:
    from docutils.core import publish_cmdline, default_description
    from docutils import nodes
    from docutils.parsers.rst import directives
    DOCUTILS = True
except ImportError:
    DOCUTILS = False
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    PYGMENTS = True
except ImportError:
    PYGMENTS = False
try:
    from epydoc import cli
    EPYDOC = True
except ImportError:
    EPYDOC = False
try:
    from mercurial import hg
    MERCURIAL = True
except ImportError:
    MERCURIAL = False

import earth_distance
import edist
import test

BASE_URL = "http://www.jnrowe.ukfsn.org/"

from sys import version_info
if version_info < (2, 5, 0, 'final'):
    raise SystemError("Requires Python v2.5+")

def write_changelog(filename):
    """
    Generate a ChangeLog from Mercurial repo

    @type filename: C{str}
    @param filename: Filename to write ChangeLog to
    """
    if os.path.isdir(".hg"):
        check_call(["hg", "log", "--exclude", ".be/", "--no-merges",
                    "--style", "changelog"],
                   stdout=open(filename, "w"))
    else:
        print("Unable to build ChangeLog, dir is not a Mercurial clone")
        return False

def write_manifest(files):
    """
    Generate a MANIFEST file

    @type files: C{list}
    @param files: Filenames to include in MANIFEST
    """
    f = open("MANIFEST", "w")
    f.write("\n".join(sorted(files)) + "\n")
    f.close()

def gen_desc(doc):
    """
    Pull simple description from docstring

    @type doc: C{str}
    @param doc: Docstring to manipulate
    @rtype: C{str}
    @return: description string suitable for C{Command} class's description
    """
    desc = doc.splitlines()[1].lstrip()
    return desc[0].lower() + desc[1:]

class NoOptsCommand(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class BuildDoc(NoOptsCommand):
    """
    Build project documentation

    @ivar force: Force documentation generation
    """
    description = gen_desc(__doc__)
    user_options = [
        ('force', 'f',
         "Force documentation generation"),
    ]
    boolean_options = ['force']

    def initialize_options(self):
        self.force = False

    def run(self):
        if not DOCUTILS:
            raise DistutilsModuleError("docutils import failed, "
                                       "skipping documentation generation")
        if not PYGMENTS:
            raise DistutilsModuleError("docutils import failed, "
                                       "skipping documentation generation")

        pygments_formatter = HtmlFormatter()

        def pygments_directive(name, arguments, options, content, lineno,
                               content_offset, block_text, state,
                               state_machine):
            try:
                lexer = get_lexer_by_name(arguments[0])
            except ValueError:
                # no lexer found - use the text one instead of an exception
                lexer = get_lexer_by_name('text')
            parsed = highlight(u'\n'.join(content), lexer, pygments_formatter)
            return [nodes.raw('', parsed, format='html')]
        pygments_directive.arguments = (1, 0, 1)
        pygments_directive.content = 1
        directives.register_directive('code-block', pygments_directive)

        for source in sorted(["NEWS", "README"] + glob('doc/*.txt')):
            dest = os.path.splitext(source)[0] + '.html'
            if self.force or newer(source, dest):
                print('Building file %s' % dest)
                if self.dry_run:
                    continue
                publish_cmdline(writer_name='html',
                                argv=['--source-link', '--strict',
                                      '--generator',
                                      '--stylesheet-path=doc/docutils.css',
                                      '--link-stylesheet', source, dest])

        if not EPYDOC:
            raise DistutilsModuleError("epydoc import failed, "
                                       "skipping API documentation generation")
        files = glob("earth_distance/*.py")
        files.append("edist.py")
        if self.force or any(newer(file, "html/index.html") for file in files):
            print('Building API documentation %s' % dest)
            if not self.dry_run:
                saved_args = sys.argv[1:]
                sys.argv[1:] = files
                cli.cli()
                sys.argv[1:] = saved_args
        if os.path.isdir(".hg"):
            if not MERCURIAL:
                raise DistutilsModuleError("Mercurial import failed")
            if self.force or not os.path.isfile("ChangeLog"):
                print('Building ChangeLog from Mercurial repository')
                execute(write_changelog, ("ChangeLog", ))
            else:
                cl_time = os.stat("ChangeLog").st_mtime
                repo = hg.repository(None)
                tip_time = repo.changelog.read(repo.lookup("tip"))[2][0]
                if tip_time > cl_time:
                    execute(write_changelog, ("ChangeLog", ))
        else:
            print("Unable to build ChangeLog, dir is not a Mercurial clone")

class HgSdist(sdist):
    """
    Create a source distribution tarball

    @see: C{sdist}
    @ivar repo: Mercurial repository object
    """
    description = gen_desc(__doc__)

    def initialize_options(self):
        sdist.initialize_options(self)
        if not MERCURIAL:
            raise DistutilsModuleError("Mercurial import failed")
        self.repo = hg.repository(None)

    def get_file_list(self):
        changeset = self.repo.changectx()
        # Include all but Bugs Everywhere data from repo in tarballs
        manifest_files = filter(lambda s: not s.startswith(".be/"),
                                changeset.manifest().keys())
        manifest_files.extend([".hg_version", "ChangeLog"])
        manifest_files.extend(glob("*.html"))
        manifest_files.extend(glob("doc/*.html"))
        for path, dir, filenames in os.walk("html"):
            for file in filenames:
                manifest_files.append(os.path.join(path, file))
        execute(write_manifest, [manifest_files], "Writing MANIFEST")
        sdist.get_file_list(self)

    def make_distribution(self):
        execute(self.write_version, ())
        execute(write_changelog, ("ChangeLog", ))
        sdist.make_distribution(self)

    def write_version(self):
        """
        Store the current Mercurial changeset in a file
        """
        repo_id = hg.short((self.repo.lookup("tip")))
        write_file(".hg_version", ("%s tip\n" % repo_id, ))

class MyClean(clean):
    """
    Clean built and temporary files

    @see: C{clean}
    """
    description = gen_desc(__doc__)

    def run(self):
        clean.run(self)
        if self.all:
            for file in [".hg_version", "ChangeLog", "MANIFEST"] \
                + glob("*.html") + glob("doc/*.html") \
                + glob("earth_distance/*.pyc"):
                os.path.exists(file) and os.unlink(file)
            execute(shutil.rmtree, ("html", True))

class Snapshot(NoOptsCommand):
    """
    Build a daily snapshot tarball
    """
    description = gen_desc(__doc__)
    user_options = []

    def run(self):
        snapshot_name="earth_distance-%s" % strftime("%Y-%m-%d")
        execute(shutil.rmtree, ("dist/%s" % snapshot_name, True))
        execute(self.generate_tree, ("dist/%s" % snapshot_name, ))
        execute(write_changelog, ("dist/%s/ChangeLog" % snapshot_name, ))
        execute(make_archive, ("dist/%s" % snapshot_name, "bztar", "dist",
                               snapshot_name))
        execute(shutil.rmtree, ("dist/%s" % snapshot_name, ))

    def generate_tree(self, snapshot_name):
        """
        Generate a clean Mercurial clone
        """
        check_call(["hg", "archive", snapshot_name])

class MyTest(NoOptsCommand):
    user_options = [
        ('exit-on-fail', 'x',
         "Exit on first failure"),
    ]
    boolean_options = ['exit-on-fail']

    def initialize_options(self):
        self.exit_on_fail = False
        self.doctest_opts = doctest.REPORT_UDIFF|doctest.NORMALIZE_WHITESPACE
        self.extraglobs = {
            "open": test.mock.open,
            "os": test.mock.os,
            "pymetar": test.mock.pymetar,
            "urllib": test.mock.urllib,
        }

class TestDoc(MyTest):
    """
    Test documentation's code examples

    @see: C{MyTest}
    """
    description = gen_desc(__doc__)

    def run(self):
        for filename in sorted(['README'] + glob("doc/*.txt")):
            print('Testing documentation file %s' % filename)
            fails, tests = doctest.testfile(filename,
                                            optionflags=self.doctest_opts,
                                            extraglobs=self.extraglobs)
            if self.exit_on_fail and not fails == 0:
                sys.exit(1)

class TestCode(MyTest):
    """
    Test script and module's doctest examples

    @see: C{MyTest}
    """
    description = gen_desc(__doc__)

    def run(self):
        for filename in sorted(['edist.py'] + glob("earth_distance/*.py")):
            print('Testing module file %s' % filename)
            module = os.path.splitext(filename)[0].replace("/", ".")
            if module.endswith("__init__"):
                module = module[:-9]
            fails, tests = doctest.testmod(sys.modules[module],
                                           optionflags=self.doctest_opts,
                                           extraglobs=self.extraglobs)
            if self.exit_on_fail and not fails == 0:
                sys.exit(1)

if __name__ == "__main__":
    setup(
        name = "earth_distance",
        version = earth_distance.__version__,
        description = sub("C{([^}]*)}", r"\1",
                          earth_distance.__doc__.splitlines()[1]),
        long_description = """\
``earth_distance`` is a collection of `GPL v3`_ licensed modules for working
with points on Earth, or other near spherical objects.  It allows you to
calculate the distance and bearings between points, mangle xearth_/xplanet_
data files, work with online UK trigpoint databases, NOAA_'s weather station
database and other such location databases.

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://www.cs.colorado.edu/~tuna/xearth/
.. _xplanet: http://xplanet.sourceforge.net/
.. _NOAA: http://weather.noaa.gov/
""",
        author = parseaddr(earth_distance.__author__)[0],
        author_email = parseaddr(earth_distance.__author__)[1],
        url = BASE_URL + "projects/earth_distance.html",
        download_url = "%sdata/earth_distance-%s.tar.bz2" \
            % (BASE_URL, earth_distance.__version__),
        packages = ['earth_distance'],
        scripts = ['edist.py'],
        license = earth_distance.__license__,
        keywords = ['navigation', 'xearth', 'trigpointing', 'cities',
                    'baken', 'weather', 'geonames'],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Database',
            'Topic :: Education',
            'Topic :: Scientific/Engineering :: GIS',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: Filters',
        ],
        options = {'sdist': {'formats': 'bztar'}},
        cmdclass = {
            'build_doc': BuildDoc, 'clean': MyClean, 'sdist': HgSdist,
            'snapshot': Snapshot, 'test_doc': TestDoc, 'test_code': TestCode,
        },
    )

