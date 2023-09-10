""" Module for requesting live PBP data """
import json
import time

from json_flatten import flatten
import pandas as pd
import pendulum as pend
import requests

from nfllivepy.requester.errors import APICallException
from nfllivepy.requester.pbp_clean import clean_pbp_df
from nfllivepy.requester.teams import get_team_id
from nfllivepy.requester.util import get_season_at_date


class PBPRequester:
    """ Requester class """
    core_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"

    def get_live_pbp_all_games(self) -> pd.DataFrame:
        """
        Get live PBP data for all ongoing games
        :return: A data frame containing all the plays. If there are no live games, this will be an empty data frame.
        :raise: APICallException if the API call to fetch PBP data fails
        """
        all_events = self._make_api_call(self.core_url + f"/events?limit=500")
        return self._get_pbp_for_events_at_time(all_events, pend.from_timestamp(time.time()))

    def get_live_pbp_for_team(self, team_abbr: str) -> pd.DataFrame:
        """
        Get live PBP data for a specific team
        :param team_abbr: The team abbreviation to get live data for
        :return: A data frame containing all the plays. If there is no live game, this will be an empty data frame.
        :raise: APICallException if the API call to fetch PBP data fails
        """
        return self._get_live_pbp_for_team_and_time(team_abbr, pend.from_timestamp(time.time()))

    def _get_live_pbp_for_team_and_time(self, team_abbr: str, dt: pend.DateTime) -> pd.DataFrame:
        """
        Get live PBP data for a specific team at a specific time. Serves as a helper for getting live pbp data but the
        time flexibility allows for testing when there are no live games (i.e. in the offseason).
        :param team_abbr: The team abbreviation to get live data for
        :param dt: A UTC datetime corresponding to when data should be gotten from
        :return: A data frame containing all the plays. If there is no game at the specified time, this will be an empty data frame.
        :raise: APICallException if the API call to fetch PBP data fails
        """
        team_id = get_team_id(team_abbr)
        team_events = self._make_api_call(self.core_url + f"/seasons/{get_season_at_date(dt)}/teams/{team_id}/events")
        return self._get_pbp_for_events_at_time(team_events, dt)

    def _get_pbp_for_event(self, event_id: str) -> pd.DataFrame:
        """
        Get Play by play data for the given event id
        :param event_id: The event id as a string
        :return: A dataframe of the PBP where each row represents a single play
        :raise: APICallException if the API call to fetch PBP data fails
        """
        data = self._make_api_call(self.core_url + f"/events/{event_id}/competitions/{event_id}/plays?limit=500")
        pbp_df = pd.DataFrame([flatten(elt) for elt in data['items']])
        return clean_pbp_df(pbp_df)

    def _get_pbp_for_events_at_time(self, events: dict, dt: pend.DateTime) -> pd.DataFrame:
        pbp_df = pd.DataFrame()

        for event in events['items']:
            event_data = self._make_api_call(event["$ref"])
            event_dt = pend.parse(event_data["date"])
            hour_difference = (event_dt - dt).in_hours()

            # Get games that started within twelve hours of the current time
            if abs(hour_difference) < 12 and dt > event_dt:
                pbp_df = pd.concat([pbp_df, self._get_pbp_for_event(event_data["id"])], ignore_index=True)

        return pbp_df


    @staticmethod
    def _make_api_call(url: str) -> dict:
        """
        Make an API call and return the json result as a python dictionary
        :param url: The url for the api call
        :return: The json response content as a python dictionary
        :raise: an APICallException if the API response does not have a 200 status code
        """
        resp = requests.get(url)
        if resp.status_code != 200:
            raise APICallException(resp.status_code, resp.text)

        return json.loads(resp.content)
