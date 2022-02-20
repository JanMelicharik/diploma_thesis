"""This script loads filtered EEA data about bookings and changes and calculates some basic
descriptive statistics."""

"""
TO DO:

DONE 1) Read a file into pandas dataframe                            
DONE 2) Pick only the variables I care about
DONE 3) Remove NaN rows from the variables that can contain them
DONE 4) Calculate new variables
    - DONE time from booking to first flight
    - DONE length of trip
    - DONE age of passengers
    - DONE number of kids in reservation
5) DONE Create new variables from multi-value variables
6) DONE Aggregate variables by day

7) Save daily data to metadata_daily_aggregates folder
8) Save atomic data to metadata folder
9) Connect daily aggregate data into a single dataset for the whole period
10) Connect atomic data into a single dataset for the whole period
11) Do the multiprocessing thing and run this script for ALL countries and also for all data just to be sure
"""

import constants as c
from typing import Union, List, Optional
from pathlib import Path
import arrow
import pandas as pd
import re
from math import floor
from statistics import mean, stdev
from helper import make_list_of
from itertools import chain
from numpy import nanmean, nanmin, nanmax, nanstd


def extract_time_to_seconds(detailed_time: str) -> Optional[str]:
    """Removes the milliseconds and timezone from time string."""
    if not pd.isna(detailed_time):
        match = re.search(c.TIME_FORMAT, detailed_time)

        if match is not None:
            return match.group(0)

    return None


def extract_date(detailed_time: str) -> Optional[str]:
    """Splits the truncated time by space and returns only the first part.

    The first part is YYYY-MM-DD. Used for later grouping.
    """
    if not pd.isna(detailed_time):
        truncated_time = extract_time_to_seconds(detailed_time)

        if truncated_time is not None:
            return truncated_time.split(" ")[0]

    return None


def convert_time_to_unix_timestamp(detailed_time: str) -> Optional[int]:
    """Parses the truncated time into arrow time object and creates a UNIX timestamp as integer."""
    if not pd.isna(detailed_time):
        truncated_time = extract_time_to_seconds(detailed_time)

        if truncated_time is not None:
            arrow_time = get_arrow_time(truncated_time)
            return round(arrow_time.timestamp())

    return None


def get_arrow_time(time_string: str) -> arrow.Arrow:
    """Parse time from string with specified format."""
    return arrow.get(time_string, c.ARROW_TIME_FORMAT)


def get_duration_in_years(earlier_time: str, later_time: str) -> Optional[int]:
    """From two long strings with specified time format get the difference in years."""
    if (not pd.isna(earlier_time)) and (not pd.isna(later_time)):
        truncated_earlier_time = extract_time_to_seconds(earlier_time)
        truncated_later_time = extract_time_to_seconds(later_time)

        if (truncated_earlier_time is not None) and (truncated_later_time is not None):
            return floor((get_arrow_time(truncated_later_time) - get_arrow_time(truncated_earlier_time)).days / 365)

    return None


def get_duration_in_days(departure_time: str, return_time: Union[str, float]) -> Optional[int]:
    """From two long strings with specified time format get the difference in days."""
    if (not pd.isna(return_time)) and (not pd.isna(departure_time)):
        truncated_departure_time = extract_time_to_seconds(departure_time)
        truncated_return_time = extract_time_to_seconds(return_time)

        if (truncated_departure_time is not None) and (truncated_return_time is not None):
            return (get_arrow_time(truncated_return_time) - get_arrow_time(truncated_departure_time)).days

    return None


def get_ages(birthday_array: str, departure_time: str) -> Optional[List[int]]:
    """From string representation of birthday array calculate ages of passengers at the time of departure.

    Example:
    >>> bday_array = "{1959-03-17 00:00:00.000000,1955-03-12 00:00:00.000000}"
    >>> dept_time = "2020-02-08 06:45:00+00"
    >>> ages = [60, 64]
    """
    if (not pd.isna(birthday_array)) and (not pd.isna(departure_time)):
        passenger_ages: List[int] = []
        list_of_birthday_dates = make_list_of(birthday_array)

        if list_of_birthday_dates is not None:
            for birthday_date in list_of_birthday_dates:
                passenger_ages.append(get_duration_in_years(birthday_date, departure_time))

            return passenger_ages

    return None


def get_number_of_kids(ages: List[int]) -> Optional[int]:
    """From list of ages of passengers get the number of integers below 18."""
    if ages is not None:
        return sum([age < 18 for age in ages])

    return None


def convert_title_to_sex(title_arr: str) -> Optional[List[str]]:
    """Convert 'MR' to 'm' and 'MS' and 'MRS' to 'f'."""
    if not pd.isna(title_arr):
        titles = [title.lower() for title in make_list_of(title_arr)]
        return [c.TITLE_TO_SEX_MAP[title] for title in titles]

    return None


def get_airlines(airlines_arr: str) -> Optional[List[str]]:
    """From string representation of airlines IATA codes array extract individual elements and return a list of them."""
    airlines = make_list_of(airlines_arr)
    if airlines is not None:
        return [airline.lower() for airline in airlines]

    return None


def get_airports(node_arr: str) -> Optional[List[str]]:
    """From string representation of airports IATA codes array extract individual elements and return a list of them."""
    airports = make_list_of(node_arr)
    if airports is not None:
        return [airport.lower() for airport in airports]

    return None


def get_country_ids(country_name_arr: str) -> Optional[List[str]]:
    """From string representation of country names array extract individual elements and return a list of them."""
    country_ids = make_list_of(country_name_arr)
    if country_ids is not None:
        return [country_id.lower() for country_id in country_ids]

    return None


def create_new_variables(original_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a copy of original dataframe, add new variables and drop NaN values from specified columns."""
    new_dataframe: pd.DataFrame = original_dataframe.copy(deep=True)

    new_dataframe["date"] = original_dataframe.apply(
        lambda row: extract_date(row.timestamp),
        axis=1
    )
    new_dataframe["days_between_purchase_and_start_of_trip"] = original_dataframe.apply(
        lambda row: get_duration_in_days(row.timestamp, row.departure_time),
        axis=1
    )
    new_dataframe["trip_length_in_days"] = original_dataframe.apply(
        lambda row: get_duration_in_days(row.departure_time, row.return_time),
        axis=1
    )
    new_dataframe["passenger_age"] = original_dataframe.apply(
        lambda row: get_ages(row.birthday_arr, row.departure_time),
        axis=1
    )
    new_dataframe["number_of_kids"] = new_dataframe.apply(
        lambda row: get_number_of_kids(row.passenger_age),
        axis=1
    )
    new_dataframe["status_closed"] = original_dataframe.apply(
        lambda row: row.status == "closed",
        axis=1
    )
    new_dataframe["status_refunded"] = original_dataframe.apply(
        lambda row: row.status == "refunded",
        axis=1
    )
    new_dataframe["search_oneway"] = original_dataframe.apply(
        lambda row: row.search_trip_type == "oneway",
        axis=1
    )
    new_dataframe["search_roundtrip"] = original_dataframe.apply(
        lambda row: row.search_trip_type == "roundtrip",
        axis=1
    )
    new_dataframe["search_multicity"] = original_dataframe.apply(
        lambda row: row.search_trip_type == "multicity",
        axis=1
    )
    new_dataframe["search_nomad"] = original_dataframe.apply(
        lambda row: row.search_trip_type == "nomad",
        axis=1
    )
    new_dataframe["service_none"] = original_dataframe.apply(
        lambda row: pd.isna(row.service_package_type),
        axis=1
    )
    new_dataframe["service_plus"] = original_dataframe.apply(
        lambda row: row.service_package_type == "plus",
        axis=1
    )
    new_dataframe["service_premium"] = original_dataframe.apply(
        lambda row: row.service_package_type == "premium",
        axis=1
    )
    new_dataframe["route_stability_new"] = original_dataframe.apply(
        lambda row: row.route_stability == "new",
        axis=1
    )
    new_dataframe["route_stability_super_stable"] = original_dataframe.apply(
        lambda row: row.route_stability == "super stable",
        axis=1
    )
    new_dataframe["route_stability_less_frequent"] = original_dataframe.apply(
        lambda row: row.route_stability == "less frequent",
        axis=1
    )
    new_dataframe["route_stability_rare"] = original_dataframe.apply(
        lambda row: row.route_stability == "rare",
        axis=1
    )
    new_dataframe["route_stability_frequent"] = original_dataframe.apply(
        lambda row: row.route_stability == "frequent",
        axis=1
    )
    new_dataframe["route_stability_stable"] = original_dataframe.apply(
        lambda row: row.route_stability == "stable",
        axis=1
    )
    new_dataframe["carriers"] = original_dataframe.apply(
        lambda row: get_airlines(row.airlines),
        axis=1
    )
    new_dataframe["sex"] = original_dataframe.apply(
        lambda row: convert_title_to_sex(row.title_arr),
        axis=1
    )
    new_dataframe["airports"] = original_dataframe.apply(
        lambda row: get_airports(row.node_arr),
        axis=1
    )
    new_dataframe["countries"] = original_dataframe.apply(
        lambda row: get_country_ids(row.country_name_arr),
        axis=1
    )
    new_dataframe["trip_start"] = original_dataframe.apply(
        lambda row: extract_time_to_seconds(row.itinerary_start),
        axis=1
    )
    new_dataframe["trip_end"] = original_dataframe.apply(
        lambda row: extract_time_to_seconds(row.itinerary_start),
        axis=1
    )
    new_dataframe["total_distance_km"] = original_dataframe["total_distance_km"]
    new_dataframe["passengers"] = original_dataframe["passengers"]
    new_dataframe["bags"] = original_dataframe["bags"]
    new_dataframe["price_in_eur"] = original_dataframe["initial_price"]

    new_dataframe = new_dataframe.dropna(axis=0, subset=c.BOOKINGS_VARIABLES_TO_DROP_IF_NAN)
    return new_dataframe[c.BOOKINGS_VARIABLES_TO_USE]


def save_new_daily_data(dataframe: pd.DataFrame): ...


def get_data_by_day(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate descriptive statistics for each day.

    Exclude carriers ,airports ,countries ,trip_start and trip_end.

    :param dataframe: new_dataframe
    :return: dataframe with number of rows equal to number of days in that month
    """

    def get_passengers_of_gender(chained_list, gender: str) -> int:
        count = 0
        for item in chained_list:
            if item == gender:
                count += 1

        return count

    grouped_df = dataframe.groupby("date")

    number_of_bookings = grouped_df.size()

    # Calculate mean, standard deviation, min, max
    days_between_purchase_and_start_of_trip_mean = grouped_df["days_between_purchase_and_start_of_trip"].apply(lambda s: nanmean(s))
    days_between_purchase_and_start_of_trip_std = grouped_df["days_between_purchase_and_start_of_trip"].apply(lambda s: nanstd(s))
    days_between_purchase_and_start_of_trip_min = grouped_df["days_between_purchase_and_start_of_trip"].apply(lambda s: nanmin(s))
    days_between_purchase_and_start_of_trip_max = grouped_df["days_between_purchase_and_start_of_trip"].apply(lambda s: nanmax(s))
    trip_length_in_days_mean = grouped_df["trip_length_in_days"].apply(lambda s: nanmean(s))
    trip_length_in_days_std = grouped_df["trip_length_in_days"].apply(lambda s: nanstd(s))
    trip_length_in_days_min = grouped_df["trip_length_in_days"].apply(lambda s: nanmin(s))
    trip_length_in_days_max = grouped_df["trip_length_in_days"].apply(lambda s: nanmax(s))
    passenger_age_mean = grouped_df["passenger_age"].apply(lambda s: mean(chain(*s)))
    passenger_age_std = grouped_df["passenger_age"].apply(lambda s: stdev(chain(*s)))
    passenger_age_min = grouped_df["passenger_age"].apply(lambda s: min(chain(*s)))
    passenger_age_max = grouped_df["passenger_age"].apply(lambda s: max(chain(*s)))
    number_of_kids_mean = grouped_df["number_of_kids"].apply(lambda s: nanmean(s))
    number_of_kids_std = grouped_df["number_of_kids"].apply(lambda s: nanstd(s))
    number_of_kids_min = grouped_df["number_of_kids"].apply(lambda s: nanmin(s))
    number_of_kids_max = grouped_df["number_of_kids"].apply(lambda s: nanmax(s))
    total_distance_km_mean = grouped_df["total_distance_km"].apply(lambda s: nanmean(s))
    total_distance_km_std = grouped_df["total_distance_km"].apply(lambda s: nanstd(s))
    total_distance_km_min = grouped_df["total_distance_km"].apply(lambda s: nanmin(s))
    total_distance_km_max = grouped_df["total_distance_km"].apply(lambda s: nanmax(s))
    passengers_count = grouped_df["passengers"].apply(lambda s: sum(s))
    passengers_mean = grouped_df["passengers"].apply(lambda s: nanmean(s))
    passengers_std = grouped_df["passengers"].apply(lambda s: nanstd(s))
    passengers_min = grouped_df["passengers"].apply(lambda s: nanmin(s))
    passengers_max = grouped_df["passengers"].apply(lambda s: nanmax(s))
    bags_mean = grouped_df["bags"].apply(lambda s: nanmean(s))
    bags_std = grouped_df["bags"].apply(lambda s: nanstd(s))
    bags_min = grouped_df["bags"].apply(lambda s: nanmin(s))
    bags_max = grouped_df["bags"].apply(lambda s: nanmax(s))
    price_in_eur_mean = grouped_df["price_in_eur"].apply(lambda s: nanmean(s))
    price_in_eur_std = grouped_df["price_in_eur"].apply(lambda s: nanstd(s))
    price_in_eur_min = grouped_df["price_in_eur"].apply(lambda s: nanmin(s))
    price_in_eur_max = grouped_df["price_in_eur"].apply(lambda s: nanmax(s))

    # Calculate counts
    status_closed = grouped_df["status_closed"].apply(lambda s: sum(s))
    status_refunded = grouped_df["status_refunded"].apply(lambda s: sum(s))
    search_oneway = grouped_df["search_oneway"].apply(lambda s: sum(s))
    search_roundtrip = grouped_df["search_roundtrip"].apply(lambda s: sum(s))
    search_multicity = grouped_df["search_multicity"].apply(lambda s: sum(s))
    search_nomad = grouped_df["search_nomad"].apply(lambda s: sum(s))
    service_none = grouped_df["service_none"].apply(lambda s: sum(s))
    service_plus = grouped_df["service_plus"].apply(lambda s: sum(s))
    service_premium = grouped_df["service_premium"].apply(lambda s: sum(s))
    route_stability_new = grouped_df["route_stability_new"].apply(lambda s: sum(s))
    route_stability_super_stable = grouped_df["route_stability_super_stable"].apply(lambda s: sum(s))
    route_stability_less_frequent = grouped_df["route_stability_less_frequent"].apply(lambda s: sum(s))
    route_stability_rare = grouped_df["route_stability_rare"].apply(lambda s: sum(s))
    route_stability_frequent = grouped_df["route_stability_frequent"].apply(lambda s: sum(s))
    route_stability_stable = grouped_df["route_stability_stable"].apply(lambda s: sum(s))
    sex_m = grouped_df["sex"].apply(lambda s: get_passengers_of_gender(chain(*s), "m"))
    sex_f = grouped_df["sex"].apply(lambda s: get_passengers_of_gender(chain(*s), "f"))

    return pd.DataFrame(
        {
            "number_of_bookings": number_of_bookings,
            "days_between_purchase_and_start_of_trip_mean": days_between_purchase_and_start_of_trip_mean,
            "days_between_purchase_and_start_of_trip_std": days_between_purchase_and_start_of_trip_std,
            "days_between_purchase_and_start_of_trip_min": days_between_purchase_and_start_of_trip_min,
            "days_between_purchase_and_start_of_trip_max": days_between_purchase_and_start_of_trip_max,
            "trip_length_in_days_mean": trip_length_in_days_mean,
            "trip_length_in_days_std": trip_length_in_days_std,
            "trip_length_in_days_min": trip_length_in_days_min,
            "trip_length_in_days_max": trip_length_in_days_max,
            "passenger_age_mean": passenger_age_mean,
            "passenger_age_std": passenger_age_std,
            "passenger_age_min": passenger_age_min,
            "passenger_age_max": passenger_age_max,
            "number_of_kids_mean": number_of_kids_mean,
            "number_of_kids_std": number_of_kids_std,
            "number_of_kids_min": number_of_kids_min,
            "number_of_kids_max": number_of_kids_max,
            "total_distance_km_mean": total_distance_km_mean,
            "total_distance_km_std": total_distance_km_std,
            "total_distance_km_min": total_distance_km_min,
            "total_distance_km_max": total_distance_km_max,
            "passengers_count": passengers_count,
            "passengers_mean": passengers_mean,
            "passengers_std": passengers_std,
            "passengers_min": passengers_min,
            "passengers_max": passengers_max,
            "bags_mean": bags_mean,
            "bags_std": bags_std,
            "bags_min": bags_min,
            "bags_max": bags_max,
            "price_in_eur_mean": price_in_eur_mean,
            "price_in_eur_std": price_in_eur_std,
            "price_in_eur_min": price_in_eur_min,
            "price_in_eur_max": price_in_eur_max,
            "status_closed": status_closed,
            "status_refunded": status_refunded,
            "search_oneway": search_oneway,
            "search_roundtrip": search_roundtrip,
            "search_multicity": search_multicity,
            "search_nomad": search_nomad,
            "service_none": service_none,
            "service_plus": service_plus,
            "service_premium": service_premium,
            "route_stability_new": route_stability_new,
            "route_stability_super_stable": route_stability_super_stable,
            "route_stability_less_frequent": route_stability_less_frequent,
            "route_stability_rare": route_stability_rare,
            "route_stability_frequent": route_stability_frequent,
            "route_stability_stable": route_stability_stable,
            "sex_m": sex_m,
            "sex_f": sex_f,
        }
    )


bookings_data_at_files = Path(f"{c.OUTPUT_DATA_DIR}/by_country/at/bookings").glob("*.csv")
file = next(bookings_data_at_files)
df = pd.read_csv(file, header=0)
new_df = create_new_variables(df)
export_df = get_data_by_day(new_df)
export_df.to_csv("TEST.csv")

# new_df.groupby("date").pipe(lambda grp: grp.size() / grp.size().sum())

