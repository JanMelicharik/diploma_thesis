import multiprocessing
import pandas
import pathlib
import time

from datetime import date, timedelta
from typing import List, Tuple

import constants as c

countries_to_process = [(n, c.lower()) for n, c in c.EEA_SUI_COUNTRIES.items()]

days = None


def load_context():
    global days

    if not days:
        start_date = date(c.START_DATE["year"], c.START_DATE["month"], c.START_DATE["day"])
        end_date = date(c.END_DATE["year"], c.END_DATE["month"], c.END_DATE["day"])

        timespan = end_date - start_date

        days = [
            (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            for day in range(timespan.days + 1)
        ]


def get_lockdowns(country_name: str) -> List[int]:
    """
    Picks either full or partial lockdowns from the restrictions dataset
    and creates a list of values of 0, 1 or 2 where 0 is no lockdown,
    1 is partial lockdown and 2 is a full lockdown.
    :param country_name:
    :return: List of restriction levels for each day.
    """
    restriction_level = [0] * len(days)
    filepath = f"{c.DATA_DIR}/restrictions.csv"
    restrictions_data = pandas.read_csv(filepath)
    lockdown_data = restrictions_data[
        (restrictions_data["country"] == country_name)
        & (restrictions_data["measure"].isin(c.LOCKDOWN_TYPES))
    ]
    for row in lockdown_data.itertuples():
        start = days.index(row.date_start)
        end = days.index(row.date_end)
        level = 1 if row.measure == "StayHomeOrderPartial" else 2
        restriction_level[start:end] = [level] * (end - start)

    return restriction_level


def sum_daily_covid_cases_deaths(covid_cases_path, month: str) -> [List[int], List[int]]:
    cases, deaths = [], []
    covid_cases = pandas.read_csv(covid_cases_path)
    month_days = [day for day in days if month.replace("_", "-") in day]
    for day in month_days:
        daily = covid_cases[covid_cases["date"].str.contains(day)]
        if daily.shape[0] > 0:
            cases.append(daily.iloc[0]["new_cases"])
            deaths.append(daily.iloc[0]["deaths"])
        else:
            cases.append(0)
            deaths.append(0)

    return cases, deaths


def sum_daily_bookings(booking_path, month: str) -> List[int]:
    bookings = pandas.read_csv(booking_path)
    month_days = [day for day in days if month.replace("_", "-") in day]
    return [
        bookings[bookings["timestamp"].str.contains(day)].shape[0]
        for day in month_days
    ]


def sum_daily_changes(changes_path: str):
    changes = pandas.read_csv(changes_path)
    return [
        changes[changes["created"].str.contains(day)].shape[0]
        for day in days
    ]


def get_index(country_code: str) -> int:
    first_month = pandas.read_csv(f"{c.BY_COUNTRY_DATA_DIR}/{country_code}/bookings/2019_10.csv")
    return first_month[first_month["timestamp"].str.contains(days[0])].shape[0]


def aggregate_data_by_country(country: Tuple[str, str]):
    country_name = country[0]
    country_code = country[1]
    print(f"Processing: {country_name}")
    start = time.time()
    daily_bookings = []
    daily_covid_cases = []
    daily_deaths = []

    output_path = f"{c.BY_COUNTRY_DATA_DIR}/{country_code}/timeseries.csv"
    changes_path = f"{c.BY_COUNTRY_DATA_DIR}/{country_code}/changes/all.csv"

    index = get_index(country_code)
    daily_changes = sum_daily_changes(changes_path)
    lockdowns = get_lockdowns(country_name)

    for year_month in c.MONTHS:
        bookings_paths = pathlib.Path(c.BY_COUNTRY_DATA_DIR).glob(f"{country_code}/bookings/{year_month}.csv")
        covid_cases_paths = pathlib.Path(c.BY_COUNTRY_DATA_DIR).glob(f"{country_code}/covid_cases/{year_month}.csv")

        for bookings_path in bookings_paths:
            daily_bookings += sum_daily_bookings(bookings_path, year_month)

        for covid_cases_path in covid_cases_paths:
            cases, deaths = sum_daily_covid_cases_deaths(covid_cases_path, year_month)
            daily_covid_cases += cases
            daily_deaths += deaths

    assert len(daily_changes) == len(days)
    assert len(daily_bookings) == len(days)
    assert len(daily_deaths) == len(days)
    assert len(daily_covid_cases) == len(days)
    assert len(lockdowns) == len(days)

    daily_changes = [change / index for change in daily_changes]
    daily_bookings = [booking / index for booking in daily_bookings]

    pandas.DataFrame({
        "date": days,
        "bookings": daily_bookings,
        "cancellations": daily_changes,
        "covid_cases": daily_covid_cases,
        "deaths": daily_deaths,
        "lockdown": lockdowns,
    }).to_csv(output_path, index=False)

    end = time.time()
    print(f"{country_name}: done in {end - start} seconds.")


def process_all_countries(countries):
    with multiprocessing.Pool(initializer=load_context) as pool:
        pool.map(aggregate_data_by_country, countries)


if __name__ == "__main__":
    process_all_countries(countries_to_process)
