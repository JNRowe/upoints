#! /usr/bin/env python
# coding=utf-8
"""setup.py - Setuptools tasks and config for upoints."""
# Copyright © 2007-2017  James Rowe <jnrowe@gmail.com>
#                        Petr Viktorin <encukou@gmail.com>
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

import imp
import io
import sys

from setuptools import setup
from setuptools.command.test import test

class PytestTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = ['tests/', ]
        self.test_suite = True

    def run_tests(self):
        from sys import exit
        from pytest import main
        exit(main(self.test_args))


# Hack to import _version file without importing upoints/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
ver_file = open('upoints/_version.py')
_version = imp.load_module('_version', ver_file, ver_file.name,
                           ('.py', ver_file.mode, imp.PY_SOURCE))


def parse_requires(file):
    deps = []
    req_file = open('extra/%s' % file)
    entries = map(str.strip, req_file.readlines())
    for dep in entries:
        if dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
            continue
        elif ';' in dep:
            dep, marker = dep.split(';')
            if not eval(marker.strip(),
                        {'python_version': '%s.%s' % sys.version_info[:2]}):
                continue
        deps.append(dep)
    return deps


install_requires = parse_requires('requirements.txt')

setup(
    name='upoints',
    version=_version.dotted,
    description='Modules for working with points on Earth',
    long_description=io.open('README.rst', encoding='UTF-8').read(),
    author='James Rowe',
    author_email='jnrowe@gmail.com',
    url='https://github.com/JNRowe/upoints/',
    license='GPL-3',
    keywords=['baken', 'cities', 'geonames', 'gis', 'gps', 'gpx', 'navigation',
              'nmea', 'openstreetmap', 'trigpointing', 'weather', 'xearth'],
    packages=['upoints', ],
    include_package_data=True,
    package_data={},
    entry_points={'console_scripts': ['edist = upoints.edist:main', ]},
    zip_safe=False,
    classifiers=[
        'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
    ],
    obsoletes=['earth_distance'],
    install_requires=install_requires,
    tests_require=['pytest', 'pytest-cov'],
    tests_require=['pytest', ],
    cmdclass={'test': PytestTest},
)
