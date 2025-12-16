"""
Unit tests for test case with two phases
"""
import os

import pytest

from vestacrystparser.parser import VestaFile

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "two_phase.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def sample_vestafile_onephase() -> VestaFile:
    return VestaFile(os.path.join(DATA_DIR, "Cu_primitive_plain.vesta"))

def test_load(sample_vestafile, sample_vesta_filename):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that it has expected number of fields
    assert len(sample_vestafile) == 89, \
        "Did not load expected number of fields."
    # Do the full comparison
    with open(sample_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile), f.read()), \
            "Full file comparison failed."


def test_save(tmp_path, sample_vestafile, sample_vesta_filename):
    # Write the file (using the tmp_path pytest fixture)
    sample_vestafile.save(tmp_path / "output.vesta")
    # Compare them
    with open(sample_vesta_filename, 'r') as f1:
        with open(tmp_path / "output.vesta", 'r') as f2:
            assert compare_vesta_strings(f1.read(), f2.read())


def test_repr(sample_vestafile):
    assert repr(sample_vestafile) == \
        "<VestaFile: New structure [1 site]; Phase Two [0 sites]>"


def test_set_current_phase(sample_vestafile):
    # Check that we have the expected initial value.
    assert sample_vestafile.current_phase == 1, \
        "Did not start with expected active phase of 1."
    # Check that we can change it
    sample_vestafile.set_current_phase(2)
    assert sample_vestafile.current_phase == 2, \
        "Active phase did not change when requested"
    # Test the errors
    # Type error
    with pytest.raises(TypeError):
        sample_vestafile.set_current_phase('foo')
    assert sample_vestafile.current_phase == 2, \
        "Active phase changed when it shouldn't have."
    # index error
    with pytest.raises(IndexError):
        sample_vestafile.set_current_phase(10)
    assert sample_vestafile.current_phase == 2, \
        "Active phase changed when it shouldn't have."
    with pytest.raises(IndexError):
        sample_vestafile.set_current_phase(-5)
    assert sample_vestafile.current_phase == 2, \
        "Active phase changed when it shouldn't have."
    with pytest.raises(IndexError):
        sample_vestafile.set_current_phase(0)
    assert sample_vestafile.current_phase == 2, \
        "Active phase changed when it shouldn't have."
    # Check negative indexing.
    sample_vestafile.set_current_phase(-2)
    assert sample_vestafile.current_phase == 1, \
        "Negative indexing didn't work as expected."


def test_getitem(sample_vestafile):
    expected_section1 = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  0 0 0 0 0 0"""
    expected_section2 = """SITET
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_section1), \
        "Did not get default phase 1 answer."
    assert compare_vesta_strings(str(sample_vestafile["SITET", 1]),
                                 expected_section1), \
        "Did not get phase 1 with index specified."
    assert compare_vesta_strings(str(sample_vestafile["SITET", 2]),
                                 expected_section2), \
        "Did not get phase 2 with index specified."
    sample_vestafile.set_current_phase(2)
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_section2), \
        "Changing current phase didn't change returned section."
    # Check that specifying an invalid phase does something sensible
    with pytest.raises(IndexError):
        sample_vestafile["SITET", 5]
    with pytest.raises(IndexError):
        sample_vestafile["SITET", -5]
    with pytest.raises(IndexError):
        sample_vestafile["SITET", 0]
    # Check that negative indexing works
    sample_vestafile.set_current_phase(1)
    assert compare_vesta_strings(
        str(sample_vestafile["SITET"]), expected_section1)
    assert compare_vesta_strings(str(sample_vestafile["SITET", -1]),
                                 expected_section2), \
        "Negative indexing of phases didn't work."


def test_title(sample_vestafile):
    assert sample_vestafile.title == "New structure", \
        "First phase title doesn't match."
    sample_vestafile.set_current_phase(2)
    assert sample_vestafile.title == "Phase Two", \
        "Second phase title doesn't match."


def test_nsites(sample_vestafile):
    assert sample_vestafile.nsites == 1, \
        "First phase nsites doesn't match."
    sample_vestafile.set_current_phase(2)
    assert sample_vestafile.nsites == 0, \
        "Second phase nsites doesn't match."


def test_new_phase(sample_vestafile, sample_vestafile_onephase):
    # Add the new empty phase
    sample_vestafile_onephase.new_phase()
    # Update the title
    sample_vestafile_onephase.set_current_phase(2)
    sample_vestafile_onephase.title = "Phase Two"
    # Compare strings.
    # (Can compare directly because both are VestaFiles)
    assert str(sample_vestafile) == str(sample_vestafile_onephase), \
        "Adding a new phase didn't work as expected."


def test_delete_phase(sample_vestafile, sample_vestafile_onephase):
    # Delete the second phase
    # And also check if current_phase gets updated
    sample_vestafile.set_current_phase(2)
    sample_vestafile.delete_phase(2)
    assert str(sample_vestafile) == str(sample_vestafile_onephase), \
        "Deleting a phase didn't work as expected."
    assert sample_vestafile.current_phase == 1, \
        "Deleting the current phase didn't change current_phase."
    # Deleting again should fail
    with pytest.raises(IndexError):
        sample_vestafile.delete_phase(1)
    assert str(sample_vestafile) == str(sample_vestafile_onephase), \
        "Failing to delete a phase changed the file!"


def test_delete_phase2(sample_vestafile, sample_vestafile_onephase):
    original_str = str(sample_vestafile)
    # Fail to delete out-of-bounds index
    with pytest.raises(IndexError):
        sample_vestafile.delete_phase(3)
    with pytest.raises(IndexError):
        sample_vestafile.delete_phase(-3)
    with pytest.raises(IndexError):
        sample_vestafile.delete_phase(0)
    assert str(sample_vestafile) == original_str, \
        "Failing to delete a phase changed the file!"
    # Delete the second phase, but with negative indexing
    # And also check if current_phase gets updated
    sample_vestafile.set_current_phase(2)
    sample_vestafile.delete_phase(-1)
    assert str(sample_vestafile) == str(sample_vestafile_onephase), \
        "Deleting a phase didn't work as expected."
    assert sample_vestafile.current_phase == 1, \
        "Deleting the current phase didn't change current_phase."


def test_copy_phase(sample_vestafile):
    original_str = str(sample_vestafile)
    # Test invalid indices
    with pytest.raises(IndexError):
        sample_vestafile.copy_phase(3)
    with pytest.raises(IndexError):
        sample_vestafile.copy_phase(-3)
    with pytest.raises(IndexError):
        sample_vestafile.copy_phase(0)
    assert str(sample_vestafile) == original_str, \
        "Failing to delete a phase changed the file!"
    # Copy phase 2
    sample_vestafile.copy_phase(2)
    assert sample_vestafile.nphases == 3, \
        "Copying a phase didn't add a new phase!"
    assert str(sample_vestafile["TITLE", 3]) == str(sample_vestafile["TITLE", 2]), \
        "Copying a phase didn't copy over the data."
    assert len(sample_vestafile) == 89 + 24, \
        "Didn't copy over the right number of fields."
    # Confirm that the copied data is, indeed, a copy.
    sample_vestafile.set_current_phase(3)
    sample_vestafile.title = "Phase Three"
    sample_vestafile.set_current_phase(2)
    assert sample_vestafile.title == "Phase Two", \
        "Copying a phase incorrectly linked the data rather than copying."
    # Test negative indexing.
    sample_vestafile.copy_phase(-3) # The first phase.
    assert sample_vestafile.nphases == 4, \
        "Copying a phase with negative index didn't add a new phase!"
    assert str(sample_vestafile["TITLE", 1]) == str(sample_vestafile["TITLE", 4]), \
        "Copying a phase with negative index didn't copy over the data!"
    assert len(sample_vestafile) == 89 + 24 + 24, \
        "Didn't copy over the right number of fields."


def test_import_phases_from_file(sample_vestafile, sample_vesta_filename):
    sample_vestafile.import_phases(sample_vesta_filename)
    assert sample_vestafile.nphases == 4, \
        "Failed to import the correct number of phases."
    assert sample_vestafile["TITLE", 4].data[0][0] == "Phase Two", \
        "Failed to import the correct number of phases."
    assert len(sample_vestafile) == 89 + 48, \
        "Didn't import the right number of fields."


def test_import_phases(sample_vestafile):
    # For simplicity, we'll import from self.
    sample_vestafile.import_phases(sample_vestafile)
    assert sample_vestafile.nphases == 4, \
        "Failed to import the correct number of phases."
    assert sample_vestafile["TITLE", 4].data[0][0] == "Phase Two", \
        "Failed to import the correct number of phases."
    assert len(sample_vestafile) == 89 + 48, \
        "Didn't import the right number of fields."
    # Check that we copied.
    sample_vestafile.title = "Foo bar"
    assert sample_vestafile["TITLE", 3].data[0][0] == "New structure", \
        "import_phases incorrectly linked data instead of copying."


def test_rearrange_phases(sample_vestafile):
    # Test invalid rearrangements
    original_str = str(sample_vestafile)
    with pytest.raises(IndexError):
        # Too short
        sample_vestafile.rearrange_phases([])
    with pytest.raises(IndexError):
        # Too long
        sample_vestafile.rearrange_phases([1, 2, 3])
    with pytest.raises(IndexError):
        # Wrong values (duplicate if accept negative indexing)
        # (We don't currently accept negative indexing, but we might later)
        sample_vestafile.rearrange_phases([-1, 2])
    with pytest.raises(IndexError):
        # Wrong values
        sample_vestafile.rearrange_phases([3, 4])
    with pytest.raises(IndexError):
        # Wrong values (including 0).
        sample_vestafile.rearrange_phases([0, 1])
    with pytest.raises(IndexError):
        # Duplicate values
        sample_vestafile.rearrange_phases([1, 1])
    assert str(sample_vestafile) == original_str, \
        "Failing to rearrange phases changed the file!"
    assert sample_vestafile.current_phase == 1, \
        "Failing to rearrange phases changed the current phase!"
    # Test null rearrangement
    sample_vestafile.rearrange_phases([1, 2])
    assert str(sample_vestafile) == original_str, \
        "Identity rearrangement changed the file."
    assert sample_vestafile.current_phase == 1, \
        "Identity rearranegement changed the current phase."
    # Test an actual swap
    sample_vestafile.rearrange_phases([2, 1])
    assert sample_vestafile.nphases == 2, \
        "Rearrangeing phases changed number of phases."
    assert sample_vestafile.current_phase == 2, \
        "Rearrangeing phases didn't change the current phase."
    assert str(sample_vestafile) != original_str, \
        "Rearranging phases failed to change the files."
    assert sample_vestafile.title == "New structure"
    assert sample_vestafile["TITLE", 1].data[0][0] == "Phase Two"


def test_set_phase_orientation_basic(sample_vestafile):
    # Simple case of testing on the basic cubic cell.
    sample_vestafile.set_current_phase(2)
    expected_lorient = """LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000"""
    expected_lmatrix = """LMATRIX
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000"""
    # Null result
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [1, 0, 0], [0, 0, 1],
                                           False, False, 0)
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient), \
        "LORIENT changed when I gave boring inputs!"
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix), \
        "LMATRIX changed when I gave boring inputs!"
    # For cubic cell, hkl and uvw are equivalent.
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [1, 0, 0], [0, 0, 1],
                                           True, True, 0)
    expected_lorient = """LORIENT
 -1   1   1   0   0
 1.000000  0.000000  0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000"""
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient), \
        "LORIENT didn't handle hkl in simple cubic setting properly."
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix), \
        "LMATRIX didn't handle hkl in simple cubic setting properly."
    # Test some simple, pre-computed cases
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [0, 1, 0], [0, 0, 1],
                                           False, False, 0)
    expected_lorient = """LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000"""
    expected_lmatrix = """LMATRIX
 0.000000 -1.000000  0.000000  0.000000
 1.000000  0.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient, prec=6), \
        "LORIENT didn't handle simple orientation change."
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix, prec=6), \
        "LMATRIX didn't handle simple orientation change."
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [1, 0, 0], [0, 1, 0],
                                           False, False, 0)
    expected_lorient = """LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  1.000000  0.000000"""
    expected_lmatrix = """LMATRIX
 1.000000  0.000000  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000 -1.000000  0.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient, prec=6), \
        "LORIENT didn't handle simple orientation change."
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix, prec=6), \
        "LMATRIX didn't handle simple orientation change."
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [0, 1, 0], [1, 0, 0],
                                           False, False, 0)
    expected_lorient = """LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  1.000000  1.000000  0.000000  0.000000"""
    expected_lmatrix = """LMATRIX
 0.000000  0.000000  1.000000  0.000000
 1.000000  0.000000  0.000000  0.000000
 0.000000  1.000000  0.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient, prec=6), \
        "LORIENT didn't handle simple orientation change."
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix, prec=6), \
        "LMATRIX didn't handle simple orientation change."
    # Try a slightly trickier orientation change
    sample_vestafile.set_phase_orientation([1, 0, 0], [0, 0, 1],
                                           [1, 1, 0], [0, 0, 1],
                                           False, False, 0)
    expected_lorient = """LORIENT
 -1   0   0   0   0
 1.000000  0.000000  0.000000  1.000000  1.000000  0.000000
 0.000000  0.000000  1.000000  0.000000  0.000000  1.000000"""
    expected_lmatrix = """LMATRIX
 0.707107 -0.707107  0.000000  0.000000
 0.707107  0.707107  0.000000  0.000000
 0.000000  0.000000  1.000000  0.000000
 0.000000  0.000000  0.000000  1.000000
 0.000000  0.000000  0.000000"""
    assert compare_vesta_strings(str(sample_vestafile["LORIENT"]), expected_lorient, prec=6), \
        "LORIENT didn't handle [110] orientation."
    assert compare_vesta_strings(str(sample_vestafile["LMATRIX"]), expected_lmatrix, prec=6), \
        "LMATRIX didn't handle [110] orientation."
    