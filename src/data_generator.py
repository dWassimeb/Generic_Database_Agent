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

    def generate_all_data(self):
        """Générer tous les jeux de données"""
        from rich.console import Console
        from rich.progress import Progress

        console = Console()

        with Progress() as progress:
            task = progress.add_task("[green]Génération des données...", total=4)

            # Maisons France Services
            console.print("📍 Génération des maisons France Services...")
            self.generate_maisons_france_services()
            progress.update(task, advance=1)

            # Usagers
            console.print("👥 Génération des usagers...")
            self.generate_usagers()
            progress.update(task, advance=1)

            # Demandes
            console.print("📄 Génération des demandes...")
            self.generate_demandes()
            progress.update(task, advance=1)

            console.print("✅ Tous les fichiers CSV ont été générés avec succès!")
            console.print(f"📂 Fichiers sauvegardés dans : {self.output_dir}")