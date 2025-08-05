**AFFICHAGE DE POEMES SUR ULANZI AWTRIX AVEC MISTRAL AI**

Ce projet utilise l'IA de Mistral pour générer des petits poèmes/haikus et les afficher sur un écran connecté Ulanzi Awtrix Smart Clock. 
Il inclut une interface web pour consulter les poèmes passés, et un second script plus léger pour afficher des poèmes déjà générés et ne nécessite donc pas l'appel à Mistral.

<img width="1024" alt="Ulanzi Awtrix Smart Clock" src="https://github.com/user-attachments/assets/487727da-05c9-4eda-b654-6a94492f4295" />

**Qu'est-ce que l'Ulanzi Awtrix Smart Clock ?**

L'Ulanzi Awtrix Smart Clock est un écran à pixels connecté au Wi-Fi. 
Il est personnalisable et peut afficher l'heure, la météo, des notifications, et surtout, des informations personnalisées envoyées via une API locale. 
Ce projet exploite cette API pour transformer l'écran en un afficheur de poèmes.

**Structure du projet**

├── awtrixPoemMistral.py  # Le script principal qui génère les poèmes

├── awtrixPoem.py         # Le script secondaire qui affiche les poèmes existants

├── requirements.txt      # Les dépendances Python

└── poemes.json           # Fichier de log, créé automatiquement par awtrixPoemMistral.py

**Note importante :** Le fichier poemes.json est généré par le script

**Fonctionnalités**

- Génération par IA : Crée des poèmes en utilisant un agent personnalisé sur la plateforme Mistral AI.
- Personnalisation : 20% des poèmes générés mentionnent un nom ou un lieu choisi au hasard dans une liste prédéfinie.
- Formatage du texte : Formate automatiquement le texte pour être compatible avec l'affichage de l'Awtrix.
- Effets Visuels : Applique des effets visuels spéciaux si le poème mentionne certains mots-clés.
- Sauvegarde de poèmes : Chaque poème est sauvegardé dans un fichier poemes.json qui est créé automatiquement.
- Interface Web : Lance un serveur web local pour consulter l'historique de tous les poèmes générés.
- Deux codes :
    - awtrixPoemMistral.py : Pour générer une nouvelle collection de poèmes.
    - awtrixPoem.py : Pour afficher les poèmes de la collection existante.

**Installation et Configuration**

Prérequis :
- Python 3
- Un Ulanzi Awtrix Smart Clock connecté à votre réseau local.
- Un compte sur la plateforme Mistral AI.
  
Étapes :
1. Clonez le dépôt.
2. Installez les dépendances : pip install -r requirements.txt
3. Configurez awtrixPoemMistral.py :
      Ouvrez le fichier et modifiez les variables de configuration :

        AWTRIX_API_URL: L'adresse IP locale de votre Ulanzi Awtrix.
   
        MISTRAL_API_KEY: Votre clé API secrète de Mistral.
   
        AGENT_ID: L'identifiant de votre agent Mistral.
   
      Pour le créer : Allez dans la section Agents de Mistral > Créez un nouvel agent > Définissez le conditionnement de l'agent
   
      Une fois l'agent créé, copiez son ID (au format ag:xxx:xxx...) et collez-le dans le script.
   
   Configurez awtrixPoem.py :
      Assurez-vous que la variable AWTRIX_API_URL est également correcte dans ce fichier. 

**Utilisation**

Le fonctionnement se fait en deux temps. Il faut d'abord créer et peupler la base de données de poèmes avant de pouvoir les afficher en boucle.

Étape 1 : Générer la collection de poèmes (awtrixPoemMistral.py)
C'est le script à lancer en premier. Il va contacter l'API de Mistral, créer le fichier de poèmes et commencer à le remplir.

- Lancez le script : python awtrixPoemMistral.py
- Laissez-le tourner : À son premier lancement, le script créera le fichier poemes.json. Laissez-le s'exécuter pendant un certain temps pour construire une collection de poèmes variée.
- Consultez la collection : Vous pouvez suivre la collection via l'interface web accessible sur http://localhost:8080

Étape 2 : Afficher les poèmes de votre collection (awtrixPoem.py)
Une fois que votre fichier poemes.json contient suffisamment de poèmes, vous pouvez utiliser ce second script, plus léger et économique.
Prérequis : Assurez-vous d'avoir déjà exécuté l'étape 1 au moins une fois et que le fichier poemes.json existe.

- Lancez le script : python awtrixPoem.py
