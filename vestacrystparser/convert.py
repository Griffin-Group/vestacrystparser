#!/usr/bin/env python3
# Copyright 2025 Bernard Field
"""Create VESTA files from structural data files (POSCAR, etc.).
"""

import numpy as np

from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.common import VolumetricData
from pymatgen.io.vasp.outputs import Chgcar

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

# Volumetric data


def vesta_from_volumetric(volu: VolumetricData, fname: str, n: float = 2,
                          chgcar_like: bool = True) -> VestaFile:
    """Return a VestaFile from pymatgen VolumetricData

    Assumes the Volumetric data is in units of Angstrom, not Bohr.

    Isosurface level is determined by (Vesta Manual section 16.7)

    .. math::
        d(iso) = \\langle \\vert \\rho \\vert \\rangle + n \\times \\sigma(\\vert \\rho \\vert)

    Args:
        volu: VolumetricData object, with structure and volumetric data
        fname: Filename where the volumetric data lives.
        n: Parameter for setting the default isosurface level.
        chgcar_like: If True, divides out the volume.
    """
    # Get the structural component
    vfile = vesta_from_structure(volu.structure)
    # Determine the isosurface level
    # See Section 16.7 of the VESTA Manual
    # Convert to Bohr and divide out volume: Section 17.4.3
    a2b = 0.148185  # Angstom^3 to Bohr^3
    if chgcar_like:
        data = volu.data["total"] / volu.structure.volume * a2b
    else:
        data = volu.data["total"] * a2b
    absrho = np.abs(data)
    level = absrho.mean() + n * absrho.std()
    # Set volumetric data
    vfile.add_volumetric_data(fname)
    vfile.add_isosurface(level)
    vfile.set_section_saturation_levels(data.min(), data.max())
    return vfile


def vesta_from_chgcar(fname: str, n: float = 2) -> VestaFile:
    """Return a VestaFile from VASP CHGCAR.

    Isosurface level is determined by (Vesta Manual section 16.7)

    .. math::
        d(iso) = \\langle \\vert \\rho \\vert \\rangle + n \\times \\sigma(\\vert \\rho \\vert)

    A caution, though. It would appear that VESTA uses a slightly strange
    method of calculating the standard deviation.
    As such, the isosurface level set by this method may be off by an amount
    (e.g. 5%).

    Args:
        fname: Filename of the CHGCAR
        n: Parameter for setting the default isosurface level.
    """
    # Load file
    chg = Chgcar.from_file(fname)
    # Parse file into VESTA format
    vfile = vesta_from_volumetric(chg, fname, n=n)
    # Add title
    vfile.title = chg.poscar.comment
    return vfile


# Thoughts...
# CIF will be tricky, because it contains symmetry and precision
# information and is variable in the data it contains, so I can't simply
# convert to Structure then use that.
# pymatgen.io.cif supports reading CIF files with all data.
# If pymatgen proves unreliable, could also attempt PyCifRW https://pypi.org/project/PyCifRW/
# In any case, CIF is hard, and I don't have much experience with CIF's.
