"""Generates data for the `Years` table."""

from calendar import isleap
import pandas as pd

from modules.df_utils import inner_join, left_join

# --- Constants ---

DAYS_PER_YEAR = 365
DAYS_PER_LEAP_YEAR = 366
WORK_HOURS_PER_DAY = 8


def get_days_in_year(year: int) -> int:
    """Returns the number of days in a given year.

    Args:
        year: Year

    Returns:
        Days
    """
    return DAYS_PER_LEAP_YEAR if isleap(year) else DAYS_PER_YEAR


def get_years(dates: pd.DataFrame, pay_periods: pd.DataFrame) -> pd.DataFrame:
    """Create the Years dimension table.

    Args:
        dates: Table of date dimensions
        pay_periods: Table of pay period dimensions

    Returns:
        Table of year dimensions
    """
    year_df = dates[["DateYear"]].drop_duplicates().copy()
    year_df.sort_values("DateYear", inplace=True)

    # Base years table
    years = year_df.copy()

    # Add total days in year
    years["TotalDays"] = years["DateYear"].apply(get_days_in_year)

    # Work days (non-weekend and not a holiday)
    work_days = dates[dates["IsWorkDay"]].groupby("DateYear").size().rename("WorkDays")
    years = inner_join(years, work_days, "DateYear")

    # Holidays
    holidays = dates[dates["IsHoliday"]].groupby("DateYear").size().rename("Holidays")
    years = inner_join(years, holidays, "DateYear")

    # Weekdays
    weekdays = dates[~dates["IsWeekend"]].groupby("DateYear").size().rename("WeekDays")
    years = inner_join(years, weekdays, "DateYear")

    # Weekends
    weekend_days = (
        dates[dates["IsWeekend"]].groupby("DateYear").size().rename("WeekendDays")
    )
    years = inner_join(years, weekend_days, "DateYear")

    # Work hours
    work_hours = weekdays * WORK_HOURS_PER_DAY
    work_hours.name = "WorkHours"
    years = inner_join(years, work_hours, "DateYear")

    # Pay periods per year
    pay_period_counts = (
        pay_periods.groupby("YearStart")["PayPeriodID"]
        .count()
        .rename("PayPeriods")
        .rename_axis("DateYear")
    )
    years = left_join(years, pay_period_counts, "DateYear")
    years["PayPeriods"] = years["PayPeriods"].fillna(0).astype(int)

    # Leap year indicator
    years["IsLeap"] = years["DateYear"].apply(isleap)

    # U.S. presidential election years (every 4 years, divisible by 4)
    years["IsPresElection"] = years["DateYear"] % 4 == 0

    # U.S. inauguration years (year after election)
    years["IsInauguration"] = years["DateYear"] % 4 == 1

    # Rename to match schema naming
    years.rename(columns={"DateYear": "YearYear"}, inplace=True)

    return years
