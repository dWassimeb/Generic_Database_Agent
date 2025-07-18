# src/data_generator.py
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
from pathlib import Path


class FranceServicesDataGenerator:
    def __init__(self, locale='fr_FR'):
        self.fake = Faker(locale)
        self.output_dir = Path("data/csv")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Données de référence
        self.regions = [
            'Auvergne-Rhône-Alpes', 'Bretagne', 'Centre-Val de Loire', 'Corse',
            'Grand Est', 'Hauts-de-France', 'Île-de-France', 'Normandie',
            'Nouvelle-Aquitaine', 'Occitanie', 'Pays de la Loire', 'Provence-Alpes-Côte d\'Azur'
        ]

        self.services_base = [
            'emploi', 'retraite', 'famille', 'social', 'sante', 'logement',
            'energie', 'services_postaux', 'acces_droit'
        ]

        self.types_structure = ['collectivite', 'association', 'entreprise', 'gip']

    def generate_maisons_france_services(self, n_maisons=300):
        """Générer les données des maisons France Services"""
        data = []

        for i in range(n_maisons):
            services_disponibles = '|'.join(
                random.sample(self.services_base, random.randint(5, 9))
            )

            data.append({
                'id': i + 1,
                'nom': f"France Services {self.fake.city()}",
                'adresse': self.fake.address().replace('\n', ' '),
                'code_postal': self.fake.postcode(),
                'ville': self.fake.city(),
                'departement': self.fake.department_name(),
                'region': random.choice(self.regions),
                'latitude': float(self.fake.latitude()),
                'longitude': float(self.fake.longitude()),
                'type_structure': random.choice(self.types_structure),
                'date_ouverture': self.fake.date_between(start_date='-5y', end_date='today'),
                'nb_conseillers': random.randint(1, 8),
                'services_disponibles': services_disponibles,
                'population_desservie': random.randint(5000, 50000),
                'statut': 'active'
            })

        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'maisons_france_services.csv', index=False)
        return df

    def generate_usagers(self, n_usagers=5000):
        """Générer les données des usagers"""
        data = []

        situations_familiales = ['celibataire', 'marie', 'divorce', 'veuf', 'concubinage']
        niveaux_numeriques = ['debutant', 'intermediaire', 'avance']
        frequences_visite = ['regulier', 'occasionnel', 'nouveau']

        for i in range(n_usagers):
            data.append({
                'id': i + 1,
                'age': random.randint(18, 85),
                'genre': random.choice(['M', 'F']),
                'situation_familiale': random.choice(situations_familiales),
                'niveau_numerique': random.choice(niveaux_numeriques),
                'code_postal': self.fake.postcode(),
                'ville': self.fake.city(),
                'date_inscription': self.fake.date_between(start_date='-2y', end_date='today'),
                'frequence_visite': random.choice(frequences_visite)
            })

        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'usagers.csv', index=False)
        return df

    def generate_demandes(self, n_demandes=15000, n_usagers=5000, n_maisons=300):
        """Générer les données des demandes"""
        data = []

        organismes = ['pole_emploi', 'caf', 'cnav', 'cpam', 'ants', 'msa', 'la_poste', 'justice']
        canaux = ['physique', 'telephone', 'visio', 'numerique']
        complexites = ['simple', 'moyen', 'complexe']

        for i in range(n_demandes):
            data.append({
                'id': i + 1,
                'usager_id': random.randint(1, n_usagers),
                'maison_fs_id': random.randint(1, n_maisons),
                'date_demande': self.fake.date_time_between(start_date='-1y', end_date='now'),
                'type_service': random.choice(self.services_base),
                'organisme_concerne': random.choice(organismes),
                'canal': random.choice(canaux),
                'duree_traitement': random.randint(15, 120),
                'satisfaction_score': random.randint(1, 5),
                'resolu': random.choice([True, False]),
                'conseiller_id': random.randint(1, 1500),
                'complexite': random.choice(complexites),
                'suivi_necessaire': random.choice([True, False])
            })

        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'demandes.csv', index=False)
        return df
        
    def generate_conseillers(self, n_maisons=300):
        """Générer les données des conseillers"""
        data = []
        conseiller_id = 1
        
        # Spécialités possibles
        specialites = ['emploi', 'retraite', 'famille', 'social', 'sante', 'logement', 'energie', 'juridique']
        
        for maison_id in range(1, n_maisons + 1):
            # Nombre de conseillers par maison (cohérent avec les maisons)
            nb_conseillers = random.randint(2, 8)
            
            for _ in range(nb_conseillers):
                data.append({
                    'id': conseiller_id,
                    'nom': self.fake.last_name(),
                    'prenom': self.fake.first_name(),
                    'maison_fs_id': maison_id,
                    'specialite': random.choice(specialites),
                    'date_embauche': self.fake.date_between(start_date='-5y', end_date='today'),
                    'temps_travail': random.choice(['temps_plein', 'temps_partiel']),
                    'niveau_experience': random.choice(['junior', 'senior', 'expert']),
                    'statut': 'actif'
                })
                conseiller_id += 1
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'conseillers.csv', index=False)
        return df
        
    def generate_plannings(self, n_maisons=300):
        """Générer les données de planning hebdomadaire"""
        data = []
        
        # Générer pour les 12 dernières semaines
        start_date = datetime.now() - timedelta(weeks=12)
        
        for week in range(12):
            week_start = start_date + timedelta(weeks=week)
            
            for maison_id in range(1, n_maisons + 1):
                # Heures d'ouverture par jour (lundi à vendredi)
                for day in range(5):  # 0-4 pour lundi-vendredi
                    current_date = week_start + timedelta(days=day)
                    
                    # Variations d'horaires
                    if day in [0, 1, 2, 3]:  # Lundi à jeudi
                        heures_ouverture = random.choice([8, 9, 8.5])
                        heures_fermeture = random.choice([17, 18, 17.5])
                    else:  # Vendredi
                        heures_ouverture = random.choice([8, 9])
                        heures_fermeture = random.choice([16, 17])
                    
                    data.append({
                        'id': len(data) + 1,
                        'maison_fs_id': maison_id,
                        'date': current_date.date(),
                        'jour_semaine': current_date.strftime('%A'),
                        'heure_ouverture': heures_ouverture,
                        'heure_fermeture': heures_fermeture,
                        'nb_conseillers_prevus': random.randint(1, 5),
                        'nb_conseillers_presents': random.randint(1, 5),
                        'fermeture_exceptionnelle': random.choice([True, False]) if random.random() < 0.05 else False
                    })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'plannings.csv', index=False)
        return df

    def generate_statistiques_mensuelles(self, n_maisons=300):
        """Générer les statistiques mensuelles par maison"""
        data = []
        
        # Générer pour les 12 derniers mois
        for month_offset in range(12):
            date_stat = datetime.now() - timedelta(days=30 * month_offset)
            
            for maison_id in range(1, n_maisons + 1):
                # Variations saisonnières
                facteur_saison = 1.0
                if date_stat.month in [1, 2, 3]:  # Début d'année, plus de demandes
                    facteur_saison = 1.3
                elif date_stat.month in [7, 8]:  # Été, moins de demandes
                    facteur_saison = 0.7
                
                base_demandes = random.randint(100, 500)
                nb_demandes = int(base_demandes * facteur_saison)
                
                data.append({
                    'id': len(data) + 1,
                    'maison_fs_id': maison_id,
                    'mois': date_stat.month,
                    'annee': date_stat.year,
                    'nb_demandes': nb_demandes,
                    'nb_demandes_resolues': int(nb_demandes * random.uniform(0.8, 0.95)),
                    'temps_moyen_resolution': random.randint(20, 90),
                    'satisfaction_moyenne': round(random.uniform(3.5, 4.8), 2),
                    'nb_usagers_uniques': random.randint(80, 300),
                    'nb_nouveaux_usagers': random.randint(10, 50),
                    'taux_retour_usagers': round(random.uniform(0.3, 0.7), 2)
                })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'statistiques_mensuelles.csv', index=False)
        return df

    def generate_temps_attente(self, n_demandes=15000):
        """Générer les données de temps d'attente"""
        data = []
        
        for demande_id in range(1, n_demandes + 1):
            # Temps d'attente varie selon le canal et l'heure
            heure_demande = random.randint(8, 18)
            
            if heure_demande in [12, 13, 14]:  # Pause déjeuner
                temps_attente = random.randint(15, 45)
            elif heure_demande in [9, 10, 11]:  # Matin chargé
                temps_attente = random.randint(5, 25)
            else:  # Après-midi
                temps_attente = random.randint(3, 20)
            
            data.append({
                'id': len(data) + 1,
                'demande_id': demande_id,
                'temps_attente_minutes': temps_attente,
                'heure_demande': heure_demande,
                'jour_semaine': random.choice(['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']),
                'canal_utilise': random.choice(['physique', 'telephone', 'visio', 'numerique']),
                'priorite': random.choice(['normale', 'urgente', 'faible'])
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'temps_attente.csv', index=False)
        return df

    def generate_services_details(self):
        """Générer les détails des services avec volumes"""
        data = []
        
        services_details = [
            {'service': 'emploi', 'sous_service': 'inscription_pole_emploi', 'complexite': 'simple'},
            {'service': 'emploi', 'sous_service': 'actualisation_situation', 'complexite': 'simple'},
            {'service': 'emploi', 'sous_service': 'recherche_formation', 'complexite': 'moyen'},
            {'service': 'retraite', 'sous_service': 'simulation_retraite', 'complexite': 'moyen'},
            {'service': 'retraite', 'sous_service': 'dossier_retraite', 'complexite': 'complexe'},
            {'service': 'famille', 'sous_service': 'caf_allocations', 'complexite': 'moyen'},
            {'service': 'famille', 'sous_service': 'prime_naissance', 'complexite': 'simple'},
            {'service': 'social', 'sous_service': 'rsa', 'complexite': 'complexe'},
            {'service': 'social', 'sous_service': 'aide_logement', 'complexite': 'moyen'},
            {'service': 'sante', 'sous_service': 'carte_vitale', 'complexite': 'simple'},
            {'service': 'sante', 'sous_service': 'remboursement_soins', 'complexite': 'moyen'},
            {'service': 'logement', 'sous_service': 'demande_HLM', 'complexite': 'complexe'},
            {'service': 'energie', 'sous_service': 'cheque_energie', 'complexite': 'simple'},
            {'service': 'services_postaux', 'sous_service': 'colis_recommande', 'complexite': 'simple'},
            {'service': 'acces_droit', 'sous_service': 'aide_juridictionnelle', 'complexite': 'complexe'}
        ]
        
        for i, service_detail in enumerate(services_details):
            # Volume mensuel moyen pour chaque service
            volume_base = random.randint(50, 500)
            
            data.append({
                'id': i + 1,
                'service': service_detail['service'],
                'sous_service': service_detail['sous_service'],
                'complexite': service_detail['complexite'],
                'volume_mensuel_moyen': volume_base,
                'duree_moyenne_traitement': random.randint(15, 120),
                'taux_resolution': round(random.uniform(0.7, 0.95), 2),
                'satisfaction_moyenne': round(random.uniform(3.2, 4.7), 2),
                'formation_requise': random.choice(['base', 'intermediaire', 'avancee'])
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'services_details.csv', index=False)
        return df

    def generate_incidents_techniques(self, n_maisons=300):
        """Générer les incidents techniques"""
        data = []
        
        types_incidents = [
            'panne_internet', 'probleme_materiel', 'logiciel_indisponible',
            'coupure_electricite', 'probleme_telephonie', 'maintenance_programmee'
        ]
        
        # Générer des incidents sur les 6 derniers mois
        start_date = datetime.now() - timedelta(days=180)
        
        for maison_id in range(1, n_maisons + 1):
            # Nombre d'incidents par maison (0 à 5)
            nb_incidents = random.randint(0, 5)
            
            for _ in range(nb_incidents):
                incident_start = self.fake.date_time_between(start_date=start_date, end_date='now')
                duree = random.randint(30, 480)  # 30 min à 8h
                
                data.append({
                    'id': len(data) + 1,
                    'maison_fs_id': maison_id,
                    'type_incident': random.choice(types_incidents),
                    'date_debut': incident_start,
                    'duree_minutes': duree,
                    'impact_usagers': random.randint(0, 50),
                    'resolu': True,
                    'gravite': random.choice(['faible', 'moyenne', 'haute'])
                })
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / 'incidents_techniques.csv', index=False)
        return df

    def generate_all_data(self):
        """Générer tous les jeux de données (version enrichie)"""
        from rich.console import Console
        from rich.progress import Progress

        console = Console()

        with Progress() as progress:
            task = progress.add_task("[green]Génération des données...", total=8)

            # Données existantes
            console.print("📍 Génération des maisons France Services...")
            self.generate_maisons_france_services()
            progress.update(task, advance=1)

            console.print("👥 Génération des usagers...")
            self.generate_usagers()
            progress.update(task, advance=1)

            console.print("📄 Génération des demandes...")
            self.generate_demandes()
            progress.update(task, advance=1)

            # Nouvelles données
            console.print("👨‍💼 Génération des conseillers...")
            self.generate_conseillers()
            progress.update(task, advance=1)

            console.print("📅 Génération des plannings...")
            self.generate_plannings()
            progress.update(task, advance=1)

            console.print("📊 Génération des statistiques mensuelles...")
            self.generate_statistiques_mensuelles()
            progress.update(task, advance=1)

            console.print("⏱️ Génération des temps d'attente...")
            self.generate_temps_attente()
            progress.update(task, advance=1)

            console.print("🔧 Génération des services détaillés...")
            self.generate_services_details()
            progress.update(task, advance=1)

            console.print("⚠️ Génération des incidents techniques...")
            self.generate_incidents_techniques()
            progress.update(task, advance=1)

            console.print("✅ Tous les fichiers CSV ont été générés avec succès!")
            console.print(f"📂 Fichiers sauvegardés dans : {self.output_dir}")