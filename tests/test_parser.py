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

def compare_vesta_strings(str1:str, str2:str) -> bool:
    """
    Takes two VESTA strings, does basic parsing so no formatting,
    then checks if they are equivalent.
    """
    data1 = [parse_line(x) for x in str1.strip().split('\n')]
    data2 = [parse_line(x) for x in str2.strip().split('\n')]
    # Compare
    assert len(data1) == len(data2)
    for line1, line2 in zip(data1,data2):
        assert line1 == line2
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