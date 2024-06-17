import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--exhaustive",
        action="store_true",
        dest="exhaustive",
        default=False,
        help="enable exhaustive testing of fan calculation",
    )
