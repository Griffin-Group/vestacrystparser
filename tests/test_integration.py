"""
Some end-to-end integration tests for some applications.
"""
import os

import pytest

from vestacrystparser.parser import VestaFile

from test_parser import compare_vesta_strings, DATA_DIR


def _hex_to_rgb(hex: str) -> tuple[int, int, int]:
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def test_lk_elf():
    """
    I had some volumetric data which I had loaded as a raw VESTA file.
    I then used vestacrystparser to alter the appearance to make it pretty.
    Here, I have copied the code I used there.
    """
    # Load the original file
    vfile = VestaFile(os.path.join(DATA_DIR, "lk_elf_before.vesta"))
    # First delete existing lattice planes
    while True:
        try:
            vfile.delete_lattice_plane(1)
        except IndexError:
            break
    # Step 1: set lattice plane
    # If we have chunnel O, target z=1/4
    stru = vfile.get_structure()
    target_height = 1/4
    # Get atoms near z=0.25
    zs = []
    for site in stru:
        z = site[5]
        if abs(z-target_height) < 0.1:
            zs.append(z)
    zmean = sum(zs)/len(zs)
    # Get the lattice height
    c = vfile.get_cell()[2]
    distance = zmean * c
    vfile.add_lattice_plane(0, 0, 1, distance)
    # Step 2: delete isosurface
    vfile.delete_isosurface(1)
    # Step 3: Set section colour scheme
    vfile.set_section_color_scheme("Y-M-C")
    # Step 4: Set section cutoff values
    vfile.set_section_cutoff_levels(0.27, 0.4)
    # Step 5: Set boundary
    vfile.set_boundary(0, 2, 0, 2)
    # Step 6: Hide unit cell lines and compass
    vfile.set_unit_cell_line_visibility(False)
    vfile.set_compass_visibility(False)
    # Set zoom
    vfile.set_scene_view_direction("c")
    vfile.set_scene_zoom(1.44)
    # Step 7: set colours
    vfile.set_atom_color("O", *_hex_to_rgb("#7F7F7F"))
    vfile.set_atom_color("Pb", *_hex_to_rgb("#6B239A"))
    # Pb1 has a different colour.
    # Got to grab the indices.
    tol = 0.1
    pb1_idx = []
    for i, element, _, x, y, z in stru:
        if element == 'Pb':
            if (abs(x-1/3) < tol and abs(y-2/3) < tol) or (abs(x-2/3) < tol and abs(y-1/3) < tol):
                pb1_idx.append(i)
    vfile.set_site_color(pb1_idx, *_hex_to_rgb("#FE009F"))
    # Get the Pb2 upper layer too.
    indices = []
    for i, element, _, x, y, z in stru:
        if element == 'Pb' and z > 1/2 and i not in pb1_idx:
            indices.append(i)
    vfile.set_site_color(indices, *_hex_to_rgb("#BA46FF"))
    vfile.set_atom_color("P", *_hex_to_rgb("#0FABF7"))
    vfile.set_atom_color("Cu", *_hex_to_rgb("#F9E60B"))
    vfile.set_atom_color("H", *_hex_to_rgb("#001883"))
    # Other chunnel ion species. (Colour unspecified, so I borrowed H's colour.)
    c_chunnel = _hex_to_rgb("#001883")
    vfile.set_atom_color("S", *c_chunnel)
    vfile.set_atom_color("Se", *c_chunnel)
    vfile.set_atom_color("F", *c_chunnel)
    vfile.set_atom_color("Cl", *c_chunnel)
    vfile.set_atom_color("Br", *c_chunnel)
    vfile.set_atom_color("I", *c_chunnel)
    # You know what? The chunnel O can be chunnel coloured too.
    vfile.set_site_color(41, *c_chunnel)
    # We're now done!
    # Compare with expected result.
    reference = VestaFile(os.path.join(DATA_DIR, "lk_elf_after.vesta"))
    # Because both objects are VestaFile, their formatting should be consistent.
    assert str(vfile) == str(reference)
