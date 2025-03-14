import os

import pytest

from vestacrystparser.parser import VestaFile, parse_line

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')

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

def test_load():
    # Read a file
    fname = os.path.join(DATA_DIR, "Cu_primitive_plain.vesta")
    vfile = VestaFile(fname)
    # Test that is has expected number of fields
    assert len(vfile) == 65, "Did not load expected number of fields."
    # Test that we read the atom data right.
    section = vfile["SITET"]
    expected_sitet = [[1,"Cu",1.28,34,71,220,34,71,220,204,0],
                      [0,0,0,0,0,0]]
    assert section.data == expected_sitet, "SITET data not what was expected."
    expected_bondp = """BONDP
  1  16  0.250  2.000 127 127 127"""
    assert compare_vesta_strings(str(vfile["BONDP"]), expected_bondp)
    # Do the full comparison
    with open(fname, 'r') as f:
        assert compare_vesta_strings(str(vfile), f.read()), "Full file comparison failed."