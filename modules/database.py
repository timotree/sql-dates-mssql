"""Generic SQL Server database access layer using SQLAlchemy and pyodbc.

This module provides classes and functions for connecting to and interacting
with SQL Server databases, including executing queries and writing data from
pandas DataFrames.
"""

from dataclasses import dataclass

import pandas as pd
import sqlalchemy as sa


@dataclass
class Connection:
    """Data class for holding SQL Server connection details.

    Attributes:
        host: The server hostname or IP address.
        database: The database name.
        username: The username for authentication.
        password: The password for authentication.
        port: The port number (defaults to 1433).
    """

    host: str
    database: str
    username: str
    password: str
    port: int = 1433


def escape_object(obj: str) -> tuple[str, str]:
    """Escapes object names for SQL and splits qualified names.

    Wraps schema and table names in SQL brackets for safe use in queries.

    Args:
        obj: Object name (table or schema.table format).

    Returns:
        Tuple of (escaped_schema, escaped_table).
    """
    schema, table = split_object_name(obj)
    return (f"[{schema}]", f"[{table}]")


def split_object_name(obj: str) -> tuple[str, str]:
    """Splits a qualified object name into schema and table components.

    If no schema is specified, defaults to 'dbo'.

    Args:
        obj: Qualified object name (table or schema.table format).

    Returns:
        Tuple of (schema, table).

    Raises:
        AssertionError: If the object name contains more than 2 dots.
    """
    dots = obj.count(".")

    # Two dots indicates database name provided
    assert 0 <= dots <= 2

    # Default, zero dots
    schema = "dbo"
    table = obj

    if dots == 1:
        schema, table = obj.split(".")

    return (schema, table)


class Database:
    """SQL Server database access using SQLAlchemy.

    This class provides methods to connect to a SQL Server database and
    perform operations like executing queries and writing data.
    """

    def __init__(self, connection: Connection):
        """Initializes the database connection and creates the SQLAlchemy engine.

        Args:
            connection: Connection details for the SQL Server database.
        """
        connection_url = sa.URL.create(
            "mssql+pyodbc",
            host=connection.host,
            database=connection.database,
            username=connection.username,
            password=connection.password,
            port=connection.port,
            query={"driver": "ODBC Driver 17 for SQL Server"},
        )
        self._engine = sa.create_engine(connection_url, fast_executemany=True)

    def execute(self, statement: str) -> None:
        """Executes a SQL statement without returning results.

        Args:
            statement: SQL statement to execute.
        """
        with self._engine.connect() as connect:
            with connect.begin():
                connect.execution_options(autocommit=True).execute(sa.text(statement))

    def query(self, statement: str) -> pd.DataFrame:
        """Executes a SQL query and returns the results as a DataFrame.

        Args:
            statement: SQL query to execute.

        Returns:
            DataFrame containing the query results.
        """
        with self._engine.connect() as connect:
            data = pd.read_sql(sa.text(statement), connect)

        return data

    def read_table(self, obj: str) -> pd.DataFrame:
        """Reads all data from a table.

        Args:
            obj: Fully qualified object name (e.g., 'schema.table').

        Returns:
            DataFrame containing all data from the table.
        """
        return self.query(f"SELECT * FROM {escape_object(obj)};")

    def write_table(self, obj: str, data: pd.DataFrame) -> None:
        """Writes data to a table in the database.

        Note: This method appends data rather than replacing. If you need to
        clear a table first, use execute() with a TRUNCATE statement.

        Args:
            obj: Fully qualified object name (e.g., 'schema.table').
            data: DataFrame containing the data to write.
        """
        schema, table = split_object_name(obj)

        with self._engine.begin():
            data.to_sql(
                table,
                self._engine,
                schema=schema,
                index=False,
                if_exists="append",
            )
