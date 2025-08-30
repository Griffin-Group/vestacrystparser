import os
import math

import pytest

from vestacrystparser.parser import VestaFile, parse_line, invert_matrix
import vestacrystparser.parser

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "Cu_primitive_plain.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def default_vesta_filename() -> str:
    ROOT_DIR = os.path.dirname(TEST_DIR)
    return os.path.join(ROOT_DIR, 'vestacrystparser', 'resources',
                        'default.vesta')


def compare_vesta_strings(str1: str, str2: str, prec: int = None) -> bool:
    """
    Takes two VESTA strings, does basic parsing so no formatting,
    then checks if they are equivalent.

    If provided, prec means floats are compared to prec digits of precision.
    """
    data1 = [parse_line(x) for x in str1.strip().split('\n')]
    data2 = [parse_line(x) for x in str2.strip().split('\n')]
    # Compare
    if not len(data1) == len(data2):
        return False
    for line1, line2 in zip(data1, data2):
        if not line1 == line2:
            if prec is not None:
                for x1, x2 in zip(line1, line2):
                    if isinstance(x1, str) or isinstance(x2, str):
                        if x1 != x2:
                            return False
                    else:
                        if abs(x1-x2) >= 10**(-prec):
                            return False
            else:
                return False
    return True


def compare_matrices(M1, M2, prec: int = None) -> bool:
    """
    Takes two matrix-like objects and compares them.

    If provided, prec means floats are compared to prec digits of precision.
    """
    # Check first dimension is the same length.
    if not len(M1) == len(M2):
        return False
    for i in range(len(M1)):
        # Check second dimension is the same length
        if not len(M1[i]) == len(M2[i]):
            return False
        for j in range(len(M1[i])):
            # Compare elements
            if prec is None:
                if not M1[i][j] == M2[i][j]:
                    return False
            else:
                if not abs(M1[i][j] - M2[i][j]) <= 10**(-prec):
                    return False
    return True


# TODO: test case with volumetric data (so IMPORT_DENISTY is called)
def test_load(sample_vestafile, sample_vesta_filename):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that it has expected number of fields
    assert len(sample_vestafile) == 65, \
        "Did not load expected number of fields."
    # Test that we read the atom data right.
    section = sample_vestafile["SITET"]
    expected_sitet = [[1, "Cu", 1.28, 34, 71, 220, 34, 71, 220, 204, 0],
                      [0, 0, 0, 0, 0, 0]]
    assert section.data == expected_sitet, "SITET data not what was expected."
    expected_bondp = """BONDP
  1  16  0.250  2.000 127 127 127"""
    assert compare_vesta_strings(
        str(sample_vestafile["BONDP"]), expected_bondp)
    # Do the full comparison
    with open(sample_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile), f.read()), \
            "Full file comparison failed."


def test_empty(default_vesta_filename):
    sample = VestaFile()
    with open(default_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample), f.read()), \
            "Loaded default Vesta file didn't match saved file."


def test_save(tmp_path, sample_vestafile, sample_vesta_filename):
    # Write the file (using the tmp_path pytest fixture)
    sample_vestafile.save(tmp_path / "output.vesta")
    # Compare them
    with open(sample_vesta_filename, 'r') as f1:
        with open(tmp_path / "output.vesta", 'r') as f2:
            assert compare_vesta_strings(f1.read(), f2.read())


def test_repr(sample_vestafile):
    assert repr(sample_vestafile) == "<VestaFile: New structure [1 site]>"


def test_load_default_bond_length():
    assert vestacrystparser.parser.load_default_bond_length('C', 'C') == 1.89002, \
        "Failed to load correct same-atom bond length."
    assert vestacrystparser.parser.load_default_bond_length('F', 'Ac') == 2.58646, \
        "Failed to load bond length for swapped A2 and A1."
    assert vestacrystparser.parser.load_default_bond_length('Fe', 'Mg') is None, \
        "Failed to handle case where no bond length was present."


def test_set_site_color(sample_vestafile):
    """Tests set_site_color"""
    # Check that writing works as expected.
    sample_vestafile.set_site_color(1, 12, 16, 100)
    expected_sitet = """SITET
    1 Cu 1.2800 12 16 100 34 71 220 204 0
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color not changed as expected"
    # Check exception
    with pytest.raises(IndexError):
        sample_vestafile.set_site_color(0, 20, 30, 40)
    # Make sure nothing got changed.
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color changed when it shouldn't have"
    # Test what happens if do a list indexing.
    sample_vestafile.set_site_color([1], 15, 25, 35)
    expected_sitet = """SITET
    1 Cu 1.2800 15 25 35 34 71 220 204 0
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color from list of indices didn't work"
    # To test: index out of range.
    try:
        sample_vestafile.set_site_color(2, 11, 22, 33)
    except IndexError:
        # Currently it logs a warning.
        # But I might change this behaviour in the future.
        pass
    # Confirm that nothing changed.
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site colors changed when called out-of-range index"
    # I don't *expect* any side-effects from this function.
    # Dunno how to easily test that, though.


def test_set_atom_color(sample_vestafile):
    # Check that writing works as expected
    sample_vestafile.set_atom_color(1, 12, 16, 100)
    expected_sitet = """SITET
    1 Cu 1.2800 12 16 100 34 71 220 204 0
    0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800  12  16 100  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color not changed as expected"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color not changed as expected"
    # Check exception
    with pytest.raises(IndexError):
        sample_vestafile.set_atom_color(0, 20, 30, 40)
    # Make sure nothing got changed
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color changed when it shouldn't have"
    # Test element-based indexing
    sample_vestafile.set_atom_color('Cu', 15, 25, 35)
    expected_sitet = """SITET
    1 Cu 1.2800 15 25 35 34 71 220 204 0
    0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800  15  25  35  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color not changed as expected from element-based indexing"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color not changed as expected from element-based indexing"
    # Test that override_site_colors=False works
    sample_vestafile.set_atom_color(
        'Cu', 11, 22, 33, overwrite_site_colors=False)
    expected_atomt = """ATOMT
  1         Cu  1.2800  11  22  33  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color not changed as expected when overwrite_site_colors=False"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color changed despite overwrite_site_colors=False"
    # Test exception in element
    with pytest.raises(TypeError):
        sample_vestafile.set_atom_color(str, 20, 30, 40)
    # Make sure nothing got changed
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color changed when it shouldn't have"
    # Set element that isn't present
    # (Currently it just logs a warning. This might change in the future.)
    sample_vestafile.set_atom_color('Fe', 20, 30, 40)
    # Make sure nothing got changed
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Atom color changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Site color changed when it shouldn't have"


def test_lattice_plane(sample_vestafile):
    # Check that deleting a lattice plane that doesn't exist doesn't change
    # things
    with pytest.raises(IndexError):
        sample_vestafile.delete_lattice_plane(0)
    empty_splan = """SPLAN
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), empty_splan), \
        "SPLAN changed when it shouldn't have"
    # Check that we can add a lattice plane
    sample_vestafile.add_lattice_plane(1.5, -1, 10, 5.35)
    expected_splan = """SPLAN
    1 1.5 -1 10 5.35 255 0 255 192
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), \
        "Expected lattice plane didn't get added"
    # Add a second lattice plane, with colour
    sample_vestafile.add_lattice_plane(1, 0, 0, -10, 0, 200, 0, 10)
    expected_splan2 = """SPLAN
    1 1.5 -1 10 5.35 255 0 255 192
    2 1 0 0 -10 0 200 0 10
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan2), \
        "Expected lattice plane didn't get added"
    # Check that deleting reverts as expected
    sample_vestafile.delete_lattice_plane(2)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), \
        "Expected lattice plane didn't get deleted"
    # Add it back then remove number 1. See how re-indexing gets handled.
    sample_vestafile.add_lattice_plane(1, 0, 0, -10, 0, 200, 0, 10)
    sample_vestafile.delete_lattice_plane(1)
    expected_splan = """SPLAN
    1 1 0 0 -10 0 200 0 10
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), \
        "Expected lattice plane didn't get deleted or reindexed"
    # Check out-of-range
    with pytest.raises(IndexError):
        sample_vestafile.delete_lattice_plane(3)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), \
        "SPLAN changed when it shouldn't have"
    # Check deleting negative indices
    sample_vestafile.delete_lattice_plane(-1)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), empty_splan), \
        "Didn't delete expected lattice plane"


def test_delete_isosurface(sample_vestafile):
    # We currently have no isosurface test fixtures.
    # So here we'll make sure it throws the right errors.
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(1)
    empty_isurf = """ISURF
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), empty_isurf), \
        "ISURF changed when it shouldn't have"
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(0)
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), empty_isurf), \
        "ISURF changed when it shouldn't have"


def test_set_section_color_scheme(sample_vestafile):
    # Initial values
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""
    expected_sects = "SECTS  32  1"
    expected_seccl = "SECCL 0"
    # Set to the current colour scheme
    sample_vestafile.set_section_color_scheme("B-G-R")
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), \
        "SECTP doesn't match B-G-R"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), \
        "SECTS doesn't match B-G-R"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), \
        "SECCL doesn't match B-G-R"
    # Reverse it
    sample_vestafile.set_section_color_scheme("R-G-B")
    expected_sectp = """SECTP
 -1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""
    expected_seccl = "SECCL 1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), \
        "SECTP doesn't match R-G-B"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), \
        "SECTS doesn't match R-G-B"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), \
        "SECCL doesn't match R-G-B"
    # Try an index-based assignment for Y-M-C (a reversed map)
    sample_vestafile.set_section_color_scheme(3)
    expected_seccl = "SECCL 3"
    expected_sects = "SECTS  40  1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), \
        "SECTP doesn't match Y-M-C"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), \
        "SECTS doesn't match Y-M-C"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), \
        "SECCL doesn't match Y-M-C"
    # Finally, cyclic ostwald
    sample_vestafile.set_section_color_scheme("Cyclic: Ostwald")
    expected_seccl = "SECCL 10"
    expected_sects = "SECTS  48  1"
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), \
        "SECTP doesn't match Cyclic: Ostwald"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), \
        "SECTS doesn't match Cyclic: Ostwald"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), \
        "SECCL doesn't match Cyclic: Ostwald"
    # Finally, test an error
    with pytest.raises(ValueError):
        sample_vestafile.set_section_color_scheme("Not a real color scheme")
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), \
        "SECTP changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), \
        "SECTS changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), \
        "SECCL changed when it shouldn't have"


def test_set_section_cutoff_levels(sample_vestafile):
    # Changing one thing at a time
    expected_sects = "SECTS  32  1"
    sample_vestafile.set_section_cutoff_levels(lattice_max=0.5)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.50000E+00  0.00000E+00  0.00000E+00"""
    assert compare_vesta_strings(
        str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(
        str(sample_vestafile["SECTS"]), expected_sects)
    # Change two things
    sample_vestafile.set_section_cutoff_levels(
        lattice_min=0.1, isosurface_min=0.12)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.10000E+00  0.50000E+00  0.12000E+00  0.00000E+00"""
    assert compare_vesta_strings(
        str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(
        str(sample_vestafile["SECTS"]), expected_sects)
    # Set the manual flag too
    sample_vestafile.set_section_cutoff_levels(
        isosurface_max=12, isosurface_auto=False)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.10000E+00  0.50000E+00  0.12000E+00  0.12000E+02"""
    expected_sects = "SECTS 160  1"
    assert compare_vesta_strings(
        str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(
        str(sample_vestafile["SECTS"]), expected_sects)
    # Then unset the manual flag
    sample_vestafile.set_section_cutoff_levels(isosurface_auto=True)
    expected_sects = "SECTS  32  1"
    assert compare_vesta_strings(
        str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(
        str(sample_vestafile["SECTS"]), expected_sects)


def test_set_boundary(sample_vestafile):
    # Test setting all 6 parameters
    sample_vestafile.set_boundary(-0.1, 1.1, -0.2, 1.2, -0.5, 0.5)
    expected_bound = """BOUND
       -0.1      1.1      -0.2      1.2      -0.5        0.5
  0   0   0   0  0"""
    assert compare_vesta_strings(
        str(sample_vestafile["BOUND"]), expected_bound)
    # Test changing one parameter
    sample_vestafile.set_boundary(ymin=0.3)
    expected_bound = """BOUND
       -0.1      1.1       0.3      1.2      -0.5        0.5
  0   0   0   0  0"""
    assert compare_vesta_strings(
        str(sample_vestafile["BOUND"]), expected_bound)


def test_set_unit_cell_line_visibility(sample_vestafile):
    # Hide line
    assert sample_vestafile.set_unit_cell_line_visibility(show=False) == 0
    expected_ucolp = """UCOLP
   0   0  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp), \
        "Hiding unit cell lines didn't work."
    # Show all lines
    assert sample_vestafile.set_unit_cell_line_visibility(all=True) == 2
    expected_ucolp = """UCOLP
   0   2  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp), \
        "Showing all cell lines didn't work."
    # Show just one line
    assert sample_vestafile.set_unit_cell_line_visibility(show=True) == 1
    expected_ucolp = """UCOLP
   0   1  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp), \
        "Showing one unit cell line didn't work."
    # Some of the less well-defined cases.
    assert sample_vestafile.set_unit_cell_line_visibility(
        show=False, all=True) == 0
    expected_ucolp = """UCOLP
   0   0  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp), \
        "Hiding unit cell lines with all=True didn't hide."
    assert sample_vestafile.set_unit_cell_line_visibility(all=False) == 0
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp), \
        "Setting just all=False caused a change."


def test_set_compass_visibility(sample_vestafile):
    # Turn off compass
    assert sample_vestafile.set_compass_visibility(False) == 0
    expected_comps = "COMPS 0"
    assert compare_vesta_strings(
        str(sample_vestafile["COMPS"]), expected_comps)
    # Turn on compass
    assert sample_vestafile.set_compass_visibility(True) == 1
    expected_comps = "COMPS 1"
    assert compare_vesta_strings(
        str(sample_vestafile["COMPS"]), expected_comps)
    # Turn on compass, but without axes labels
    assert sample_vestafile.set_compass_visibility(True, axes=False) == 2
    expected_comps = "COMPS 2"
    assert compare_vesta_strings(
        str(sample_vestafile["COMPS"]), expected_comps)


def test_set_scene_view_matrix(sample_vestafile):
    # Apply a valid matrix
    sample_vestafile.set_scene_view_matrix(
        [[0.707107, 0.707107, 0], [-0.707107, 0.707107, 0], [0, 0, 1]])
    expected_scene = """SCENE
 0.707107  0.707107  0.000000  0.000000
-0.707107  0.707107  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.000"""
    assert compare_vesta_strings(
        str(sample_vestafile["SCENE"]), expected_scene)
    # Apply invalid matrix
    with pytest.raises(ValueError):
        sample_vestafile.set_scene_view_matrix(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0]])
    # Check nothing changed
    assert compare_vesta_strings(
        str(sample_vestafile["SCENE"]), expected_scene)


def test_set_scene_view_direction(sample_vestafile):
    # Preset: 1
    sample_vestafile.set_scene_view_direction('1')
    expected_scene = """SCENE
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.000"""
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene), \
        "Did not properly set view to '1'."
    # Preset: c
    sample_vestafile.set_scene_view_direction('c')
    # Expected data obtained by actually doing it in VESTA.
    expected_scene = """SCENE
 0.866025 -0.166667 -0.471405  0.000000
 0.000000  0.942809 -0.333333  0.000000
 0.500000  0.288675  0.816497  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.000"""
    # Because floating-point operations are involved, only compare floats to
    # 6 digits of precision, which is VESTA's default for SCENE.
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene, prec=6), \
        "Did not properly set view to 'c'."
    # Ask for an invalid direction
    with pytest.raises(ValueError):
        sample_vestafile.set_scene_view_direction('wrong')
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene, prec=6), \
        "SCENE changed when it shouldn't have following error."


def test_set_scene_zoom(sample_vestafile):
    sample_vestafile.set_scene_zoom(1.5)
    expected_scene = """SCENE
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 1.000000  0.000000  0.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.500"""
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene), \
        "Did not properly set zoom."


# TODO: Add test case with THERM.
# TODO: Test case with hBN where I play with add_bonds
def test_add_site(sample_vestafile):
    sample_vestafile.add_site('Cu', 'Cu', 0.2, 0.3, 0.4, U=0.05)
    expected_struc = """STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  2 Cu         Cu  1.0000   0.200000   0.300000   0.400000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0"""
    expected_theri = """THERI 1
  1         Cu  0.050000
  2         Cu  0.050000
  0 0 0"""
    expected_sitet = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  2         Cu  1.2800  34  71 220  34  71 220 204  0
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["STRUC"]), expected_struc), \
        "Adding one atom did not change STRUC properly."
    assert compare_vesta_strings(str(sample_vestafile["THERI"]), expected_theri), \
        "Adding one atom did not change THERI properly."
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Adding one atom did not change SITET properly."
    # Check that changing atom colours works as expected.
    sample_vestafile.set_atom_color(
        'Cu', 100, 110, 120, overwrite_site_colors=False)
    sample_vestafile.add_site('Cu', 'X', 0.5, 0.5, 0.5)
    expected_struc = """STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  2 Cu         Cu  1.0000   0.200000   0.300000   0.400000    1a       1
                            0.000000   0.000000   0.000000  0.00
  3 Cu         X   1.0000   0.500000   0.500000   0.500000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0"""
    expected_theri = """THERI 1
  1         Cu  0.050000
  2         Cu  0.050000
  3         X   0.000000
  0 0 0"""
    expected_sitet = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  2         Cu  1.2800  34  71 220  34  71 220 204  0
  3         X   1.2800 100 110 120  34  71 220 204  0
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["STRUC"]), expected_struc), \
        "Adding atom of different colour did not change STRUC properly."
    assert compare_vesta_strings(str(sample_vestafile["THERI"]), expected_theri), \
        "Adding atom of different colour did not change THERI properly."
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Adding atom of different colour did not change SITET properly."
    # Add a different element. It should load default colours.
    sample_vestafile.add_site('Mg', 'XX', 0.1, 0.1, 0.3)
    expected_struc = """STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  2 Cu         Cu  1.0000   0.200000   0.300000   0.400000    1a       1
                            0.000000   0.000000   0.000000  0.00
  3 Cu         X   1.0000   0.500000   0.500000   0.500000    1a       1
                            0.000000   0.000000   0.000000  0.00
  4 Mg         XX  1.0000   0.100000   0.100000   0.300000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0"""
    expected_theri = """THERI 1
  1         Cu  0.050000
  2         Cu  0.050000
  3         X   0.000000
  4         XX  0.000000
  0 0 0"""
    expected_sitet = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  2         Cu  1.2800  34  71 220  34  71 220 204  0
  3         X   1.2800 100 110 120  34  71 220 204  0
  4         XX  1.6000 251 123  21 251 123  21 204  0
  0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800 100 110 120  34  71 220 204
  2         Mg  1.6000 251 123  21 251 123  21 204
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["STRUC"]), expected_struc), \
        "Adding atom of new element did not change STRUC properly."
    assert compare_vesta_strings(str(sample_vestafile["THERI"]), expected_theri), \
        "Adding atom of new element did not change THERI properly."
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Adding atom of new element did not change SITET properly."
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Adding atom of new element did not change ATOMT properly."
    # Add an element with a symbol not in elements.ini
    # It should load the default values, 'XX' in elements.ini
    sample_vestafile.add_site('A', 'A', 0.3, 0.3, 0.1)
    expected_struc = """STRUC
  1 Cu         Cu  1.0000   0.000000   0.000000   0.000000    1a       1
                            0.000000   0.000000   0.000000  0.00
  2 Cu         Cu  1.0000   0.200000   0.300000   0.400000    1a       1
                            0.000000   0.000000   0.000000  0.00
  3 Cu         X   1.0000   0.500000   0.500000   0.500000    1a       1
                            0.000000   0.000000   0.000000  0.00
  4 Mg         XX  1.0000   0.100000   0.100000   0.300000    1a       1
                            0.000000   0.000000   0.000000  0.00
  5 A          A   1.0000   0.300000   0.300000   0.100000    1a       1
                            0.000000   0.000000   0.000000  0.00
  0 0 0 0 0 0 0"""
    expected_theri = """THERI 1
  1         Cu  0.050000
  2         Cu  0.050000
  3         X   0.000000
  4         XX  0.000000
  5         A  0.000000
  0 0 0"""
    expected_sitet = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  2         Cu  1.2800  34  71 220  34  71 220 204  0
  3         X   1.2800 100 110 120  34  71 220 204  0
  4         XX  1.6000 251 123  21 251 123  21 204  0
  5         A   0.8000  76  76  76  76  76  76 204  0
  0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800 100 110 120  34  71 220 204
  2         Mg  1.6000 251 123  21 251 123  21 204
  3         A   0.8000  76  76  76  76  76  76 204
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["STRUC"]), expected_struc), \
        "Adding atom of unspecified element did not change STRUC properly."
    assert compare_vesta_strings(str(sample_vestafile["THERI"]), expected_theri), \
        "Adding atom of unspecified element did not change THERI properly."
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), \
        "Adding atom of unspecified element did not change SITET properly."
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), \
        "Adding atom of unspecified element did not change ATOMT properly."


def test_add_bond(sample_vestafile):
    expected_sbond = """SBOND
    1 Cu Cu 0.00000 2.5000 0 1 1 0 1 0.250 2.000 127 127 127
    0 0 0 0"""
    sample_vestafile.add_bond('Cu', 'Cu', max_length=2.5)
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "Adding a bond didn't work as expected."
    # Test some failure cases
    with pytest.raises(ValueError):
        sample_vestafile.add_bond('Cu', 'Cu', search_mode=1.5)
    with pytest.raises(ValueError):
        sample_vestafile.add_bond('Cu', 'Cu', search_mode=4)
    with pytest.raises(ValueError):
        sample_vestafile.add_bond('Cu', 'Cu', boundary_mode=1.5)
    with pytest.raises(ValueError):
        sample_vestafile.add_bond('Cu', 'Cu', boundary_mode=0)
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "SBOND changed despite add_bond hitting an error."
    # Try a different search mode
    expected_sbond = """SBOND
    1 Cu Cu 0.00000 2.5000 0 1 1 0 1 0.250 2.000 127 127 127
    2 XX XX 0.00000 1.6000 2 2 1 0 1 0.250 2.000 127 127 127
    0 0 0 0"""
    sample_vestafile.add_bond('Cu', 'Cu', search_mode=3)
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "search_mode=3 didn't work as expected."
    # Add some other flags.
    expected_sbond = """SBOND
    1 Cu Cu 0.00000 2.5000 0 1 1 0 1 0.250 2.000 127 127 127
    2 XX XX 0.00000 1.6000 2 2 1 0 1 0.250 2.000 127 127 127
    3 Cu Cu 0.10000 1.6000 0 1 0 1 1 0.250 2.000 127 127 127
    0 0 0 0"""
    sample_vestafile.add_bond('Cu', 'Cu', min_length=0.1, show_polyhedra=False,
                              search_by_label=True)
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "show_polyhedra, search_by_label, or min_length didn't work as expected."


def test_get_structure(sample_vestafile):
    data = sample_vestafile.get_structure()
    expected_data = [[1, 'Cu', 'Cu', 0, 0, 0]]
    assert data == expected_data
    # See what happens if we modify
    sample_vestafile.add_site('Cu', 'X', 0.5, 0.5, 0.5)
    expected_data = [[1, 'Cu', 'Cu', 0, 0, 0],
                     [2, 'Cu', 'X', 0.5, 0.5, 0.5]]
    data = sample_vestafile.get_structure()
    assert data == expected_data, \
        "Adding site did not properly change get_structure."
    # Ensure returned data is a copy
    data[1][2] = 'foo'
    assert sample_vestafile.get_structure() == expected_data, \
        "Modifying returned list changed original data!"


def test_set_cell(sample_vestafile):
    # Set all values at once
    sample_vestafile.set_cell(1.1, 1.2, 1.3, 20, 30, 40)
    expected_cellp = """CELLP
  1.100000   1.200000   1.300000  20.000000  30.000000  40.000000
  0.000000   0.000000   0.000000   0.000000   0.000000   0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["CELLP"]), expected_cellp), \
        "Setting all cell parameters didn't work as expected."
    # Keyword set one value
    sample_vestafile.set_cell(b=1.5)
    expected_cellp = """CELLP
  1.100000   1.500000   1.300000  20.000000  30.000000  40.000000
  0.000000   0.000000   0.000000   0.000000   0.000000   0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["CELLP"]), expected_cellp), \
        "Setting one cell parameter didn't work as expected."


def test_get_cell(sample_vestafile):
    cell = sample_vestafile.get_cell()
    expected_data = [2.530000, 2.530000,
                     2.530000, 60.000000, 60.000000, 60.000000]
    assert cell == expected_data, "get_cell gave the wrong data."
    # Ensure data is read-only
    cell[0] = 1.5
    assert sample_vestafile.get_cell() == expected_data, \
        "Modifying returned list changed original data!"


def test_set_atom_material(sample_vestafile):
    # Set RGB
    sample_vestafile.set_atom_material(110, 120, 130)
    expected_atomm = """ATOMM
 110 120 130 255
  25.600"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMM"]), expected_atomm), \
        "Setting RGB by position did not work as expected."
    # Set shininess
    sample_vestafile.set_atom_material(shininess=50)
    expected_atomm = """ATOMM
 110 120 130 255
  64.000"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMM"]), expected_atomm), \
        "Setting shininess didn't work as expected."
    # Set colour value by keyword
    sample_vestafile.set_atom_material(g=99)
    expected_atomm = """ATOMM
 110  99 130 255
  64.000"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMM"]), expected_atomm), \
        "Setting just Green didn't work as expected."


def test_set_background_color(sample_vestafile):
    sample_vestafile.set_background_color(110, 120, 130)
    expected_bkgrc = """BKGRC
 110 120 130"""
    assert compare_vesta_strings(
        str(sample_vestafile["BKGRC"]), expected_bkgrc)


def test_set_enable_lighting(sample_vestafile):
    # Turn off the lights
    sample_vestafile.set_enable_lighting(False)
    expected_light0 = """LIGHT0 0
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
  26  26  26 255
 179 179 179 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Turning off the lighting didn't work as expected."
    # Turn on the lights
    sample_vestafile.set_enable_lighting(True)
    expected_light0 = """LIGHT0 1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
  26  26  26 255
 179 179 179 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Turning on the lighting didn't work as expected."
    # Check that turning it on again doesn't change things
    sample_vestafile.set_enable_lighting(True)
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Turning on lighting again changed things when it shouldn't have."


def test_set_lighting_angle(sample_vestafile):
    sample_vestafile.set_lighting_angle(
        [[0.707107, 0.707107, 0], [-0.707107, 0.707107, 0], [0, 0, 1]])
    expected_light0 = """LIGHT0 1
 0.707107  0.707107  0.000000  0.000000
-0.707107  0.707107  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
  26  26  26 255
 179 179 179 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0, prec=6), \
        "Setting lighting angle matrix didn't work as expected."
    # Reset
    sample_vestafile.reset_lighting_angle()
    expected_light0 = """LIGHT0 1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
  26  26  26 255
 179 179 179 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Resetting lighting angle didn't work as expected."


def test_set_lighting(sample_vestafile):
    sample_vestafile.set_lighting(ambient=100, diffuse=0)
    expected_light0 = """LIGHT0 1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
 255 255 255 255
   0   0   0 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Setting ambient=100% and diffuse=0% didn't work as expected."
    sample_vestafile.set_lighting(diffuse=50)
    expected_light0 = """LIGHT0 1
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000 20.000000  0.000000
 0.000000  0.000000 -1.000000
 255 255 255 255
 127 127 127 255
 255 255 255 255"""
    assert compare_vesta_strings(str(sample_vestafile["LIGHT0"]), expected_light0), \
        "Setting diffuse=50% didn't work as expected."


def test_set_depth_cueing(sample_vestafile):
    # Turn it off
    sample_vestafile.set_depth_cueing(enable=False)
    expected_dpthq = "DPTHQ 0 -0.5000  3.5000"
    assert compare_vesta_strings(str(sample_vestafile["DPTHQ"]), expected_dpthq), \
        "Turning off depth cueing didnt work as expected."
    # Turn it on again
    sample_vestafile.set_depth_cueing(enable=True)
    expected_dpthq = "DPTHQ 1 -0.5000  3.5000"
    assert compare_vesta_strings(str(sample_vestafile["DPTHQ"]), expected_dpthq), \
        "Turning on depth cueing didnt work as expected."
    sample_vestafile.set_depth_cueing(enable=True)
    assert compare_vesta_strings(str(sample_vestafile["DPTHQ"]), expected_dpthq), \
        "Turning on depth cueing again changed things when it shouldn't have."
    # Now play with the depth
    sample_vestafile.set_depth_cueing(start=1.2, end=2.4)
    expected_dpthq = "DPTHQ 1  1.2000  2.4000"
    assert compare_vesta_strings(str(sample_vestafile["DPTHQ"]), expected_dpthq), \
        "Changing start and end of depth cueing didn't work as expected."


def test_find_sites(sample_vestafile):
    # sample_vestafile has a single Cu atom at 0,0,0.
    assert sample_vestafile.find_sites() == [1]
    assert sample_vestafile.find_sites('Cu') == [1]
    assert sample_vestafile.find_sites('C') == []
    assert sample_vestafile.find_sites(
        xmin=0, xmax=0.5, ymin=0, ymax=0.5) == [1]
    assert sample_vestafile.find_sites(
        xmin=0, xmax=0.5, zmin=0.1, zmax=1) == []


def test_set_title(sample_vestafile):
    expected_title = """TITLE
Foobar
"""
    sample_vestafile.set_title("Foobar")
    assert compare_vesta_strings(str(sample_vestafile["TITLE"]), expected_title), \
        "Title did not change as expected."
    # Test error case. No newlines allowed.
    with pytest.raises(ValueError):
        sample_vestafile.set_title("Hello \nWorld")
    assert compare_vesta_strings(str(sample_vestafile["TITLE"]), expected_title), \
        "Title changed despite error setting title."


def test_get_cell_matrix(sample_vestafile):
    mat = sample_vestafile.get_cell_matrix()
    # Obtained from converting to POSCAR.
    expected_mat = [[2.5299999714, 0.0000000000, 0.0000000000],
                    [1.2649999857, 2.1910442468, 0.0000000000],
                    [1.2649999857, 0.7303480823, 2.0657363264]]
    assert compare_matrices(mat, expected_mat, prec=6)


def test_invert_matrix():
    M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert compare_matrices(invert_matrix(
        M), M, prec=12), "Identity matrix not matched"
    # Get a more complex inversion
    M = [[2.53, 0, 0],
         [1.2650000000000001, 2.1910442715746297, 0],
         [1.2650000000000001, 0.7303480905248766, 2.0657363497471466]]
    # Inverse from numpy.linalg.inv(M)
    Mi = [[0.39525692,  0.,  0.],
          [-0.22820169,  0.45640337,  0.],
          [-0.16136296, -0.16136296,  0.48408888]]
    assert compare_matrices(invert_matrix(M), Mi, prec=7)


def test_add_vector_type(sample_vestafile):
    # Set with default x-y-z, in y direction.
    sample_vestafile.add_vector_type(5/2, math.sqrt(3)*5/2, 0)
    expected_vectr = """VECTR
    1    0.00000    5.00000    0.00000 0
    0 0 0 0 0
    0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.500 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=5), \
        "VECTR doesn't match expected value from xyz coords."
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT wasn't updated properly from defaults."
    # Try uvw with some changed defaults
    sample_vestafile.add_vector_type(1, 0, 0, polar=True, r=100, g=120, b=140,
                                     coord_type="uvw", penetrate_atoms=False)
    expected_vectr = """VECTR
    1    0.00000    5.00000    0.00000 0
    0 0 0 0 0
    2    2.53000    0.00000    0.00000 1
    0 0 0 0 0
    0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.500 255   0   0 1
   2  0.500 100 120 140 0
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=5), \
        "VECTR doesn't match expected value from uvw coords or polar vector."
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT wasn't updated properly with different colours or penetrate_atoms=False."
    # Now do modulus with some other parameters.
    sample_vestafile.add_vector_type(0, 5, 0, radius=0.35, add_atom_radius=True,
                                     penetrate_atoms=True, coord_type="modulus")
    expected_vectr = """VECTR
    1    0.00000    5.00000    0.00000 0
    0 0 0 0 0
    2    2.53000    0.00000    0.00000 1
    0 0 0 0 0
    3    0.00000    5.00000    0.00000 0
    0 0 0 0 0
    0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.500 255   0   0 1
   2  0.500 100 120 140 0
   3  0.350 255   0   0 3
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=5), \
        "VECTR doesn't match expected value from modulus coords."
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT wasn't updated properly with radius or add_atom_radius."
    # Invalid coords type
    with pytest.raises(ValueError):
        sample_vestafile.add_vector_type(1, 2, 3, coord_type="jhfdak")
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=5), \
        "VECTR changed despite invalid coords type."
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT changed despite invalid coords type."


def test_delete_vector_type(sample_vestafile):
    # We have no vectors.
    # Attempting to delete should raise an error and not do anything.
    expected_vectr = """VECTR
 0 0 0 0 0"""
    expected_vectt = """VECTT
 0 0 0 0 0"""
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(1)
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(0)
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(-1)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR changed despite no vectors to delete."
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT changed despite no vectors to delete."


def test_title(sample_vestafile):
    assert sample_vestafile.title == "New structure"


def test_nphases(sample_vestafile):
    assert sample_vestafile.nphases == 1


def test_nsites(sample_vestafile):
    assert sample_vestafile.nsites == 1


def test_nvectors(sample_vestafile):
    assert sample_vestafile.nvectors == 0


def test_set_vector_scale(sample_vestafile):
    expected_vects = """VECTS 2.300000"""
    sample_vestafile.set_vector_scale(2.3)
    assert compare_vesta_strings(str(sample_vestafile["VECTS"]), expected_vects), \
        """Did not set vector scale factor."""


def test_delete_bond(sample_vestafile):
    # Test deleting bonds that don't exist.
    expected_sbond = """SBOND
  0 0 0 0"""
    with pytest.raises(IndexError):
        sample_vestafile.delete_bond(1)
    with pytest.raises(IndexError):
        sample_vestafile.delete_bond(0)
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "Deleting non-existent bonds changed things!"


def test_edit_bond(sample_vestafile):
    # Test editing bonds that don't exist.
    expected_sbond = """SBOND
  0 0 0 0"""
    with pytest.raises(IndexError):
        sample_vestafile.edit_bond(1)
    with pytest.raises(IndexError):
        sample_vestafile.edit_bond(0)
    with pytest.raises(IndexError):
        sample_vestafile.edit_bond(1, A1="Cu")
    assert compare_vesta_strings(str(sample_vestafile["SBOND"]), expected_sbond), \
        "Editing non-existent bonds changed things!"
