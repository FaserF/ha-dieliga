"""Fixtures for tests."""
import pytest

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(hass):
    """Enable custom integrations."""
    return True
