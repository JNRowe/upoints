Cities and cities.py
====================

A colleague pointed me to the `GNU miscfiles`_ cities database after
I posted `geolocation and path cross`_, suggesting that it would be
a useful database to support.  Being that it includes five hundred
places around the globe, and I already have the database installed,
I have to agree.

GNU miscfiles is a package of, well miscellaneous files.  It contains,
amongst other things a list of world currencies, languages and the file
we're looking at today :file:`cities.dat`.

In v1.4.2, the version I have installed, :file:`cities.dat` contains 497
entries.  The file is a simple flat Unicode database, with records
separated by ``//``, a format that would be as well suited to processing
with awk_ as it would with Python_.

.. literalinclude:: ../tests/data/cities.dat
   :lines: 155-181

You don't need to hand process the data though, I've added
:mod:`~upoints.cities` to the ``upoints`` tarball that takes care of
importing the data.  When you import the entries with
:meth:`~upoints.cities.Cities.import_locations` it returns a dictionary
of :class:`~upoints.cities.City` objects that are children of the
:class:`~upoints.trigpoints.Trigpoint` objects defined for `Trigpointing
and point.py`_

On my Gentoo_ desktop the cities database is installed as
:file:`/usr/share/misc/cities.dat`, and can be imported as simply as::

    >>> from upoints import cities
    >>> Cities = cities.Cities(open("/usr/share/misc/cities.dat"))

And the imported database can be used in a variety of ways::

    >>> print("%i cities" % len(Cities))
    497 cities
    >>> print("Cities larger with more than 8 million people")
    Cities larger with more than 8 million people
    >>> for city in Cities:
    ...     if city.population > 8000000:
    ...         print("  %s - %s" % (city.name, city.population))
       Bombay - 8243405
       Jakarta - 9200000
       Moskwa - 8769000
       Sao Paolo - 10063110
       Tokyo - 8354615
       Mexico - 8831079
    >>> print("Mountains")
    Mountains
    >>> for city in Cities:
    ...     if city.ptype == "Mountain":
    ...         print("  %s" % city.name)
       Aconcagua
       Popocatepetl

You can recreate the database as a smoke test using the following::

    >>> f = open("cities.dat", "w")
    >>> f.write("\n//\n".join(map(str, Cities)))
    >>> f.close()

unfortunately the files aren't simply comparable using :command:`diff`
because of some unusual formatting in the original file, but visually
scanning over the :command:`diff -w` output to ignore the whitespace
changes shows that we have a correct export.

The :class:`~upoints.cities.City` class inherits
:class:`~upoints.trigpoints.Trigpoint` which in turn inherits
:class:`~upoints.point.Point`, and therefore has all the same methods
they do.  This allows you to calculate distances and bearings between
the class:`~upoints.cities.City` objects or any other derivative object
of the parent classes.  For example, you could use the
:func:`~upoints.utils.dump_xearth_markers` function::

    >>> from upoints.utils import dump_xearth_markers
    >>> scottish_markers = dict((x.identifier, x) for x in Cities
    ...                         if x.region == "Scotland")
    >>> print("\n".join(dump_xearth_markers(scottish_markers, "name")))
    57.150000 -2.083000 "Aberdeen" # 1
    55.950000 -3.183000 "Edinburgh" # 83
    55.867000 -4.267000 "Glasgow" # 92

Take a look at the Sphinx_ generated documentation that is included in the
tarball to see what can be done.

.. _GNU miscfiles: http://directory.fsf.org/project/miscfiles/
.. _awk: http://www.gnu.org/software/gawk/gawk.html
.. _geolocation and path cross: geolocation_and_pathcross.html
.. _Mercurial: http://www.selenic.com/mercurial/
.. _Python: http://www.python.org/
.. _Trigpointing and point.py: trigpointing_and_point_py.html
.. _gentoo: http://www.gentoo.org/
.. _Sphinx: http://sphinx.pocoo.org/
