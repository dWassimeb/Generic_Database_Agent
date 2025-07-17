import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os


class PostgreSQLLoader:
    def __init__(self, db_config):
        self.db_config = db_config
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        )

    def create_tables(self):
        """Créer les tables PostgreSQL"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        # Supprimer les tables existantes
        tables = ['performances_mensuelles', 'demandes', 'conseillers', 'usagers', 'maisons_france_services']
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

        # Créer les tables
        cur.execute("""
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
                    """)

        cur.execute("""
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
                    """)

        cur.execute("""
                    CREATE TABLE conseillers
                    (
                        id                      SERIAL PRIMARY KEY,
                        nom                     VARCHAR(100),
                        prenom                  VARCHAR(100),
                        maison_fs_id            INTEGER REFERENCES maisons_france_services (id),
                        specialites             TEXT,
                        date_embauche           DATE,
                        charge_travail_actuelle INTEGER DEFAULT 0,
                        formations_suivies      TEXT
                    );
                    """)

        cur.execute("""
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
                        conseiller_id      INTEGER REFERENCES conseillers (id),
                        complexite         VARCHAR(20),
                        suivi_necessaire   BOOLEAN DEFAULT FALSE
                    );
                    """)

        cur.execute("""
                    CREATE TABLE performances_mensuelles
                    (
                        id                   SERIAL PRIMARY KEY,
                        maison_fs_id         INTEGER REFERENCES maisons_france_services (id),
                        mois                 DATE,
                        nb_visites           INTEGER,
                        nb_demandes_traitees INTEGER,
                        taux_satisfaction    DECIMAL(3, 2),
                        temps_attente_moyen  INTEGER,
                        taux_resolution      DECIMAL(3, 2)
                    );
                    """)

        conn.commit()
        cur.close()
        conn.close()
        print("✓ Tables créées")

    def load_csv_to_postgres(self, csv_file, table_name):
        """Charger un CSV dans PostgreSQL"""
        if not os.path.exists(csv_file):
            print(f"❌ Fichier {csv_file} non trouvé")
            return

        df = pd.read_csv(csv_file)

        # Traitement spécifique pour certaines tables
        if table_name == 'demandes':
            df['date_demande'] = pd.to_datetime(df['date_demande'])
        elif table_name == 'performances_mensuelles':
            df['mois'] = pd.to_datetime(df['mois'])
        elif table_name in ['maisons_france_services', 'usagers', 'conseillers']:
            if 'date_ouverture' in df.columns:
                df['date_ouverture'] = pd.to_datetime(df['date_ouverture'])
            if 'date_inscription' in df.columns:
                df['date_inscription'] = pd.to_datetime(df['date_inscription'])
            if 'date_embauche' in df.columns:
                df['date_embauche'] = pd.to_datetime(df['date_embauche'])

        df.to_sql(table_name, self.engine, if_exists='append', index=False)
        print(f"✓ {csv_file} chargé dans {table_name} ({len(df)} lignes)")

    def load_all_data(self):
        """Charger tous les CSV dans PostgreSQL"""
        csv_files = [
            ('data/maisons_france_services.csv', 'maisons_france_services'),
            ('data/usagers.csv', 'usagers'),
            ('data/conseillers.csv', 'conseillers'),
            ('data/demandes.csv', 'demandes'),
            ('data/performances_mensuelles.csv', 'performances_mensuelles')
        ]

        for csv_file, table_name in csv_files:
            self.load_csv_to_postgres(csv_file, table_name)

    def create_indexes(self):
        """Créer des index pour optimiser les requêtes"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        indexes = [
            "CREATE INDEX idx_demandes_date ON demandes(date_demande);",
            "CREATE INDEX idx_demandes_maison ON demandes(maison_fs_id);",
            "CREATE INDEX idx_demandes_usager ON demandes(usager_id);",
            "CREATE INDEX idx_demandes_service ON demandes(type_service);",
            "CREATE INDEX idx_maisons_region ON maisons_france_services(region);",
            "CREATE INDEX idx_performances_mois ON performances_mensuelles(mois);",
        ]

        for index_sql in indexes:
            cur.execute(index_sql)

        conn.commit()
        cur.close()
        conn.close()
        print("✓ Index créés")


def main():
    """Fonction principale"""
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'france_services_db',
        'user': 'postgres',
        'password': 'password'
    }

    loader = PostgreSQLLoader(DB_CONFIG)

    print("🚀 Initialisation de la base de données...")
    loader.create_tables()
    loader.load_all_data()
    loader.create_indexes()
    print("\n🎉 Base de données initialisée avec succès!")


if __name__ == "__main__":
    main()
