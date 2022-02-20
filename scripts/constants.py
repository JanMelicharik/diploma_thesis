HOME_DIR = "/Users/janmelicharik/Documents/Diplomka"
CACHE_PATH = f"{HOME_DIR}/cache"
DATA_DIR = f"{HOME_DIR}/data"
METADATA_DIR = f"{DATA_DIR}/metadata"
BOOKINGS_DATA_DIR = f"{DATA_DIR}/bookings"
CHANGES_DATA_DIR = f"{DATA_DIR}/changes"
OUTPUT_DATA_DIR = f"{DATA_DIR}/output"
BY_COUNTRY_DATA_DIR = f"{OUTPUT_DATA_DIR}/by_country"
COVID_CASES_DATAFILE_PATH = f"{DATA_DIR}/daily_covid_cases_deaths.csv"

FLIGHT_HASH_REGEX = r"^(?P<year>\d{4})" \
                    r"(?P<month>\d{2})" \
                    r"(?P<day>\d{2})-" \
                    r"(?P<airline>[A-Z0-9]+)-" \
                    r"(?P<dep_airport>[A-Z0-9]+)-" \
                    r"(?P<arr_airport>[A-Z0-9]+)-" \
                    r"(?P<flight_no>\d+)$"

AIRPORTS_VARIABLES = [
    "id",
    "name",
    "city_name",
    "country_name",
    "country_id",
    "continent_name",
    "continent_id",
    "type",
    "metrocode"
]

CANCELLATIONS_VARIABLES = [
    "flight_hash",
    "created",
    "updated"
]

EU_CHANGES_COLUMNS = [
    "dep_year",
    "dep_month",
    "dep_day",
    "airline",
    "dep_airport",
    "arr_airport",
    "flight_no",
    "announced",
    "country",
]

BOOKINGS_VARIABLES = [
    "bid",
    "timestamp",
    "status",  # "closed", "refunded"
    "search_trip_type",  # "oneway", "roundtrip", "multicity", nan, "nomad"
    "departure_time",
    "return_time",
    "total_distance_km",
    "airlines",
    "leg_count",
    "passengers",
    "bags",
    "customer_nationality",
    "customer_age",
    "currency",
    "initial_price",
    "weeks_to_departure",
    "booking_window",
    "route_stability",  # "new", "super stable", "less frequent", "rare", "frequent", "stable", nan
    "travel_group",  # "single", "couple", "family", "group"
    "segment",  # "business", "super stable route", "single", "couple", "family", "group", "ota"
    "service_package_type",  # nan, "plus", "premium"
    "fare_type_name",  # nan
    "node_arr",
    "city_id_arr",
    "city_name_arr",
    "country_id_arr",
    "country_name_arr",
    "itinerary_start",
    "itinerary_end",
    "birthday_arr",
    "nationality_arr",
    "pax_category_arr",  # adult, child, infant
    "title_arr"  # MR, MS
]

BOOKINGS_VARIABLES_TO_USE = [
    "date",
    "days_between_purchase_and_start_of_trip",
    "trip_length_in_days",
    "passenger_age",
    "number_of_kids",
    "status_closed",
    "status_refunded",
    "search_oneway",
    "search_roundtrip",
    "search_multicity",
    "search_nomad",
    "service_none",
    "service_plus",
    "service_premium",
    "route_stability_new",
    "route_stability_super_stable",
    "route_stability_less_frequent",
    "route_stability_rare",
    "route_stability_frequent",
    "route_stability_stable",
    "carriers",
    "sex",
    "airports",
    "countries",
    "trip_start",
    "trip_end",
    "total_distance_km",
    "passengers",
    "bags",
    "price_in_eur",
]

BOOKINGS_VARIABLES_TO_DROP_IF_NAN = [
    "date",
    "days_between_purchase_and_start_of_trip",
    "passenger_age",
    "number_of_kids",
    "status",
    "search_trip_type",
    "route_stability",
    "airlines",
    "sex",
    "total_distance_km",
    "passengers",
    "bags",
    "price_in_eur",
    "airports",
    "countries",
    "trip_start",
    "trip_end",
]

TITLE_TO_SEX_MAP = {
    "mr": "m",
    "ms": "f",
    "mrs": "f",
}

TIME_FORMAT = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
ARROW_TIME_FORMAT = "YYYY-MM-DD HH:mm:ss"

TIMESERIES_GRAPH_VARIABLES = [
    "date",
    "bookings",
    "cancellations",
    "covid_cases",
    "deaths",
]

EU_COUNTRIES = {
    "Germany": "DE",
    "Denmark": "DK",
    "Portugal": "PT",
    "Spain": "ES",
    "France": "FR",
    "Italy": "IT",
    "Ireland": "IE",
    "Austria": "AT",
    "Greece": "GR",
    "Belgium": "BE",
    "Netherlands": "NL",
    "Bulgaria": "BG",
    "Hungary": "HU",
    "Finland": "FI",
    "Romania": "RO",
    "Sweden": "SE",
    "Poland": "PL",
    "Malta": "MT",
    "Croatia": "HR",
    "Luxembourg": "LU",
    "Lithuania": "LT",
    "Latvia": "LV",
    "Estonia": "EE",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Czechia": "CZ",
    "Cyprus": "CY",
}

EEA_SUI_COUNTRIES = {
    **EU_COUNTRIES,
    "Norway": "NO",
    "Iceland": "IS",
    "Switzerland": "CH",
}

MONTHS = [
    *[f"2019_{str(month).zfill(2)}" for month in range(10, 13)],
    *[f"2020_{str(month).zfill(2)}" for month in range(1, 13)],
    *[f"2021_{str(month).zfill(2)}" for month in range(1, 11)],
]

START_DATE = {"year": 2019, "month": 10, "day": 1}
END_DATE = {"year": 2021, "month": 10, "day": 31}

LOCKDOWN_TYPES = ["StayHomeOrderPartial", "StayHomeOrder"]
