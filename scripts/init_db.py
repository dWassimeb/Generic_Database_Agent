# scripts/init_db.py
import click
from src.database.loader import DatabaseLoader

@click.command()
def main():
    """Initialiser la base de données PostgreSQL"""
    loader = DatabaseLoader()
    loader.initialize_database()

if __name__ == "__main__":
    main()
