FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock* ./

# Installer Poetry et les dépendances
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only=main --no-root

# Copier le code source
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p users_data data/charts

# Exposer le port Streamlit
EXPOSE 8501

# Configuration Streamlit pour l'environnement containerisé
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Script de démarrage Streamlit
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]