``upoints``
===========

User-visible changes
--------------------

.. contents::

0.12.0 - 2014-01-27
-------------------

* Python 3 support, but Python 2.6 is now the lowest supported version
* New support files to handle dependencies for pip_ users in ``extra/``
* GPX 1.0 support has been removed
* KML support for versions older than 2.2 has been removed
* Unicode output guessing has been removed from ``edist``
* Added a zsh completion script for edist
* PEP-3101_ format support
* aaargh_ is now required
* lxml_ is no longer optional, and is now required for XML support
* The testsuite now requires expecter_ and nose2_
* Added support for metadata in GPX files
* Added support for route data in GPX files

.. _pip: https://crate.io/packages/pip/
.. _pep-3101: http://www.python.org/dev/peps/pep-3101/
.. _aaargh: https://crate.io/packages/aaargh/
.. _expecter: https://crate.io/packages/expecter/
.. _nose2: https://crate.io/packages/nose2/

0.11.0 - 2008-05-20
-------------------

* This is likely to be the *final* non-bugfix release before v1.0.0 is cut, if
  you don't like how something works now is the time to speak up!
* This package has been renamed ``upoints`` from ``earth_distance`` to better
  reflect its usage, and as a bonus it is more compliant with PEP-8_'s naming
  guidelines
* Added support for a generic ``Point`` object container type
* Support for reading OpenCellID_ exports
* Can now use lxml_ for XML processing on systems where ``cElementTree`` isn't
  available
* Python "egg" packages can now be built if setuptools_ is installed

.. _OpenCellID: http://opencellid.org/
.. _lxml: http://codespeak.net/lxml/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _PEP-8: http://www.python.org/dev/peps/pep-0008/

0.10.0 - 2008-03-27
-------------------

* Support for reading and writing `GPX v1.0`_ files
* Support for GPX ``trkpt`` elements

.. _GPX v1.0: http://www.topografix.com/GPX/1/0

0.9.0 - 2008-01-25
------------------

* Support for reading OpenStreetMap_ exports
* Support for reading configuration file in ``edist.py`` for enable simple named
  location support.

.. _OpenStreetMap: http://wiki.openstreetmap.org/

0.8.0 - 2008-01-09
------------------

* Support for reading `GPS eXchange`_ format

.. _GPS eXchange: http://www.topografix.com/GPX/

0.7.0 - 2008-01-08
------------------

* Support for reading `NMEA 0183`_ formatted data

.. _NMEA 0183: http://en.wikipedia.org/wiki/NMEA_0183

0.6.0 - 2007-12-14
------------------

* Support for importing KML_ data files
* Support for importing zoneinfo zone descriptions
* Latitude and longitude values are now managed attributes, and can be updated
  in place(as can Baken Maidenhead locators)
* Locations now support a much prettier Unicode output mode
* ``edist.py`` a new user script that allows one to manipulate locations in
  various ways from the command line
* Package no longer requires ``make`` for development functions
* Tests no longer span network boundaries, and should run on any default Python
  install once initially seeded

.. _KML: http://code.google.com/apis/kml/documentation/kmlreference.html

0.5.0 - 2007-01-01
------------------

* All ``Point`` children now have dictionary-based collection objects, named
  ``<base>s``
* Import and export routines of ``Point`` objects have now moved in to their
  respective collection objects

0.4.0 - 2007-10-02
------------------

* Support for baken_ data files in ``baken``

.. _baken: http://www.qsl.net/g4klx/

0.3.0 - 2007-10-01
------------------

* Support for geonames_ database exports in ``geonames``
* Support for ISO 6709 coordinate strings in ``utils.from_iso6709`` and
  ``utils.to_iso6709``
* Support for Maidenhead locator strings in ``utils.from_grid_locator`` and
  ``utils.to_grid_locator``
* Support for creating Xearth_ markers files with any ``Point``-compatible
  objects using ``utils.dump_xearth_markers``

.. _geonames: http://www.geonames.org/
.. _Xearth: http://hewgill.com/xearth/original/
