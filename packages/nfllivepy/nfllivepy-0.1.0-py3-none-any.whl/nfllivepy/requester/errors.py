""" Module for various custom errors related to this package """


class APICallException(Exception):
    """ Exception for when the API response does not have a status code of 200"""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"API call resulted in status {self.status_code} with the following message: {self.message}"
