"""Generic SQL Server access with the pyodbc module."""

from dataclasses import dataclass

import pandas as pd
import sqlalchemy as sa


@dataclass
class Connection:
    """Data class for holding connection details."""

    host: str
    database: str
    username: str
    password: str
    port: int = 1433


def escape_object(obj: str) -> tuple[str, str]:
    """Escapes object names and splits a qualified object if needed.

    Args:
        obj: Object name

    Returns:
        Escaped schema and table names
    """
    schema, table = split_object_name(obj)
    return (f"[{schema}]", f"[{table}]")


def split_object_name(obj: str) -> tuple[str, str]:
    """Splits a qualified object name into it's schema and table name. If no
    schema is provided then it defaults to 'dbo'.

    Args:
        obj: Qualified object name

    Returns:
        Schema and table names
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
    """SQL Server database access."""

    def __init__(self, connection: Connection):
        """Default constructor. Creates the SQL Alchemy engine.

        Args:
            connection: Connection details
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
        """Executes a custom SQL statement.

        Args:
            statement: Statement to execute
        """
        with self._engine.connect() as connect:
            with connect.begin():
                connect.execution_options(autocommit=True).execute(sa.text(statement))

    def query(self, statement: str) -> pd.DataFrame:
        """Executes a custom SQL query that returns a dataset.

        Args:
            statement: Query to execute

        Returns:
            Data from the query
        """
        with self._engine.connect() as connect:
            data = pd.read_sql(sa.text(statement), connect)

        return data

    def read_table(self, obj: str) -> pd.DataFrame:
        """Reads data from a table.

        Args:
            obj: Object name

        Returns:
            Data from the object
        """
        return self.query(f"SELECT * FROM {escape_object(obj)};")

    def write_table(self, obj: str, data: pd.DataFrame) -> None:
        """Writes data to a table.

        This doesn't take advantage of if_exists='replace' because it drops the
        table and destroys the schema. Use execute() with a truncate statement
        beforehand if needed.

        Args:
            obj: Object name
            data: Data to be written
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
