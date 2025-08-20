Usage
=====

.. _installation:

Installation
------------

At release I'll probably put this on pip, at which point you can do

.. code-block:: console

    pip install vestacrystparser

But that isn't available yet.
Until then, it lives on GitHub, at https://github.com/GriffinGroup/vestacrystparser.

Modifying VESTA files
---------------------

You can load an existing VESTA file as so.

.. code-block:: python

    from vestacrystparser import VestaFile

    vfile = VestaFile("file.vesta")

:class:`.VestaFile` holds all the data for a VESTA file and provides methods for
inspecting and modifying that data.
For example, you can change the view boundary and hide the compass with,

.. code-block:: python

    vfile.set_boundary(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)
    vfile.set_compass_visibility(False)

The methods of VestaFile are not yet comprehensive.
If you need to perform an action not covered by the high-level API, you can
modify the sections directly (which are represented with :class:`.VestaSection`
objects).
Beware that no safety checks are performed here, so be careful not to leave the
sections in a corrupt state.

.. code-block:: python

    section1 = vfile["BOUND"]
    section1.data[0] = [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5]
    section2 = vfile["COMPS"]
    section2.inline[0] = 0

For VESTA files with multiple phases, :meth:`.VestaFile.set_current_phase`
should be used to change the phase referenced by default by the API.
Alternatively, :meth:`.VestaFile.__getitem__` accepts
a second argument, the index of the desired phase.

E.g. The following two code blocks both unset the compass visibility for
Phase 1 (phase indices are 0-based).

.. code-block:: python

    vfile.set_current_phase(1)
    vfile.set_compass_visibility(False)

.. code-block:: python

    section = vfile["COMPS", 1]
    section.inline[0] = 0