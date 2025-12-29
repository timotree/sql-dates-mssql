"""Generates data for the `PayPeriods` table."""

from dataclasses import dataclass
from datetime import date, timedelta
import logging

import pandas as pd

from dates import is_holiday, nth_weekday_of_month


FIRST_PAY_PERIOD_START = date(2025, 1, 12)
LAST_PAY_PERIOD_END = date(2085, 12, 22)
WORK_HOURS_PER_DAY = 8

logging.basicConfig(level=logging.INFO)


@dataclass
class DayCounts:
    """Data class for holding day counts."""

    holidays: int
    days_in_year_start: int
    days_in_year_end: int


def adjust_pay_date(pay_date: date, pay_period_start: date) -> date:
    """Adjusts the pay date if it falls on a holiday (excluding Black Friday)."""
    # Shift the pay date to Thursday if it falls on a holiday, except for Black
    # Friday
    is_bf = pay_period_start == nth_weekday_of_month(4, 6, 11, pay_period_start.year)
    if is_holiday(pay_date) and not is_bf:
        return pay_date - timedelta(days=1)


def get_day_counts(
    dates: pd.DataFrame,
    year_start: int,
    year_end: int,
) -> DayCounts:
    """Returns the counts of days within a pay period.

    Args:
        dates: Table of date dimensions for the pay period
        year_start: Year start
        year_end: Year end

    Returns:
        Data class of day counts
    """
    is_start_year = dates["DateYear"] == year_start
    is_end_year = dates["DateYear"] == year_end
    is_weekday = ~dates["IsWeekend"]

    holidays = dates["IsHoliday"].sum()
    start_work_days = (is_start_year & is_weekday).sum()
    end_work_days = (is_end_year & is_weekday).sum()

    return DayCounts(
        holidays=int(holidays),
        days_in_year_start=int(start_work_days),
        days_in_year_end=int(end_work_days),
    )


def get_pay_periods(dates: pd.DataFrame) -> pd.DataFrame:
    """Create the Pay Periods dimension table.

    Args:
        dates: Table of date dimensions

    Returns:
        Table of pay period dimensions
    """
    # Start date = 1994-01-09 (PP 199401)
    index = 1
    pp_number = 1
    records = []
    pay_periods = {
        "PayPeriodID": [],
        "StartDate": [],
        "EndDate": [],
        "PPIndex": [],
        "PPNumber": [],
        "YearStart": [],
        "YearEnd": [],
        "IsSplitYear": [],
        "Holidays": [],
        "WorkDaysInYearStart": [],
        "WorkDaysInYearEnd": [],
        "HoursInYearStart": [],
        "HoursInYearEnd": [],
        "PayDate": [],
        "PayYear": [],
    }

    current = FIRST_PAY_PERIOD_START
    # Stop at the end of PP25 because `dates` doesn't contain a full PP26
    while current <= LAST_PAY_PERIOD_END:
        end_date = current + timedelta(days=13)
        pay_date = adjust_pay_date(end_date + timedelta(days=6), current)

        year_start = int(dates.loc[dates["DateDate"] == current, "DateYear"].values[0])
        year_end = end_date.year

        in_range = dates["DateDate"].between(current, end_date)
        day_counts = get_day_counts(dates[in_range], year_start, year_end)

        record = {
            "PayPeriodID": int(f"{year_start}{pp_number:02d}"),
            "StartDate": current,
            "EndDate": end_date,
            "PPIndex": index,
            "PPNumber": pp_number,
            "YearStart": year_start,
            "YearEnd": year_end,
            "IsSplitYear": year_start != year_end,
            "Holidays": day_counts.holidays,
            "WorkDaysInYearStart": day_counts.days_in_year_start,
            "WorkDaysInYearEnd": day_counts.days_in_year_end,
            "HoursInYearStart": day_counts.days_in_year_start * WORK_HOURS_PER_DAY,
            "HoursInYearEnd": day_counts.days_in_year_end * WORK_HOURS_PER_DAY,
            "PayDate": pay_date,
            "PayYear": pay_date.year,
        }
        logging.info(f"Generated PayPeriod {record['PayPeriodID']}")
        records.append(record)

        # If the period doesn't cross the year boundary (and isn't the last one),
        # increment PP number
        if year_start == year_end and end_date != date(year_start, 12, 31):
            pp_number += 1
        else:
            pp_number = 1  # Reset for new year

        current += timedelta(days=14)
        index += 1

    return pd.DataFrame(pay_periods)
