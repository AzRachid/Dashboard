from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

app = Flask(__name__)

# Récupérer l'URL de l'API FastAPI depuis une variable d'environnement
API_URL = os.getenv("API_URL", "https://appliscoring-1f1f7c4e1003.herokuapp.com")  # URL de votre API

@app.route("/", methods=["GET", "POST"])
def home():
    """Rendu de la page d'accueil"""
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".csv"):
            file.save("train-data.csv")
            return jsonify({"message": "Fichier chargé avec succès."}), 200
    return render_template("index.html")

@app.route("/clients", methods=["GET"])
def get_clients():
    """Récupère la liste des clients depuis l'API FastAPI"""
    response = requests.get(f"{API_URL}/clients")
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Impossible de charger les clients"}), response.status_code

@app.route("/client/<int:client_id>", methods=["GET"])
def get_client_data(client_id):
    """Récupère les informations d'un client spécifique"""
    response = requests.get(f"{API_URL}/client/{client_id}")
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Client non trouvé"}), response.status_code

@app.route("/analyze/<int:client_id>", methods=["GET"])
def analyze_client(client_id):
    """Analyse un client spécifique"""
    response = requests.get(f"{API_URL}/analyze/{client_id}")
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Analyse impossible"}), response.status_code

@app.route("/predict/<int:client_id>", methods=["GET"])
def predict_client(client_id):
    """Prédit si le client est accepté ou refusé"""
    client_data = requests.get(f"{API_URL}/client/{client_id}").json()
    score = client_data.get("score", 0)
    decision = "Accepté" if score > 0.51 else "Refusé"
    return jsonify({"score": score, "decision": decision})

@app.route("/global-importance", methods=["GET"])
def get_global_importance():
    """Récupère les importances globales et génère un graphique"""
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

    return jsonify({"image": image_base64})

@app.route("/local-importance/<int:client_id>", methods=["GET"])
def get_local_importance(client_id):
    """Récupère les importances locales et génère un graphique"""
    local_importance = requests.get(f"{API_URL}/analyze/{client_id}").json()
    names = local_importance["local_importance_names"]
    values = local_importance["local_importance_values"]

    # Générer un graphique
    plt.figure(figsize=(10, 6))
    sns.barplot(x=values, y=names, palette="coolwarm")
    plt.title("Importance Locale des Features pour le Client")
    plt.xlabel("Impact")
    plt.ylabel("Feature")
    plt.tight_layout()

    # Convertir le graphique en base64
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return jsonify({"image": image_base64})

@app.route("/distribution/<string:variable>", methods=["GET"])
def get_distribution(variable):
    """Affiche la distribution d'une variable selon la cible"""
    if not os.path.exists("train-data.csv"):
        return jsonify({"error": "Aucun fichier d'entraînement chargé."}), 400

    train_data = pd.read_csv("train-data.csv")
    if variable not in train_data.columns:
        return jsonify({"error": f"Variable {variable} introuvable dans le fichier."}), 400

    # Supposons que la colonne cible s'appelle "TARGET"
    if "TARGET" not in train_data.columns:
        return jsonify({"error": "Colonne TARGET introuvable dans le fichier."}), 400

    plt.figure(figsize=(10, 6))
    sns.kdeplot(train_data[train_data["TARGET"] == 0][variable], label="Accepted", shade=True)
    sns.kdeplot(train_data[train_data["TARGET"] == 1][variable], label="Rejected", shade=True)
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

    return jsonify({"image": image_base64})

if __name__ == "__main__":
    app.run(debug=True)
