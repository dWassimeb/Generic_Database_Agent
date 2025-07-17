# scripts/demo.py
import click
import pandas as pd
from src.database.connection import DatabaseConnection
from rich.console import Console
from rich.table import Table


@click.command()
def main():
    """Lancer la démonstration"""
    console = Console()
    db_connection = DatabaseConnection()

    # Test de connexion
    with db_connection.get_engine().connect() as conn:
        # Statistiques générales
        stats = pd.read_sql_query("""
                                  SELECT (SELECT COUNT(*) FROM maisons_france_services)           as nb_maisons,
                                         (SELECT COUNT(*) FROM usagers)                           as nb_usagers,
                                         (SELECT COUNT(*) FROM demandes)                          as nb_demandes,
                                         (SELECT ROUND(AVG(satisfaction_score), 2) FROM demandes) as satisfaction_moyenne
                                  """, conn)

        # Affichage avec Rich
        table = Table(title="📊 Statistiques France Services")
        table.add_column("Métrique", style="cyan")
        table.add_column("Valeur", style="magenta")

        for col in stats.columns:
            table.add_row(col, str(stats[col].iloc[0]))

        console.print(table)

    console.print("\n🎉 Démonstration prête ! Base de données opérationnelle.")


if __name__ == "__main__":
    main()
