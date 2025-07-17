# src/database/loader.py
import pandas as pd
import psycopg2
from sqlalchemy import text
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from .connection import DatabaseConnection


class DatabaseLoader:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.engine = self.db_connection.get_engine()
        self.console = Console()

    def create_tables(self):
        """Créer les tables PostgreSQL"""
        with self.engine.connect() as conn:
            # Supprimer les tables existantes
            tables = ['demandes', 'usagers', 'maisons_france_services']
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

            # Créer les tables
            conn.execute(text("""
                              CREATE TABLE maisons_france_services
                              (
                                  id                   SERIAL PRIMARY KEY,
                                  nom                  VARCHAR(255) NOT NULL,
                                  adresse              TEXT,
                                  code_postal          VARCHAR(10),
                                  ville                VARCHAR(100),
                                  departement          VARCHAR(100),
                                  region               VARCHAR(100),
                                  latitude             DECIMAL(10, 8),
                                  longitude            DECIMAL(11, 8),
                                  type_structure       VARCHAR(50),
                                  date_ouverture       DATE,
                                  nb_conseillers       INTEGER,
                                  services_disponibles TEXT,
                                  population_desservie INTEGER,
                                  statut               VARCHAR(20) DEFAULT 'active'
                              );
                              """))

            conn.execute(text("""
                              CREATE TABLE usagers
                              (
                                  id                  SERIAL PRIMARY KEY,
                                  age                 INTEGER,
                                  genre               VARCHAR(10),
                                  situation_familiale VARCHAR(50),
                                  niveau_numerique    VARCHAR(20),
                                  code_postal         VARCHAR(10),
                                  ville               VARCHAR(100),
                                  date_inscription    DATE,
                                  frequence_visite    VARCHAR(20)
                              );
                              """))

            conn.execute(text("""
                              CREATE TABLE demandes
                              (
                                  id                 SERIAL PRIMARY KEY,
                                  usager_id          INTEGER REFERENCES usagers (id),
                                  maison_fs_id       INTEGER REFERENCES maisons_france_services (id),
                                  date_demande       TIMESTAMP,
                                  type_service       VARCHAR(100),
                                  organisme_concerne VARCHAR(100),
                                  canal              VARCHAR(20),
                                  duree_traitement   INTEGER,
                                  satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
                                  resolu             BOOLEAN DEFAULT FALSE,
                                  conseiller_id      INTEGER,
                                  complexite         VARCHAR(20),
                                  suivi_necessaire   BOOLEAN DEFAULT FALSE
                              );
                              """))

            conn.commit()

        self.console.print("✅ Tables créées avec succès")

    def load_csv_data(self):
        """Charger les données CSV dans PostgreSQL"""
        csv_dir = Path("data/csv")

        files_to_load = [
            ('maisons_france_services.csv', 'maisons_france_services'),
            ('usagers.csv', 'usagers'),
            ('demandes.csv', 'demandes')
        ]

        with Progress() as progress:
            task = progress.add_task("[blue]Chargement des données...", total=len(files_to_load))

            for csv_file, table_name in files_to_load:
                file_path = csv_dir / csv_file

                if not file_path.exists():
                    self.console.print(f"❌ Fichier {csv_file} non trouvé")
                    continue

                df = pd.read_csv(file_path)

                # Traitement des dates
                if 'date_demande' in df.columns:
                    df['date_demande'] = pd.to_datetime(df['date_demande'])
                if 'date_ouverture' in df.columns:
                    df['date_ouverture'] = pd.to_datetime(df['date_ouverture'])
                if 'date_inscription' in df.columns:
                    df['date_inscription'] = pd.to_datetime(df['date_inscription'])

                df.to_sql(table_name, self.engine, if_exists='append', index=False)
                self.console.print(f"✅ {csv_file} chargé ({len(df)} lignes)")
                progress.update(task, advance=1)

    def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        with self.engine.connect() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_demandes_date ON demandes(date_demande);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_maison ON demandes(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_usager ON demandes(usager_id);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_service ON demandes(type_service);",
                "CREATE INDEX IF NOT EXISTS idx_maisons_region ON maisons_france_services(region);",
            ]

            for index_sql in indexes:
                conn.execute(text(index_sql))

            conn.commit()

        self.console.print("✅ Index créés avec succès")

    def initialize_database(self):
        """Initialiser complètement la base de données"""
        self.console.print("🚀 Initialisation de la base de données...")
        self.create_tables()
        self.load_csv_data()
        self.create_indexes()
        self.console.print("🎉 Base de données initialisée avec succès!")
