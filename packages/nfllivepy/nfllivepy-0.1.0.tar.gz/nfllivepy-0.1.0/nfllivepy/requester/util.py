""" Utilities module """
from datetime import datetime


def get_current_season() -> int:
    """
    Get the current football season
    :return: The current season
    """
    return get_season_at_date(datetime.today())


def get_season_at_date(dt: datetime) -> int:
    """
    Get the football season year associated with the given date
    :param dt: The date of interest
    :return: The season (year) of the date
    """
    return dt.year if dt.month > 6 else dt.year - 1
