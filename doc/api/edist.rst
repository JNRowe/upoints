``edist``
=========

.. module:: upoints.edist
   :synopsis: Simple command line coordinate processing

.. autoclass:: LocationsError
.. autoclass:: NumberedPoint
.. autoclass:: NumberedPoints

.. autofunction:: read_locations
.. autofunction:: read_csv
.. autofunction:: main


Commands
--------

.. autofunction:: cli(ctx, verbose, config, csv_file, format, units, location)
.. autofunction:: bearing(globs, string)
.. autofunction:: destination(globs, locator, distance, bearing)
.. autofunction:: display(globs, locator)
.. autofunction:: distance(globs)
.. autofunction:: final_bearing(globs, string)
.. autofunction:: flight_plan(globs, speed, time)
.. autofunction:: range(globs, distance)
.. autofunction:: sunrise(globs)
.. autofunction:: sunset(globs)

.. spelling::

    Config
    Todo
    config
    dict
    upoints
