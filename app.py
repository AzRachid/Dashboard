from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Récupérer l'URL de l'API FastAPI depuis une variable d'environnement
API_URL = os.getenv("API_URL", "https://appliscoring-1f1f7c4e1003.herokuapp.com")  # URL de votre API

@app.route("/", methods=["GET"])
def home():
    """Rendu de la page d'accueil"""
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

if __name__ == "__main__":
    app.run(debug=True)
