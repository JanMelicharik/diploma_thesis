import pandas


def get_airport_country(airport: str, eu_airports):
    """ Works with eu_airports variable from the scope of the script
    in which this function is used.

    :param eu_airports: Dataframe of EU airports.
    :param airport: Airport IATA
    :return: Airport details from /data/output/eu_airports.csv as dict
    """
    a = eu_airports.loc[eu_airports["id"] == airport, "country_id"].values[0]
    return a
