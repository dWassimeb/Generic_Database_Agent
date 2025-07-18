# scripts/generate_data.py
import click
from src.data_generator import FranceServicesDataGenerator

@click.command()
@click.option('--maisons', default=300, help='Nombre de maisons France Services à générer')
@click.option('--usagers', default=5000, help='Nombre d\'usagers à générer')
@click.option('--demandes', default=15000, help='Nombre de demandes à générer')
def main(maisons, usagers, demandes):
    """Générer les données CSV pour la démonstration"""
    generator = FranceServicesDataGenerator()
    generator.generate_all_data()

if __name__ == "__main__":
    main()
