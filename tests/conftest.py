"""Fixtures for tests."""
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(hass):
    """Enable custom integrations."""
    return True
