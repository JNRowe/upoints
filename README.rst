``upoints`` - Modules for working with points on Earth
======================================================

.. warning::

   At this point ``upoints`` only exists to assist the users who have been using
   it for years, I *absolutely* do **not** recommend its use to new users.

Introduction
------------

``upoints`` is a collection of `GPL v3`_ licensed modules for working with
points on Earth, or other near spherical objects.  It allows you to calculate
the distance and bearings between points, mangle xearth_/xplanet_ data files,
work with online UK trigpoint databases, NOAA_'s weather station database and
other such location databases.

Previous versions of ``upoints`` were called ``earth_distance``, but the name
was changed as it no longer reflected the majority of uses the packages was
targeted at.

Requirements
------------

``upoints``'s only strict requirements beyond the Python_ standard library are
aaargh_ and lxml_, and as such should run with Python 2.6 or newer [#]_.  If
``upoints`` doesn't work with the version of Python you have installed, drop me
a mail_ and I'll endeavour to fix it.

The modules have been tested on many UNIX-like systems, including Linux and OS
X, but it should work fine on other systems too.  The modules and scripts
contain a large collection of tests that can be checked with nose2_.

.. [#] If you still use Python v2.5 only small changes are required, for example
       to the property definitions.

.. [#] Some tests may fail due to rounding errors depending on the system the
       tests are being run on, but such instances should be obvious even to the
       casual user and some effort has been put in to reduce the likelihood of
       such failures.

Example
-------

The simplest way to show how ``upoints`` works is by example, and here goes::

    >>> from upoints import point
    >>> Home = point.Point(52.015, -0.221)
    >>> Telford = point.Point(52.6333, -2.5000)
    >>> print("%d kM, with an initial bearing of %d°"
    ...       % (Home.distance(Telford), Home.bearing(Telford)))
    169 kM, with an initial bearing of 294°

All the class definitions, methods and independent functions contain hopefully
useful usage examples in the docstrings.  The API documentation is built with
Sphinx_, and is available in ``doc/html/api/``.

There is some accompanying text and examples for ``point.py``, formerly
``edist.py``, available in `geolocation and path cross`_.  More examples are
available for ``xearth.py`` in `xearth and path cross`_.  Some background and
more examples for ``trigpoints.py`` is online in `Trigpointing and point.py`_.
Usage examples for ``cities.py`` is available in `Cities and cities.py`_.  And
finally, `Pythons on a plane`_ contains information on ``weather_stations.py``.

Thanks
------

The following people have submitted patches, testing and feedback:

* Cédric Dufour - ``edist.py``'s CSV import, and flight plan output
* Thomas Traber - GPX support enhancements, Points filtering, and some cool
  usage scenarios
* Kelly Turner - Xearth_ import idea, and copious testing
* Simon Woods - Testing

API Stability
-------------

API stability isn't guaranteed across versions, although frivolous changes won't
be made.

When ``upoints`` 1.0 is released the API will be frozen, and any changes which
aren't backwards compatible will force a major version bump.

Limitations
-----------

The modules assume the caller will take care of significant digits, and output
formatting [#]_.  All results are returned with whatever precision your Python
install or system generates; unintuitive float representation, rounding errors,
warts and all.

The reasoning is simple, the caller should always know what is required and any
heuristics added to the code would be just that -- guesses, which can and will
be wrong.

The ``upoints`` modules do not take flattening in to account, as in calculations
based in most populated areas of the earth the errors introduced by ignoring the
earth's flattening are quite small.  Future versions may change if the
limitation becomes an issue in real use.

Although not really a limitation one should also be careful to use data sources
that are based around the same datum, and even within two data sources that use
the same datum you should make sure they use the same representations.  It isn't
unusual to find data sources from the USA that specify longitudes west of
Greenwich as positive for example.

.. [#] A future release may include more standard output definitions, but there
       is no intention to add "magic" data mangling.

Bugs
----

If you find a bug don't hesitate to drop me a mail_ preferably including
a minimal testcase, or even better a patch!

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://hewgill.com/xearth/original/
.. _xplanet: http://xplanet.sourceforge.net/
.. _Python: http://www.python.org/
.. _geolocation and path cross: doc/geolocation_and_pathcross.html
.. _xearth and path cross: doc/xearth_and_pathcross.html
.. _Trigpointing and point.py: doc/trigpointing_and_point_py.html
.. _Cities and cities.py: doc/python_cities.html
.. _Pythons on a plane: doc/pythons_on_a_plane.html
.. _NOAA: http://weather.noaa.gov/
.. _mail: jnrowe@gmail.com
.. _aaargh: https://crate.io/packages/aaargh/
.. _lxml: http://codespeak.net/lxml/
.. _Sphinx: http://sphinx.pocoo.org/
.. _nose2: https://crate.io/packages/nose2/
