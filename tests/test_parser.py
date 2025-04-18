import os

import pytest

from vestacrystparser.parser import VestaFile, parse_line

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')

@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "Cu_primitive_plain.vesta")
@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)

def compare_vesta_strings(str1:str, str2:str, prec:int=None) -> bool:
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
    for line1, line2 in zip(data1,data2):
        if not line1 == line2:
            if prec is not None:
                for x1,x2 in zip(line1,line2):
                    if isinstance(x1,str) or isinstance(x2,str):
                        if x1 != x2:
                            return False
                    else:
                        if abs(x1-x2) >= 10**(-prec):
                            return False
            else:
                return False
    return True

def test_load(sample_vestafile, sample_vesta_filename):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that is has expected number of fields
    assert len(sample_vestafile) == 65, "Did not load expected number of fields."
    # Test that we read the atom data right.
    section = sample_vestafile["SITET"]
    expected_sitet = [[1,"Cu",1.28,34,71,220,34,71,220,204,0],
                      [0,0,0,0,0,0]]
    assert section.data == expected_sitet, "SITET data not what was expected."
    expected_bondp = """BONDP
  1  16  0.250  2.000 127 127 127"""
    assert compare_vesta_strings(str(sample_vestafile["BONDP"]), expected_bondp)
    # Do the full comparison
    with open(sample_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile), f.read()), "Full file comparison failed."

def test_save(tmp_path, sample_vestafile, sample_vesta_filename):
    # Write the file (using the tmp_path pytest fixture)
    sample_vestafile.save(tmp_path / "output.vesta")
    # Compare them
    with open(sample_vesta_filename, 'r') as f1:
        with open(tmp_path / "output.vesta", 'r') as f2:
            assert compare_vesta_strings(f1.read(), f2.read())

def test_set_site_color(sample_vestafile):
    """Tests set_site_color"""
    # Check that writing works as expected.
    sample_vestafile.set_site_color(1,12,16,100)
    expected_sitet = """SITET
    1 Cu 1.2800 12 16 100 34 71 220 204 0
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color not changed as expected"
    # Check exception
    with pytest.raises(IndexError):
        sample_vestafile.set_site_color(0,20,30,40)
    # Make sure nothing got changed.
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color changed when it shouldn't have"
    # Test what happens if do a list indexing.
    sample_vestafile.set_site_color([1],15,25,35)
    expected_sitet = """SITET
    1 Cu 1.2800 15 25 35 34 71 220 204 0
    0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color from list of indices didn't work"
    # To test: index out of range.
    try:
        sample_vestafile.set_site_color(2,11,22,33)
    except IndexError:
        # Currently it logs a warning. But I might change this behaviour in the future.
        pass
    # Confirm that nothing changed.
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site colors changed when called out-of-range index"
    # I don't *expect* any side-effects from this function. Dunno how to easily test that, though.

def test_set_atom_color(sample_vestafile):
    # Check that writing works as expected
    sample_vestafile.set_atom_color(1,12,16,100)
    expected_sitet = """SITET
    1 Cu 1.2800 12 16 100 34 71 220 204 0
    0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800  12  16 100  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), "Atom color not changed as expected"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color not changed as expected"
    # Check exception
    with pytest.raises(IndexError):
        sample_vestafile.set_atom_color(0,20,30,40)
    # Make sure nothing got changed
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), "Atom color changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color changed when it shouldn't have"
    # Test element-based indexing
    sample_vestafile.set_atom_color('Cu', 15,25,35)
    expected_sitet = """SITET
    1 Cu 1.2800 15 25 35 34 71 220 204 0
    0 0 0 0 0 0"""
    expected_atomt = """ATOMT
  1         Cu  1.2800  15  25  35  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), "Atom color not changed as expected"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color not changed as expected"
    # Test that override_site_colors=False works
    sample_vestafile.set_atom_color('Cu', 11,22,33, overwrite_site_colors=False)
    expected_atomt = """ATOMT
  1         Cu  1.2800  11  22  33  34  71 220 204
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ATOMT"]), expected_atomt), "Atom color not changed as expected"
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_sitet), "Site color changed when it shouldn't have"
    
def test_lattice_plane(sample_vestafile):
    # Check that deleting a lattice plane that doesn't exist doesn't change things
    with pytest.raises(IndexError):
        sample_vestafile.delete_lattice_plane(0)
    empty_splan = """SPLAN
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), empty_splan), "SPLAN changed when it shouldn't have"
    # Check that we can add a lattice plane
    sample_vestafile.add_lattice_plane(1.5,-1,10, 5.35)
    expected_splan = """SPLAN
    1 1.5 -1 10 5.35 255 0 255 192
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), "Expected lattice plane didn't get added"
    # Add a second lattice plane, with colour
    sample_vestafile.add_lattice_plane(1,0,0, -10, 0, 200, 0, 10)
    expected_splan2 = """SPLAN
    1 1.5 -1 10 5.35 255 0 255 192
    2 1 0 0 -10 0 200 0 10
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan2), "Expected lattice plane didn't get added"
    # Check that deleting reverts as expected
    sample_vestafile.delete_lattice_plane(2)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), "Expected lattice plane didn't get deleted"
    # Add it back then remove number 1. See how re-indexing gets handled.
    sample_vestafile.add_lattice_plane(1,0,0, -10, 0, 200, 0, 10)
    sample_vestafile.delete_lattice_plane(1)
    expected_splan = """SPLAN
    1 1 0 0 -10 0 200 0 10
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), "Expected lattice plane didn't get deleted or reindexed"
    # Check out-of-range
    with pytest.raises(IndexError):
        sample_vestafile.delete_lattice_plane(3)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), expected_splan), "SPLAN changed when it shouldn't have"
    # Check deleting negative indices
    sample_vestafile.delete_lattice_plane(-1)
    assert compare_vesta_strings(str(sample_vestafile["SPLAN"]), empty_splan), "Didn't delete expected lattice plane"
    
def test_delete_isosurface(sample_vestafile):
    # We currently have no isosurface test fixtures.
    # So here we'll make sure it throws the right errors.
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(1)
    empty_isurf = """ISURF
    0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), empty_isurf), "ISURF changed when it shouldn't have"
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(0)
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), empty_isurf), "ISURF changed when it shouldn't have"

def test_set_section_color_scheme(sample_vestafile):
    # Initial values
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""    
    expected_sects = "SECTS  32  1"
    expected_seccl = "SECCL 0"
    # Set to the current colour scheme
    sample_vestafile.set_section_color_scheme("B-G-R")
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), "SECTP doesn't match B-G-R"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), "SECTS doesn't match B-G-R"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), "SECCL doesn't match B-G-R"
    # Reverse it
    sample_vestafile.set_section_color_scheme("R-G-B")
    expected_sectp = """SECTP
 -1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""  
    expected_seccl = "SECCL 1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), "SECTP doesn't match R-G-B"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), "SECTS doesn't match R-G-B"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), "SECCL doesn't match R-G-B"
    # Try an index-based assignment for Y-M-C (a reversed map)
    sample_vestafile.set_section_color_scheme(3)
    expected_seccl = "SECCL 3"
    expected_sects = "SECTS  40  1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), "SECTP doesn't match Y-M-C"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), "SECTS doesn't match Y-M-C"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), "SECCL doesn't match Y-M-C"
    # Finally, cyclic ostwald
    sample_vestafile.set_section_color_scheme("Cyclic: Ostwald")
    expected_seccl = "SECCL 10"
    expected_sects = "SECTS  48  1"
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00"""
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), "SECTP doesn't match Cyclic: Ostwald"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), "SECTS doesn't match Cyclic: Ostwald"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), "SECCL doesn't match Cyclic: Ostwald"
    # Finally, test an error
    with pytest.raises(ValueError):
        sample_vestafile.set_section_color_scheme("Not a real color scheme")
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp), "SECTP changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects), "SECTS changed when it shouldn't have"
    assert compare_vesta_strings(str(sample_vestafile["SECCL"]), expected_seccl), "SECCL changed when it shouldn't have"
    
def test_set_section_cutoff_levels(sample_vestafile):
    # Changing one thing at a time
    expected_sects = "SECTS  32  1"
    sample_vestafile.set_section_cutoff_levels(lattice_max=0.5)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.00000E+00  0.50000E+00  0.00000E+00  0.00000E+00"""
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects)
    # Change two things
    sample_vestafile.set_section_cutoff_levels(lattice_min=0.1, isosurface_min=0.12)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.10000E+00  0.50000E+00  0.12000E+00  0.00000E+00"""
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects)
    # Set the manual flag too
    sample_vestafile.set_section_cutoff_levels(isosurface_max=12, isosurface_auto=False)
    expected_sectp = """SECTP
  1  0.00000E+00  1.00000E+00  0.10000E+00  0.50000E+00  0.12000E+00  0.12000E+02"""
    expected_sects = "SECTS 160  1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects)
    # Then unset the manual flag
    sample_vestafile.set_section_cutoff_levels(isosurface_auto=True)
    expected_sects = "SECTS  32  1"
    assert compare_vesta_strings(str(sample_vestafile["SECTP"]), expected_sectp)
    assert compare_vesta_strings(str(sample_vestafile["SECTS"]), expected_sects)

def test_set_boundary(sample_vestafile):
    # Test setting all 6 parameters
    sample_vestafile.set_boundary(-0.1,1.1,-0.2,1.2,-0.5,0.5)
    expected_bound = """BOUND
       -0.1      1.1      -0.2      1.2      -0.5        0.5
  0   0   0   0  0"""
    assert compare_vesta_strings(str(sample_vestafile["BOUND"]), expected_bound)
    # Test changing one parameter
    sample_vestafile.set_boundary(ymin=0.3)
    expected_bound = """BOUND
       -0.1      1.1       0.3      1.2      -0.5        0.5
  0   0   0   0  0"""
    assert compare_vesta_strings(str(sample_vestafile["BOUND"]), expected_bound)

def test_set_unit_cell_line_visibility(sample_vestafile):
    # Hide line
    assert sample_vestafile.set_unit_cell_line_visibility(show=False) == 0
    expected_ucolp = """UCOLP
   0   0  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp)
    # Show all lines
    assert sample_vestafile.set_unit_cell_line_visibility(all=True) == 2
    expected_ucolp = """UCOLP
   0   2  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp)
    # Show just one line
    assert sample_vestafile.set_unit_cell_line_visibility(show=True) == 1
    expected_ucolp = """UCOLP
   0   1  1.000   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["UCOLP"]), expected_ucolp)

def test_set_compass_visibility(sample_vestafile):
    # Turn off compass
    assert sample_vestafile.set_compass_visibility(False) == 0
    expected_comps = "COMPS 0"
    assert compare_vesta_strings(str(sample_vestafile["COMPS"]), expected_comps)
    # Turn on compass
    assert sample_vestafile.set_compass_visibility(True) == 1
    expected_comps = "COMPS 1"
    assert compare_vesta_strings(str(sample_vestafile["COMPS"]), expected_comps)
    # Turn on compass, but without axes labels
    assert sample_vestafile.set_compass_visibility(True, axes=False) == 2
    expected_comps = "COMPS 2"
    assert compare_vesta_strings(str(sample_vestafile["COMPS"]), expected_comps)

def test_set_scene_view_matrix(sample_vestafile):
    # Apply a valid matrix
    sample_vestafile.set_scene_view_matrix([[0.707107,0.707107,0],[-0.707107,0.707107,0],[0,0,1]])
    expected_scene = """SCENE
 0.707107  0.707107  0.000000  0.000000
-0.707107  0.707107  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
  0.000   0.000
  0.000
  1.000"""
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene)
    # Apply invalid matrix
    with pytest.raises(ValueError):
        sample_vestafile.set_scene_view_matrix([[1,0,0],[0,1,0],[0,0,1],[1,0,0]])
    # Check nothing changed
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene)

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
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene),\
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
    assert compare_vesta_strings(str(sample_vestafile["SCENE"]), expected_scene, prec=6),\
        "Did not properly set view to 'c'."