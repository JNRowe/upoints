Contributing
============

Pull requests are most welcome, but I'd appreciate it if you could follow the
guidelines below to make it easier to integrate your changes.  These are
guidelines however, and as such can be broken if the need arises or you just
want to convince me that your style is better.

* `PEP 8`_, the style guide, should be followed where possible.
* `PEP 257`_, the docstring style guide, should be followed at all times
* While support for Python versions prior to v2.4 may be added in the future if
  such a need were to arise, you are encouraged to use v2.4 features now.
* Tests *must not* span network boundaries, see ``test.mock`` for workarounds.
* All new classes and methods should be accompanied by new tests, and Sphinx_
  ``autodoc``-compatible descriptions.

New examples for the ``doc`` directory are as appreciated as code changes.

.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _PEP 257: https://www.python.org/dev/peps/pep-0257/
.. _Sphinx: http://sphinx.pocoo.org/
