import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('fr_FR')


def create_data_directory():
    """Créer le répertoire data s'il n'existe pas"""
    if not os.path.exists('../data'):
        os.makedirs('../data')


def generate_maisons_france_services_csv():
    """Générer le CSV des maisons France Services"""
    regions = ['Auvergne-Rhône-Alpes', 'Bretagne', 'Centre-Val de Loire', 'Corse',
               'Grand Est', 'Hauts-de-France', 'Île-de-France', 'Normandie',
               'Nouvelle-Aquitaine', 'Occitanie', 'Pays de la Loire', 'Provence-Alpes-Côte d\'Azur']

    types_structure = ['collectivite', 'association', 'entreprise', 'gip']
    services_base = ['emploi', 'retraite', 'famille', 'social', 'sante', 'logement',
                     'energie', 'services_postaux', 'acces_droit']

    data = []
    for i in range(300):
        services_disponibles = '|'.join(random.sample(services_base, random.randint(5, 9)))

        data.append({
            'id': i + 1,
            'nom': f"France Services {fake.city()}",
            'adresse': fake.address().replace('\n', ' '),
            'code_postal': fake.postcode(),
            'ville': fake.city(),
            'departement': fake.state(),
            'region': random.choice(regions),
            'latitude': float(fake.latitude()),
            'longitude': float(fake.longitude()),
            'type_structure': random.choice(types_structure),
            'date_ouverture': fake.date_between(start_date='-5y', end_date='today'),
            'nb_conseillers': random.randint(1, 8),
            'services_disponibles': services_disponibles,
            'population_desservie': random.randint(5000, 50000),
            'statut': 'active'
        })

    df = pd.DataFrame(data)
    df.to_csv('data/maisons_france_services.csv', index=False)
    print("✓ maisons_france_services.csv généré")


def generate_usagers_csv():
    """Générer le CSV des usagers"""
    data = []
    for i in range(5000):
        data.append({
            'id': i + 1,
            'age': random.randint(18, 85),
            'genre': random.choice(['M', 'F']),
            'situation_familiale': random.choice(['celibataire', 'marie', 'divorce', 'veuf', 'concubinage']),
            'niveau_numerique': random.choice(['debutant', 'intermediaire', 'avance']),
            'code_postal': fake.postcode(),
            'ville': fake.city(),
            'date_inscription': fake.date_between(start_date='-2y', end_date='today'),
            'frequence_visite': random.choice(['regulier', 'occasionnel', 'nouveau'])
        })

    df = pd.DataFrame(data)
    df.to_csv('data/usagers.csv', index=False)
    print("✓ usagers.csv généré")


def generate_conseillers_csv():
    """Générer le CSV des conseillers"""
    specialites_possibles = ['emploi', 'retraite', 'famille', 'social', 'sante', 'logement',
                             'energie', 'services_postaux', 'acces_droit', 'numerique']
    formations_possibles = ['accueil_usagers', 'procedures_caf', 'pole_emploi', 'numerique_senior',
                            'mediation_numerique', 'droit_social']

    data = []
    for i in range(1500):
        nb_specialites = random.randint(2, 5)
        specialites = '|'.join(random.sample(specialites_possibles, nb_specialites))

        nb_formations = random.randint(1, 4)
        formations = '|'.join(random.sample(formations_possibles, nb_formations))

        data.append({
            'id': i + 1,
            'nom': fake.last_name(),
            'prenom': fake.first_name(),
            'maison_fs_id': random.randint(1, 300),
            'specialites': specialites,
            'date_embauche': fake.date_between(start_date='-10y', end_date='today'),
            'charge_travail_actuelle': random.randint(0, 100),
            'formations_suivies': formations
        })

    df = pd.DataFrame(data)
    df.to_csv('data/conseillers.csv', index=False)
    print("✓ conseillers.csv généré")


def generate_demandes_csv():
    """Générer le CSV des demandes"""
    services_base = ['emploi', 'retraite', 'famille', 'social', 'sante', 'logement',
                     'energie', 'services_postaux', 'acces_droit']
    organismes = ['pole_emploi', 'caf', 'cnav', 'cpam', 'ants', 'msa', 'la_poste', 'justice']
    canaux = ['physique', 'telephone', 'visio', 'numerique']
    complexites = ['simple', 'moyen', 'complexe']

    data = []
    for i in range(15000):
        data.append({
            'id': i + 1,
            'usager_id': random.randint(1, 5000),
            'maison_fs_id': random.randint(1, 300),
            'date_demande': fake.date_time_between(start_date='-1y', end_date='now'),
            'type_service': random.choice(services_base),
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
    df.to_csv('data/demandes.csv', index=False)
    print("✓ demandes.csv généré")


def generate_performances_mensuelles_csv():
    """Générer le CSV des performances mensuelles"""
    data = []

    # Générer 12 mois de données pour chaque maison
    for maison_id in range(1, 301):
        for mois in pd.date_range(start='2023-01-01', end='2024-12-01', freq='MS'):
            data.append({
                'id': len(data) + 1,
                'maison_fs_id': maison_id,
                'mois': mois.strftime('%Y-%m-%d'),
                'nb_visites': random.randint(50, 500),
                'nb_demandes_traitees': random.randint(30, 300),
                'taux_satisfaction': round(random.uniform(3.0, 5.0), 2),
                'temps_attente_moyen': random.randint(5, 45),
                'taux_resolution': round(random.uniform(0.6, 0.95), 2)
            })

    df = pd.DataFrame(data)
    df.to_csv('data/performances_mensuelles.csv', index=False)
    print("✓ performances_mensuelles.csv généré")


def generate_all_csv():
    """Générer tous les CSV"""
    create_data_directory()
    generate_maisons_france_services_csv()
    generate_usagers_csv()
    generate_conseillers_csv()
    generate_demandes_csv()
    generate_performances_mensuelles_csv()
    print("\n🎉 Tous les fichiers CSV ont été générés avec succès!")


if __name__ == "__main__":
    generate_all_csv()
