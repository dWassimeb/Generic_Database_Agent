# src/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'database': os.getenv('DATABASE_NAME', 'france_services_db'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('DATABASE_PASSWORD', 'password'),
            'port': os.getenv('DATABASE_PORT', '5432')
        }

        self.engine = create_engine(
            f"postgresql://{self.config['user']}:{self.config['password']}@"
            f"{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.SessionLocal()