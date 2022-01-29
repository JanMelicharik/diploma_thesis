import pandas

import constants as c


airports = pandas.read_csv(f"{c.DATA_DIR}/airports.csv", names=c.AIRPORTS_VARIABLES)
eu_airports = airports.loc[
    airports["country_id"].isin(c.EU_COUNTRIES.values())
]

eu_airports.to_csv(f"{c.OUTPUT_DATA_DIR}/eu_airports.csv", index=False)
