#!/usr/bin/env python3
# fichier: haiku_mistral_awtrix.py

import os
import time
import requests
import re
import unicodedata
import schedule
import random
import json
import datetime
from mistralai import Mistral
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import html
import urllib.parse

# Configuration
MISTRAL_API_KEY = "xxx"
AGENT_ID = "ag:xxx:date-de-creation-agent:nom-agent:xxx" # Format de l'ID de l'agent
AWTRIX_API_URL = "http://192.168.10.250/api/custom"
POETRY_LOG_FILE = "poemes.json"
WEB_SERVER_PORT = 8080
POEMS_PER_PAGE = 10  # Nombre de poèmes par page

# Variable globale pour l'effet
effect = "aucun"  # Valeur par défaut

def clean_text(text):
    global effect
    
    # Remplacer les apostrophes par des espaces
    text = text.replace("'", "-APOSTROPHE-") # Awtrix ne peux pas afficher les apostrophes classiques
    # Remplacer les sauts de ligne par des virgules
    text = text.replace(",\n", ", ")
    text = text.replace(".\n", ". ")
    text = text.replace("\n", ", ")
    text = text.replace("œ", "oe")
    
    # Normaliser les caractères accentués (décomposer en caractère de base + accent)
    text = unicodedata.normalize('NFKD', text)
    
    # Supprimer les caractères non ASCII (comme les accents décomposés)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    
    # Ne garder que les caractères autorisés (A-Z, chiffres, tiret, point, virgule, espace)
    text = re.sub(r'[^A-Za-z0-9\-.,\s]', '', text)
    
    # remplacer l'apostrophe standard par celle (accent aigu) qui est affichable par awtrix
    text = text.replace("-APOSTROPHE-","´")

    # Mettre en majuscules + tirer un effet au hasard si le texte contient certains mots-clés
    lowercase_text = text.lower()
    effect = "aucun"  # Réinitialiser l'effet par défaut
    if any(keyword in lowercase_text for keyword in ["tef", "guef", "darsana", "isabelle", "judith", "loys"]):
        text = text.upper()
        effect = get_random_effect()

    # affiche le texte modifié
    print(f"Texte modifié: {text}")
    print(f"Effet choisi: {effect}")
    return text

def get_random_effect():
    # Retourne un effet aléatoire pour les textes en majuscules
    effects = ["Ripple", "Matrix", "Plasma"]
    return random.choice(effects)

def get_haiku_from_mistral():
    try:
        # Environ 1 fois sur 5, demander un poème avec mention d'une personne/lieu
        if random.random() < 0.2:  # 20% de chance
            # Liste des personnes ou lieux à mentionner
            mentions = [
                "la GALEXIE (le showroom technologique dans lequel va s'afficher ce poème)",
                "Guef",
                "Tef",
                "Loys",
                "Isabelle",
                "Judith",
                "Darsana"
            ]
            mention = random.choice(mentions)
            prompt = f"Crée un poème en mentionnant {mention}"
            print(f"Demande à Mistral avec mention: {prompt}")
        else:
            prompt = "Crée un poème stp"
            print("Demande à Mistral standard")
        
        client = Mistral(api_key=MISTRAL_API_KEY)
        chat_response = client.agents.complete(
            agent_id=AGENT_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Mistral: {e}")
        return "ERREUR API MISTRAL"

def log_poem(original_poem, cleaned_poem):
    """Enregistre un poème dans le fichier de log avec horodatage"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Créer ou charger le fichier JSON existant
    if os.path.exists(POETRY_LOG_FILE):
        try:
            with open(POETRY_LOG_FILE, 'r', encoding='utf-8') as f:
                poems = json.load(f)
        except:
            poems = []
    else:
        poems = []
    
    # Ajouter le nouveau poème
    poems.append({
        "timestamp": timestamp,
        "original_poem": original_poem,
        "cleaned_poem": cleaned_poem,
        "effect": effect
    })
    
    # Enregistrer le fichier mis à jour
    with open(POETRY_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(poems, f, ensure_ascii=False, indent=2)

def send_to_awtrix(text):
    try:
        cleaned_text = clean_text(text)
        payload = {
            "name": "haiku",
            "icon": "Stormyy",
            "pushIcon": 2,
            "text": cleaned_text,
            "duration": 25,
            "effect": effect
        }
        
        response = requests.post(AWTRIX_API_URL, json=payload)
        print(f"Statut de l'envoi à Awtrix: {response.status_code}")
        if response.status_code != 200:
            print(f"Réponse: {response.text}")
            
        # Retourner le texte nettoyé pour le stocker
        return cleaned_text
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Awtrix: {e}")
        return None

def job():
    print("Exécution du job à", time.strftime("%H:%M:%S"))
    haiku = get_haiku_from_mistral()
    print(f"Poème reçu: {haiku}")
    
    # Envoyer à Awtrix et récupérer le texte nettoyé
    cleaned_text = send_to_awtrix(haiku)
    
    if cleaned_text:
        # Enregistrer le poème original et nettoyé dans le fichier log
        log_poem(haiku, cleaned_text)

# Classe de serveur Web pour afficher les poèmes
class PoemServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Analyser les paramètres de l'URL
        if '?' in self.path:
            path, query = self.path.split('?', 1)
            params = urllib.parse.parse_qs(query)
            page = int(params.get('page', ['1'])[0])
        else:
            page = 1
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Générer la page HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Collection de Poèmes</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                .poem {
                    background-color: white;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .timestamp {
                    color: #666;
                    font-size: 0.8em;
                }
                .pagination {
                    text-align: center;
                    margin: 20px 0;
                }
                .pagination a {
                    margin: 0 5px;
                    padding: 5px 10px;
                    text-decoration: none;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 3px;
                }
                .current-page {
                    font-weight: bold;
                    margin: 0 5px;
                }
                button {
                    padding: 5px 10px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>Collection de Poèmes</h1>
            <div style="text-align: center; margin-bottom: 20px;">
                <button onclick="window.location.href='/'">Actualiser</button>
            </div>
        """
        
        # Charger les poèmes depuis le fichier
        if os.path.exists(POETRY_LOG_FILE):
            try:
                with open(POETRY_LOG_FILE, 'r', encoding='utf-8') as f:
                    poems = json.load(f)
                
                # Calculer les informations de pagination
                total_poems = len(poems)
                total_pages = max(1, (total_poems + POEMS_PER_PAGE - 1) // POEMS_PER_PAGE)
                
                # S'assurer que la page demandée est valide
                page = max(1, min(page, total_pages))
                
                # Calculer l'indice de début et de fin pour la page actuelle
                start_idx = (page - 1) * POEMS_PER_PAGE
                end_idx = min(start_idx + POEMS_PER_PAGE, total_poems)
                
                # Pagination simple en haut
                html_content += '<div class="pagination">'
                if page > 1:
                    html_content += f'<a href="/?page={page-1}">Page précédente</a>'
                html_content += f'<span class="current-page">Page {page} sur {total_pages}</span>'
                if page < total_pages:
                    html_content += f'<a href="/?page={page+1}">Page suivante</a>'
                html_content += '</div>'
                
                # Afficher les poèmes pour la page actuelle (du plus récent au plus ancien)
                poems_to_display = list(reversed(poems))[start_idx:end_idx]
                
                for poem in poems_to_display:
                    timestamp = poem.get("timestamp", "Date inconnue")
                    cleaned_poem = poem.get("cleaned_poem", "")
                    original_poem = poem.get("original_poem", "")
                    poem_effect = poem.get("effect", "aucun")
                    
                    html_content += f"""
                    <div class="poem">
                        <div class="timestamp">{html.escape(timestamp)}</div>
                        <p><strong>Effet:</strong> {html.escape(poem_effect)}</p>
                        <p><strong>Texte affiché:</strong><br>{html.escape(cleaned_poem)}</p>
                        <details>
                            <summary>Voir poème original</summary>
                            <p>{html.escape(original_poem).replace("\n", "<br>")}</p>
                        </details>
                    </div>
                    """
                
                # Pagination en bas
                html_content += '<div class="pagination">'
                if page > 1:
                    html_content += f'<a href="/?page={page-1}">Page précédente</a>'
                html_content += f'<span class="current-page">Page {page} sur {total_pages}</span>'
                if page < total_pages:
                    html_content += f'<a href="/?page={page+1}">Page suivante</a>'
                html_content += '</div>'
                
            except Exception as e:
                html_content += f"<p>Erreur lors du chargement des poèmes: {html.escape(str(e))}</p>"
        else:
            html_content += "<p>Aucun poème n'a encore été enregistré.</p>"
        
        html_content += """
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))

# Fonction pour démarrer le serveur HTTP dans un thread séparé
def run_web_server():
    server_address = ('', WEB_SERVER_PORT)
    httpd = HTTPServer(server_address, PoemServer)
    print(f"Serveur web démarré sur le port {WEB_SERVER_PORT}")
    httpd.serve_forever()

# Démarrer le serveur web dans un thread séparé
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# Exécution immédiate
job()

# Programmation toutes les minutes
schedule.every(1).minutes.do(job)

print(f"Serveur web accessible à l'adresse: http://localhost:{WEB_SERVER_PORT}")
print("Pour arrêter le programme, appuyez sur Ctrl+C")

# Boucle principale
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur")