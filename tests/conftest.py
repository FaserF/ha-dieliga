"""Fixtures for tests."""
import pytest

import sys
import os

@pytest.fixture(autouse=True)
def enable_custom_integrations(hass):
    """Enable custom integrations."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    yield
