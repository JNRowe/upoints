Imagine ``upoints2`` was being built…
=====================================

|modref| was never supposed to last this long, it was never really
supposed to be a *released* package at all.  Like all bad habits it just grew
and grew, became comfortable in the same way that cancer sticks and their
associated yellow fingers became comfortable, and eventually led itself to its
own demise.

If ``upoints2`` was on the horizon, it would:

* Be simpler

** Generic ``Position`` with attached metadata, not specialised with combined
   metadata

** Only support reasonably new versions of Python, just drop support for old
   versions instead of adding support for newer versions to the tower of
   workarounds

* Be cleaner

** |modref| grew in the :abbr:`REPL (Read–Eval–Print Loop)` and arranged
   itself by being pasted in to files as and when the mood suited

** While memory reduction with hacks [#]_ were necessary eleven years ago, it
   really isn’t now.  And if it was, a special case for that would be more
   useful than heaps of ugliness everywhere you look

.. rubric:: Footnotes

.. [#] Semi-dynamic ``__slots__`` abuse is the perfect awful example here
