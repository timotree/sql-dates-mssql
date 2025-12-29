"""Populates date tables."""

from datetime import date
import json
import logging
from typing import Any

from dates import get_dates
from modules.database import Connection, Database
from pay_periods import get_pay_periods
from years import get_years


CONFIG_FILE = "config.json"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def read_config(path: str = CONFIG_FILE) -> dict[str, Any]:
    """Reads configuration from a JSON file.

    Args:
        path: Path to configuration file

    Returns:
        Parsed configuration dictionary
    """
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        raise


def generate_and_store_data(config: dict[str, Any]) -> None:
    """Generates and stores date-related data in the database.

    Args:
        config: Configuration dictionary
    """
    try:
        logging.info("Generating date data...")
        dates = get_dates(date(1983, 1, 1), date(2085, 12, 31))
        pay_periods = get_pay_periods(dates)
        years = get_years(dates, pay_periods)

        logging.info("Connecting to database...")
        db = Database(
            Connection(
                host=config["host"],
                database=config["database"],
                username=config["username"],
                password=config["password"],
                port=config.get("port", 1433),
            )
        )

        schema = config["schema"]

        logging.info("Writing data to database...")
        db.write_table(f"{schema}.Dates", dates)
        db.write_table(f"{schema}.PayPeriods", pay_periods)
        db.write_table(f"{schema}.Years", years)

        logging.info("Data successfully written to database.")

    except Exception as e:
        logging.exception("An error occurred while generating or writing data.")
        raise


def main():
    """Main entry point.

    Returns:
        Exit status code (0 = success)
    """
    try:
        generate_and_store_data(read_config())
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
