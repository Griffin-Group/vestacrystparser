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
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch

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


@pytest.mark.vesta
def test_export_image_subdirectory():
    """Regression test for Issue #1.
    https://github.com/Griffin-Group/vestacrystparser/issues/1

    When input is not in the PWD, VESTA would interpret a relative
    output path as relative to the input file's directory, causing it to write
    to the wrong location (e.g. work/work/file.png instead of work/file.png).
    Passing an absolute output path to VESTA fixes this.
    """
    with tempfile.TemporaryDirectory() as td:
        # Place the input file in a subdirectory of the temp dir.
        subdir = os.path.join(td, "subdir")
        os.makedirs(subdir)
        src = os.path.join(DATA_DIR, "Cu_primitive_plain.vesta")
        vesta_path = os.path.join(subdir, "Cu_primitive_plain.vesta")
        shutil.copy(src, vesta_path)
        # Output is in the same subdirectory.
        outfile = os.path.join(subdir, "out.png")
        try:
            vestacrystparser.export.export_image_from_file(
                vesta_path,
                outfile,
                block=True,
                timeout=10,
            )
        except vestacrystparser.export.NoVestaError:
            pytest.xfail("VESTA not found. NoVestaError raised properly.")
        else:
            time.sleep(0.1)
            # The file must exist at the expected absolute location,
            # NOT at subdir/subdir/out.png (the old buggy behaviour).
            wrong_path = os.path.join(subdir, "subdir", "out.png")
            assert not os.path.exists(wrong_path), \
                f"File written to wrong (doubly-nested) path: {wrong_path}"
            try:
                assert os.path.getsize(outfile) > 60, \
                    "PNG file too small to be a PNG."
            except FileNotFoundError:
                pytest.fail("Image file was not written to the expected path!")


# TODO
# Input file not found.
# Output file invalid.
# VESTA hangs and times out.
# Without close tag.

# Also, the proper way to handle temporary files is probably with pytest fixtures.


# ---------------------------------------------------------------------------
# CLI tests
# These tests do NOT require VESTA to be installed. They verify that main()
# parses arguments correctly and passes them through to
# export_image_from_file. export_image_from_file is mocked out entirely.
# ---------------------------------------------------------------------------

def _run_cli(argv):
    """Run the export CLI main() with the given argv.

    Patches sys.argv and replaces export_image_from_file with a MagicMock so
    that no real VESTA call is made. Returns the mock so callers can inspect
    how it was called.
    """
    mock_fn = MagicMock()
    with patch("sys.argv", argv), \
         patch("vestacrystparser.export.export_image_from_file", mock_fn):
        vestacrystparser.export.main()
    return mock_fn


def test_cli_basic():
    """Positional args only: scale defaults to 1, timeout defaults to None."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=1, timeout=None)


def test_cli_scale_long():
    """--scale long form is parsed as an int and forwarded."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png",
                        "--scale", "4"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=4, timeout=None)


def test_cli_scale_short():
    """-s short form is equivalent to --scale."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png",
                        "-s", "4"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=4, timeout=None)


def test_cli_timeout_long():
    """--timeout long form is parsed as a float and forwarded."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png",
                        "--timeout", "30.5"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=1, timeout=30.5)


def test_cli_timeout_short():
    """-t short form is equivalent to --timeout."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png",
                        "-t", "30.5"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=1, timeout=30.5)


def test_cli_all_args():
    """All optional arguments together are forwarded correctly."""
    mock_fn = _run_cli(["vestacrystparser.export", "in.vesta", "out.png",
                        "-s", "2", "-t", "10.0"])
    mock_fn.assert_called_once_with("in.vesta", "out.png",
                                    scale=2, timeout=10.0)


def test_cli_missing_args():
    """Omitting required positional arguments causes argparse to exit."""
    with pytest.raises(SystemExit):
        _run_cli(["vestacrystparser.export"])
