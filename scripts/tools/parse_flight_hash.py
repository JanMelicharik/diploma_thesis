import re

import constants as c


def parse_flight_hash(flight_hash: str):
    """ Return basic details about flight.

    :param flight_hash:
    :return: Dictionary of departure date, airline code and airports
    """
    match = re.match(c.FLIGHT_HASH_REGEX, flight_hash)
    return {
        "dep_year": match.group("year"),
        "dep_month": match.group("month"),
        "dep_day": match.group("day"),
        "airline": match.group("airline"),
        "dep_airport": match.group("dep_airport"),
        "arr_airport": match.group("arr_airport"),
        "flight_no": match.group("flight_no"),
    }
