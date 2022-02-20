import re
from datetime import datetime
import json
from typing import List
from pandas import isna


# Methods to process data on observation base
def make_list_of(val: str) -> List[str]:
    if not isna(val):
        return val.replace("{", "").replace("}", "").split(",")

    return None


def convert_to_time(val: str):
    return datetime.strptime(re.match(r"(\d{4}-\d{2}-\d{2}) \d+:\d+\d+.*", val).group(1), "%Y-%m-%d")


def diff_in_days(time_1: datetime, time_2: datetime):
    return (time_2 - time_1).days


def count_passenger_age(birthday: str, timestamp: str):
    return round(diff_in_days(convert_to_time(birthday), convert_to_time(timestamp)) / 365)


def save_daily_data(date: str, daily_data: dict):
    with open(f"metadata_last/{date}.json", "w") as outfile:
        json.dump(daily_data, outfile, indent=4)


def load_empty_template():
    with open("template.json", "r") as infile:
        template = json.load(infile)

    return template


def get_empty_processable():
    return {
        "days_to_trip": [],
        "trip_length": [],
        "passenger_age": [],
        "price": [],
        "price_per_passenger": [],
        "total_distance": [],
        "number_of_flights": [],
        "number_of_passengers": [],
        "number_of_checked_bags": [],
        "passenger_sex": [],
        "countries_visited_id": [],
        "countries_visited_name": [],
        "passenger_nationality": [],
        "service_package": []
    }


def save_status(s: str):
    with open("processing_info.txt", "a") as f:
        f.write(s)
