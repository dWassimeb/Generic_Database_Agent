# Guide d'installation et configuration de PostgreSQL sur macOS

Ce guide vous aidera à installer, configurer et résoudre les problèmes courants de PostgreSQL sur macOS, en particulier lorsqu'il est installé via Homebrew.

## Table des matières

1. [Installation de PostgreSQL](#1-installation-de-postgresql)
2. [Démarrage du serveur PostgreSQL](#2-démarrage-du-serveur-postgresql)
3. [Connexion à PostgreSQL](#3-connexion-à-postgresql)
4. [Création de la base de données](#4-création-de-la-base-de-données)
5. [Configuration de l'application](#5-configuration-de-lapplication)
6. [Résolution des problèmes courants](#6-résolution-des-problèmes-courants)

## 1. Installation de PostgreSQL

### Via Homebrew (recommandé)

```bash
# Installation de PostgreSQL 14
brew install postgresql@14

# Ou pour la dernière version
brew install postgresql
```

### Via Postgres.app

Alternativement, vous pouvez installer [Postgres.app](https://postgresapp.com/), qui est une application autonome avec une interface graphique.

## 2. Démarrage du serveur PostgreSQL

### Avec Homebrew

```bash
# Pour PostgreSQL 14
brew services start postgresql@14

# Pour la dernière version
brew services start postgresql
```

### Avec Postgres.app

Lancez simplement l'application Postgres.app depuis votre dossier Applications.

## 3. Connexion à PostgreSQL

### Particularité de PostgreSQL sur macOS avec Homebrew

**Important:** Contrairement aux installations standard de PostgreSQL, Homebrew configure PostgreSQL pour utiliser votre nom d'utilisateur macOS comme superutilisateur par défaut, et non 'postgres'.

### Connexion avec votre nom d'utilisateur macOS

```bash
# Remplacez 'votre_nom_utilisateur' par votre nom d'utilisateur macOS
psql -U votre_nom_utilisateur

# Ou simplement (sans spécifier d'utilisateur)
psql
```

### Vérifier que la connexion fonctionne

Une fois connecté, vous devriez voir une invite psql comme celle-ci:

```
votre_nom_utilisateur=#
```

Vous pouvez exécuter `\conninfo` pour vérifier les détails de votre connexion:

```sql
\conninfo
```

## 4. Création de la base de données

### Option 1: Utiliser le script automatique (recommandé)

Nous fournissons un script qui configure automatiquement PostgreSQL:

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

### Option 2: Création manuelle

1. Connectez-vous à PostgreSQL:

```bash
psql
```

2. Créez la base de données:

```sql
CREATE DATABASE france_services_db;
```

3. Créez un utilisateur:

```sql
CREATE USER fs_user WITH PASSWORD 'fs_password';
```

4. Accordez les privilèges:

```sql
GRANT ALL PRIVILEGES ON DATABASE france_services_db TO fs_user;
```

5. Quittez psql:

```sql
\q
```

## 5. Configuration de l'application

Créez un fichier `.env` à la racine du projet avec les informations de connexion:

```
DATABASE_HOST=localhost
DATABASE_NAME=france_services_db
DATABASE_USER=fs_user
DATABASE_PASSWORD=fs_password
DATABASE_PORT=5432
```

## 6. Résolution des problèmes courants

### Erreur: role "postgres" does not exist

Cette erreur est courante sur macOS avec PostgreSQL installé via Homebrew.

**Cause:** Homebrew configure PostgreSQL pour utiliser votre nom d'utilisateur macOS comme superutilisateur par défaut, et non 'postgres'.

**Solutions:**

1. Utilisez votre nom d'utilisateur macOS pour vous connecter:
   ```bash
   # Remplacez 'votre_nom_utilisateur' par votre nom d'utilisateur macOS
   psql -U votre_nom_utilisateur
   
   # Ou simplement
   psql
   ```

2. Utilisez le script d'initialisation automatique:
   ```bash
   chmod +x scripts/init_postgres_mac.sh
   ./scripts/init_postgres_mac.sh
   ```

3. Créez un utilisateur postgres si nécessaire:
   ```bash
   # Connectez-vous d'abord avec votre nom d'utilisateur macOS
   psql
   
   # Puis créez l'utilisateur postgres (dans psql)
   CREATE USER postgres WITH SUPERUSER PASSWORD 'votre_mot_de_passe';
   ```

### Erreur: command not found: CREATE DATABASE

Cette erreur se produit lorsque vous essayez d'exécuter des commandes SQL directement dans le terminal.

**Solution:** Les commandes SQL doivent être exécutées à l'intérieur du client psql, pas directement dans le terminal.

1. Connectez-vous d'abord à psql:
   ```bash
   psql
   ```

2. Puis exécutez les commandes SQL dans l'invite psql:
   ```sql
   CREATE DATABASE france_services_db;
   ```

### Erreur: connection to server at "localhost", port 5432 failed

Cette erreur indique que le serveur PostgreSQL n'est pas démarré ou n'accepte pas les connexions.

**Solutions:**

1. Vérifiez que PostgreSQL est démarré:
   ```bash
   brew services list
   ```

2. Démarrez PostgreSQL:
   ```bash
   brew services start postgresql@14
   ```

3. Vérifiez les logs PostgreSQL:
   ```bash
   brew services log postgresql@14
   ```

### Vérifier l'état de PostgreSQL

```bash
# Liste tous les services Homebrew et leur état
brew services list

# Affiche les logs de PostgreSQL
brew services log postgresql@14
```

### Réinitialiser PostgreSQL (en dernier recours)

Si vous rencontrez des problèmes persistants, vous pouvez réinitialiser complètement PostgreSQL:

```bash
# Arrêter le service
brew services stop postgresql@14

# Désinstaller PostgreSQL
brew uninstall postgresql@14

# Supprimer les données
rm -rf /usr/local/var/postgres@14

# Réinstaller PostgreSQL
brew install postgresql@14

# Démarrer le service
brew services start postgresql@14
```

## Utilisation de l'application

Une fois PostgreSQL configuré, vous pouvez utiliser l'application:

```bash
# Générer les données
poetry run generate-data

# Initialiser la base de données
poetry run init-db

# Exécuter la démonstration complète
poetry run python run_demo.py
```