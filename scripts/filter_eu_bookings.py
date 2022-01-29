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

from tools.parse_airport_array import parse_airport_array

files = pathlib.Path(f"{c.BOOKINGS_DATA_DIR}").glob("*.csv")

airports = None
eu_airports_list = None
eu_eea_sui_airports_list = None


def read_file(bookings_file_path):
    return pandas.read_csv(bookings_file_path, names=c.BOOKINGS_VARIABLES)


def save_dataframe_to_csv(processed_data, filename):
    processed_data[processed_data["eu"]].to_csv(f"{c.OUTPUT_DATA_DIR}/bookings/eu_{filename}", index=False)
    processed_data[processed_data["eea_sui"]].to_csv(f"{c.OUTPUT_DATA_DIR}/bookings/eea_sui_{filename}", index=False)
    for country in c.EEA_SUI_COUNTRIES.values():
        export_path = f"{c.OUTPUT_DATA_DIR}/by_country/{country.lower()}/bookings/{filename}"
        processed_data[processed_data["country"] == country].to_csv(export_path, index=False)


def is_eu_airport(airport_array: str):
    global eu_airports_list
    try:
        airport_list = parse_airport_array(airport_array)
        return airport_list[0] in eu_airports_list
    except AttributeError:
        return False


def is_eu_eea_sui_airport(airport_array: str):
    global eu_eea_sui_airports_list
    try:
        airport_list = parse_airport_array(airport_array)
        return airport_list[0] in eu_eea_sui_airports_list
    except AttributeError:
        return False


def get_airport_country(airport_array: str):
    global airports
    try:
        airport_list = parse_airport_array(airport_array)
        return airports.loc[airports["id"] == airport_list[0], "country_id"].values[0]
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


def process_data(bookings_file):
    bookings = read_file(bookings_file)
    print(f"Started: {bookings_file.name}")
    start = time.time()
    bookings["eu"] = bookings.apply(lambda row: is_eu_airport(row["node_arr"]), axis=1)
    bookings["eea_sui"] = bookings.apply(lambda row: is_eu_eea_sui_airport(row["node_arr"]), axis=1)
    bookings["country"] = bookings.apply(lambda row: get_airport_country(row["node_arr"]), axis=1)
    end = time.time()
    print(f"Finished: {bookings_file.name} - Processed {bookings.shape[0]} rows in {end - start} seconds.")
    save_dataframe_to_csv(bookings, bookings_file.name)


def process_all_files(files_to_process):
    with multiprocessing.Pool(initializer=load_context) as pool:
        pool.map(process_data, files_to_process)


if __name__ == "__main__":
    process_all_files(files)
