"""Tests for DieligaApiClient."""
import pytest
import aiohttp
from custom_components.dieliga.api import DieligaApiClient

SCOREBOARD_XML = """
<results>
    <group>Group A</group>
    <region>Region 1</region>
    <last_change>2026-01-31</last_change>
    <league>Test League</league>
    <table>
        <team>
            <name>Team 1</name>
            <points positive="10" negative="2" />
            <sets positive="20" negative="5" />
            <balls positive="500" negative="400" />
            <games>5</games>
            <games_won>4</games_won>
        </team>
    </table>
</results>
"""

SCHEDULE_XML = """
<results>
    <group>Group A</group>
    <region>Region 1</region>
    <day_of_play>
        <game>
            <gamenr>101</gamenr>
            <date>2026-01-01</date>
            <new_date>-</new_date>
            <time>10:00</time>
            <team_a name="Team 1" points="2" sets="3" balls="75" />
            <team_b name="Team 2" points="1" sets="1" balls="50" />
            <state>Completed</state>
        </game>
    </day_of_play>
</results>
"""

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_get_scoreboard(aioclient_mock):
    """Test fetching scoreboard."""
    url = "https://example.com/schedule/summary/1234?output=xml"
    aioclient_mock.get(url, text=SCOREBOARD_XML)

    async with aiohttp.ClientSession() as session:
        client = DieligaApiClient(session, "https://example.com")
        data = await client.async_get_scoreboard("1234")

        assert data["league"] == "Test League"
        assert len(data["teams"]) == 1
        assert data["teams"][0]["name"] == "Team 1"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_get_schedule(aioclient_mock):
    """Test fetching schedule."""
    url = "https://example.com/schedule/schedule/1234?output=xml"
    aioclient_mock.get(url, text=SCHEDULE_XML)

    async with aiohttp.ClientSession() as session:
        client = DieligaApiClient(session, "https://example.com")
        data = await client.async_get_schedule("1234")

        assert len(data["games"]) == 1
        assert data["games"][0]["team_a_name"] == "Team 1"
        assert data["total_games"] == 1
