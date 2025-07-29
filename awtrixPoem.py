#!/usr/bin/env python3
# Fichier : apostropheV2.py (version simplifiée)
# Description : Envoie un poème aléatoire à Awtrix à intervalle régulier.

import os
import time
import requests
import schedule
import random
import json

# --- Configuration ---
AWTRIX_API_URL = "http://192.168.20.22/api/custom"
POETRY_LOG_FILE = "poemes.json"

def get_random_poem_from_log():
    """
    Charge les poèmes depuis le fichier JSON et retourne un objet poème complet au hasard.
    Retourne None si une erreur survient.
    """
    print("Chargement d'un poème depuis le fichier local...")
    
    if not os.path.exists(POETRY_LOG_FILE):
        print(f"ERREUR: Le fichier '{POETRY_LOG_FILE}' n'a pas été trouvé.")
        return None
    
    try:
        with open(POETRY_LOG_FILE, 'r', encoding='utf-8') as f:
            poems = json.load(f)
        
        if not poems or not isinstance(poems, list):
            print("ERREUR: Le fichier de poèmes est vide ou mal formaté.")
            return None
            
        return random.choice(poems)
        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de poèmes : {e}")
        return None

def send_to_awtrix(cleaned_text, effect_to_use):
    """Envoie le texte et l'effet déjà formatés à l'API Awtrix."""
    print(f"Envoi du texte à Awtrix avec l'effet '{effect_to_use}'")
    try:
        payload = {
            "name": "haiku",
            "icon": "Stormyy",  # Vous pouvez changer l'icône ici
            "pushIcon": 2,
            "text": cleaned_text,
            "duration": 25,
            "effect": effect_to_use
        }
        response = requests.post(AWTRIX_API_URL, json=payload, timeout=5)
        print(f"Statut de l'envoi à Awtrix: {response.status_code}")
        if response.status_code != 200:
            print(f"Réponse: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau lors de l'appel à l'API Awtrix: {e}")
    except Exception as e:
        print(f"Erreur inattendue dans send_to_awtrix: {e}")

def job():
    """Tâche principale : choisit un poème et l'envoie."""
    print("\n" + "="*40)
    print("Exécution du job à", time.strftime("%H:%M:%S"))
    
    poem_data = get_random_poem_from_log()
    
    if poem_data and isinstance(poem_data, dict):
        # Utiliser .get() est plus sûr au cas où une clé manquerait dans le JSON
        cleaned_text = poem_data.get('cleaned_poem', 'Erreur: texte nettoye manquant')
        effect = poem_data.get('effect', 'aucun')
        
        print(f"Poème choisi: {cleaned_text}")
        send_to_awtrix(cleaned_text, effect)
    else:
        print("Aucun poème valide n'a pu être récupéré pour l'affichage.")
        
    print("="*40)

if __name__ == "__main__":
    # Exécute la tâche une fois immédiatement au démarrage
    job()
    
    # Programme la tâche pour s'exécuter toutes les 30 minutes
    schedule.every(30).minutes.do(job)

    print("Le script est lancé. Il enverra un poème toutes les 30 minutes.")
    print("Pour arrêter le programme, appuyez sur Ctrl+C")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgramme arrêté par l'utilisateur.")