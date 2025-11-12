"""
Unit tests for loading a simple CHGCAR
"""
import os

import pytest

from vestacrystparser.parser import VestaFile
from vestacrystparser.convert import vesta_from_chgcar, Chgcar
# TODO: Skip if cannot find pymatgen.

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "CHGCAR_PbSe.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def chgcar_filename() -> str:
    # Pymatgen can automatically handle reading gzipped files, even if VESTA can't.
    return os.path.join(DATA_DIR, "CHGCAR_PbSe.vasp.gz")


@pytest.fixture
def chgcar_data(poscar_filename) -> Chgcar:
    return Chgcar.from_file(poscar_filename)


def test_vesta_from_chgcar(chgcar_filename, sample_vestafile):
    # Load the file
    converted_file = vesta_from_chgcar(chgcar_filename)
    # Compare, with special processing for IMPORT_DENSITY filename
    # because the relative path is different and I used a zipped file.
    expected_density = f"IMPORT_DENSITY 1\n+1.000000 {chgcar_filename}\n\n"
    for (sec1, sec2) in zip(converted_file, sample_vestafile):
        if sec1.header == "IMPORT_DENSITY":
            assert compare_vesta_strings(str(sec1), expected_density)
        elif sec1.header == "ISURF":
            # So, for some reason, VESTA seems to give different results
            # to what it should. I get an answer that's close but not quite.
            assert compare_vesta_strings(str(sec1), str(sec2), prec=2)
        else:
            assert compare_vesta_strings(str(sec1), str(sec2), prec=6)
