"""Utility functions for pandas DataFrame operations.

This module provides wrapper functions for common join operations on DataFrames
and Series, simplifying the API for inner and left outer joins.
"""

import pandas as pd


def inner_join(
    left: pd.DataFrame | pd.Series,
    right: pd.DataFrame | pd.Series,
    left_on: str,
    right_on: str | None = None,
) -> pd.DataFrame:
    """Wrapper function to provide inner join functionality.

    Args:
        left: Left-side DataFrame.
        right: Right-side DataFrame.
        left_on: Left-side column(s) to join on.
        right_on: Right-side column(s) to join on. If not provided then 'left_on'
            is used for both sides.

    Returns:
        New DataFrame with the two joined.
    """
    right_on = left_on if not right_on else right_on

    return pd.merge(left, right, left_on=left_on, right_on=right_on)


def left_join(
    left: pd.DataFrame | pd.Series,
    right: pd.DataFrame | pd.Series,
    left_on: str,
    right_on: str | None = None,
) -> pd.DataFrame:
    """Wrapper function to provide left outer join functionality.

    Args:
        left: Left-side DataFrame.
        right: Right-side DataFrame.
        left_on: Left-side column(s) to join on.
        right_on: Right-side column(s) to join on. If not provided then 'left_on'
            is used for both sides.

    Returns:
        New DataFrame with the two joined.
    """
    right_on = left_on if not right_on else right_on

    return pd.merge(left, right, how="left", left_on=left_on, right_on=right_on)
