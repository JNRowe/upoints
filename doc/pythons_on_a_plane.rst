Pythons on a plane
==================

In what is probably the final spin-off from `geolocation and path
cross`_ we'll be using the :mod:`upoints` modules to work with airport
locations.  This can be useful if you'd like to calculate how far you've
travelled in a certain period, or just as a large database for
calculating rough distances between other places using the closest
airports as locations because of their abundance.

NOAA publishes an enormous amount of world weather information,
and often it is keyed to airport location's weather stations.  Unlike
many of the commercial weather data companies NOAA publish their
data in clean, well defined formats, and along with the weather data they also
publish extensive location data for the weather stations they monitor.
And many thanks to them, because we can use their databases to populate
our local geolocation databases.

::

    >>> from upoints import (point, weather_stations)
    >>> WMO_stations_database = urllib.urlopen("http://weather.noaa.gov/data/nsd_bbsss.txt")
    >>> WMO_stations = weather_stations.Stations(WMO_stations_database)

The above snippet will import the WMO identifier keyed database
available from the `meteorological station location information page`_.
They also provide a database keyed with ICAO identifiers, which
can also be imported::

    >>> ICAO_stations_database = urllib.urlopen("http://weather.noaa.gov/data/nsd_cccc.txt")
    >>> ICAO_stations = weather_stations.Stations(ICAO_stations_database, "ICAO")

The WMO indexed database contains 11548 entries and the
ICAO keyed database contains 6611 entries as of 2007-05-30.
Unfortunately, the WMO database isn't a superset of the
ICAO data so you either have to choose one, work with duplicates
or import both and filter the duplicates.

Another thing to consider because of the size of the database is whether
you need to operate on all the entries at once.  Maybe you only want to
work with entries in the UK::

    >>> UK_locations = dict(x for x in ICAO_stations.items()
    ...                     if x[1].country == "United Kingdom")

Let us imagine for a minute that next month you're flying from London
Luton to our office in Toulouse, then dropping by Birmingham for GUADEC,
and returning to Stansted.  If we assume that the planes fly directly
along Great Circles and don't get stuck in holding patterns waiting to
land then we can calculate the distance for the whole journey quite
easily.

::

    >>> Europe = dict(x for x in ICAO_stations.items() if x[1].wmo == 6)
    >>> del(ICAO_stations)
    >>> print(len(Europe))
    1130

First we can see that the trip is entirely based in Europe, and
according to the `station location page`_ all the European stations are
located within WMO region 6.  If we only work with the region
6 locations then our operating database need only contain 1130 entries,
and if we wished we could release the full database containing 10000
entries we don't need from memory using code similar to the snippet
above [#]_.

::

    >>> Trip = point.Points([Europe[i] for i in ('EGGW', 'LFBO', 'EGBB', 'EGSS')])
    >>> legs = list(Trip.inverse())

    >>> print("%i legs" % (len(Trip) - 1))
    3 legs
    >>> for i in range(len(Trip) - 1):
    ...     print("  * %s to %s" % (Trip[i].name, Trip[i+1].name))
    ...     print("    - %i kilometres on a bearing of %i degrees" % (legs[i][1], legs[i][0]))
      * Luton Airport  to Toulouse / Blagnac
        - 923 kilometres on a bearing of 171 degrees
      * Toulouse / Blagnac to Birmingham / Airport
        - 1006 kilometres on a bearing of 347 degrees
      * Birmingham / Airport to Stansted Airport
        - 148 kilometres on a bearing of 114 degrees
    >>> print("For a total of %i kilometres" % sum(i[1] for i in legs))
    For a total of 2078 kilometres

The :class:`~upoints.weather_stations.Station` class inherits from
:class:`~upoints.trigpoints.Trigpoint` and as such you can use the
functions and methods defined for it with
:class:`~upoints.weather_station.Station` objects.  You could, for
example, create a nice graphical view of your trip with xplanet_::

    >>> Trip = dict(zip(("2007-06-29", "2007-06-30", "2007-07-12",
    ...                  "2007-07-14"),
    ...                 Trip))
    >>> f = open("trip.txt", "w")
    >>> from upoints import utils
    >>> f.write("\n".join(utils.dump_xearth_markers(Trip, "name")))
    >>> f.close()

.. figure:: .static/xearth_trip_mini.png
   :alt: Xplanet showing the locations for a small European trip
   :width: 256
   :height: 192
   :target: .static/xearth_trip.png

The code above will create a file named :file:`trip.txt` that can be
used with xplanet or xearth_.  It actually produces a reasonably
accurate, and quite useful graphical representation of a trip.  An
example of the output with xplanet can be seen on the right.

If you'd prefer to see locations marked up with dates, perhaps as an aid
to your own `path cross`_ suite, simply don't set the :attr:`name`
parameter in your call to :func:`~upoints.utils.dump_xearth_markers`.
Also, as the function only requires a dictionary of
:class:`~upoints.trigpoints.Trigpoint`-style objects you could apply
:func:`filter` and :func:`map` expressions to the objects to generate
your own labels for the markers.

.. figure:: .static/xplanet_trip_date_mini.png
   :alt: Xplanet showing the location points and dates for a trip
   :width: 256
   :height: 192
   :target: .static/xplanet_trip_date.png

There is a wealth of Sphinx_ generated HTML output in the tarball, including
documentation and usage examples.  If you still have any questions after reading
the documentation, drop me a mail_ and I'll do my best to answer your questions.
Also, I'd love to hear from you if come up with any clever uses for for the
modules in :mod:`upoints`.

.. [#] I've personally taken to creating and using :mod:`cPickle` dumps
       of the database, where each WMO region is stored in a separate
       file.  If you do this you end up with some interesting results
       including the 123 locations from the Antarctic, and the
       8 obviously classifiable locations missing an WMO region in the
       data file.  I personally found it quite interesting that the list
       of entries by region is Europe(30%), Asia(30%), North and Central
       America(12%).  I'd expected it be more along the lines of one
       third Asia and one quarter each for Europe and North America with
       the rest split reasonably evenly.

.. _geolocation and path cross: geolocation_and_pathcross.html
.. _Mercurial: http://www.selenic.com/mercurial/
.. _meteorological station location information page: http://weather.noaa.gov/tg/site.shtml
.. _station location page: http://weather.noaa.gov/tg/site.shtml
.. _mail: jnrowe@gmail.com
.. _xplanet: http://xplanet.sourceforge.net/
.. _xearth: http://hewgill.com/xearth/original/
.. _path cross: http://www.w3.org/wiki/PathCross
.. _Sphinx: http://sphinx.pocoo.org/
