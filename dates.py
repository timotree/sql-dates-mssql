"""Generates data for the Dates dimension table.

This module provides functions to create a comprehensive date dimension table
including attributes such as day of week, month, holidays, work days, and
calendar-based calculations.
"""

from datetime import date, datetime, timedelta

import pandas as pd

# --- Constants ---

DAY_OF_WEEK_NAMES = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
    6: "Friday",
    7: "Saturday",
}

DAY_OF_WEEK_NUMBERS = {
    "Sunday": 1,
    "Monday": 2,
    "Tuesday": 3,
    "Wednesday": 4,
    "Thursday": 5,
    "Friday": 6,
    "Saturday": 7,
}

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

THIRTY_DAY_MONTHS = {4, 6, 9, 11}


# --- Utility functions ---


def get_cy_day(this_date: date) -> int:
    """Returns the numeric day of the calendar year for a date.

    Args:
        this_date: Date.

    Returns:
        Day of the calendar year.
    """
    return this_date.timetuple().tm_yday


def get_cy_week(this_date: date) -> int:
    """Returns the numeric week of the calendar year for a date.

    Args:
        this_date: Date.

    Returns:
        Week of the calendar year.
    """
    return int(this_date.strftime("%U")) + 1


def get_cy_quarter(month: int) -> int:
    """Returns the numeric quarter of the calendar year for a month.

    Args:
        month: Month.

    Returns:
        Quarter of the calendar year.
    """
    assert 1 <= month <= 12

    return (month - 1) // 3 + 1


def get_day_of_week_name(day_of_week: int) -> str:
    """Returns the full name of the day.

    Args:
        day_of_week: Day of the week (SQL-based).

    Returns:
        Name of the day of the week.
    """
    assert 1 <= day_of_week <= 7

    return DAY_OF_WEEK_NAMES[day_of_week]


def get_month_name(month: int) -> str:
    """Returns the full name of the month.

    Args:
        month: Month.

    Returns:
        Name of the month.
    """
    assert 1 <= month <= 12

    return MONTH_NAMES[month]


def to_date(iso_string: str) -> date:
    """Converts a string in ISO 8601 date format to a date object.

    Args:
        iso_string: Date in ISO 8601 format.

    Returns:
        Date instance.
    """
    return datetime.strptime(iso_string, "%Y-%m-%d").date()


def to_sql_weekday(this_date: date) -> int:
    """Converts the weekday number. SQL counts from Sunday = 1.

    Args:
        this_date: Date.

    Returns:
        Day of the week from Sunday = 1 to Saturday = 6.
    """
    return this_date.isoweekday() % 7 + 1


# --- Date logic ---


def is_last_day_of_month(this_date: date) -> bool:
    """Determines if the date is the last day of a month.

    Args:
        this_date: Date.

    Returns:
        True if it's the last day of the month, False otherwise.
    """
    next_day = this_date + timedelta(days=1)
    return next_day.month != this_date.month


def is_weekend(day_of_week: int) -> bool:
    """Determines if the date is a weekend.

    Args:
        day_of_week: Day of the week (SQL-based).

    Returns:
        True if it's a weekend, False otherwise.
    """
    assert 1 <= day_of_week <= 7

    return day_of_week in {1, 7}


def nth_weekday_of_month(
    n: int,
    weekday: int,
    month: int,
    year: int,
) -> date:
    """Returns the date of the nth weekday of the nth month, e.g., the 4th
    Thursday of November.

    Args:
        n: The nth occurrence.
        weekday: Day of the week.
        month: Month.
        year: Year.

    Returns:
        Date.
    """
    first_day = date(year, month, 1)
    first_weekday = to_sql_weekday(first_day)
    days_offset = (weekday - first_weekday + 7) % 7

    return first_day + timedelta(days=days_offset + (n - 1) * 7)


# --- Holiday logic ---


def is_fixed_holiday(this_date: date) -> bool:
    """Determines if the date is a holiday of a fixed date.

    Args:
        this_date: Date.

    Returns:
        True if it's a holiday, False otherwise.
    """
    day_of_week = to_sql_weekday(this_date)
    is_weekday = 1 < day_of_week < 7
    is_friday = day_of_week == 6
    is_monday = day_of_week == 2

    # New Year's Day
    is_on_weekday = this_date.month == 1 and this_date.day == 1 and is_weekday
    is_on_saturday = this_date.month == 12 and this_date.day == 31 and is_friday
    is_on_sunday = this_date.month == 1 and this_date.day == 2 and is_monday
    if is_on_weekday or is_on_saturday or is_on_sunday:
        return True

    # Independence Day
    is_on_weekday = this_date.month == 7 and this_date.day == 4 and is_weekday
    is_on_saturday = this_date.month == 7 and this_date.day == 3 and is_friday
    is_on_sunday = this_date.month == 7 and this_date.day == 5 and is_monday
    if is_on_weekday or is_on_saturday or is_on_sunday:
        return True

    # Christmas Day
    is_on_weekday = this_date.month == 12 and this_date.day == 25 and is_weekday
    is_on_saturday = this_date.month == 12 and this_date.day == 24 and is_friday
    is_on_sunday = this_date.month == 12 and this_date.day == 26 and is_monday
    if is_on_weekday or is_on_saturday or is_on_sunday:
        return True

    return False


def is_floating_holiday(this_date: date) -> bool:
    """Determines if the date is a holiday of a floating date.

    Args:
        this_date: Date.

    Returns:
        True if it's a holiday, False otherwise.
    """
    year = this_date.year
    day_of_week = to_sql_weekday(this_date)
    is_monday = day_of_week == DAY_OF_WEEK_NUMBERS["Monday"]

    # Martin Luther King Jr. Day (Third Monday of January)
    mlk_day = nth_weekday_of_month(3, 2, 1, year)

    # Labor Day (First Monday in September)
    labor_day = nth_weekday_of_month(1, 2, 9, year)

    # Thanksgiving Day (Fourth Thursday in November)
    thanksgiving = nth_weekday_of_month(4, 5, 11, year)

    # Day after Thanksgiving (Fourth Friday in November)
    day_after_thanksgiving = nth_weekday_of_month(4, 6, 11, year)

    # Memorial Day (Last Monday in May)
    memorial_day = this_date.month == 5 and is_monday and this_date.day >= 25

    return (
        this_date in {labor_day, thanksgiving, day_after_thanksgiving}
        or (this_date == mlk_day and year >= 1986)  # MLK Day
        or memorial_day
    )


def is_holiday(this_date: date) -> bool:
    """Determines if the date is a holiday.

    Args:
        this_date: Date.

    Returns:
        True if it's a holiday, False otherwise.
    """
    return is_fixed_holiday(this_date) or is_floating_holiday(this_date)


def is_work_day(this_date: date) -> bool:
    """Determines if the date is a work day.

    Args:
        this_date: Date.

    Returns:
        True if it's a work day, False otherwise.
    """
    return not (is_holiday(this_date) or is_weekend(to_sql_weekday(this_date)))


# --- Main Table Generator ---


def create_dates(start: date, end: date) -> pd.DataFrame:
    """Creates a date table.

    Args:
        start: Start date.
        end: End date.

    Returns:
        Table of date dimensions.
    """
    date_range = pd.date_range(start, end)
    dates = pd.DataFrame({"DateDate": date_range})

    dates["DateYear"] = dates["DateDate"].dt.year
    dates["DateMonth"] = dates["DateDate"].dt.month
    dates["DateDay"] = dates["DateDate"].dt.day
    dates["DateDayOfWeek"] = dates["DateDate"].apply(to_sql_weekday)
    dates["IsLastDayOfMonth"] = dates["DateDate"].apply(is_last_day_of_month)
    dates["IsWeekend"] = dates["DateDayOfWeek"].apply(is_weekend)
    dates["IsHoliday"] = dates["DateDate"].apply(is_holiday)
    dates["IsWorkDay"] = dates["DateDate"].apply(is_work_day)
    dates["IsPayDay"] = False
    dates["DayOfWeekName"] = dates["DateDayOfWeek"].apply(get_day_of_week_name)
    dates["NameOfMonth"] = dates["DateMonth"].apply(get_month_name)
    dates["CYQuarter"] = dates["DateMonth"].apply(get_cy_quarter)
    dates["CYDay"] = dates["DateDate"].apply(get_cy_day)
    dates["CYWeek"] = dates["DateDate"].apply(get_cy_week)

    return dates


def fill_pay_days(dates: pd.DataFrame) -> None:
    """Fills the pay days.

    Args:
        dates: Table of date dimensions.
    """
    assert not dates.empty

    current = date(2011, 1, 7)
    max_date = dates["DateDate"].max().date()

    while current <= max_date:
        # Shift the pay date to Thursday if it falls on a holiday, except for
        # Black Friday
        is_bf = current == nth_weekday_of_month(4, 6, 11, current.year)
        if is_holiday(current) and not is_bf:
            current -= timedelta(days=1)

        dates.loc[dates["DateDate"] == pd.Timestamp(current), "IsPayDay"] = True
        current += timedelta(days=14)


def get_dates(start: date, end: date) -> pd.DataFrame:
    """Wrapper function to create a date table.

    Args:
        start: Start date in ISO 8601 format.
        end: End date in ISO 8601 format.

    Returns:
        Table of date dimensions.
    """
    dates = create_dates(start, end)
    fill_pay_days(dates)

    return dates
