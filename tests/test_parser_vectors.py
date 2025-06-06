"""
Unit tests for test case with existing vectors
"""
import os
import math

import pytest

from vestacrystparser.parser import VestaFile

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "DTO_template.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


def test_load(sample_vestafile, sample_vesta_filename):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that it has expected number of fields
    assert len(sample_vestafile) == 65, \
        "Did not load expected number of fields."
    # Do the full comparison
    with open(sample_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile), f.read()), \
            "Full file comparison failed."


def test_edit_vector_type(sample_vestafile):
    # Simple updating of coordinates
    sample_vestafile.edit_vector_type(
        1, x=0.11, y=0.22, z=0.33, coord_type="modulus")
    expected_vectr = """VECTR
   1    0.11000    0.22000    0.33000 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.350 255   0   0 1
   3  0.350 255   0   0 1
   4  0.350 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "Updating modulus coordinates didn't work as expected"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "Updating modulus coordinates didn't work as expected"
    # Change some other parameters (and leave some the same, but explicitly).
    sample_vestafile.edit_vector_type(2, polar=True, g=150, radius=0.5,
                                      add_atom_radius=False, penetrate_atoms=True)
    expected_vectr = """VECTR
   1    0.11000    0.22000    0.33000 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 1
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.500 255 150   0 1
   3  0.350 255   0   0 1
   4  0.350 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "Updating polar, g, radius of 2 didn't work as expected"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "Updating polar, g, radius of 2 didn't work as expected"
    # Use negative indexing, and add_atom_radius
    sample_vestafile.edit_vector_type(-2, r=100, g=110, b=120,
                                      add_atom_radius=True)
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.500 255 150   0 1
   3  0.350 100 110 120 3
   4  0.350 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "Updating colour and add_atom_radius of -2 didn't work as expected"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "Updating colour and add_atom_radius of -2 didn't work as expected"
    # Test xyz coords
    sample_vestafile.edit_vector_type(4, 5/2, math.sqrt(3)*5/2, 0, coord_type="xyz",
                                      penetrate_atoms=False, polar=False)
    expected_vectr = """VECTR
   1    0.11000    0.22000    0.33000 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 1
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    0.00000    5.00000    0.00000 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.500 255 150   0 1
   3  0.350 100 110 120 3
   4  0.350 255   0   0 0
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=6), \
        "Updating xyz coords didn't work as expected"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "Updating penetrate_atoms didn't work as expected"
    # Test index errors
    with pytest.raises(IndexError):
        sample_vestafile.edit_vector_type(5, 1, 2, 3)
    with pytest.raises(IndexError):
        sample_vestafile.edit_vector_type(0, 4, 5, 6)
    with pytest.raises(IndexError):
        sample_vestafile.edit_vector_type(-10, 7, 8, 9)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=6), \
        "VECTR changed when it shouldn't have due to IndexError"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT changed when it shouldn't have due to IndexError"
    # Test incomplete x,y,z specification
    with pytest.raises(TypeError):
        sample_vestafile.edit_vector_type(1, x=1.0)
    with pytest.raises(TypeError):
        sample_vestafile.edit_vector_type(1, y=1.0)
    with pytest.raises(TypeError):
        sample_vestafile.edit_vector_type(1, z=1.0)
    with pytest.raises(TypeError):
        sample_vestafile.edit_vector_type(2, x=1.5, z=1.2)
    with pytest.raises(TypeError):
        sample_vestafile.edit_vector_type(2, x=1.5, y=2.0, radius=5.0)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr, prec=6), \
        "VECTR changed when it shouldn't have due to incomplete x,y,z"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT changed when it shouldn't have due to incomplete x,y,z"


def test_delete_vector_type(sample_vestafile):
    expected_vectr = """VECTR
   1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.350 255   0   0 1
   3  0.350 255   0   0 1
   4  0.350 255   0   0 1
 0 0 0 0 0"""
    # First, we'll test index errors before we delete our list.
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(5)
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(0)
    with pytest.raises(IndexError):
        sample_vestafile.delete_vector_type(-10)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR changed when it shouldn't have due to IndexError"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT changed when it shouldn't have due to IndexError"
    # Test that deleting the first element works as expected.
    sample_vestafile.delete_vector_type(1)
    expected_vectr = """VECTR
   1    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   2   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   3    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.350 255   0   0 1
   3  0.350 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly deleted vector 1"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT improperly deleted vector 1"
    # Try negative indexing
    sample_vestafile.delete_vector_type(-2)
    expected_vectr = """VECTR
   1    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   2    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    expected_vectt = """VECTT
   1  0.350 255   0   0 1
   2  0.350 255   0   0 1
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly deleted vector -2"
    assert compare_vesta_strings(str(sample_vestafile["VECTT"]), expected_vectt), \
        "VECTT improperly deleted vector -2"


def test_set_vector_to_site(sample_vestafile):
    expected_vectr = """VECTR
   1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    # Test invalid inputs
    with pytest.raises(IndexError):
        sample_vestafile.set_vector_to_site(0, 1)
    with pytest.raises(IndexError):
        sample_vestafile.set_vector_to_site(2, -1)
    with pytest.raises(IndexError):
        sample_vestafile.set_vector_to_site(5, 1)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly modified with invalid indices."
    # Now add a vector.
    sample_vestafile.set_vector_to_site(3, 1)
    expected_vectr = """VECTR
   1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
    1   0    0    0    0 
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "Failed to attach a vector to a site."


def test_remove_vector_from_site(sample_vestafile):
    expected_vectr = """VECTR
   1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
    3   0    0    0    0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    # Test invalid inputs
    with pytest.raises(IndexError):
        sample_vestafile.remove_vector_from_site(0, 1)
    with pytest.raises(IndexError):
        sample_vestafile.remove_vector_from_site(5, 1)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly modified with invalid type."
    # Test removing a vector from a non-matching site,
    # which should do nothing.
    sample_vestafile.remove_vector_from_site(1, 2)
    sample_vestafile.remove_vector_from_site(2, 0)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly modified with non-matching sites."
    # Now delete a vector.
    sample_vestafile.remove_vector_from_site(3, 3)
    expected_vectr = """VECTR
   1    0.40825    0.40825    0.40825 0
    1   0    0    0    0
 0 0 0 0 0
   2    0.40825    0.40825   -1.22474 0
    2   0    0    0    0
 0 0 0 0 0
   3   -0.40825    1.22474   -0.40825 0
 0 0 0 0 0
   4    1.22474   -0.40825   -0.40825 0
    4   0    0    0    0
 0 0 0 0 0
 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "Did not properly delete vector."
    sample_vestafile.remove_vector_from_site(3, 0)
    assert compare_vesta_strings(str(sample_vestafile["VECTR"]), expected_vectr), \
        "VECTR improperly modified with non-matching sites."


def test_nvectors(sample_vestafile):
    assert sample_vestafile.nvectors == 4


def test_set_boundary(sample_vestafile):
    # Not, strictly, a vector test. But this file also has hidden atoms.
    # So we see if my handling of this is okay.
    sample_vestafile.set_boundary(xmax=2)
    expected_bound = """BOUND
       0        2         0        1         0        1
  0   0   0   0  0"""
    expected_dlatm = """DLATM
 -1"""
    assert compare_vesta_strings(str(sample_vestafile["BOUND"]), expected_bound), \
        "Boundary did not change as expected!"
    assert compare_vesta_strings(str(sample_vestafile["DLATM"]), expected_dlatm), \
        "On changing the boundary, DLATM should have reset. But it didn't."

def test_add_site(sample_vestafile):
    # Mostly to see DLATM get reset.
    # It also draws in a H-bond.
    sample_vestafile.add_site("H", "H1", 0.1, 0.1, 0.1, add_bonds=True)
    expected_dlatm = """DLATM
 -1"""
    assert compare_vesta_strings(str(sample_vestafile["DLATM"]), expected_dlatm), \
        "On adding a site, DLATM should have reset. But it didn't."

