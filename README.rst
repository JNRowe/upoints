``upoints`` - Modules for working with points on Earth
======================================================

|actions| |coveralls| |pypi| |readthedocs|

.. warning::

   At this point ``upoints`` only exists to assist the users who have been using
   it for years, I *absolutely* do **not** recommend its use to new users.

``upoints`` is a collection of `GPL v3`_ licensed modules for working with
points on Earth, or other near spherical objects.  It allows you to calculate
the distance and bearings between points, mangle xearth_/xplanet_ data files,
work with online UK trigpoint databases, NOAA_’s weather station database and
other such location databases.

Previous versions of ``upoints`` were called ``earth_distance``, but the name
was changed as it no longer reflected the majority of uses the packages was
targeted at.

Requirements
------------

``upoints``’s only strict requirements beyond the Python_ standard library are
click_ and lxml_, and as such should run with Python 3.6 or newer.  If
``upoints`` doesn't work with the version of Python you have installed, drop me
a mail_ and I’ll endeavour to fix it.

The module has been tested on many UNIX-like systems, including Linux and OS X,
but it should work fine on other systems too.

To run the tests you’ll need pytest_.  Once you have pytest_ installed you can
run the tests with the following commands:

.. code:: console

    $ pytest tests

Example
-------

The simplest way to show how ``upoints`` works is by example, and here goes::

    >>> from upoints import point
    >>> Home = point.Point(52.015, -0.221)
    >>> Telford = point.Point(52.6333, -2.5000)
    >>> print('%d kM, with an initial bearing of %d°'
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

Contributors
------------

I'd like to thank the following people who have contributed to ``upoints``.

Patches
'''''''

* Cédric Dufour - ``edist.py``’s CSV import, and flight plan output
* Thomas Traber - GPX support enhancements, Points filtering, and some cool
  usage scenarios

Bug reports
'''''''''''

Ideas
'''''

* Kelly Turner - Xearth_ import idea, and copious testing
* Simon Woods

If I've forgotten to include your name I wholeheartedly apologise.  Just drop me
a mail_ and I’ll update the list!

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
earth’s flattening are quite small.  Future versions may change if the
limitation becomes an issue in real use.

Although not really a limitation one should also be careful to use data sources
that are based around the same datum, and even within two data sources that use
the same datum you should make sure they use the same representations.  It isn't
unusual to find data sources from the USA that specify longitudes west of
Greenwich as positive for example.

.. [#] A future release may include more standard output definitions, but there
       is no intention to add “magic” data mangling.

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you've found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _GPL v3: http://www.gnu.org/licenses/
.. _xearth: http://hewgill.com/xearth/original/
.. _xplanet: http://xplanet.sourceforge.net/
.. _Python: https://www.python.org/
.. _geolocation and path cross: doc/geolocation_and_pathcross.html
.. _xearth and path cross: doc/xearth_and_pathcross.html
.. _Trigpointing and point.py: doc/trigpointing_and_point_py.html
.. _Cities and cities.py: doc/python_cities.html
.. _Pythons on a plane: doc/pythons_on_a_plane.html
.. _NOAA: http://weather.noaa.gov/
.. _mail: jnrowe@gmail.com
.. _click: https://pypi.org/project/click/
.. _lxml: http://codespeak.net/lxml/
.. _Sphinx: http://sphinx.pocoo.org/
.. _pytest: https://pypi.org/project/pytest/
.. _issue: https://github.com/JNRowe/upoints/issues

.. |actions| image:: https://img.shields.io/github/workflow/status/JNRowe/upoints/Test%20with%20pytest
   :alt: Test state on master

.. |coveralls| image:: https://img.shields.io/coveralls/github/JNRowe/upoints/master.png
   :target: https://coveralls.io/repos/JNRowe/upoints
   :alt: Coverage state on master

.. |pypi| image:: https://img.shields.io/pypi/v/upoints.png
   :target: https://pypi.org/project/upoints/
   :alt: Current PyPI release

.. |readthedocs| image:: https://img.shields.io/readthedocs/upoints/stable.png
   :target: https://upoints.readthedocs.io/
   :alt: Documentation
