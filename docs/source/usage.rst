Usage
=====

.. _installation:

Installation
------------

vestacrystparser can be installed via ``pip``:

.. code-block:: console

    pip install vestacrystparser

You can also find the latest source code on GitHub, at
https://github.com/Griffin-Group/vestacrystparser, where you can install it via
the standard means for installing from source from GitHub.

vestacrystparser itself is lightweight. However, :mod:`vestacrystparser.convert`
requires `pymatgen`_ to parse structure files.
This can be installed as an extra via

.. code-block:: console

    pip install "vestacyrstparser[pymatgen]"

or installed separately via ``pip`` or ``conda``.

Dependencies for development can be installed with the ``[dev]`` extra.

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

Finally, the VestaFile may be written back to file with :meth:`.VestaFile.save`.

Importing structure files to VESTA
----------------------------------

Often, you may have structure data which you could open in VESTA, but not yet
a VESTA file.
In these cases, the :mod:`.convert` module allows reading in structure data and
outputing a :class:`.VestaFile` object (which can be written to a VESTA file).
Currently, POSCAR files and generic :class:`pymatgen.core.Structure` objects are
supported.

The :mod:`.convert` module requires `pymatgen`_ to be installed.

.. _pymatgen: https://pymatgen.org/

.. code-block:: python

    import vestacrystparser.convert

    # Load directly from POSCAR file.
    vfile = vestacrystparser.convert.vesta_from_poscar("POSCAR")

    from pymatgen.core import Structure

    # Create VestaFile from Structure object (which may be parsed from anything)
    stru = Structure.from_file("POSCAR")
    vfile = vestacrystparser.convert.vesta_from_structure(stru)
