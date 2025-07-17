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
            # Statistiques de base
            stats = pd.read_sql_query("""
                                      SELECT (SELECT COUNT(*) FROM maisons_france_services)           as nb_maisons,
                                             (SELECT COUNT(*) FROM usagers)                           as nb_usagers,
                                             (SELECT COUNT(*) FROM demandes)                          as nb_demandes,
                                             (SELECT ROUND(AVG(satisfaction_score), 2) FROM demandes) as satisfaction_moyenne
                                      """, conn)

            console.print(f"✅ Maisons France Services: {int(stats['nb_maisons'].iloc[0])}")
            console.print(f"✅ Usagers enregistrés: {int(stats['nb_usagers'].iloc[0])}")
            console.print(f"✅ Demandes traitées: {int(stats['nb_demandes'].iloc[0])}")
            console.print(f"✅ Satisfaction moyenne: {stats['satisfaction_moyenne'].iloc[0]}/5")

            # Tests des nouvelles tables avec requêtes avancées
            console.print("\n📊 Tests des nouvelles fonctionnalités:")
            
            # 1. Évolution du nombre de demandes par mois
            console.print("\n🔍 1. Évolution des demandes par mois (3 derniers mois):")
            query_evolution_demandes = """
            SELECT 
                mois, annee,
                SUM(nb_demandes) as total_demandes,
                ROUND(AVG(satisfaction_moyenne), 2) as satisfaction_moyenne
            FROM statistiques_mensuelles 
            GROUP BY mois, annee 
            ORDER BY annee DESC, mois DESC
            LIMIT 3;
            """
            evolution_stats = pd.read_sql_query(query_evolution_demandes, conn)
            for _, row in evolution_stats.iterrows():
                console.print(f"   📅 {int(row['mois']):02d}/{int(row['annee'])}: {int(row['total_demandes'])} demandes (satisfaction: {row['satisfaction_moyenne']}/5)")

            # 2. Répartition des services par type
            console.print("\n🔍 2. Top 5 des services les plus demandés:")
            query_services_repartition = """
            SELECT 
                type_service,
                COUNT(*) as nb_demandes,
                ROUND(AVG(satisfaction_score), 2) as satisfaction_moyenne
            FROM demandes 
            GROUP BY type_service 
            ORDER BY nb_demandes DESC
            LIMIT 5;
            """
            services_stats = pd.read_sql_query(query_services_repartition, conn)
            for _, row in services_stats.iterrows():
                console.print(f"   🎯 {row['type_service']}: {int(row['nb_demandes'])} demandes (satisfaction: {row['satisfaction_moyenne']}/5)")

            # 3. Temps d'attente par canal
            console.print("\n🔍 3. Temps d'attente moyen par canal:")
            query_temps_attente = """
            SELECT 
                ta.canal_utilise,
                ROUND(AVG(ta.temps_attente_minutes), 1) as temps_attente_moyen,
                COUNT(*) as nb_demandes
            FROM temps_attente ta
            JOIN demandes d ON ta.demande_id = d.id
            GROUP BY ta.canal_utilise
            ORDER BY temps_attente_moyen;
            """
            attente_stats = pd.read_sql_query(query_temps_attente, conn)
            for _, row in attente_stats.iterrows():
                console.print(f"   ⏱️ {row['canal_utilise']}: {row['temps_attente_moyen']} min (sur {int(row['nb_demandes'])} demandes)")

            # 4. Statistiques des nouvelles tables
            console.print("\n🔍 4. Statistiques des nouvelles tables:")
            nouvelles_tables_stats = pd.read_sql_query("""
                SELECT 
                    (SELECT COUNT(*) FROM conseillers) as nb_conseillers,
                    (SELECT COUNT(*) FROM plannings) as nb_plannings,
                    (SELECT COUNT(*) FROM statistiques_mensuelles) as nb_stats_mensuelles,
                    (SELECT COUNT(*) FROM temps_attente) as nb_temps_attente,
                    (SELECT COUNT(*) FROM services_details) as nb_services_details,
                    (SELECT COUNT(*) FROM incidents_techniques) as nb_incidents
            """, conn)
            
            stats_row = nouvelles_tables_stats.iloc[0]
            console.print(f"   👨‍💼 Conseillers: {int(stats_row['nb_conseillers'])}")
            console.print(f"   📅 Entrées de planning: {int(stats_row['nb_plannings'])}")
            console.print(f"   📊 Statistiques mensuelles: {int(stats_row['nb_stats_mensuelles'])}")
            console.print(f"   ⏱️ Données temps d'attente: {int(stats_row['nb_temps_attente'])}")
            console.print(f"   🔧 Services détaillés: {int(stats_row['nb_services_details'])}")
            console.print(f"   ⚠️ Incidents techniques: {int(stats_row['nb_incidents'])}")

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
