"""
Unit tests for test case with two phases
"""
import os

import pytest

from vestacrystparser.parser import VestaFile
from vestacrystparser.convert import vesta_from_structure, Structure

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "hBN.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def poscar_filename() -> str:
    return os.path.join(DATA_DIR, "POSCAR_hBN.vasp")


@pytest.fixture
def poscar_structure(poscar_filename) -> Structure:
    return Structure.from_file(poscar_filename)


def test_hBN_title(sample_vestafile):
    """This file has a title with quotes and caps in it. May be tricky."""
    expected_title = """TITLE
"B1 N1"
"""
    assert compare_vesta_strings(
        str(sample_vestafile["TITLE"]), expected_title)


def test_convert(poscar_structure, sample_vestafile):
    # Load the file, then compare it with the file we loaded.
    converted_file = vesta_from_structure(poscar_structure)
    # Compare line-by-line, so can diagnose issues
    for (sec1, sec2) in zip(converted_file, sample_vestafile):
        if sec1.header != "TITLE":
            # Title is not saved in pymatgen.core.Structure
            assert compare_vesta_strings(str(sec1), str(sec2), prec=6)
