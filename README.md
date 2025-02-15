# Analyse de Sentiments des Tweets

Ce projet est une API d'analyse de sentiments qui permet d'évaluer la tonalité émotionnelle des tweets en utilisant des modèles de machine learning.

## Description

L'application utilise deux modèles de classification pour analyser les sentiments :
- Un modèle pour détecter les sentiments positifs
- Un modèle pour détecter les sentiments négatifs

Les modèles sont régulièrement réentraînés pour maintenir leur précision.

## Structure du Projet

```
.
├── app/                    # Code source principal
├── Docker/                # Configuration Docker
│   ├── DataBase/         # Configuration MySQL
│   ├── Python/           # Configuration Python
│   └── docker-compose.yml # Orchestration Docker
├── docs/                  # Documentation
├── log/                   # Fichiers de logs
└── requirements.txt       # Dépendances Python
```

## Configuration

Le fichier `config.py` contient toutes les configurations importantes du projet :

### Base de données
- Host : Automatiquement configuré via Docker
- Base de données : tweets_db
- Utilisateur : user
- Port : 3306

### Logs
- Format : `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Niveau : INFO
- Emplacement : `./log/app.log`

### Paramètres du modèle
- Features maximum : 2500
- Taille du jeu de test : 15%
- Random state : 50

### Scheduler
- Intervalle de réentraînement : 3600 secondes (1 heure)
- Taille des lots : 50000 tweets

## Installation et Démarrage

Le projet utilise Docker pour faciliter le déploiement. Une seule commande suffit pour tout démarrer :

```bash
cd Docker && docker compose up
```

Cette commande va :
1. Construire l'image Python avec votre code
2. Démarrer la base de données MySQL
3. Démarrer l'API sur le port 5000

L'API sera accessible à l'adresse : http://localhost:5000

## Documentation

- La documentation complète de l'API est disponible dans `docs/api_documentation.md`
- Les rapports de performance sont disponibles dans `docs/rapport_performance.md`

## Prérequis

- Docker
- Docker Compose v2

## Logs

Les logs de l'application sont persistés dans le dossier `log/` de votre machine hôte grâce au montage de volume Docker.