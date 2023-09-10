""" Module dedicated towards cleaning the play by play data frame """
import pandas as pd

from nfllivepy.requester.teams import get_team_abbr

FIELD_RENAMES = {
    # old_name: better_name
    "id": "play_id",
    "type.text": "play_type",
    "text": "play_description",
    "shortText": "play_description_short",
    "awayScore$int": "away_score",
    "homeScore$int": "home_score",
    "period.number$int": "quarter",
    "clock.value$float": "seconds_remaining_in_quarter",
    "clock.displayValue": "clock_display_value",
    "scoringPlay$bool": "scoring_play",
    "scoreValue$int": "play_score_value",
    "start.team.$ref": "posteam",
    "start.down$int": "start_down",
    "start.distance$int": "start_yards_to_go",
    "start.yardsToEndzone$int": "start_yards_to_endzone",
    "end.down$int": "end_down",
    "end.distance$int": "end_yards_to_go",
    "end.yardsToEndzone$int": "end_yards_to_endzone",
    "statYardage$int": "yards_gained"
}


def clean_pbp_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the play by play data frame to improve column names and only include relevant data
    :param df: The pbp data frame (uncleaned)
    :return: A new data frame that is cleaned and much more user friendly
    """
    # Replace column names for readability and filter only those columns
    df_renamed = df.rename(columns=FIELD_RENAMES)
    df_clean = df_renamed[list(FIELD_RENAMES.values())]

    # If start team link is present, parse it to find team id and convert to team abbreviation
    # If no link is present (e.g. end of quarter, opening kickoff) posteam is set to "N/A"
    df_clean["posteam"] = df_clean["posteam"].map(
        lambda url: get_team_abbr(int(url.split("/teams/")[1].split("?")[0])) if type(url) == str else "N/A"
    )
    return df_clean
