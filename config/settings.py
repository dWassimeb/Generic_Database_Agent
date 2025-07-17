"""
Configuration settings for the Generic SQL Agent.
"""

from pydantic import BaseModel
from typing import Optional

class DatabaseConfig(BaseModel):
    """Generic database configuration."""
    db_type: str = "sqlite"
    db_path: str = "user_data/database.db"
    csv_directory: str = "database/csv_files"
    auto_import_csv: bool = True
    backup_enabled: bool = True
    backup_directory: str = "user_data/backups"

    @property
    def connection_params(self) -> dict:
        """Get connection parameters."""
        return {
            "db_type": self.db_type,
            "db_path": self.db_path,
            "csv_directory": self.csv_directory,
            "auto_import_csv": self.auto_import_csv
        }

class AgentConfig(BaseModel):
    """Agent configuration settings."""
    verbose: bool = True
    max_query_results: int = 1000
    enable_visualization: bool = True
    enable_csv_export: bool = True
    query_timeout: int = 30  # seconds

class AppConfig(BaseModel):
    """Application configuration."""
    app_name: str = "Generic SQL Agent"
    version: str = "1.0.0"
    debug_mode: bool = False
    export_directory: str = "exports"
    visualization_directory: str = "visualizations"
    log_level: str = "INFO"

# Global configuration instances
DATABASE_CONFIG = DatabaseConfig()
AGENT_CONFIG = AgentConfig()
APP_CONFIG = AppConfig()