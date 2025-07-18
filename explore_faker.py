from faker import Faker

# Create a Faker instance with French locale
fake_fr = Faker('fr_FR')

# Print available methods
print("Available methods in Faker fr_FR:")
methods = [method for method in dir(fake_fr) if not method.startswith('_') and callable(getattr(fake_fr, method))]
for method in sorted(methods):
    print(f"- {method}")

# Try to get some examples of French administrative divisions
print("\nExamples of French administrative divisions:")
try:
    print(f"Department name: {fake_fr.department_name()}")
except AttributeError:
    print("department_name() method not available")

try:
    print(f"Department number: {fake_fr.department_number()}")
except AttributeError:
    print("department_number() method not available")

try:
    print(f"Region: {fake_fr.region()}")
except AttributeError:
    print("region() method not available")

# Create a list of French departments
print("\nCreating a list of French departments:")
departments = [
    "Ain", "Aisne", "Allier", "Alpes-de-Haute-Provence", "Hautes-Alpes", "Alpes-Maritimes", 
    "Ardèche", "Ardennes", "Ariège", "Aube", "Aude", "Aveyron", "Bouches-du-Rhône", "Calvados", 
    "Cantal", "Charente", "Charente-Maritime", "Cher", "Corrèze", "Corse-du-Sud", "Haute-Corse", 
    "Côte-d'Or", "Côtes-d'Armor", "Creuse", "Dordogne", "Doubs", "Drôme", "Eure", "Eure-et-Loir", 
    "Finistère", "Gard", "Haute-Garonne", "Gers", "Gironde", "Hérault", "Ille-et-Vilaine", "Indre", 
    "Indre-et-Loire", "Isère", "Jura", "Landes", "Loir-et-Cher", "Loire", "Haute-Loire", "Loire-Atlantique", 
    "Loiret", "Lot", "Lot-et-Garonne", "Lozère", "Maine-et-Loire", "Manche", "Marne", "Haute-Marne", 
    "Mayenne", "Meurthe-et-Moselle", "Meuse", "Morbihan", "Moselle", "Nièvre", "Nord", "Oise", "Orne", 
    "Pas-de-Calais", "Puy-de-Dôme", "Pyrénées-Atlantiques", "Hautes-Pyrénées", "Pyrénées-Orientales", 
    "Bas-Rhin", "Haut-Rhin", "Rhône", "Haute-Saône", "Saône-et-Loire", "Sarthe", "Savoie", "Haute-Savoie", 
    "Paris", "Seine-Maritime", "Seine-et-Marne", "Yvelines", "Deux-Sèvres", "Somme", "Tarn", 
    "Tarn-et-Garonne", "Var", "Vaucluse", "Vendée", "Vienne", "Haute-Vienne", "Vosges", "Yonne", 
    "Territoire de Belfort", "Essonne", "Hauts-de-Seine", "Seine-Saint-Denis", "Val-de-Marne", 
    "Val-d'Oise", "Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"
]
print(f"Number of departments: {len(departments)}")
print("First 5 departments:", departments[:5])