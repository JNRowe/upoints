Geolocation and path cross
==========================

Spurred on by `Seemant's voyage`_ in to geoip_ for deciding on the
location of users writing comments on his website I decided to have
a look in to MaxMind's library with the intent of using it in
a semi-private pathcross_-type application.  Unfortunately, it turns out
it isn't all that simple but there is some fun to be had along the way.

If, like Seemant, you're looking to simply infer the country a specific
IP address originates from then the accuracy of the results from the
geoip library are generally quite good.  Out of the fifty requests
I tried the MaxMind database managed to return the correct results for
all but three, and each of those incorrect results are because of
interesting proxying games being played by their service providers.  The
accuracy would likely be much higher than 94% using a more random
selection of IPs, but I went out of my way to find ones I expected to
return incorrect data(large multinational ISPs, mobile providers and
backbone infrastructure owners).  That being said, the accuracy of the
results drops considerably as you zoom in from country-wide geolocation.

My initial idea had been to use the city_ data to populate an
automatically updating database that could be queried to find people in
the local area [#]_.  Much like some of those oh-so-cool Web 2.0
buzzword laden sites do but without the manual updating, Javascript,
lack of privacy and continual spam.  Me and a few friends already do
such a thing using our published hCalendar_ entries, a heap of nifty
Haskell code and some dirty hack infested XSLT.  It works well, but it
could do so much better given more data.  Unfortunately, the geoip
solution wouldn't work as I envisaged because the precision of the city
data isn't what I naïvely hoped for.

All that aside, and with the failed plan in tatters on the floor, it did
leave a few interesting artefacts to be mulled over instead of doing
Real Work™.

How inaccurate?
---------------

Using MaxMind's `Locate my IP`_ service, which presumably queries their
largest and most current database to attract customers, I'm reported as
being:

    =================== =========================
    Attribute           Data
    =================== =========================
    Your IP Address     62.249.253.214
    Countries           United Kingdom
    Region              O2 (Telford and Wrekin)
    Global Cities       Telford
    Latitude/Longitude  52.6333/-2.5000
    ISP                 Telford
    Organization        Entanet International Ltd
    Netspeed            Dialup
    Domain Name         entanet.co.uk
    =================== =========================

Okay, so at the moment of that query it gets the correct country, net
speed, organisation(my ISP UKFSN_ resells Entanet service) but that is
it [#]_.  Not that we really should be expecting any great accuracy with
the data, because of the way IPs are assigned and used.

Assuming that I would be happy with my location being reported as
Telford, how inaccurate is the data?  In the context of path cross the
question is "would I be likely to travel to Telford for a beer?"  Time
to brush up on spherical trigonometry basics I guess.

The data is reasonably correct in stating a location of N52.6333°;
W2.5000° for Telford.  My location, assuming the WGS-84 datum, is
N52.015°; W0.221°.

Calculating the Great-circle distance between the two coordinates is
relatively easy.  I've hacked together a really simple Python module
called :mod:`upoints` that allows you to calculate the distance between
two points on Earth(or any other approximately spherical body with a few
minor changes).  It offers the Law of Cosines and haversine methods for
calculating the distance, because they're the two I happen to know.

Too inaccurate?
---------------

::

    >>> from upoints import point
    >>> Home = point.Point(52.015, -0.221)
    >>> Telford = point.Point(52.6333, -2.5000)
    >>> print("%i kM" % Home.distance(Telford))
    169 kM

The script above tells us that the distance from my house to Telford is
approximately 170 kM (just over 100 miles for those so inclined), given
that result what is the answer to my question "would I be likely to
travel to Telford for a beer?" Probably not.

The answer isn't that simple though.  Whereas I probably wouldn't travel
170 kM for a beer with my good friend Danny(sorry Danny!), I would
consider travelling 170 kM to meet up with Roger Beckinsale.  It isn't
because Danny is bad company(quite the contrary), it is because I live
eight kilometres from Danny's house and can pop round for a beer
whenever the urge hits me.  Roger on the other hand lives on the Isle of
Lewis, as far North West as the British Isles go, and I haven't seen him
for a year or so.

There is only one conclusion to draw from this:  Accuracy is in the eye
of the beerholder(sorry!).  This conclusion has led me to implement some
new features in our manual path cross tool, all based around the idea of
relative proximity.

The "average" location of a person is important when calculating whether
your paths cross [#]_.  I'm not really interested in seeing when
somebody who works at the same site as me is within twenty kilometres of
me as it would clearly happen a lot, but I'd like to see when somebody
visits from abroad or heads to a show within perhaps thirty kilometres
of my location.

Your proximity alert
--------------------

I've hacked support for relative proximities in to our Haskell tool, but
:mod:`upoints` could be used as the basis to implement something similar
in Python.  Taking Seemant, who lives in Boston, Ma., as an example as
it is his fault I'm playing with Python and geoip :mod:`upoints` can
tell us::

    >>> Seemant = point.Point(42, -71)
    >>> print("%i kM" % Home.distance(Seemant))
    5257 kM

We now have to make a decision about the range for the proximity alert
given that Seemant lives some five thousand kilometres away.  Being that
I owe him many beers for taking care of a lot of my Gentoo_ bugs for me,
I should perhaps set the range to be quite low and save myself some
money.

Without taking in to account my stinginess it seems that a reasonable
target range is the square root of the home-to-home distance.  From
looking at the events I've tagged to meet up with someone in the past
year it seems that all of them fall surprisingly evenly within the
square root of the distance we live from each other.

Marginally weighted square roots might be more appropriate in reality
because there are some anomalies.  For example, I travelled from
Kensington to West India Dock after LinuxWorld last year to catch up
with friends who live a few minutes up the A1 from my house.  The reason
being for most of last year our schedules seemed to be stopping us
meeting up locally, but even that fell within 1.5 times the square root.
Adding in a key to show the last face to face meeting, would probably
allow one to assign weighting automatically.  Continuing the Seemant
example would mean increasing his range significantly, being
a BTS and email-only contact.

::

    >>> import math
    >>> math.sqrt(Home.distance(Seemant))
    72.51154203831521

If we forget about the anomalies, and just take the square root as being
correct I can populate the relationship for Seemant with a 73 kM limit.
I'm sure each person involved will have their own idea of what
a reasonable limit would be, so that should be user defined.

Conclusions
-----------

geoip wasn't, and isn't going to become, a viable way to update the path cross
database and until more mobile devices come equipped with :term:`GPS` automated
updates just aren't going to be usable.  If you want to start claiming those
owed beers the answer is to publish your schedule in valid hCalendar, and
publish a hCard containing your home location so you get the correct range
allowance.

If you think of any good uses for :mod:`upoints`, drop me a mail.  Cool
new uses with attached patches are even better!

Bonus
-----

Having already implemented the basic class and distance method,
I figured I may as well add bearing calculation too.  It's only 4 lines
of code, so why not?

::

    >>> print("A heading of %i° will find the beers!" % Home.bearing(Telford))
    A heading of 294° will find the beers!

.. [#] By "automatically updating" I mean simply a ping-and-forget
       service that listens for a user ID and location and updates the
       database.  My test code was a simple five line Python_ script, it
       literally reads a configuration file for the user ID and pings my
       server.

.. [#] I guess you could argue it gets the US area code, US metro code
       and zipcode correct as none of them apply here.

.. [#] The implementation actually considers the mode, and not the
       average, in calculating "home" locations.  It makes it less prone
       to errors when people only report long distance changes, because
       the clustering isn't so obvious.  If more people hosted
       a complete hCard_, we wouldn't even need to calculate this.

.. _Seemant's voyage: http://kulleen.org/seemant/blog/2007/apr/16/building-my-django-weblog-part3/
.. _geoip: http://www.maxmind.com/geoip/api/c.shtml
.. _pathcross: http://www.w3.org/wiki/PathCross
.. _city: http://www.maxmind.com/app/city
.. _Python: http://www.python.org/
.. _Locate my IP: http://www.maxmind.com/app/locate_my_ip
.. _UKFSN: http://www.ukfsn.org/
.. _hCalendar: http://microformats.org/wiki/hcalendar
.. _hCard: http://microformats.org/wiki/hcard
.. _Gentoo: http://www.gentoo.org/
.. _Mercurial: http://www.selenic.com/mercurial
.. _xearth: http://hewgill.com/xearth/original/
