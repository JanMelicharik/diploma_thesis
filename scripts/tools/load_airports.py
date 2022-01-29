import pandas

import constants as c

airports = None


def load_airports():
    """Returns a dataframe of eu airports."""
    global airports
    if not airports:
        airports = pandas.read_csv(f"{c.DATA_DIR}/airports.csv")
