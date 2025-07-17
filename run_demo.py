# run_demo.py (à la racine)
# !/usr/bin/env python3
"""
Script principal pour la démonstration France Services AI
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Exécuter la démonstration complète"""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    console.print(Panel.fit(
        "🚀 Démonstration IA France Services - ANCT",
        style="bold blue"
    ))

    # 1. Générer les données
    try:
        console.print("\n📊 Étape 1: Génération des données...")
        from src.data_generator import FranceServicesDataGenerator
        generator = FranceServicesDataGenerator()
        generator.generate_all_data()
    except Exception as e:
        console.print("\n[bold red]❌ Erreur lors de la génération des données:[/bold red]")
        console.print(f"   {str(e)}")
        return 1

    # 2. Initialiser la base de données
    try:
        console.print("\n🗄️ Étape 2: Initialisation de la base...")
        from src.database.loader import DatabaseLoader
        
        # Vérifier si psycopg2 est disponible
        try:
            import psycopg2
        except ImportError:
            console.print("\n[bold red]❌ Erreur:[/bold red] Le module psycopg2 n'est pas installé.")
            console.print("Cette application nécessite PostgreSQL et le package psycopg2.")
            console.print("\nPour installer psycopg2, vous avez besoin de:")
            console.print("1. PostgreSQL installé sur votre système")
            console.print("2. Les bibliothèques de développement PostgreSQL")
            console.print("3. Exécuter: [bold]poetry add psycopg2-binary[/bold]")
            console.print("\nPour plus d'informations: https://www.psycopg.org/docs/install.html")
            return 1
            
        # Initialiser la base de données
        loader = DatabaseLoader()
        loader.initialize_database()
        
    except Exception as e:
        # Les erreurs détaillées de connexion sont déjà gérées dans DatabaseConnection.test_connection()
        # Pas besoin d'afficher à nouveau le message d'erreur ici
        return 1

    # 3. Lancer la démonstration
    try:
        console.print("\n🎯 Étape 3: Lancement de la démonstration...")
        from src.database.connection import DatabaseConnection
        import pandas as pd

        db_connection = DatabaseConnection()
        # get_engine() va déjà tester la connexion et afficher des messages d'erreur si nécessaire
        engine = db_connection.get_engine()
        
        with engine.connect() as conn:
            stats = pd.read_sql_query("""
                                      SELECT (SELECT COUNT(*) FROM maisons_france_services)           as nb_maisons,
                                             (SELECT COUNT(*) FROM usagers)                           as nb_usagers,
                                             (SELECT COUNT(*) FROM demandes)                          as nb_demandes,
                                             (SELECT ROUND(AVG(satisfaction_score), 2) FROM demandes) as satisfaction_moyenne
                                      """, conn)

            console.print(f"✅ Maisons France Services: {stats['nb_maisons'].iloc[0]}")
            console.print(f"✅ Usagers enregistrés: {stats['nb_usagers'].iloc[0]}")
            console.print(f"✅ Demandes traitées: {stats['nb_demandes'].iloc[0]}")
            console.print(f"✅ Satisfaction moyenne: {stats['satisfaction_moyenne'].iloc[0]}/5")

        console.print(Panel.fit(
            "🎉 Démonstration prête ! Base de données opérationnelle.",
            style="bold green"
        ))

    except Exception as e:
        console.print("\n[bold red]❌ Erreur lors de l'exécution de la démonstration:[/bold red]")
        console.print(f"   {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
