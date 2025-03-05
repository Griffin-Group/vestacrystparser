#!/usr/bin/env python3
"""
Create VESTA file from pymatgen object
"""

from pymatgen.core import Structure

from vestacrystparser.parser import VestaFile

def vesta_from_structure(stru:Structure) -> VestaFile:
    # Initialise an empty Vesta file
    vfile = VestaFile()
    # Set the lattice parameters.
    vfile.set_cell(*stru.lattice.abc, *stru.lattice.angles)
    # Add the sites
    for site in stru:
        element = site.specie.symbol
        vfile.add_site(element, element, *site.frac_coords)
    # Done
    return vfile
    