"""
Unit tests for loading a complex POSCAR with H-bonds
"""
import os

import pytest

from vestacrystparser.parser import VestaFile
from vestacrystparser.convert import vesta_from_structure, vesta_from_poscar, \
    Structure
# TODO: Skip if cannot find pymatgen.

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "CBaMnBr4_sq.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def poscar_filename() -> str:
    return os.path.join(DATA_DIR, "CBaMnBr4_sq.vasp")


@pytest.fixture
def poscar_structure(poscar_filename) -> Structure:
    return Structure.from_file(poscar_filename)

def test_vesta_from_poscar(poscar_filename, sample_vestafile):
    # Load the file, then compare it with the file we loaded.
    converted_file = vesta_from_poscar(poscar_filename)
    # Compare line-by-line, so can diagnose issues
    for (sec1, sec2) in zip(converted_file, sample_vestafile):
        # Title is not saved in pymatgen.core.Structure
        assert compare_vesta_strings(str(sec1), str(sec2), prec=6)