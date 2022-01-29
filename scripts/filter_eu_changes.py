"""
This script loads all the files in data/changes one by one and checks if the cancelled flight
departs from an EU country.

If it does, the script will add this flight to a dataframe for all EU countries
and at the end it will export the data as CSV file for all eu countries and for each
country separately to 'data/output/changes' and 'data/output/by_country/<country_id>/changes'.
"""

import multiprocessing
import pandas
import pathlib
import time

import constants as c

from tools.parse_flight_hash import parse_flight_hash

files = pathlib.Path(f"{c.CHANGES_DATA_DIR}").glob("*.csv")

airports = None
eu_airports_list = None
eu_eea_sui_airports_list = None


def read_file(changes_file_path):
    return pandas.read_csv(changes_file_path, names=c.CANCELLATIONS_VARIABLES)


def save_dataframe_to_csv(processed_data, filename):
    processed_data[processed_data["eu"]].to_csv(f"{c.OUTPUT_DATA_DIR}/changes/eu_{filename}", index=False)
    processed_data[processed_data["eea_sui"]].to_csv(f"{c.OUTPUT_DATA_DIR}/changes/eea_sui_{filename}", index=False)
    for country in c.EEA_SUI_COUNTRIES.values():
        export_path = f"{c.OUTPUT_DATA_DIR}/by_country/{country.lower()}/changes/{filename}"
        processed_data[processed_data["country"] == country].to_csv(export_path, index=False)


def is_eu_airport(flight_hash: str):
    global eu_airports_list
    try:
        flight_details = parse_flight_hash(flight_hash)
        return flight_details["dep_airport"] in eu_airports_list
    except AttributeError:
        return False


def is_eu_eea_sui_airport(flight_hash: str):
    global eu_eea_sui_airports_list
    try:
        flight_details = parse_flight_hash(flight_hash)
        return flight_details["dep_airport"] in eu_eea_sui_airports_list
    except AttributeError:
        return False


def get_airport_country(flight_hash: str):
    global airports
    try:
        flight_details = parse_flight_hash(flight_hash)
        return airports.loc[airports["id"] == flight_details["dep_airport"], "country_id"].values[0]
    except AttributeError:
        return "NONE"


def load_context():
    """Returns a dataframe of eu airports."""
    global airports
    global eu_airports_list
    global eu_eea_sui_airports_list

    if not airports:
        airports = pandas.read_csv(f"{c.DATA_DIR}/airports.csv")

    if not eu_airports_list:
        eu_airports_list = airports.loc[airports["country_id"].isin(c.EU_COUNTRIES.values())]["id"].to_list()

    if not eu_eea_sui_airports_list:
        eu_eea_sui_airports_list = airports.loc[
            airports["country_id"].isin(c.EEA_SUI_COUNTRIES.values())
        ]["id"].to_list()


def process_data(changes_file):
    changes = read_file(changes_file)
    print(f"Started: {changes_file.name}")
    start = time.time()
    changes["eu"] = changes.apply(lambda row: is_eu_airport(row["flight_hash"]), axis=1)
    changes["eea_sui"] = changes.apply(lambda row: is_eu_eea_sui_airport(row["flight_hash"]), axis=1)
    changes["country"] = changes.apply(lambda row: get_airport_country(row["flight_hash"]), axis=1)
    end = time.time()
    print(f"Finished: {changes_file.name} - Processed {changes.shape[0]} rows in {end - start} seconds.")
    save_dataframe_to_csv(changes, changes_file.name)


def process_all_files(files_to_process):
    with multiprocessing.Pool(initializer=load_context) as pool:
        pool.map(process_data, files_to_process)


if __name__ == "__main__":
    process_all_files(files)
