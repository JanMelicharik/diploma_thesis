import pandas

import constants as c


def aggregate_data_to_weeks(country: str):
    mondays = []
    weekly_bookings = []
    weekly_changes = []
    weekly_covid_cases = []
    weekly_deaths = []
    lockdown = []

    country_path = f"{c.BY_COUNTRY_DATA_DIR}/{country.lower()}"
    daily = pandas.read_csv(f"{country_path}/timeseries.csv")
    index = sum(daily[6:13]["bookings"])

    # The first week (1.10.2019) starts with Tuesday - need to process first 6 observations separately
    # The last week (31.10.2019) ends with Sunday - ok
    mondays.append("2019-09-30")
    weekly_bookings.append(sum(daily[0:6]["bookings"]) / index)
    weekly_changes.append(sum(daily[0:6]["cancellations"]) / index)
    weekly_covid_cases.append(sum(daily[0:6]["covid_cases"]) / 6)
    weekly_deaths.append(sum(daily[0:6]["deaths"]))
    lockdown.append(0)

    for monday in range(6, daily.shape[0], 7):
        mondays.append(daily["date"][monday])
        weekly_bookings.append(sum(daily[monday:monday + 7]["bookings"]) / index)
        weekly_changes.append(sum(daily[monday:monday + 7]["cancellations"]) / index)
        weekly_covid_cases.append(sum(daily[monday:monday + 7]["covid_cases"]) / 7)
        weekly_deaths.append(sum(daily[monday:monday + 7]["deaths"]))
        lockdown.append(daily["lockdown"][monday])

    pandas.DataFrame({
        "date": mondays,
        "bookings": weekly_bookings,
        "cancellations": weekly_changes,
        "covid_cases": weekly_covid_cases,
        "deaths": weekly_deaths,
        "lockdown": lockdown,
    }).to_csv(f"{country_path}/timeseries_weekly.csv", index=False)


if __name__ == '__main__':
    for country_code in c.EEA_SUI_COUNTRIES.values():
        aggregate_data_to_weeks(country_code)
