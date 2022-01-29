import pandas

from datetime import date, timedelta

import constants as c


start_date = date(c.START_DATE["year"], c.START_DATE["month"], c.START_DATE["day"])
end_date = date(c.END_DATE["year"], c.END_DATE["month"], c.END_DATE["day"])

timespan = end_date - start_date

days = [
    (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
    for day in range(timespan.days + 1)
]


week_span = {1: range(0, 6)}

week_count = 2
for week_start in range(6, len(days), 7):
    week_span[week_count] = range(week_start, week_start + 7)
    week_count += 1


def get_lockdowns(country_name: str, country_code: str) -> pandas.DataFrame:
    print(f"Processing: {country_name}")
    starts = []
    starts_week = []
    ends = []
    ends_week = []
    levels = []

    filepath = f"{c.DATA_DIR}/restrictions.csv"
    restrictions_data = pandas.read_csv(filepath)
    lockdown_data = restrictions_data[
        (restrictions_data["country"] == country_name)
        & (restrictions_data["measure"].isin(c.LOCKDOWN_TYPES))
    ]

    for row in lockdown_data.itertuples():
        starts.append(days.index(row.date_start))
        ends.append(days.index(row.date_end))
        levels.append(1 if row.measure == "StayHomeOrderPartial" else 2)

    codes = [country_code.lower()] * len(starts)

    for start in starts:
        for week_number, span in week_span.items():
            if start in span:
                if start == span[6]:
                    starts_week.append(week_number + 1)
                    break

                starts_week.append(week_number)
                break

    for end in ends:
        for week_number, span in week_span.items():
            if end in span:
                if end == span[6]:
                    ends_week.append(week_number + 1)
                    break

                ends_week.append(week_number)
                break

    lockdown_data["week_start_index"] = starts_week
    lockdown_data["week_end_index"] = ends_week
    lockdown_data["level"] = levels
    lockdown_data["code"] = codes

    return lockdown_data


if __name__ == "__main__":
    data = []
    for name, code in c.EEA_SUI_COUNTRIES.items():
        data.append(
            get_lockdowns(name, code)
        )

    full_data = pandas.concat(data)
    full_data.to_csv(f"{c.OUTPUT_DATA_DIR}/lockdowns.csv", index=False)
