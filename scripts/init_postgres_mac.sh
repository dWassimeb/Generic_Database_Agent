#!/bin/bash
# Script pour initialiser PostgreSQL sur macOS avec Homebrew
# Ce script crée la base de données et l'utilisateur nécessaires pour l'application

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Initialisation de PostgreSQL pour Generic Database Agent ===${NC}"

# Vérifier si PostgreSQL est installé via Homebrew
if ! command -v brew &> /dev/null; then
    echo -e "${RED}Homebrew n'est pas installé. Veuillez l'installer d'abord.${NC}"
    echo "Voir https://brew.sh/ pour les instructions."
    exit 1
fi

# Vérifier si PostgreSQL est installé
if brew list postgresql@14 &>/dev/null; then
    echo -e "${GREEN}PostgreSQL 14 est installé via Homebrew.${NC}"
    PG_VERSION="postgresql@14"
elif brew list postgresql &>/dev/null; then
    echo -e "${GREEN}PostgreSQL est installé via Homebrew.${NC}"
    PG_VERSION="postgresql"
else
    echo -e "${RED}PostgreSQL n'est pas installé via Homebrew.${NC}"
    echo "Installez-le avec: brew install postgresql@14"
    exit 1
fi

# Vérifier si PostgreSQL est en cours d'exécution
if brew services list | grep $PG_VERSION | grep started &>/dev/null; then
    echo -e "${GREEN}PostgreSQL est en cours d'exécution.${NC}"
else
    echo -e "${YELLOW}PostgreSQL n'est pas en cours d'exécution. Démarrage...${NC}"
    brew services start $PG_VERSION
    sleep 3 # Attendre que PostgreSQL démarre
fi

# Obtenir le nom d'utilisateur actuel (qui est le superutilisateur par défaut dans PostgreSQL Homebrew)
CURRENT_USER=$(whoami)
echo -e "${YELLOW}Sur macOS avec Homebrew, l'utilisateur PostgreSQL par défaut est votre nom d'utilisateur: ${GREEN}$CURRENT_USER${NC}"

# Créer la base de données et l'utilisateur
echo -e "${YELLOW}Création de la base de données et de l'utilisateur...${NC}"

# Définir les variables pour la base de données
DB_NAME="france_services_db"
DB_USER="fs_user"
DB_PASSWORD="fs_password"

# Vérifier si la base de données existe déjà
if psql -U $CURRENT_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}La base de données $DB_NAME existe déjà.${NC}"
else
    # Créer la base de données
    psql -U $CURRENT_USER -c "CREATE DATABASE $DB_NAME;"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Base de données $DB_NAME créée avec succès.${NC}"
    else
        echo -e "${RED}Erreur lors de la création de la base de données.${NC}"
        exit 1
    fi
fi

# Vérifier si l'utilisateur existe déjà
if psql -U $CURRENT_USER -c "\du" | grep -qw $DB_USER; then
    echo -e "${YELLOW}L'utilisateur $DB_USER existe déjà.${NC}"
else
    # Créer l'utilisateur
    psql -U $CURRENT_USER -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Utilisateur $DB_USER créé avec succès.${NC}"
    else
        echo -e "${RED}Erreur lors de la création de l'utilisateur.${NC}"
        exit 1
    fi
fi

# Accorder les privilèges
psql -U $CURRENT_USER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Privilèges accordés à $DB_USER sur $DB_NAME.${NC}"
else
    echo -e "${RED}Erreur lors de l'attribution des privilèges.${NC}"
    exit 1
fi

# Créer le fichier .env
echo -e "${YELLOW}Création du fichier .env...${NC}"
cat > .env << EOF
DATABASE_HOST=localhost
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_PORT=5432
EOF

echo -e "${GREEN}Fichier .env créé avec succès.${NC}"
echo -e "${GREEN}=== Configuration PostgreSQL terminée avec succès! ===${NC}"
echo -e "${YELLOW}Vous pouvez maintenant exécuter:${NC}"
echo -e "  ${GREEN}poetry run generate-data${NC}"
echo -e "  ${GREEN}poetry run init-db${NC}"
echo -e "  ${GREEN}poetry run python run_demo.py${NC}"