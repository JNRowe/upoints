The MERLIN system
=================

Introduction
------------

MERLIN_, the Multi-Element Radio Linked Interferometer Network, radio
telescope array that is spread throughout central England and Wales.
The interesting aspect of MERLIN for our uses is high-quality, minimally
diverse location identifiers are available publicly.  They make
a reasonably useful test case for :mod:`upoints` objects across small
geographic distances.

According to the official MERLIN documentation the locations of
the array elements are:

+------------------+-----------------------------+------------------------------+
| Name             | Latitude                    | Longitude                    |
+==================+=============================+==============================+
| Cambridge        | 52°10′06.48″N               | 000°02′23.25″E               |
+------------------+-----------------------------+------------------------------+
| Darnhall         | 53°08′38.40″N               | 002°32′45.57″W               |
+------------------+-----------------------------+------------------------------+
| Defford          | 52°05′27.61″N               | 002°08′09.62″W               |
+------------------+-----------------------------+------------------------------+
| Knocking         | 52°46′40.83″N               | 003°00′39.55″W               |
+------------------+-----------------------------+------------------------------+
| Lovell Telescope | 53°14′10.50″N               | 002°18′25.74″W               |
+------------------+-----------------------------+------------------------------+
| Mark II          | 53°13′51.62″N               | 002°18′34.16″W               |
+------------------+-----------------------------+------------------------------+
| Pickmere         | 53°16′44.42″N               | 002°26′41.98″W               |
+------------------+-----------------------------+------------------------------+

Using :class:`~upoints.point.Point` objects
-------------------------------------------

We can create a Python dictionary containing the locations of the array
very simply::

    >>> from upoints.point import (Point, KeyedPoints)
    >>> from upoints import utils
    >>> MERLIN = KeyedPoints({
    ...     'Cambridge': Point((52, 10, 6.48), (0, 2, 23.25)),
    ...     'Darnhall': Point((53, 8, 38.4), (-2, -32, -45.57)),
    ...     'Defford': Point((52, 5, 27.61), (-2, -8, -9.62)),
    ...     'Knocking': Point((52, 46, 40.83), (-3, -0, -39.55)),
    ...     'Lovell Telescope': Point((53, 14, 10.5), (-2, -18, -25.74)),
    ...     'Mark II': Point((53, 13, 51.62), (-2, -18, -34.16)),
    ...     'Pickmere': Point((53, 16, 44.42), (-2, -26, -41.98)),
    ... })

As a simple smoke test the MERLIN website contains a `location page`_
which states the longest baseline in the array is Cambridge to Knocking
at 217 kM, and also that the shortest baseline is between the Jodrell
Bank site and Pickmere at 11.2 kM.  The :class:`~upoints.point.Point`
object's :meth:`~upoints.point.Point.distance` method can calculate
these distances for us quite simply::

    >>> "%.3f kM" % MERLIN['Cambridge'].distance(MERLIN['Knocking'])
    '217.312 kM'
    >>> "%.3f kM" % MERLIN['Lovell Telescope'].distance(MERLIN['Pickmere'])
    '10.322 kM'
    >>> "%.3f kM" % MERLIN['Mark II'].distance(MERLIN['Pickmere'])
    '10.469 kM'

.. Note::
   The web page gives the shortest baseline as the distance from
   Pickmere to Jodrell Bank, but doesn't give a location for Jodrell
   Bank.  However, as can be seen from the example above the two array
   elements based at Jodrell Bank(Lovell Telescope and the Mark II) are
   giving a plausible value.

Using :func:`~upoints.utils.dump_xearth_markers`
------------------------------------------------

The MERLIN website also contains a `layman description page`_
that has a nice map showing the locations of the array elements, we can
create a similar image with xplanet_ or xearth_::

    >>> print("\n".join(utils.dump_xearth_markers(MERLIN)))
    52.168467 0.039792 "Cambridge"
    53.144000 -2.545992 "Darnhall"
    52.091003 -2.136006 "Defford"
    52.778008 -3.010986 "Knocking"
    53.236250 -2.307150 "Lovell Telescope"
    53.231006 -2.309489 "Mark II"
    53.279006 -2.444994 "Pickmere"

The map on the website contains a few more locations presumably to help
the viewer with orientation, but the image below is useful as a good
approximation.  And, of course, the locations could be supplemented
either by hand, or by using one of the other :mod:`upoints` supported
databases.

.. image:: .static/merlin_xearth.png
   :alt: xearth displaying array locations

Examining local solar time
--------------------------

Imagine the contrived example that we were allowed access to each of the
locations and we're hoping to catch the end of an imaginary partial
eclipse occurring at 05:45 UTC on 2007-09-20 we can find the best
location to view from quite simply.  Clearly, the most important factor
is whether the Sun will be visible at the given time and this can be
calculated very easily::

    >>> import datetime
    >>> for name, rise in MERLIN.sunrise(datetime.date(2007, 9, 20)):
    ...     if rise > datetime.time(5, 45): continue
    ...     print(name)
    ...     print("     - sunrise @ %s UTC" % rise.strftime("%H:%M"))
    Cambridge
         - sunrise @ 05:41 UTC

This simple code snippet shows us that we should set up our equipment at
the Cambridge site, which lucky for me is only a short trip up the road::

    >>> Home = Point(52.015, -0.221)
    >>> print("%i kM" % Home.distance(MERLIN['Cambridge']))
    24 kM

Comparisons with other :class:`~upoints.point.Point`-type objects
-----------------------------------------------------------------

In our contrived example above we may wish to travel only if the weather
will be warm enough that we're unlikely to freeze to death(that risk is
only acceptable for a full eclipse), and we can use the other
:mod:`upoints` tools to find closest weather station quite easily::

    >>> from upoints import weather_stations
    >>> ICAO_stations_database = urllib.urlopen("http://weather.noaa.gov/data/nsd_cccc.txt")
    >>> ICAO_stations = weather_stations.Stations(ICAO_stations_database, "ICAO")
    >>> calc_distance = lambda (name, location): MERLIN['Cambridge'].distance(location)
    >>> station_id, station_data = sorted(ICAO_stations.items(), key=calc_distance)[0]
    >>> print(station_data)
    Cambridge (N52.200°; E000.183°)

The :func:`calc_distance` function simply returns the distance from the
Cambridge MERLIN station to the provided station, and we use it as the
sorting method to discover the closest weather station from the NOAA_
database.  The ``station_id`` and ``station_data`` variables are set to
the first result from the sorted list of station distances, which thanks
to the :func:`calc_distance` sorting method are the details of the
closest weather station.

As we're already using Python_ we may as well use Python to fetch the
weather data for the station using the ever useful pymetar_ library.

::

    >>> report = pymetar.ReportFetcher(station_id).FetchReport()
    >>> report_decoded = pymetar.ReportParser().ParseReport(report)
    >>> print("%i°C @ %s" % (report_decoded.getTemperatureCelsius(),
    ...                      report_decoded.getISOTime()))
    10°C @ 2007-11-28 19:20:00Z

.. _MERLIN: http://www.merlin.ac.uk/
.. _location page: http://www.merlin.ac.uk/user_guide/OnlineMUG-ajh/newch0-node62.html
.. _layman description page: http://www.merlin.ac.uk/about/layman/merlin.html
.. _xplanet: http://xplanet.sourceforge.net/
.. _xearth: http://hewgill.com/xearth/original/
.. _NOAA: http://weather.noaa.gov/
.. _Python: http://www.python.org/
.. _pymetar: http://www.schwarzvogel.de/software-pymetar.shtml
