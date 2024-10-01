"""Pytest Configuration and Fixtures."""

from pathlib import Path

import ucdp as u
from pytest import fixture

import ucdp_glbl


@fixture
def template_path():
    """Path to templates."""
    return Path(ucdp_glbl.__file__).parent / "templates"


@fixture
def testdata_path():
    """Register Testdata."""
    path = Path(__file__).parent / "testdata"
    with u.extend_sys_path([path]):
        yield path
