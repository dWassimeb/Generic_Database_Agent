# src/database/connection.py
import os
import sys
import platform
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from rich.console import Console
from dotenv import load_dotenv
import pandas as pd

# Load .env.local first (for host development), then .env (for Docker)
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.console = Console()
        self.config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'database': os.getenv('DATABASE_NAME', 'france_services_db'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('DATABASE_PASSWORD', 'password'),
            'port': os.getenv('DATABASE_PORT', '5432')
        }

        self.connection_string = (
            f"postgresql://{self.config['user']}:{self.config['password']}@"
            f"{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )

        # Create engine but don't test connection yet
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._is_connected = False

    def get_engine(self):
        """Get the SQLAlchemy engine, testing the connection first"""
        if not self.test_connection():
            sys.exit(1)
        return self.engine

    def get_session(self):
        """Get a new database session, testing the connection first"""
        if not self.test_connection():
            sys.exit(1)
        return self.SessionLocal()

    def connect(self) -> None:
        """Establish connection - for compatibility with old interface"""
        if not self._is_connected:
            self.test_connection()

    def disconnect(self) -> None:
        """Close the database connection - for compatibility with old interface"""
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
            self._is_connected = False

    def test_connection(self) -> bool:
        """Test the database connection and provide helpful error messages if it fails"""
        try:
            # Test the connection by executing a simple query
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            self._is_connected = True
            return True
        except OperationalError as e:
            self.console.print(f"\n[bold red]❌ Erreur de connexion à PostgreSQL:[/bold red] {str(e)}")
            self.console.print("\n[bold yellow]Le serveur PostgreSQL n'est pas démarré ou n'accepte pas les connexions.[/bold yellow]")

            # Provide OS-specific instructions
            os_name = platform.system()
            self.console.print("\n[bold]Pour démarrer PostgreSQL:[/bold]")

            if os_name == "Darwin":  # macOS
                self.console.print("  [bold]macOS:[/bold]")
                self.console.print("  1. Si vous avez installé PostgreSQL via Homebrew:")
                self.console.print("     brew services start postgresql")
                self.console.print("  2. Ou via PostgreSQL.app, démarrez l'application")
                self.console.print("  3. Vérifiez le port avec: brew services list | grep postgres")
            elif os_name == "Linux":  # Linux
                self.console.print("  [bold]Linux:[/bold]")
                self.console.print("  sudo systemctl start postgresql")
                self.console.print("  sudo systemctl enable postgresql")
            elif os_name == "Windows":  # Windows
                self.console.print("  [bold]Windows:[/bold]")
                self.console.print("  net start postgresql-x64-13")
                self.console.print("  Ou utilisez Services.msc pour démarrer PostgreSQL")

            self.console.print(f"\n[bold]Configuration actuelle:[/bold]")
            self.console.print(f"  Host: {self.config['host']}")
            self.console.print(f"  Port: {self.config['port']}")
            self.console.print(f"  Database: {self.config['database']}")
            self.console.print(f"  User: {self.config['user']}")

            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._is_connected = False
            return False

    def execute_query_with_names(self, query: str) -> Dict[str, Any]:
        """Execute query and return results with column names."""
        if not self._is_connected:
            if not self.test_connection():
                raise Exception("Database connection failed")

        try:
            logger.info(f"Executing query: {query}")

            with self.engine.connect() as connection:
                result = connection.execute(text(query))

                # Get column names
                columns = list(result.keys()) if result.returns_rows else []

                # Get data
                rows = result.fetchall() if result.returns_rows else []
                data = [list(row) for row in rows] if rows else []

                # Get column types (simplified for PostgreSQL)
                types = ['TEXT' for _ in columns] if columns else []

            logger.info(f"Query executed successfully, returned {len(data)} rows")

            return {
                "columns": columns,
                "data": data,
                "types": types,
                "row_count": len(data)
            }

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        try:
            if not self._is_connected:
                if not self.test_connection():
                    return []

            with self.engine.connect() as connection:
                # Query to get all table names from public schema
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))

                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Found {len(tables)} tables: {tables}")

                return tables

        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        try:
            if not self._is_connected:
                if not self.test_connection():
                    return {}

            with self.engine.connect() as connection:
                # Query to get column information
                result = connection.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name AND table_schema = 'public'
                    ORDER BY ordinal_position
                """), {"table_name": table_name})

                columns = {}
                for row in result.fetchall():
                    col_name, col_type, is_nullable, col_default = row
                    columns[col_name] = {
                        'type': col_type,
                        'nullable': is_nullable == 'YES',
                        'default': col_default
                    }

                return {
                    'table_name': table_name,
                    'columns': columns
                }

        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return {}

    def import_csv_to_table(self, csv_file_path: str, table_name: str,
                            if_exists: str = 'replace') -> bool:
        """Import CSV file to database table."""
        try:
            if not self._is_connected:
                if not self.test_connection():
                    return False

            # Read CSV file
            df = pd.read_csv(csv_file_path)

            # Import to PostgreSQL using pandas
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)

            logger.info(f"Successfully imported {csv_file_path} to table {table_name}")
            logger.info(f"Table {table_name} now has {len(df)} rows and {len(df.columns)} columns")

            return True

        except Exception as e:
            logger.error(f"Failed to import CSV {csv_file_path}: {e}")
            return False

    def initialize_from_csv_directory(self, csv_directory: str) -> bool:
        """Initialize database from a directory of CSV files."""
        try:
            from pathlib import Path

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

# Global connection instance (this was missing!)
database_connection = DatabaseConnection()

# Aliases for backward compatibility with old code
generic_db_connection = database_connection
clickhouse_connection = database_connection  # For old code that imports this