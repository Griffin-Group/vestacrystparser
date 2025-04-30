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


def test_set_current_phase(sample_vestafile):
    # Check that we have the expected initial value.
    assert sample_vestafile.current_phase == 0, \
        "Did not start with expected active phase of 0."
    # Check that we can change it
    sample_vestafile.set_current_phase(1)
    assert sample_vestafile.current_phase == 1, \
        "Active phase did not change when requested"
    # Test the errors
    # Type error
    with pytest.raises(TypeError):
        sample_vestafile.set_current_phase('foo')
    assert sample_vestafile.current_phase == 1, \
        "Active phase changed when it shouldn't have."
    # index error
    with pytest.raises(IndexError):
        sample_vestafile.set_current_phase(10)
    assert sample_vestafile.current_phase == 1, \
        "Active phase changed when it shouldn't have."
    with pytest.raises(IndexError):
        sample_vestafile.set_current_phase(-5)
    assert sample_vestafile.current_phase == 1, \
        "Active phase changed when it shouldn't have."
    # Check negative indexing.
    sample_vestafile.set_current_phase(-2)
    assert sample_vestafile.current_phase == 0, \
        "Negative indexing didn't work as expected."


def test_getitem(sample_vestafile):
    expected_section1 = """SITET
  1         Cu  1.2800  34  71 220  34  71 220 204  0
  0 0 0 0 0 0"""
    expected_section2 = """SITET
  0 0 0 0 0 0"""
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_section1), \
        "Did not get default phase 0 answer."
    assert compare_vesta_strings(str(sample_vestafile["SITET", 0]),
                                 expected_section1), \
        "Did not get phase 0 with index specified."
    assert compare_vesta_strings(str(sample_vestafile["SITET", 1]),
                                 expected_section2), \
        "Did not get phase 1 with index specified."
    sample_vestafile.set_current_phase(1)
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_section2), \
        "Changing current phase didn't change returned section."
    # Check that specifying an invalid phase does something sensible
    with pytest.raises(IndexError):
        sample_vestafile["SITET", 5]
    with pytest.raises(IndexError):
        sample_vestafile["SITET", -5]
    # Check that negative indexing works
    sample_vestafile.set_current_phase(0)
    assert compare_vesta_strings(str(sample_vestafile["SITET"]), expected_section1)
    assert compare_vesta_strings(str(sample_vestafile["SITET", -1]),
                                 expected_section2), \
        "Negative indexing of phases didn't work."