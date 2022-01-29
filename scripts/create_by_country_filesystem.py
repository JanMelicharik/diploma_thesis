import pathlib

import constants as c


for country_code in c.EEA_SUI_COUNTRIES.values():
    # pathlib.Path(f"{c.OUTPUT_DATA_DIR}/by_country/{country_code.lower()}/bookings").mkdir(parents=True)
    # pathlib.Path(f"{c.OUTPUT_DATA_DIR}/by_country/{country_code.lower()}/changes").mkdir(parents=True)
    pathlib.Path(f"{c.OUTPUT_DATA_DIR}/by_country/{country_code.lower()}/covid_cases").mkdir(parents=True)
