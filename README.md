# Generic Database Agent - France Services

Un agent intelligent pour l'analyse des données des Maisons France Services, permettant de générer, stocker et interroger des données via une interface conversationnelle.

## Introduction

Ce projet fournit un système complet pour:
- Générer des données synthétiques représentatives des Maisons France Services
- Stocker ces données dans une base PostgreSQL
- Analyser et visualiser ces données via un agent conversationnel

## Prérequis

- Python 3.9+ (mais pas 3.9.7 qui a un bug connu)
- Poetry (gestionnaire de dépendances)
- PostgreSQL 12+

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-organisation/Generic_Database_Agent.git
cd Generic_Database_Agent
```

### 2. Installer les dépendances avec Poetry

```bash
poetry install
```

### 3. Configuration de PostgreSQL

> **Guide détaillé:** Pour des instructions complètes sur l'installation et la configuration de PostgreSQL sur macOS, consultez notre [Guide PostgreSQL pour macOS](docs/postgresql_macos_guide.md).

#### Installation de PostgreSQL

**macOS avec Homebrew:**
```bash
# Installation de PostgreSQL
brew install postgresql@14  # ou simplement postgresql pour la dernière version

# Démarrage du service
brew services start postgresql@14  # ou postgresql pour la dernière version
```

> **Note importante pour macOS avec Homebrew:** Contrairement aux installations standard de PostgreSQL, Homebrew configure PostgreSQL pour utiliser votre nom d'utilisateur macOS comme superutilisateur par défaut, et non 'postgres'.

**macOS avec Postgres.app:**
- Télécharger et installer depuis [Postgres.app](https://postgresapp.com/)
- Lancer l'application pour démarrer le serveur

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- Télécharger et installer depuis [postgresql.org](https://www.postgresql.org/download/windows/)
- Le service PostgreSQL devrait démarrer automatiquement

#### Création de la base de données

##### Option 1: Utiliser le script d'initialisation automatique (recommandé pour macOS)

Nous fournissons un script qui configure automatiquement PostgreSQL sur macOS avec Homebrew:

```bash
# Rendre le script exécutable
chmod +x scripts/init_postgres_mac.sh

# Exécuter le script
./scripts/init_postgres_mac.sh
```

Ce script:
- Vérifie si PostgreSQL est installé et en cours d'exécution
- Crée la base de données france_services_db
- Crée un utilisateur fs_user avec mot de passe fs_password
- Configure le fichier .env avec les informations de connexion

##### Option 2: Configuration manuelle

1. Connectez-vous à PostgreSQL:

```bash
# macOS avec Homebrew (remplacez 'votre_nom_utilisateur' par votre nom d'utilisateur macOS)
psql -U votre_nom_utilisateur

# macOS avec Postgres.app
psql

# Linux
sudo -u postgres psql

# Windows (après avoir ajouté psql au PATH)
psql -U postgres
```

2. Créez un utilisateur et une base de données (à exécuter dans l'invite psql):
```sql
CREATE USER votre_utilisateur WITH PASSWORD 'votre_mot_de_passe';
CREATE DATABASE france_services_db;
GRANT ALL PRIVILEGES ON DATABASE france_services_db TO votre_utilisateur;
```

> **Important:** Les commandes SQL comme `CREATE DATABASE` doivent être exécutées à l'intérieur du client psql, pas directement dans le terminal.

#### Configuration de la connexion

Créez un fichier `.env` à la racine du projet avec les informations de connexion:

```
DATABASE_HOST=localhost
DATABASE_NAME=france_services_db
DATABASE_USER=votre_utilisateur
DATABASE_PASSWORD=votre_mot_de_passe
DATABASE_PORT=5432
```

## Utilisation

### Générer les données

```bash
poetry run generate-data
```

### Initialiser la base de données

```bash
poetry run init-db
```

### Exécuter la démonstration complète

```bash
poetry run python run_demo.py
```

## Résolution des problèmes

### Erreur: psycopg2 module not found

Si vous rencontrez cette erreur, installez le package psycopg2-binary:

```bash
poetry add psycopg2-binary
```

### Erreur: role "postgres" does not exist

Cette erreur est courante sur macOS avec PostgreSQL installé via Homebrew.

**Cause:** Contrairement aux installations standard de PostgreSQL, Homebrew configure PostgreSQL pour utiliser votre nom d'utilisateur macOS comme superutilisateur par défaut, et non 'postgres'.

**Solutions:**

1. **Utilisez votre nom d'utilisateur macOS pour vous connecter:**
   ```bash
   # Remplacez 'votre_nom_utilisateur' par votre nom d'utilisateur macOS
   psql -U votre_nom_utilisateur
   ```

2. **Utilisez le script d'initialisation automatique:**
   ```bash
   chmod +x scripts/init_postgres_mac.sh
   ./scripts/init_postgres_mac.sh
   ```

3. **Créez un utilisateur postgres si nécessaire:**
   ```bash
   # Connectez-vous d'abord avec votre nom d'utilisateur macOS
   psql
   
   # Puis créez l'utilisateur postgres (dans psql)
   CREATE USER postgres WITH SUPERUSER PASSWORD 'votre_mot_de_passe';
   ```

### Erreur: command not found: CREATE DATABASE

Cette erreur se produit lorsque vous essayez d'exécuter des commandes SQL directement dans le terminal.

**Solution:** Les commandes SQL doivent être exécutées à l'intérieur du client psql, pas directement dans le terminal.

1. **Connectez-vous d'abord à psql:**
   ```bash
   # macOS avec Homebrew
   psql -U votre_nom_utilisateur
   
   # Ou simplement
   psql
   ```

2. **Puis exécutez les commandes SQL dans l'invite psql:**
   ```sql
   CREATE DATABASE france_services_db;
   ```

### Erreur: connection to server at "localhost", port 5432 failed

Cette erreur indique que le serveur PostgreSQL n'est pas démarré ou n'accepte pas les connexions.

**Solutions:**

1. **Vérifier que PostgreSQL est démarré:**

   - **macOS avec Homebrew:** `brew services list`
   - **macOS avec Postgres.app:** Vérifier que l'application est lancée
   - **Linux:** `sudo systemctl status postgresql`
   - **Windows:** Vérifier les services Windows (services.msc)

2. **Démarrer PostgreSQL:**

   - **macOS avec Homebrew:** `brew services start postgresql@14` (ou `postgresql` pour la dernière version)
   - **macOS avec Postgres.app:** Ouvrir l'application
   - **Linux:** `sudo systemctl start postgresql`
   - **Windows:** Démarrer le service PostgreSQL dans les services Windows

3. **Vérifier la configuration:**
   - Assurez-vous que les informations dans le fichier `.env` sont correctes
   - Vérifiez que PostgreSQL écoute sur le port 5432 (port par défaut)
   - Vérifiez que la base de données existe: `psql -c "\l"` (sur macOS) ou `psql -U postgres -c "\l"` (sur Linux/Windows)

4. **Vérifier les logs PostgreSQL:**
   - **macOS:** `brew services log postgresql@14` ou `log show --predicate 'process == "postgres"' --last 30m`
   - **Linux:** `sudo journalctl -u postgresql`
   - **Windows:** Consultez les journaux d'événements Windows

## Licence

Ce projet est sous licence [MIT](LICENSE).