"""
https://docs.pytest.org/en/stable/example/simple.html#control-skipping-of-tests-according-to-command-line-option
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--vesta", action="store_true", default=False, help="Run tests which call VESTA"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "vesta: mark test as calling VESTA")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--vesta"):
        # --vesta given in cli: do not skip vesta tests
        return
    if config.getoption("-m") and "vesta" in config.getoption("-m"):
        # Requested to run the vesta tests specifically.
        # Do not skip.
        return
    skip_vesta = pytest.mark.skip(reason="need --vesta option to run")
    for item in items:
        if "vesta" in item.keywords:
            item.add_marker(skip_vesta)