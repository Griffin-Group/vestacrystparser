"""
Unit tests for test case with volumetric data
"""
import os

import pytest

from vestacrystparser.parser import VestaFile

from test_parser import compare_vesta_strings, DATA_DIR


@pytest.fixture
def sample_vesta_filename() -> str:
    return os.path.join(DATA_DIR, "CHGCAR_PbSe.vesta")


@pytest.fixture
def sample_vestafile(sample_vesta_filename) -> VestaFile:
    return VestaFile(sample_vesta_filename)


@pytest.fixture
def sample_vesta_filename2() -> str:
    return os.path.join(DATA_DIR, "CHGCAR_PbSe_div.vesta")


@pytest.fixture
def sample_vestafile2(sample_vesta_filename2) -> VestaFile:
    return VestaFile(sample_vesta_filename2)


def test_load(sample_vestafile, sample_vesta_filename):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that it has expected number of fields
    assert len(sample_vestafile) == 66, \
        "Did not load expected number of fields."
    # Do the full comparison
    with open(sample_vesta_filename, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile), f.read()), \
            "Full file comparison failed."


def test_load2(sample_vestafile2, sample_vesta_filename2):
    # Implicitly by the Fixture, we're testing the Load function.
    # Test that it has expected number of fields
    assert len(sample_vestafile2) == 66, \
        "Did not load expected number of fields."
    # Do the full comparison
    with open(sample_vesta_filename2, 'r') as f:
        assert compare_vesta_strings(str(sample_vestafile2), f.read()), \
            "Full file comparison failed."


def test_add_isosurface(sample_vestafile):
    # Isosurface with default parameters
    sample_vestafile.add_isosurface(0.1234)
    expected_isurf = """ISURF
  1   0  0.0321249 255 255   0 127 255
  2   0  0.1234000 255 255   0 127 255
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Adding default isosurface didn't work as expected"
    # Isosurface with modified parameters
    sample_vestafile.add_isosurface(0.54321, mode=2, r=100, g=110, b=120,
                                    opacity1=150, opacity2=80)
    expected_isurf = """ISURF
  1   0  0.0321249 255 255   0 127 255
  2   0  0.1234000 255 255   0 127 255
  3   2  0.5432100 100 110 120 150  80
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Adding custom isosurface didn't work as expected"


def test_delete_isosurface(sample_vestafile):
    # Check invalid indices while we still have an isosurface.
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(0)
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(2)
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(-2)
    expected_isurf = """ISURF
  1   0  0.0321249 255 255   0 127 255
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf), \
        "ISURF modified in failed deletion!"
    # Delete the isosurface
    sample_vestafile.delete_isosurface(1)
    expected_isurf = """ISURF
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf), \
        "Failed to delete the isosurface."
    # Check that we can't delete more.
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(0)
    with pytest.raises(IndexError):
        sample_vestafile.delete_isosurface(1)
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf), \
        "ISURF modified in failed deletion!"


def test_delete_isosurface_negative(sample_vestafile):
    # Delete the isosurface using a negative index
    sample_vestafile.delete_isosurface(-1)
    expected_isurf = """ISURF
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf), \
        "Failed to delete the isosurface."


def test_delete_isosurface_multi(sample_vestafile):
    # Add an isosurface, so we can delete the other one and test re-indexing
    sample_vestafile.add_isosurface(0.1234)
    expected_isurf = """ISURF
  1   0  0.0321249 255 255   0 127 255
  2   0  0.1234000 255 255   0 127 255
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Adding default isosurface didn't work as expected"
    sample_vestafile.delete_isosurface(-2)
    expected_isurf = """ISURF
  1   0  0.1234000 255 255   0 127 255
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Deleting an isosurface didn't reindex the others properly."


def test_edit_isosurface(sample_vestafile):
    # Edit one property
    sample_vestafile.edit_isosurface(1, level=0.1)
    expected_isurf = """ISURF
  1   0  0.1000000 255 255   0 127 255
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Failed to edit isosurface level."
    # Edit all the other properties
    sample_vestafile.edit_isosurface(1, mode=1, r=120, g=105, b=200,
                                     opacity1=0, opacity2=200)
    expected_isurf = """ISURF
  1   1  0.1000000 120 105 200   0 200
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "Failed to edit isosurface properties."
    # Use negative indexing
    sample_vestafile.edit_isosurface(-1, level=0.2)
    expected_isurf = """ISURF
  1   1  0.2000000 120 105 200   0 200
  0   0   0   0"""
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "edit_isosurface failed to read negative index."
    # Check that invalid indices are invalid
    with pytest.raises(IndexError):
        sample_vestafile.edit_isosurface(0, level=0.3)
    with pytest.raises(IndexError):
        sample_vestafile.edit_isosurface(2, mode=2)
    with pytest.raises(IndexError):
        sample_vestafile.edit_isosurface(-2, opacity1=42)
    assert compare_vesta_strings(str(sample_vestafile["ISURF"]), expected_isurf, prec=1e-6), \
        "ISURF edited on failed index!"


def test_add_volumetric_data(sample_vestafile):
    # Default parameters
    sample_vestafile.add_volumetric_data("Option1.vasp")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Couldn't add volumetric data with default parameters."
    # other options
    sample_vestafile.add_volumetric_data(
        "ABC.vasp", factor=1.5, mode="subtract")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
-1.500000 ABC.vasp
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to subtract volumetric data."
    sample_vestafile.add_volumetric_data(
        "XYZ.vasp", factor=-0.1, mode="multiply")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
-1.500000 ABC.vasp
x-0.100000 XYZ.vasp
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to multiply volumetric data."
    sample_vestafile.add_volumetric_data(
        "../my cool directory/my file.xyz", mode="divide")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
-1.500000 ABC.vasp
x-0.100000 XYZ.vasp
/+1.000000 ../my cool directory/my file.xyz
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to divide volumetric data with spaces in name."
    # Check symbolic options
    sample_vestafile.add_volumetric_data("FOO", factor=2, mode="+")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
-1.500000 ABC.vasp
x-0.100000 XYZ.vasp
/+1.000000 ../my cool directory/my file.xyz
+2.000000 FOO
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to add volumetric data."
    sample_vestafile.add_volumetric_data("BAR", mode="-")
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
+1.000000 Option1.vasp
-1.500000 ABC.vasp
x-0.100000 XYZ.vasp
/+1.000000 ../my cool directory/my file.xyz
+2.000000 FOO
-1.000000 BAR
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to subtract volumetric data."
    # Test invalid mode
    with pytest.raises(ValueError):
        sample_vestafile.add_volumetric_data("ERROR", mode="?")
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "IMPORT_DENSITY incorrectly altered on failed write."


def test_add_volumetric_data_replace(sample_vestafile):
    # Replace
    sample_vestafile.add_volumetric_data("void.xyz", mode="replace", factor=4)
    expected_density = """IMPORT_DENSITY 1
+4.000000 void.xyz
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to replace volumetric data."


def test_add_volumetric_data_replace2(sample_vestafile):
    # Replace
    sample_vestafile.set_volumetric_interpolation_factor(4)
    sample_vestafile.add_volumetric_data("void.xyz", mode="replace", factor=4)
    expected_density = """IMPORT_DENSITY 4
+4.000000 void.xyz
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to replace volumetric data with interpolation factor."


def test_delete_volumetric_data(sample_vestafile):
    # Check invalid indices while we still have data.
    with pytest.raises(IndexError):
        sample_vestafile.delete_volumetric_data(0)
    with pytest.raises(IndexError):
        sample_vestafile.delete_volumetric_data(2)
    with pytest.raises(IndexError):
        sample_vestafile.delete_volumetric_data(-2)
    expected_density = """IMPORT_DENSITY 1
+1.000000 CHGCAR_PbSe.vasp
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "IMPORT_DENSITY modified in failed deletion!"
    # Delete the data
    sample_vestafile.delete_volumetric_data(1)
    assert "IMPORT_DENSITY" not in sample_vestafile, \
        "Deleting the only data didn't delete IMPORT_DENSITY"
    # Check that we can't delete more.
    with pytest.raises(IndexError):
        sample_vestafile.delete_volumetric_data(1)
    with pytest.raises(IndexError):
        sample_vestafile.delete_volumetric_data(0)


def test_delete_volumetric_data_complex(sample_vestafile):
    # Set up a more elaborate volumetric data.
    sample_vestafile.add_volumetric_data("FOO")
    sample_vestafile.set_volumetric_interpolation_factor(4)
    expected_density = """IMPORT_DENSITY 4
+1.000000 CHGCAR_PbSe.vasp
+1.000000 FOO
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to configure volumetric data"
    # Delete the isosurface using a negative index
    sample_vestafile.delete_volumetric_data(-2)
    expected_density = """IMPORT_DENSITY 4
+1.000000 FOO
"""
    assert "IMPORT_DENSITY" in sample_vestafile, \
        "Accidentally deleted IMPORT_DENSITY!"
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to delete the correct isosurface."


def test_set_volumetric_interpolation_factor(sample_vestafile):
    sample_vestafile.set_volumetric_interpolation_factor(7)
    expected_density = """IMPORT_DENSITY 7
+1.000000 CHGCAR_PbSe.vasp
"""
    assert compare_vesta_strings(str(sample_vestafile["IMPORT_DENSITY"]), expected_density), \
        "Failed to set volumetric interpolation factor"
