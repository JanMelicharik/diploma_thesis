import pandas

import constants as c
from tools.parse_date import get_year_month


def read_file(filename: str) -> pandas.DataFrame:
    return pandas.read_csv(filename)


def country_is_eea_sui(country: str) -> bool:
    return country in c.EEA_SUI_COUNTRIES.keys()


def save_dataframe_to_csv(processed_data) -> None:
    for year_month in c.MONTHS:
        export_path_aggregate = f"{c.OUTPUT_DATA_DIR}/covid_cases/{year_month}.csv"
        processed_data[
            (processed_data["is_eea_sui"])
            & (processed_data["year_month"] == year_month)
        ].to_csv(export_path_aggregate, index=False)

        for country, code in c.EEA_SUI_COUNTRIES.items():
            export_path_individual = f"{c.OUTPUT_DATA_DIR}/by_country/{code.lower()}/covid_cases/{year_month}.csv"
            processed_data[
                (processed_data["country"] == country)
                & (processed_data["year_month"] == year_month)
            ].to_csv(export_path_individual, index=False)


def process_data() -> None:
    covid_cases = read_file(c.COVID_CASES_DATAFILE_PATH)
    covid_cases["year_month"] = covid_cases.apply(lambda row: get_year_month(row["date"]), axis=1)
    covid_cases["is_eea_sui"] = covid_cases.apply(lambda row: country_is_eea_sui(row["country"]), axis=1)
    save_dataframe_to_csv(covid_cases)


if __name__ == "__main__":
    process_data()
