# db_manager.py
import pandas as pd
from sqlalchemy import create_engine


class FranceServicesDB:
    def __init__(self, db_config):
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        )

    def query(self, sql_query):
        """Exécuter une requête SQL et retourner un DataFrame"""
        return pd.read_sql_query(sql_query, self.engine)

    def get_sample_data(self, table_name, limit=10):
        """Obtenir un échantillon de données"""
        return self.query(f"SELECT * FROM {table_name} LIMIT {limit}")

    def get_dashboard_data(self):
        """Obtenir les données pour un dashboard"""
        return {
            'total_maisons': self.query("SELECT COUNT(*) as count FROM maisons_france_services").iloc[0]['count'],
            'total_usagers': self.query("SELECT COUNT(*) as count FROM usagers").iloc[0]['count'],
            'total_demandes': self.query("SELECT COUNT(*) as count FROM demandes").iloc[0]['count'],
            'satisfaction_moyenne': self.query("SELECT AVG(satisfaction_score) as avg FROM demandes").iloc[0]['avg']
        }


# Exemple d'utilisation
if __name__ == "__main__":
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'france_services_db',
        'user': 'postgres',
        'password': 'password'
    }

    db = FranceServicesDB(DB_CONFIG)

    # Test de connexion
    print("📊 Statistiques générales:")
    stats = db.get_dashboard_data()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n📋 Exemple de données:")
    print(db.get_sample_data('maisons_france_services', 5))
