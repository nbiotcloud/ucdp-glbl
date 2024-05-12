"""Pytest Configuration and Fixtures."""

from pathlib import Path

import ucdp_glbl
from pytest import fixture


@fixture
def template_path():
    """Path to templates."""
    return Path(ucdp_glbl.__file__).parent / "templates"
