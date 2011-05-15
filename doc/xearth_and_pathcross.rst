xearth and path cross
=====================

As a final comment in the `geolocation and path cross`_ entry I wrote:

  If you think of any good uses for :mod:`upoints`, drop me a mail.
  Cool new uses with attached patches are even better!

The first chunk of feedback I received was from a co-worker, Kelly
Turner, who asked how difficult it would be to use :mod:`upoints` with
xearth_'s marker files.  The answer is not too difficult, not too
difficult at all.

As a little background the reason for wanting access to the data in
marker files is that our internal contact database allows us to export
a file containing a subset of our contact's known current locations
[#]_.  The original reasoning behind the feature was to allow simple
visualisation of a team's members, for example to quickly locate
somebody who is close to a customer's site.

I've reworked the original ``edist.py`` script in to something a little
more generic, and it also now includes a new module,
:mod:`~upoints.xearth`, that can import locations from an xearth marker
file.  Unfortunately, I can't use an example generated from our system
because I don't have permission to publish the data but I'll give an
example of its usage with a public file::

    >>> from upoints import xearth
    >>> earth_markers = urllib.urlopen("http://xplanet.sourceforge.net/Extras/earth-markers-schaumann")
    >>> markers = xearth.Xearths(earth_markers)
    >>> print(repr(markers['Cairo']))
    Xearth(30.05, 31.25, 'Egypt')
    >>> print(markers['Warsaw'])
    Poland (N52.250°; E021.000°)

There are plenty of comments in the :mod:`~upoints.xearth` file, but
what you get from the :class:`~upoints.xearth.Xearths` is a dictionary
with the location name as a key, and value consisting of a tuple of
a :class:`~upoints.point.Point` object and any associated comments from
the source file.

You can use all the methods, such as
:meth:`~upoints.point.Point.distance` and
:meth:`~upoints.point.Point.bearing`, that are defined in the
:class:`~upoints.point.Point` class on :class:`~upoints.xearth.Xearth`
objects.

::

    >>> print("Suva to Tokyo is %i kM" % markers['Suva'].distance(markers['Tokyo']))
    Suva to Tokyo is 7253 kM
    >>> print("Vienna to Brussels on %i°" % markers['Vienna'].bearing(markers['Brussels']))
    Vienna to Brussels on 293°

With the original purpose of the marker file export feature being
finding people local to a customer it would be nice to use
:mod:`~upoints.xearth` to do the same in a more programmatic way, and of
course that is possible too.

::

    >>> Customer = xearth.point.Point(52.015, -0.221)
    >>> for marker in markers:
    ...      distance = Customer.distance(markers[marker])
    ...      if distance < 300:
    ...          print("%i kM - %s, %s" % (distance, marker, markers[marker]))
    57 kM - London, United Kingdom (N51.500°; W000.170°)

Imagining for a second the customer lives in my house, the only marker
within 300 kilometres of me in the city marker file we've imported is
London.

I'll end this entry with similar text to that which created it:  If you
think of any good uses for :mod:`upoints`, drop me a mail.  Cool new
uses with attached patches are even better!

.. [#] All thanks to Simon Woods according to the source code
       repository, so a big thanks to him!

.. _geolocation and path cross: geolocation_and_pathcross.html
.. _xearth: http://hewgill.com/xearth/original/
.. _Mercurial: http://www.selenic.com/mercurial/
