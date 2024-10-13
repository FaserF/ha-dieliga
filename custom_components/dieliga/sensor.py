import aiohttp
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, TEAM_NAME, LIGA_URL

class TeamRankingSensor(Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self._name = config[TEAM_NAME]
        self._liga_url = config[LIGA_URL]
        self._state = None
        self._attributes = {}

    async def async_update(self):
        # Abrufen der HTML-Seite
        async with aiohttp.ClientSession() as session:
            async with session.get(self._liga_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Platzierung und Ergebnisse parsen
                    ranking_table = soup.find("table", {"class": "ranking"})
                    team_row = None
                    for row in ranking_table.find_all("tr"):
                        if self._name in row.text:
                            team_row = row
                            break

                    if team_row:
                        columns = team_row.find_all("td")
                        self._state = columns[0].text.strip()  # Platzierung
                        self._attributes["matches_played"] = columns[1].text.strip()
                        self._attributes["matches_won"] = columns[2].text.strip()

                    # Kommende und vergangene Spiele parsen
                    self._attributes["upcoming_games"] = self._get_upcoming_games(soup)
                    self._attributes["past_games"] = self._get_past_games(soup)
                else:
                    self._state = "Error: Unable to fetch data"

    def _get_upcoming_games(self, soup):
        upcoming_games = []
        games_section = soup.find("section", {"id": "upcoming_games"})  # Beispiel: Anpassen an die richtige Struktur
        for game in games_section.find_all("div", {"class": "game"}):
            date = game.find("span", {"class": "date"}).text
            opponent = game.find("span", {"class": "opponent"}).text
            upcoming_games.append({"date": date, "opponent": opponent})
        return upcoming_games

    def _get_past_games(self, soup):
        past_games = []
        games_section = soup.find("section", {"id": "past_games"})  # Beispiel: Anpassen an die richtige Struktur
        for game in games_section.find_all("div", {"class": "game"}):
            date = game.find("span", {"class": "date"}).text
            opponent = game.find("span", {"class": "opponent"}).text
            result = game.find("span", {"class": "result"}).text
            past_games.append({"date": date, "opponent": opponent, "result": result})
        return past_games

    @property
    def name(self):
        return f"{self._name} Ranking"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([TeamRankingSensor(hass, config)], True)
