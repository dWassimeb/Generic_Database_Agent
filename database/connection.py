"""
Generic SQL Database Connection using SQLite with CSV import capability
"""

import sqlite3
import pandas as pd
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GenericDatabaseConnection:
    """Manages generic SQL database connections using SQLite with CSV import."""

    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._is_connected = False
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self) -> None:
        """Establish connection to SQLite database."""
        if self._is_connected and self.connection:
            return

        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self._is_connected = True
            logger.info(f"Successfully connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self._is_connected = False
            raise

    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None
                self._is_connected = False

    def execute_query_with_names(self, query: str) -> Dict[str, Any]:
        """Execute query and return results with column names."""
        if not self._is_connected:
            self.connect()

        if not self.connection:
            raise Exception("No database connection available")

        try:
            logger.info(f"Executing query: {query}")

            cursor = self.connection.cursor()
            cursor.execute(query)

            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []

            # Get data
            rows = cursor.fetchall()
            data = [list(row) for row in rows] if rows else []

            # Get column types (simplified)
            types = ['TEXT' for _ in columns]  # SQLite is dynamically typed

            logger.info(f"Query executed successfully, returned {len(data)} rows")

            return {
                "columns": columns,
                "data": data,
                "types": types
            }

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def import_csv_to_table(self, csv_file_path: str, table_name: str,
                           if_exists: str = 'replace') -> bool:
        """Import CSV file to database table."""
        try:
            if not self._is_connected:
                self.connect()

            # Read CSV file
            df = pd.read_csv(csv_file_path)

            # Import to SQLite
            df.to_sql(table_name, self.connection, if_exists=if_exists, index=False)

            logger.info(f"Successfully imported {csv_file_path} to table {table_name}")
            logger.info(f"Table {table_name} now has {len(df)} rows and {len(df.columns)} columns")

            return True

        except Exception as e:
            logger.error(f"Failed to import CSV {csv_file_path}: {e}")
            return False

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        try:
            if not self._is_connected:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")

            columns = {}
            for row in cursor.fetchall():
                col_name = row[1]
                col_type = row[2]
                columns[col_name] = {
                    'type': col_type,
                    'nullable': not row[3],
                    'default': row[4]
                }

            return {
                'table_name': table_name,
                'columns': columns
            }

        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return {}

    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        try:
            if not self._is_connected:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Found {len(tables)} tables: {tables}")

            return tables

        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []

    def test_connection(self) -> bool:
        """Test if connection is working."""
        try:
            if not self._is_connected:
                self.connect()
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._is_connected = False
        return False

    def initialize_from_csv_directory(self, csv_directory: str) -> bool:
        """Initialize database from a directory of CSV files."""
        try:
            csv_dir = Path(csv_directory)
            if not csv_dir.exists():
                logger.error(f"CSV directory {csv_directory} does not exist")
                return False

            csv_files = list(csv_dir.glob("*.csv"))
            if not csv_files:
                logger.warning(f"No CSV files found in {csv_directory}")
                return False

            logger.info(f"Found {len(csv_files)} CSV files to import")

            for csv_file in csv_files:
                table_name = csv_file.stem  # Use filename without extension as table name
                success = self.import_csv_to_table(str(csv_file), table_name)
                if not success:
                    logger.error(f"Failed to import {csv_file}")
                    return False

            logger.info(f"Successfully initialized database with {len(csv_files)} tables")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize from CSV directory: {e}")
            return False

# Global connection instance
generic_db_connection = GenericDatabaseConnection()