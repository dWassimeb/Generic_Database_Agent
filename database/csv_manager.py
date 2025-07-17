"""
CSV Data Manager for handling CSV files and database initialization
"""

import os
import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CSVDataManager:
    """Manages CSV data files and database initialization."""

    def __init__(self, csv_directory: str = "database/csv_files"):
        self.csv_directory = Path(csv_directory)
        self.csv_directory.mkdir(parents=True, exist_ok=True)
        self.table_schemas = {}
        self._discover_csv_files()

    def _discover_csv_files(self):
        """Discover and analyze CSV files in the directory."""
        try:
            csv_files = list(self.csv_directory.glob("*.csv"))
            logger.info(f"Discovered {len(csv_files)} CSV files")

            for csv_file in csv_files:
                self._analyze_csv_file(csv_file)

        except Exception as e:
            logger.error(f"Error discovering CSV files: {e}")

    def _analyze_csv_file(self, csv_file: Path):
        """Analyze a CSV file and extract schema information."""
        try:
            # Read first few rows to analyze structure
            df = pd.read_csv(csv_file, nrows=100)

            table_name = csv_file.stem
            columns = {}

            for col_name in df.columns:
                col_data = df[col_name].dropna()

                # Determine data type
                if col_data.dtype == 'object':
                    # Check if it's actually numeric
                    try:
                        pd.to_numeric(col_data.head(10))
                        data_type = 'NUMERIC'
                    except:
                        data_type = 'TEXT'
                elif col_data.dtype in ['int64', 'int32', 'int16', 'int8']:
                    data_type = 'INTEGER'
                elif col_data.dtype in ['float64', 'float32']:
                    data_type = 'REAL'
                else:
                    data_type = 'TEXT'

                columns[col_name] = {
                    'type': data_type,
                    'nullable': df[col_name].isnull().any(),
                    'unique_values': len(col_data.unique()) if len(col_data) > 0 else 0,
                    'sample_values': col_data.head(5).tolist() if len(col_data) > 0 else []
                }

            self.table_schemas[table_name] = {
                'file_path': str(csv_file),
                'table_name': table_name,
                'columns': columns,
                'row_count': len(df),
                'description': f"Data from {csv_file.name}"
            }

            logger.info(f"Analyzed {csv_file.name}: {len(df)} rows, {len(columns)} columns")

        except Exception as e:
            logger.error(f"Error analyzing CSV file {csv_file}: {e}")

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a specific table."""
        return self.table_schemas.get(table_name, {})

    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all table schemas."""
        return self.table_schemas

    def add_csv_file(self, csv_file_path: str, table_name: Optional[str] = None) -> bool:
        """Add a new CSV file to the managed collection."""
        try:
            source_path = Path(csv_file_path)
            if not source_path.exists():
                logger.error(f"CSV file {csv_file_path} does not exist")
                return False

            # Determine table name
            if table_name is None:
                table_name = source_path.stem

            # Copy file to managed directory
            dest_path = self.csv_directory / f"{table_name}.csv"

            # Copy the file
            import shutil
            shutil.copy2(source_path, dest_path)

            # Analyze the new file
            self._analyze_csv_file(dest_path)

            logger.info(f"Added CSV file {csv_file_path} as table {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error adding CSV file {csv_file_path}: {e}")
            return False

    def remove_csv_file(self, table_name: str) -> bool:
        """Remove a CSV file from the managed collection."""
        try:
            csv_file = self.csv_directory / f"{table_name}.csv"
            if csv_file.exists():
                csv_file.unlink()

            if table_name in self.table_schemas:
                del self.table_schemas[table_name]

            logger.info(f"Removed CSV file for table {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error removing CSV file for table {table_name}: {e}")
            return False

    def list_available_tables(self) -> List[str]:
        """List all available tables."""
        return list(self.table_schemas.keys())

    def get_sample_data(self, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get sample data from a table."""
        try:
            if table_name not in self.table_schemas:
                logger.error(f"Table {table_name} not found")
                return {}

            csv_file = self.table_schemas[table_name]['file_path']
            df = pd.read_csv(csv_file, nrows=limit)

            return {
                'columns': df.columns.tolist(),
                'data': df.values.tolist(),
                'row_count': len(df)
            }

        except Exception as e:
            logger.error(f"Error getting sample data for table {table_name}: {e}")
            return {}

    def get_csv_directory(self) -> str:
        """Get the CSV directory path."""
        return str(self.csv_directory)

# Global instance
csv_manager = CSVDataManager()