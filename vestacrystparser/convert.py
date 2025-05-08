#!/usr/bin/env python3
"""
Create VESTA file from pymatgen object
"""

from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Poscar

from vestacrystparser.parser import VestaFile


def vesta_from_structure(stru: Structure) -> VestaFile:
    """From pymatgen.core.Structure, create a VestaFile"""
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
    # Done
    return vfile


def vesta_from_poscar(fname: str) -> VestaFile:
    """From a POSCAR file a fname, create a VestaFile"""
    # Load the POSCAR
    pos = Poscar.from_file(fname)
    # Create a VestaFile from the structure
    vfile = vesta_from_structure(pos.structure)
    # Set the title
    vfile.title = pos.comment
    return vfile
