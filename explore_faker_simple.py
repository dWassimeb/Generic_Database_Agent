from faker import Faker

# Create a Faker instance with French locale
fake_fr = Faker('fr_FR')

# Try some methods that might be relevant for French administrative divisions
print("Testing methods for French administrative divisions:")

# Try department-related methods
try:
    print(f"Department: {fake_fr.department()}")
except AttributeError:
    print("department() method not available")

try:
    print(f"Department name: {fake_fr.department_name()}")
except AttributeError:
    print("department_name() method not available")

# Try region-related methods
try:
    print(f"Region: {fake_fr.region()}")
except AttributeError:
    print("region() method not available")

# Try administrative unit methods
try:
    print(f"Administrative unit: {fake_fr.administrative_unit()}")
except AttributeError:
    print("administrative_unit() method not available")

# Print some examples of city and address generation
print("\nExamples of city and address generation:")
print(f"City: {fake_fr.city()}")
print(f"Address: {fake_fr.address()}")

# Create a list of French departments as a fallback solution
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
print(f"\nNumber of departments in our list: {len(departments)}")
print("First 5 departments:", departments[:5])