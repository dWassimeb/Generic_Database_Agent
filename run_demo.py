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


def generate_interactive_charts(conn, console):
    """Générer des graphiques interactifs avec plotly"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        import pandas as pd
        from datetime import datetime
        import traceback
        
        console.print("   📊 Création des visualisations...")
        console.print("   🔍 [DEBUG] Plotly version:", px.__version__ if hasattr(px, '__version__') else "Version inconnue")
        
        # Créer le dossier pour les graphiques
        charts_dir = Path("data/charts")
        charts_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"   🔍 [DEBUG] Dossier charts créé: {charts_dir}")
        
        # 1. Graphique d'évolution des demandes par mois
        console.print("      📈 Évolution mensuelle des demandes...")
        
        try:
            # Étape 1: Exécution de la requête
            console.print("      🔍 [DEBUG] Exécution de la requête SQL...")
            query_evolution = """
            SELECT 
                annee, mois,
                SUM(nb_demandes) as total_demandes,
                AVG(satisfaction_moyenne) as satisfaction_moyenne
            FROM statistiques_mensuelles 
            GROUP BY annee, mois 
            ORDER BY annee, mois;
            """
            df_evolution = pd.read_sql_query(query_evolution, conn)
            console.print(f"      🔍 [DEBUG] Requête exécutée. Nombre de lignes: {len(df_evolution)}")
            
            # Étape 2: Validation des données
            if df_evolution.empty:
                console.print("      ⚠️ Aucune donnée trouvée pour l'évolution mensuelle")
                return
            
            console.print(f"      🔍 [DEBUG] Colonnes disponibles: {list(df_evolution.columns)}")
            console.print(f"      🔍 [DEBUG] Types de données: {df_evolution.dtypes.to_dict()}")
            console.print(f"      🔍 [DEBUG] Premières lignes:")
            for i, row in df_evolution.head(3).iterrows():
                console.print(f"         Ligne {i}: annee={row['annee']}, mois={row['mois']}, total_demandes={row['total_demandes']}, satisfaction={row['satisfaction_moyenne']}")
            
            # Étape 3: Conversion des dates
            console.print("      🔍 [DEBUG] Conversion des dates...")
            try:
                # Vérifier et nettoyer les données avant conversion
                console.print(f"      🔍 [DEBUG] Vérification des valeurs NaN - annee: {df_evolution['annee'].isna().sum()}, mois: {df_evolution['mois'].isna().sum()}")
                
                # Supprimer les lignes avec des valeurs NaN dans annee ou mois
                df_evolution_clean = df_evolution.dropna(subset=['annee', 'mois'])
                console.print(f"      🔍 [DEBUG] Lignes après nettoyage: {len(df_evolution_clean)} (supprimées: {len(df_evolution) - len(df_evolution_clean)})")
                
                if df_evolution_clean.empty:
                    console.print("      ⚠️ Aucune donnée valide après nettoyage")
                    return
                
                # Convertir en entiers pour éviter les problèmes de type
                df_evolution_clean['annee'] = df_evolution_clean['annee'].astype(int)
                df_evolution_clean['mois'] = df_evolution_clean['mois'].astype(int)
                
                # Méthode alternative: créer la date en utilisant une approche plus robuste
                df_evolution_clean['date'] = pd.to_datetime(
                    df_evolution_clean['annee'].astype(str) + '-' + 
                    df_evolution_clean['mois'].astype(str).str.zfill(2) + '-01'
                )
                
                # Mettre à jour le DataFrame principal
                df_evolution = df_evolution_clean
                
                console.print(f"      🔍 [DEBUG] Dates converties. Première date: {df_evolution['date'].iloc[0]}, Dernière date: {df_evolution['date'].iloc[-1]}")
            except Exception as date_error:
                console.print(f"      ❌ [ERROR] Erreur lors de la conversion des dates: {str(date_error)}")
                console.print(f"      🔍 [DEBUG] Traceback conversion dates:")
                console.print(f"         {traceback.format_exc()}")
                raise
            
            # Étape 4: Création de la figure
            console.print("      🔍 [DEBUG] Création de la figure Plotly...")
            try:
                fig_evolution = go.Figure()
                console.print("      🔍 [DEBUG] Figure créée avec succès")
            except Exception as fig_error:
                console.print(f"      ❌ [ERROR] Erreur lors de la création de la figure: {str(fig_error)}")
                console.print(f"      🔍 [DEBUG] Traceback création figure:")
                console.print(f"         {traceback.format_exc()}")
                raise
            
            # Étape 5: Ajout de la première trace (demandes)
            console.print("      🔍 [DEBUG] Ajout de la trace des demandes...")
            try:
                trace_data_1 = {
                    'x': df_evolution['date'].tolist(),
                    'y': df_evolution['total_demandes'].tolist(),
                    'name': "Nombre de demandes",
                    'line': dict(color='blue'),
                    'yaxis': 'y'
                }
                console.print(f"      🔍 [DEBUG] Données trace 1 - X: {len(trace_data_1['x'])} points, Y: {len(trace_data_1['y'])} points")
                console.print(f"      🔍 [DEBUG] Exemple X: {trace_data_1['x'][:2]}")
                console.print(f"      🔍 [DEBUG] Exemple Y: {trace_data_1['y'][:2]}")
                
                fig_evolution.add_trace(go.Scatter(**trace_data_1))
                console.print("      🔍 [DEBUG] Première trace ajoutée avec succès")
            except Exception as trace1_error:
                console.print(f"      ❌ [ERROR] Erreur lors de l'ajout de la première trace: {str(trace1_error)}")
                console.print(f"      🔍 [DEBUG] Traceback première trace:")
                console.print(f"         {traceback.format_exc()}")
                raise
            
            # Étape 6: Ajout de la deuxième trace (satisfaction)
            console.print("      🔍 [DEBUG] Ajout de la trace de satisfaction...")
            try:
                trace_data_2 = {
                    'x': df_evolution['date'].tolist(),
                    'y': df_evolution['satisfaction_moyenne'].tolist(),
                    'name': "Satisfaction moyenne",
                    'line': dict(color='red'),
                    'yaxis': 'y2'
                }
                console.print(f"      🔍 [DEBUG] Données trace 2 - X: {len(trace_data_2['x'])} points, Y: {len(trace_data_2['y'])} points")
                console.print(f"      🔍 [DEBUG] Exemple X: {trace_data_2['x'][:2]}")
                console.print(f"      🔍 [DEBUG] Exemple Y: {trace_data_2['y'][:2]}")
                
                fig_evolution.add_trace(go.Scatter(**trace_data_2))
                console.print("      🔍 [DEBUG] Deuxième trace ajoutée avec succès")
            except Exception as trace2_error:
                console.print(f"      ❌ [ERROR] Erreur lors de l'ajout de la deuxième trace: {str(trace2_error)}")
                console.print(f"      🔍 [DEBUG] Traceback deuxième trace:")
                console.print(f"         {traceback.format_exc()}")
                raise
            
            # Étape 7: Configuration du layout
            console.print("      🔍 [DEBUG] Configuration du layout...")
            try:
                layout_config = {
                    'title': "Évolution mensuelle des demandes et satisfaction",
                    'xaxis': dict(title="Mois"),
                    'yaxis': dict(
                        title="Nombre de demandes",
                        side="left"
                    ),
                    'yaxis2': dict(
                        title="Satisfaction moyenne (/5)",
                        side="right",
                        overlaying="y"
                    )
                }
                console.print(f"      🔍 [DEBUG] Configuration layout: {layout_config}")
                
                fig_evolution.update_layout(**layout_config)
                console.print("      🔍 [DEBUG] Layout configuré avec succès")
            except Exception as layout_error:
                console.print(f"      ❌ [ERROR] Erreur lors de la configuration du layout: {str(layout_error)}")
                console.print(f"      🔍 [DEBUG] Traceback layout:")
                console.print(f"         {traceback.format_exc()}")
                raise
            
            # Étape 8: Sauvegarde du fichier
            console.print("      🔍 [DEBUG] Sauvegarde du fichier HTML...")
            try:
                output_path = charts_dir / "evolution_demandes.html"
                fig_evolution.write_html(output_path)
                console.print(f"      🔍 [DEBUG] Fichier sauvegardé: {output_path}")
            except Exception as save_error:
                console.print(f"      ❌ [ERROR] Erreur lors de la sauvegarde: {str(save_error)}")
                console.print(f"      🔍 [DEBUG] Traceback sauvegarde:")
                console.print(f"         {traceback.format_exc()}")
                raise
                
        except Exception as evolution_error:
            console.print(f"      ❌ [ERROR] Erreur dans la création du graphique d'évolution: {str(evolution_error)}")
            console.print(f"      🔍 [DEBUG] Traceback complet:")
            console.print(f"         {traceback.format_exc()}")
            raise
        
        # 2. Graphique en secteurs des services
        console.print("      🥧 Répartition des services...")
        query_services = """
        SELECT type_service, COUNT(*) as nb_demandes
        FROM demandes 
        GROUP BY type_service 
        ORDER BY nb_demandes DESC;
        """
        df_services = pd.read_sql_query(query_services, conn)
        
        fig_services = px.pie(df_services, values='nb_demandes', names='type_service',
                             title="Répartition des demandes par type de service")
        fig_services.write_html(charts_dir / "repartition_services.html")
        
        # 3. Graphique en barres des temps d'attente par canal
        console.print("      📊 Temps d'attente par canal...")
        query_attente = """
        SELECT 
            ta.canal_utilise,
            AVG(ta.temps_attente_minutes) as temps_attente_moyen,
            COUNT(*) as nb_demandes
        FROM temps_attente ta
        JOIN demandes d ON ta.demande_id = d.id
        GROUP BY ta.canal_utilise
        ORDER BY temps_attente_moyen;
        """
        df_attente = pd.read_sql_query(query_attente, conn)
        
        fig_attente = px.bar(df_attente, x='canal_utilise', y='temps_attente_moyen',
                            title="Temps d'attente moyen par canal de communication",
                            labels={'canal_utilise': 'Canal', 'temps_attente_moyen': 'Temps d\'attente (min)'})
        fig_attente.write_html(charts_dir / "temps_attente_canal.html")
        
        # 4. Heatmap des performances par région
        console.print("      🗺️ Performance par région...")
        query_regions = """
        SELECT 
            mfs.region,
            COUNT(d.id) as nb_demandes,
            AVG(d.satisfaction_score) as satisfaction_moyenne,
            AVG(d.duree_traitement) as duree_moyenne
        FROM maisons_france_services mfs
        LEFT JOIN demandes d ON mfs.id = d.maison_fs_id
        GROUP BY mfs.region;
        """
        df_regions = pd.read_sql_query(query_regions, conn)
        
        fig_regions = px.scatter(df_regions, x='duree_moyenne', y='satisfaction_moyenne',
                               size='nb_demandes', hover_name='region',
                               title="Performance par région (taille = nombre de demandes)",
                               labels={'duree_moyenne': 'Durée moyenne (min)', 
                                      'satisfaction_moyenne': 'Satisfaction moyenne'})
        fig_regions.write_html(charts_dir / "performance_regions.html")
        
        # 5. Distribution des conseillers par spécialité
        console.print("      👥 Répartition des conseillers...")
        query_conseillers = """
        SELECT 
            specialite,
            COUNT(*) as nb_conseillers,
            niveau_experience
        FROM conseillers 
        WHERE statut = 'actif'
        GROUP BY specialite, niveau_experience
        ORDER BY specialite, niveau_experience;
        """
        df_conseillers = pd.read_sql_query(query_conseillers, conn)
        
        fig_conseillers = px.bar(df_conseillers, x='specialite', y='nb_conseillers', 
                               color='niveau_experience',
                               title="Répartition des conseillers par spécialité et niveau d'expérience")
        fig_conseillers.update_xaxes(tickangle=45)
        fig_conseillers.write_html(charts_dir / "conseillers_specialite.html")
        
        # 6. Timeline des incidents techniques
        console.print("      ⚠️ Timeline des incidents...")
        query_incidents = """
        SELECT 
            DATE(date_debut) as date_incident,
            COUNT(*) as nb_incidents,
            AVG(duree_minutes) as duree_moyenne,
            type_incident
        FROM incidents_techniques 
        GROUP BY DATE(date_debut), type_incident
        ORDER BY date_incident;
        """
        df_incidents = pd.read_sql_query(query_incidents, conn)
        
        fig_incidents = px.scatter(df_incidents, x='date_incident', y='nb_incidents',
                                 size='duree_moyenne', color='type_incident',
                                 title="Timeline des incidents techniques",
                                 labels={'date_incident': 'Date', 'nb_incidents': 'Nombre d\'incidents'})
        fig_incidents.write_html(charts_dir / "timeline_incidents.html")
        
        # 7. Corrélation temps d'attente vs satisfaction
        console.print("      🔗 Corrélation attente-satisfaction...")
        query_correlation = """
        SELECT 
            ta.temps_attente_minutes,
            d.satisfaction_score,
            ta.canal_utilise
        FROM temps_attente ta
        JOIN demandes d ON ta.demande_id = d.id
        LIMIT 1000;
        """
        df_correlation = pd.read_sql_query(query_correlation, conn)
        
        fig_correlation = px.scatter(df_correlation, x='temps_attente_minutes', y='satisfaction_score',
                                   color='canal_utilise', trendline="ols",
                                   title="Corrélation entre temps d'attente et satisfaction",
                                   labels={'temps_attente_minutes': 'Temps d\'attente (min)', 
                                          'satisfaction_score': 'Score de satisfaction'})
        fig_correlation.write_html(charts_dir / "correlation_attente_satisfaction.html")
        
        # 8. Dashboard combiné
        console.print("      📋 Dashboard global...")
        fig_dashboard = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Demandes par mois", "Services populaires", "Temps d'attente", "Satisfaction régionale"),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Ajout des graphiques au dashboard
        fig_dashboard.add_trace(
            go.Scatter(x=df_evolution['date'], y=df_evolution['total_demandes'], name="Demandes"),
            row=1, col=1
        )
        
        fig_dashboard.add_trace(
            go.Pie(labels=df_services['type_service'][:5], values=df_services['nb_demandes'][:5], name="Services"),
            row=1, col=2
        )
        
        fig_dashboard.add_trace(
            go.Bar(x=df_attente['canal_utilise'], y=df_attente['temps_attente_moyen'], name="Attente"),
            row=2, col=1
        )
        
        fig_dashboard.add_trace(
            go.Scatter(x=df_regions['duree_moyenne'], y=df_regions['satisfaction_moyenne'], 
                      mode='markers', name="Régions"),
            row=2, col=2
        )
        
        fig_dashboard.update_layout(height=800, showlegend=False, title_text="Dashboard France Services")
        fig_dashboard.write_html(charts_dir / "dashboard_global.html")
        
        console.print(f"   ✅ {8} graphiques générés dans {charts_dir}/")
        console.print("      📁 Fichiers créés:")
        console.print("         - evolution_demandes.html")
        console.print("         - repartition_services.html") 
        console.print("         - temps_attente_canal.html")
        console.print("         - performance_regions.html")
        console.print("         - conseillers_specialite.html")
        console.print("         - timeline_incidents.html")
        console.print("         - correlation_attente_satisfaction.html")
        console.print("         - dashboard_global.html")
        
    except ImportError as import_error:
        console.print("   ⚠️ Plotly non disponible - graphiques non générés")
        console.print("   💡 Pour installer: poetry add plotly ou pip install plotly")
        console.print(f"   🔍 [DEBUG] Détails de l'erreur d'import: {str(import_error)}")
    except Exception as e:
        console.print(f"   ❌ Erreur lors de la génération des graphiques: {str(e)}")
        console.print("   🔍 [DEBUG] Informations détaillées sur l'erreur:")
        console.print(f"      Type d'erreur: {type(e).__name__}")
        console.print(f"      Message: {str(e)}")
        console.print("   🔍 [DEBUG] Stack trace complet:")
        import traceback
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                console.print(f"      {line}")
        console.print("   💡 Les analyses textuelles restent disponibles ci-dessus")


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

            # 4. Analyse des conseillers par spécialité
            console.print("\n🔍 4. Répartition des conseillers par spécialité:")
            query_conseillers = """
            SELECT 
                specialite,
                COUNT(*) as nb_conseillers,
                ROUND(AVG(CASE 
                    WHEN niveau_experience = 'junior' THEN 1
                    WHEN niveau_experience = 'senior' THEN 2
                    WHEN niveau_experience = 'expert' THEN 3
                END), 2) as niveau_moyen
            FROM conseillers 
            WHERE statut = 'actif'
            GROUP BY specialite 
            ORDER BY nb_conseillers DESC;
            """
            conseillers_stats = pd.read_sql_query(query_conseillers, conn)
            for _, row in conseillers_stats.iterrows():
                console.print(f"   👨‍💼 {row['specialite']}: {int(row['nb_conseillers'])} conseillers (niveau moyen: {row['niveau_moyen']}/3)")

            # 5. Analyse des horaires d'ouverture
            console.print("\n🔍 5. Analyse des horaires d'ouverture:")
            query_horaires = """
            SELECT 
                jour_semaine,
                ROUND(AVG(heure_ouverture), 1) as heure_ouverture_moyenne,
                ROUND(AVG(heure_fermeture), 1) as heure_fermeture_moyenne,
                ROUND(AVG(heure_fermeture - heure_ouverture), 1) as duree_moyenne,
                COUNT(CASE WHEN fermeture_exceptionnelle = true THEN 1 END) as nb_fermetures_exceptionnelles
            FROM plannings 
            GROUP BY jour_semaine 
            ORDER BY 
                CASE jour_semaine 
                    WHEN 'Monday' THEN 1 
                    WHEN 'Tuesday' THEN 2 
                    WHEN 'Wednesday' THEN 3 
                    WHEN 'Thursday' THEN 4 
                    WHEN 'Friday' THEN 5 
                END;
            """
            horaires_stats = pd.read_sql_query(query_horaires, conn)
            for _, row in horaires_stats.iterrows():
                console.print(f"   📅 {row['jour_semaine']}: {row['heure_ouverture_moyenne']}h-{row['heure_fermeture_moyenne']}h ({row['duree_moyenne']}h) - {int(row['nb_fermetures_exceptionnelles'])} fermetures exceptionnelles")

            # 6. Analyse des incidents techniques
            console.print("\n🔍 6. Analyse des incidents techniques:")
            query_incidents = """
            SELECT 
                type_incident,
                COUNT(*) as nb_incidents,
                ROUND(AVG(duree_minutes), 1) as duree_moyenne_min,
                ROUND(AVG(impact_usagers), 1) as impact_moyen_usagers,
                COUNT(CASE WHEN gravite = 'haute' THEN 1 END) as nb_incidents_graves
            FROM incidents_techniques 
            GROUP BY type_incident 
            ORDER BY nb_incidents DESC;
            """
            incidents_stats = pd.read_sql_query(query_incidents, conn)
            for _, row in incidents_stats.iterrows():
                console.print(f"   ⚠️ {row['type_incident']}: {int(row['nb_incidents'])} incidents ({row['duree_moyenne_min']} min, impact: {row['impact_moyen_usagers']} usagers, {int(row['nb_incidents_graves'])} graves)")

            # 7. Performance par région
            console.print("\n🔍 7. Performance par région:")
            query_regions = """
            SELECT 
                mfs.region,
                COUNT(DISTINCT mfs.id) as nb_maisons,
                COUNT(d.id) as nb_demandes_totales,
                ROUND(AVG(d.satisfaction_score), 2) as satisfaction_moyenne,
                ROUND(AVG(d.duree_traitement), 1) as duree_traitement_moyenne
            FROM maisons_france_services mfs
            LEFT JOIN demandes d ON mfs.id = d.maison_fs_id
            GROUP BY mfs.region 
            ORDER BY satisfaction_moyenne DESC
            LIMIT 5;
            """
            regions_stats = pd.read_sql_query(query_regions, conn)
            for _, row in regions_stats.iterrows():
                console.print(f"   🗺️ {row['region']}: {int(row['nb_maisons'])} maisons, {int(row['nb_demandes_totales'])} demandes (satisfaction: {row['satisfaction_moyenne']}/5, durée: {row['duree_traitement_moyenne']} min)")

            # 8. Analyse des services détaillés
            console.print("\n🔍 8. Services les plus complexes:")
            query_services_complexes = """
            SELECT 
                service,
                sous_service,
                complexite,
                volume_mensuel_moyen,
                duree_moyenne_traitement,
                satisfaction_moyenne
            FROM services_details 
            WHERE complexite = 'complexe'
            ORDER BY duree_moyenne_traitement DESC;
            """
            services_complexes = pd.read_sql_query(query_services_complexes, conn)
            for _, row in services_complexes.iterrows():
                console.print(f"   🔧 {row['service']} - {row['sous_service']}: {int(row['volume_mensuel_moyen'])} demandes/mois ({int(row['duree_moyenne_traitement'])} min, satisfaction: {row['satisfaction_moyenne']}/5)")

            # 9. Corrélations avancées
            console.print("\n🔍 9. Analyses de corrélation:")
            
            # Corrélation entre temps d'attente et satisfaction
            query_correlation = """
            SELECT 
                CASE 
                    WHEN ta.temps_attente_minutes <= 10 THEN '≤ 10 min'
                    WHEN ta.temps_attente_minutes <= 20 THEN '11-20 min'
                    WHEN ta.temps_attente_minutes <= 30 THEN '21-30 min'
                    ELSE '> 30 min'
                END as tranche_attente,
                COUNT(*) as nb_demandes,
                ROUND(AVG(d.satisfaction_score), 2) as satisfaction_moyenne
            FROM temps_attente ta
            JOIN demandes d ON ta.demande_id = d.id
            GROUP BY 
                CASE 
                    WHEN ta.temps_attente_minutes <= 10 THEN '≤ 10 min'
                    WHEN ta.temps_attente_minutes <= 20 THEN '11-20 min'
                    WHEN ta.temps_attente_minutes <= 30 THEN '21-30 min'
                    ELSE '> 30 min'
                END
            ORDER BY satisfaction_moyenne DESC;
            """
            correlation_stats = pd.read_sql_query(query_correlation, conn)
            console.print("   📊 Impact du temps d'attente sur la satisfaction:")
            for _, row in correlation_stats.iterrows():
                console.print(f"      ⏱️ {row['tranche_attente']}: {int(row['nb_demandes'])} demandes (satisfaction: {row['satisfaction_moyenne']}/5)")

            # 10. Statistiques des nouvelles tables (résumé)
            console.print("\n🔍 10. Résumé des données:")
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

            # 11. Génération des graphiques
            console.print("\n📈 Génération des graphiques interactifs...")
            try:
                generate_interactive_charts(conn, console)
            except Exception as e:
                console.print(f"   ❌ Erreur lors de la génération des graphiques: {str(e)}")
                console.print("   💡 Les analyses textuelles restent disponibles ci-dessus")

            # 12. Résumé des fonctionnalités
            console.print("\n" + "="*60)
            console.print("📋 RÉSUMÉ DES ANALYSES DISPONIBLES")
            console.print("="*60)
            console.print("✅ Analyses textuelles (10 sections):")
            console.print("   1. Évolution des demandes par mois")
            console.print("   2. Top 5 des services les plus demandés")
            console.print("   3. Temps d'attente moyen par canal")
            console.print("   4. Répartition des conseillers par spécialité")
            console.print("   5. Analyse des horaires d'ouverture")
            console.print("   6. Analyse des incidents techniques")
            console.print("   7. Performance par région")
            console.print("   8. Services les plus complexes")
            console.print("   9. Analyses de corrélation")
            console.print("   10. Résumé des données")
            
            console.print("\n📊 Visualisations interactives (8 graphiques):")
            console.print("   • Évolution mensuelle des demandes")
            console.print("   • Répartition des services (camembert)")
            console.print("   • Temps d'attente par canal (barres)")
            console.print("   • Performance régionale (scatter)")
            console.print("   • Distribution des conseillers")
            console.print("   • Timeline des incidents")
            console.print("   • Corrélation attente-satisfaction")
            console.print("   • Dashboard global combiné")
            
            console.print("\n🗂️ Tables analysées (9 au total):")
            console.print("   📍 maisons_france_services - Localisation et caractéristiques")
            console.print("   👥 usagers - Profils des utilisateurs")
            console.print("   📄 demandes - Requêtes de service")
            console.print("   👨‍💼 conseillers - Personnel et spécialités")
            console.print("   📅 plannings - Horaires et disponibilités")
            console.print("   📊 statistiques_mensuelles - Métriques temporelles")
            console.print("   ⏱️ temps_attente - Performance d'accueil")
            console.print("   🔧 services_details - Catalogue des services")
            console.print("   ⚠️ incidents_techniques - Problèmes et résolutions")

        console.print(Panel.fit(
            "🎉 Démonstration complète ! Base de données analysée avec succès.\n" +
            "📁 Consultez data/charts/ pour les visualisations interactives.",
            style="bold green"
        ))

    except Exception as e:
        console.print("\n[bold red]❌ Erreur lors de l'exécution de la démonstration:[/bold red]")
        console.print(f"   {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
