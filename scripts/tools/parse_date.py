import re


def get_year_month(date_str: str):
    match = re.match(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", date_str)
    return f"{match.group('year')}_{match.group('month')}"
