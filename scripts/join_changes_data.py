import pandas
import pathlib
import time

from typing import List

import constants as c


def join_dataframes_for_country(country_path: str) -> None:
    all_changes_files: List[pandas.DataFrame] = [
        pandas.read_csv(filepath)
        for filepath in pathlib.Path(country_path).glob("*.csv")
    ]
    joined_changes = pandas.concat(all_changes_files[1:])
    joined_changes.to_csv(f"{country_path}/all.csv", index=False)


def main():
    for country in c.EEA_SUI_COUNTRIES.values():
        print(f"Processing: {country}")
        start = time.time()
        country_path = f"{c.BY_COUNTRY_DATA_DIR}/{country.lower()}/changes"
        join_dataframes_for_country(country_path)
        end = time.time()
        print(f"Done in {end - start} seconds.")


if __name__ == '__main__':
    main()
