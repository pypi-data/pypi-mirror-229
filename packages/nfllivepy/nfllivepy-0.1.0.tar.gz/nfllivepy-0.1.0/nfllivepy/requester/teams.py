""" Module for mapping team abbreviations to team IDs as used by the ESPN v2 API"""


TEAMS = [
    {"teamId": 1, "teamAbbr": 'ATL'},
    {"teamId": 2, "teamAbbr": 'BUF'},
    {"teamId": 3, "teamAbbr": 'CHI'},
    {"teamId": 4, "teamAbbr": 'CIN'},
    {"teamId": 5, "teamAbbr": 'CLE'},
    {"teamId": 6, "teamAbbr": 'DAL'},
    {"teamId": 7, "teamAbbr": 'DEN'},
    {"teamId": 8, "teamAbbr": 'DET'},
    {"teamId": 9, "teamAbbr": 'GB'},
    {"teamId": 10, "teamAbbr": 'TEN'},
    {"teamId": 11, "teamAbbr": 'IND'},
    {"teamId": 12, "teamAbbr": 'KC'},
    {"teamId": 13, "teamAbbr": 'OAK'},
    {"teamId": 14, "teamAbbr": 'LAR'},
    {"teamId": 15, "teamAbbr": 'MIA'},
    {"teamId": 16, "teamAbbr": 'MIN'},
    {"teamId": 17, "teamAbbr": 'NE'},
    {"teamId": 18, "teamAbbr": 'NO'},
    {"teamId": 19, "teamAbbr": 'NYG'},
    {"teamId": 20, "teamAbbr": 'NYJ'},
    {"teamId": 21, "teamAbbr": 'PHI'},
    {"teamId": 22, "teamAbbr": 'ARI'},
    {"teamId": 23, "teamAbbr": 'PIT'},
    {"teamId": 24, "teamAbbr": 'LAC'},
    {"teamId": 25, "teamAbbr": 'SF'},
    {"teamId": 26, "teamAbbr": 'SEA'},
    {"teamId": 27, "teamAbbr": 'TB'},
    {"teamId": 28, "teamAbbr": 'WSH'},
    {"teamId": 29, "teamAbbr": 'CAR'},
    {"teamId": 30, "teamAbbr": 'JAX'},
    {"teamId": 33, "teamAbbr": 'BAL'},
    {"teamId": 34, "teamAbbr": 'HOU'}
]


def get_team_abbr(team_id: int) -> int:
    """
    Get the team abbreviation associated with the given team id
    :param team_id: The team id
    :return: The team abbreviation
    :raise: ValueError if the provided team id is invalid
    """
    for team in TEAMS:
        if team["teamId"] == team_id:
            return team["teamAbbr"]
    raise ValueError(f"{team_id} is an invalid team ID")


def get_team_id(team_abbr: str) -> int:
    """
    Get the team id associated with the given team abbreviation
    :param team_abbr: The team abbreviation
    :return: The team ID as an integer
    :raise: ValueError if the provided team abbreviation is invalid
    """
    for team in TEAMS:
        if team["teamAbbr"] == team_abbr.upper():
            return team["teamId"]
    raise ValueError(f"{team_abbr} is an invalid team abbreviation")
