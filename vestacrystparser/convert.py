#!/usr/bin/env python3
# Copyright 2025 Bernard Field
"""Create VESTA files from structural data files (POSCAR, etc.).
"""

from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Poscar

from vestacrystparser.parser import VestaFile


def vesta_from_structure(stru: Structure) -> VestaFile:
    """Return a VestaFile from pymatgen.core.Structure"""
    # TODO Convert numpy floats to regular floats.
    # Initialise an empty Vesta file
    vfile = VestaFile()
    # Set the lattice parameters.
    vfile.set_cell(*stru.lattice.abc, *stru.lattice.angles)
    # Add the sites
    counts = {}
    for site in stru:
        element = site.specie.symbol
        # When loading POSCAR, site labels in VESTA are numbered.
        if element in counts:
            counts[element] += 1
        else:
            counts[element] = 1
        vfile.add_site(element, element+str(counts[element]),
                       *site.frac_coords,
                       add_bonds=True)
    # Sort SBOND
    vfile.sort_bonds()
    # Done
    return vfile


def vesta_from_poscar(fname: str) -> VestaFile:
    """Return a VestaFile from a POSCAR file at fname"""
    # Load the POSCAR
    pos = Poscar.from_file(fname)
    # Create a VestaFile from the structure
    vfile = vesta_from_structure(pos.structure)
    # Set the title
    vfile.title = pos.comment
    return vfile

# Thoughts...
# CIF will be tricky, because it contains symmetry and precision
# information and is variable in the data it contains, so I can't simply
# convert to Structure then use that.
# pymatgen.io.cif supports reading CIF files with all data.
# If pymatgen proves unreliable, could also attempt PyCifRW https://pypi.org/project/PyCifRW/
# In any case, CIF is hard, and I don't have much experience with CIF's.
