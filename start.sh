#!/bin/bash

echo "🚀 Initialisation de l'application France Services..."

# Exécuter le script de démonstration
echo "📊 Génération des données et initialisation de la base..."
if poetry run python run_demo.py; then
    echo "✅ Script de démonstration exécuté avec succès"
else
    echo "⚠️ Erreur dans le script de démonstration, mais continuation..."
    echo "💡 Streamlit sera lancé sans les données de démonstration"
fi

# Lancer Streamlit
echo "🌟 Lancement de Streamlit..."
exec poetry run streamlit run app.py --server.port=8501 --server.address=0.0.0.0