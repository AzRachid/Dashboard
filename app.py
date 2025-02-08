from flask import Flask, render_template, request, jsonify
import requests
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend Agg pour éviter les erreurs sur Heroku
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import logging

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupérer l'URL de l'API FastAPI depuis une variable d'environnement
API_URL = os.getenv("API_URL", "https://appliscoring-1f1f7c4e1003.herokuapp.com")

@app.before_first_request
def init_app():
    """Initialisation de l'application"""
    logger.info("Application started successfully.")
    try:
        # Vérifiez ici si vos ressources externes sont accessibles
        response = requests.get(f"{API_URL}/clients")
        if response.status_code != 200:
            logger.error("Impossible de se connecter à l'API FastAPI.")
            raise Exception("L'API FastAPI est inaccessible.")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation : {e}")
        raise

@app.route("/", methods=["GET"])
def home():
    """Rendu de la page d'accueil"""
    logger.info("Rendering home page")
    return render_template("index.html")

@app.route("/clients", methods=["GET"])
def get_clients():
    """Récupère la liste des clients depuis l'API FastAPI"""
    logger.info("Fetching client list from API")
    response = requests.get(f"{API_URL}/clients")
    if response.status_code == 200:
        logger.info("Client list fetched successfully")
        return jsonify(response.json())
    else:
        logger.error("Failed to fetch client list")
        return jsonify({"error": "Impossible de charger les clients"}), response.status_code

@app.route("/client/<int:client_id>", methods=["GET"])
def get_client_data(client_id):
    """Récupère les informations d'un client spécifique"""
    logger.info(f"Fetching data for client ID {client_id}")
    response = requests.get(f"{API_URL}/client/{client_id}")
    if response.status_code == 200:
        logger.info(f"Data fetched successfully for client ID {client_id}")
        return jsonify(response.json())
    else:
        logger.error(f"Failed to fetch data for client ID {client_id}")
        return jsonify({"error": "Client non trouvé"}), response.status_code

@app.route("/analyze/<int:client_id>", methods=["GET"])
def analyze_client(client_id):
    """Analyse un client spécifique"""
    logger.info(f"Fetching feature importance for client ID {client_id}")
    response = requests.get(f"{API_URL}/analyze/{client_id}")
    if response.status_code == 200:
        logger.info(f"Feature importance fetched successfully for client ID {client_id}")
        return jsonify(response.json())
    else:
        logger.error(f"Failed to fetch feature importance for client ID {client_id}")
        return jsonify({"error": "Analyse impossible"}), response.status_code

@app.route("/predict/<int:client_id>", methods=["GET"])
def predict_client(client_id):
    """Prédit si le client est accepté ou refusé"""
    logger.info(f"Predicting decision for client ID {client_id}")
    try:
        client_data = requests.get(f"{API_URL}/client/{client_id}").json()
        score = client_data.get("score", 0)
        decision = "Accepté" if score > 0.51 else "Refusé"
        logger.info(f"Prediction for client ID {client_id}: Decision={decision}, Score={score}")
        return jsonify({"score": score, "decision": decision})
    except Exception as e:
        logger.error(f"Error predicting decision for client ID {client_id}: {e}")
        return jsonify({"error": "Prédiction impossible"}), 500

@app.route("/global-importance", methods=["GET"])
def get_global_importance():
    """Récupère les importances globales et génère un graphique"""
    logger.info("Fetching global feature importance")
    try:
        global_importance = requests.get(f"{API_URL}/analyze/1").json()  # Utilisez un client arbitraire
        names = global_importance["global_importance_names"]
        values = global_importance["global_importance_values"]

        # Générer un graphique
        plt.figure(figsize=(10, 6))
        sns.barplot(x=values, y=names, palette="viridis")
        plt.title("Importance Globale des Features")
        plt.xlabel("Valeur d'Importance")
        plt.ylabel("Feature")
        plt.tight_layout()

        # Convertir le graphique en base64
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()

        logger.info("Global feature importance chart generated successfully")
        return jsonify({"image": image_base64})
    except Exception as e:
        logger.error(f"Error generating global feature importance chart: {e}")
        return jsonify({"error": "Échec de la génération du graphique."}), 500

@app.route("/local-importance/<int:client_id>", methods=["GET"])
def get_local_importance(client_id):
    """Récupère les importances locales et génère un graphique"""
    logger.info(f"Fetching local feature importance for client ID {client_id}")
    try:
        local_importance = requests.get(f"{API_URL}/analyze/{client_id}").json()
        names = local_importance["local_importance_names"]
        values = local_importance["local_importance_values"]

        # Générer un graphique
        plt.figure(figsize=(10, 6))
        sns.barplot(x=values, y=names, palette="coolwarm")
        plt.title(f"Importance Locale des Features pour le Client {client_id}")
        plt.xlabel("Impact")
        plt.ylabel("Feature")
        plt.tight_layout()

        # Convertir le graphique en base64
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()

        logger.info(f"Local feature importance chart generated successfully for client ID {client_id}")
        return jsonify({"image": image_base64})
    except Exception as e:
        logger.error(f"Error generating local feature importance chart for client ID {client_id}: {e}")
        return jsonify({"error": "Échec de la génération du graphique."}), 500

@app.route("/distribution/<string:variable>", methods=["GET"])
def get_distribution(variable):
    """Affiche la distribution d'une variable selon la cible (simulée)"""
    logger.info(f"Fetching distribution for variable {variable}")
    try:
        # Simuler les données de distribution (remplacez cela par vos propres données si nécessaire)
        data = {
            "accepted": [1, 2, 3, 4, 5],
            "rejected": [5, 4, 3, 2, 1]
        }
        accepted_values = data.get("accepted", [])
        rejected_values = data.get("rejected", [])

        plt.figure(figsize=(10, 6))
        sns.kdeplot(accepted_values, label="Acceptés", shade=True)
        sns.kdeplot(rejected_values, label="Rejetés", shade=True)
        plt.title(f"Distribution de {variable} selon la cible")
        plt.xlabel(variable)
        plt.ylabel("Densité")
        plt.legend()
        plt.tight_layout()

        # Convertir le graphique en base64
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()

        logger.info(f"Distribution chart generated successfully for variable {variable}")
        return jsonify({"image": image_base64})
    except Exception as e:
        logger.error(f"Error generating distribution chart for variable {variable}: {e}")
        return jsonify({"error": "Échec de la génération du graphique."}), 500

if __name__ == "__main__":
    app.run(debug=True)
