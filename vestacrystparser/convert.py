#!/usr/bin/env python3
"""
Create VESTA file from pymatgen object
"""

from pymatgen.core import Structure

from vestacrystparser.parser import VestaFile


def vesta_from_structure(stru: Structure) -> VestaFile:
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
