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

# Exposer le port
EXPOSE 8000

# Script de démarrage
CMD ["python", "run_demo.py"]