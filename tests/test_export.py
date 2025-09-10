"""
Unit tests for the export module.

Needs to accept both the cases where VESTA does or does not exist.
And to only run when requested (because it litters).

Complicated further by asynchronicity.

Call pytest with --vesta to test these functions.
If VESTA is not found during execution (or we believe we don't find VESTA),
then these tests will be flagged as an expected failure.
"""

import os
import tempfile
import time

import pytest

import vestacrystparser.export

from test_parser import DATA_DIR


@pytest.mark.vesta
def test_export_image():
    with tempfile.NamedTemporaryFile('w+b', suffix=".png") as f:
        try:
            vestacrystparser.export.export_image_from_file(
                os.path.join(DATA_DIR, "Cu_primitive_plain.vesta"),
                f.name,
                block=False,
            )
        except vestacrystparser.export.NoVestaError:
            pytest.xfail("VESTA not found. NoVestaError raised properly.")
        else:
            # Check that the file was actually written.
            # We manually reproduce the Timeout logic here.
            # N.B. NamedTemporaryFile creates an empty file.
            elapsed = 0
            increment = 0.05
            while elapsed < 2:
                time.sleep(0.05)
                if os.path.getsize(f.name) > 60:
                    # Test passed
                    return
                else:
                    elapsed += increment
            pytest.fail("Failed to write PNG file within time limit.")


@pytest.mark.vesta
def test_export_image_block():
    with tempfile.TemporaryDirectory() as td:
        outfile = os.path.join(td, "tmp.png")
        try:
            vestacrystparser.export.export_image_from_file(
                os.path.join(DATA_DIR, "Cu_primitive_plain.vesta"),
                outfile,
                block=True,
                timeout=2,
            )
        except vestacrystparser.export.NoVestaError:
            pytest.xfail("VESTA not found. NoVestaError raised properly.")
        else:
            # Check that the file was actually written.
            try:
                # I find we need to sleep a bit just to let the OS catch up.
                time.sleep(0.1)
                assert os.path.getsize(outfile) > 60, \
                    "PNG file too small to be a PNG."
            except FileNotFoundError:
                pytest.fail("Image file was not written!")

# TODO
# Input file not found.
# Output file invalid.
# VESTA hangs and times out.
# Without close tag.

# Also, the proper way to handle temporary files is probably with pytest fixtures.
