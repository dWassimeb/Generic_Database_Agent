# src/database/loader.py
import pandas as pd
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

# Try to import psycopg2, but handle the case where it's not installed
try:
    import psycopg2
    from sqlalchemy import text
    from .connection import DatabaseConnection
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class DatabaseLoader:
    def __init__(self):
        self.console = Console()
        
        if not PSYCOPG2_AVAILABLE:
            self.console.print("[bold red]Error:[/bold red] psycopg2 module not found.")
            self.console.print("This script requires PostgreSQL and the psycopg2 package to run.")
            self.console.print("\nTo install psycopg2, you need:")
            self.console.print("1. PostgreSQL installed on your system")
            self.console.print("2. PostgreSQL development libraries")
            self.console.print("3. Run: [bold]pip install psycopg2-binary[/bold] or [bold]poetry add psycopg2-binary[/bold]")
            self.console.print("\nFor more information, visit: https://www.psycopg.org/docs/install.html")
            return
            
        self.db_connection = DatabaseConnection()
        self.engine = self.db_connection.get_engine()

    def create_tables(self):
        """Créer les tables PostgreSQL (version enrichie)"""
        with self.engine.connect() as conn:
            # Supprimer les tables existantes
            tables = [
                'incidents_techniques', 'temps_attente', 'services_details',
                'statistiques_mensuelles', 'plannings', 'conseillers', 
                'demandes', 'usagers', 'maisons_france_services'
            ]
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

            # Tables existantes (maisons_france_services, usagers, demandes)
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

            # Nouvelles tables
            conn.execute(text("""
                CREATE TABLE conseillers (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    maison_fs_id INTEGER REFERENCES maisons_france_services(id),
                    specialite VARCHAR(50),
                    date_embauche DATE,
                    temps_travail VARCHAR(20),
                    niveau_experience VARCHAR(20),
                    statut VARCHAR(20) DEFAULT 'actif'
                );
            """))

            conn.execute(text("""
                CREATE TABLE plannings (
                    id SERIAL PRIMARY KEY,
                    maison_fs_id INTEGER REFERENCES maisons_france_services(id),
                    date DATE,
                    jour_semaine VARCHAR(20),
                    heure_ouverture DECIMAL(3,1),
                    heure_fermeture DECIMAL(3,1),
                    nb_conseillers_prevus INTEGER,
                    nb_conseillers_presents INTEGER,
                    fermeture_exceptionnelle BOOLEAN DEFAULT FALSE
                );
            """))

            conn.execute(text("""
                CREATE TABLE statistiques_mensuelles (
                    id SERIAL PRIMARY KEY,
                    maison_fs_id INTEGER REFERENCES maisons_france_services(id),
                    mois INTEGER,
                    annee INTEGER,
                    nb_demandes INTEGER,
                    nb_demandes_resolues INTEGER,
                    temps_moyen_resolution INTEGER,
                    satisfaction_moyenne DECIMAL(3,2),
                    nb_usagers_uniques INTEGER,
                    nb_nouveaux_usagers INTEGER,
                    taux_retour_usagers DECIMAL(3,2)
                );
            """))

            conn.execute(text("""
                CREATE TABLE services_details (
                    id SERIAL PRIMARY KEY,
                    service VARCHAR(50),
                    sous_service VARCHAR(100),
                    complexite VARCHAR(20),
                    volume_mensuel_moyen INTEGER,
                    duree_moyenne_traitement INTEGER,
                    taux_resolution DECIMAL(3,2),
                    satisfaction_moyenne DECIMAL(3,2),
                    formation_requise VARCHAR(20)
                );
            """))

            conn.execute(text("""
                CREATE TABLE temps_attente (
                    id SERIAL PRIMARY KEY,
                    demande_id INTEGER REFERENCES demandes(id),
                    temps_attente_minutes INTEGER,
                    heure_demande INTEGER,
                    jour_semaine VARCHAR(20),
                    canal_utilise VARCHAR(20),
                    priorite VARCHAR(20)
                );
            """))

            conn.execute(text("""
                CREATE TABLE incidents_techniques (
                    id SERIAL PRIMARY KEY,
                    maison_fs_id INTEGER REFERENCES maisons_france_services(id),
                    type_incident VARCHAR(50),
                    date_debut TIMESTAMP,
                    duree_minutes INTEGER,
                    impact_usagers INTEGER,
                    resolu BOOLEAN DEFAULT FALSE,
                    gravite VARCHAR(20)
                );
            """))

            conn.commit()

        self.console.print("✅ Tables créées avec succès")

    def load_csv_data(self):
        """Charger les données CSV dans PostgreSQL (version enrichie)"""
        csv_dir = Path("data/csv")

        files_to_load = [
            ('maisons_france_services.csv', 'maisons_france_services'),
            ('usagers.csv', 'usagers'),
            ('conseillers.csv', 'conseillers'),
            ('demandes.csv', 'demandes'),
            ('plannings.csv', 'plannings'),
            ('statistiques_mensuelles.csv', 'statistiques_mensuelles'),
            ('temps_attente.csv', 'temps_attente'),
            ('services_details.csv', 'services_details'),
            ('incidents_techniques.csv', 'incidents_techniques')
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
                date_columns = ['date_demande', 'date_ouverture', 'date_inscription', 
                               'date_embauche', 'date', 'date_debut']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])

                df.to_sql(table_name, self.engine, if_exists='append', index=False)
                self.console.print(f"✅ {csv_file} chargé ({len(df)} lignes)")
                progress.update(task, advance=1)

    def create_indexes(self):
        """Créer les index pour optimiser les performances (version enrichie)"""
        with self.engine.connect() as conn:
            indexes = [
                # Index existants
                "CREATE INDEX IF NOT EXISTS idx_demandes_date ON demandes(date_demande);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_maison ON demandes(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_usager ON demandes(usager_id);",
                "CREATE INDEX IF NOT EXISTS idx_demandes_service ON demandes(type_service);",
                "CREATE INDEX IF NOT EXISTS idx_maisons_region ON maisons_france_services(region);",
                
                # Nouveaux index
                "CREATE INDEX IF NOT EXISTS idx_conseillers_maison ON conseillers(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_plannings_date ON plannings(date);",
                "CREATE INDEX IF NOT EXISTS idx_plannings_maison ON plannings(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_stats_date ON statistiques_mensuelles(annee, mois);",
                "CREATE INDEX IF NOT EXISTS idx_stats_maison ON statistiques_mensuelles(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_attente_demande ON temps_attente(demande_id);",
                "CREATE INDEX IF NOT EXISTS idx_incidents_maison ON incidents_techniques(maison_fs_id);",
                "CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents_techniques(date_debut);"
            ]

            for index_sql in indexes:
                conn.execute(text(index_sql))

            conn.commit()

        self.console.print("✅ Index créés avec succès")

    def initialize_database(self):
        """Initialiser complètement la base de données"""
        if not PSYCOPG2_AVAILABLE:
            self.console.print("[bold red]Error:[/bold red] Cannot initialize database.")
            self.console.print("This script requires PostgreSQL and the psycopg2 package to run.")
            self.console.print("\nTo install psycopg2, you need:")
            self.console.print("1. PostgreSQL installed on your system")
            self.console.print("2. PostgreSQL development libraries")
            self.console.print("3. Run: [bold]pip install psycopg2-binary[/bold] or [bold]poetry add psycopg2-binary[/bold]")
            self.console.print("\nFor more information, visit: https://www.psycopg.org/docs/install.html")
            sys.exit(1)
            
        self.console.print("🚀 Initialisation de la base de données...")
        self.create_tables()
        self.load_csv_data()
        self.create_indexes()
        self.console.print("🎉 Base de données initialisée avec succès!")
