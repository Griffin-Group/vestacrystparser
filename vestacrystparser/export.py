#!/usr/bin/env python3
# Copyright 2025 Bernard Field
"""Open VESTA and export images.

:func:`export_image_from_file` is the core function,
which directly opens a VESTA file then exports an image file
using VESTA's (rather sparse) command line interface.

This requires a working VESTA installation on your system.
"""

import platform
import os
import subprocess
import time


class NoVestaError(OSError):
    """VESTA does not exist or cannot be found."""
    pass


def export_image_from_file(input: str, output: str, scale: int = 1,
                           close: bool = True, block: bool = True,
                           timeout: float = None):
    """Opens a file in VESTA and saves it as an image.

    You can open VESTA before running this command to set the size of the
    window, which determines the size of the image.

    Runs ASYNCHRONOUSLY. May be subject to race conditions.
    Modifying the files while running this command will
    cause unexpected behaviour. I do not know how to retrieve an exit call,
    besides checking if `output` has been written (which is what `block` does).

    Note that, even with the `close` argument, VESTA will remain open after
    this call. (`close` just closes the tab within VESTA.) You are 
    responsible for closing it yourself when you're done.

    `block` is strongly recommended if you are doing more than a couple
    at once, because I've found VESTA will max-out on processes if it
    tries to open too many files simultaneously.

    VESTA has a command line interface:
    https://jp-minerals.org/vesta/en/doc/VESTAch17.html

    Koichi Momma gives directions on how to use VESTA's command line interface:
    https://groups.google.com/g/vesta-discuss/c/xePcwJ3Mdgw/m/GyC8_UZbAwAJ

    Args:
        input: Path to file readable by VESTA.
        output: Path to write image to. Should include a recognisable image
            file extension.
        scale: Amount to scale raster image by.
        close: Whether to close the VESTA tab afterward.
        block: Whether to block the main process until the file is written.
            If the export process fails on VESTA's end, then this will hang!
            However, it is recommended to reduce race conditions or system
            overload.
        timeout: Number of seconds to block for until we raise TimeoutError.
            If None, will count indefinitely.
            Note, though, that VESTA will still be running if we hit the
            Timeout. We just hand the focus back to Python.

    Raises:
        NoVestaError: If fails to run VESTA.
        OSError: If run on an unsupport OS.
            (Supports Windows, Linux, MacOS/Darwin.)
        FileNotFoundError: If `input` doesn't exist or `output`'s directory
            doesn't exist.
        TimeoutError: block=True and we timeout.
    """
    # First, identify which platform we are on.
    opsys = platform.system()
    # This determines the form of the VESTA command
    if opsys == "Darwin":  # a.k.a. MacOS
        vesta_cmd = ["open", "-n", "-a", "VESTA.app", "--args"]
    elif opsys == "Windows" or opsys == "Linux":
        vesta_cmd = ["VESTA"]
    else:
        # If we're here, then python platform has dones something wrong.
        raise OSError(f"Unrecognised operating system {opsys}.")
    # Next, identify the absolute path to the input,
    # as my tests on MacOS have found that we must specify the absolute path
    # or else it will do the path from /Applications/VESTA
    abs_input = os.path.abspath(input)
    # Validate that the file exists.
    if not os.path.isfile(abs_input):
        raise FileNotFoundError(f"Cannot find file {abs_input}.")
    # Sanitise scale
    if not isinstance(scale, int):
        scale = int(scale)
    # Validate that output directory exists.
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.isdir(output_dir):
        # output_dir may be an empty string if output has no path.
        # That is acceptable, but isdir would say False.
        # So only check if the directory doesn't exist if non-empty.
        raise FileNotFoundError(f"Cannot find directory {output_dir}.")
    # Prepare current state for blocking.
    if block:
        # If the file exists, we'll check when it gets overwritten.
        if os.path.exists(output):
            old_time = os.path.getmtime(output)
        else:
            # Otherwise, we'll check when it gets written.
            old_time = None
    # Form the command to execute.
    cmd = vesta_cmd + ["-open", abs_input,
                       "-export_img", f"scale={scale}", str(output)]
    if close:
        cmd += ["-close"]
    # Run
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # MacOS gave the following stderr:
        #   Unable to find application named 'VESTA.app'\n
        # But there might be other reasons this fails, or platform
        # dependencies.
        raise NoVestaError("Failed to run VESTA.")
    except FileNotFoundError:
        # I find that Mac and Linux will give FileNotFoundError if the
        # specified command does not exist.
        raise NoVestaError("Failed to run VESTA.")
    if block:
        elapsed = 0
        increment = 0.02
        if old_time is None:
            # Check if the file has been created.
            while not os.path.exists(output) and \
                    (timeout is None or elapsed < timeout):
                time.sleep(increment)
                elapsed += increment
        else:
            # Check if the file has been overwritten.
            while os.path.getmtime(output) == old_time and \
                    (timeout is None or elapsed < timeout):
                time.sleep(increment)
                elapsed += increment
        if timeout is not None and elapsed >= timeout:
            raise TimeoutError(
                f"export_image_from_file timed out after {elapsed} seconds.")
