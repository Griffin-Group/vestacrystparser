parser
======

Classes and functions in the :mod:`parser` module.
Besides :class:`.VestaFile` (which is listed separately and can be imported from
the top-level), the most important is :class:`.VestaSection`, which you need to
manipulate for low-level API calls.
The other objects are probably only useful for developers.

.. autoclass:: vestacrystparser.parser.VestaSection
    :members:
    :special-members:
    :exclude-members: __weakref__

.. autoclass:: vestacrystparser.parser.VestaPhase
    :members:
    :special-members:
    :exclude-members: __weakref__

.. automodule:: vestacrystparser.parser
    :members:
    :exclude-members: VestaFile, VestaSection, VestaPhase
    :member-order: alphabetical