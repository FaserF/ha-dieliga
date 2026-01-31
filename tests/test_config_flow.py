"""Tests for dieLiga config flow."""
from unittest.mock import patch
from homeassistant import config_entries, data_entry_flow
from custom_components.dieliga.const import DOMAIN

async def test_flow_user_init(hass):
    """Test the user initiated flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

async def test_flow_user_success(hass, aioclient_mock):
    """Test successful flow."""
    url = "https://www.ost.volleyball-freizeit.de/schedule/summary/1234?output=xml"
    aioclient_mock.get(url, text="<results><league>Test</league></results>")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.dieliga.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "base_url": "https://www.ost.volleyball-freizeit.de",
                "liga_id": 1234,
                "team_name": "Team 1",
            },
        )

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == "dieLiga 1234"
    assert result2["data"] == {
        "base_url": "https://www.ost.volleyball-freizeit.de",
        "liga_id": 1234,
        "team_name": "Team 1",
    }

async def test_flow_user_cannot_connect(hass, aioclient_mock):
    """Test flow with connection error."""
    url = "https://www.ost.volleyball-freizeit.de/schedule/summary/1234?output=xml"
    aioclient_mock.get(url, status=500)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "base_url": "https://www.ost.volleyball-freizeit.de",
            "liga_id": 1234,
        },
    )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
