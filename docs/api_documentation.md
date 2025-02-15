# Documentation de l'API d'Analyse de Sentiments

Cette API permet d'analyser le sentiment de tweets en utilisant des modèles d'apprentissage automatique.

## Configuration

L'API est accessible à l'adresse suivante :
```
http://127.0.0.1:5000
```

## Endpoints

### POST /analyse

Analyse le sentiment des tweets fournis.

#### Request
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
    "tweets": [
        "I like this product",
        "I hate this service",
        ...
    ]
}
```

#### Response
- Content-Type: `application/json`
- Body:
```json
{
    "I like this product": 0.8,
    "I hate this service": -0.7
}
```

Le score de sentiment varie de -1 (très négatif) à 1 (très positif).

#### Status Codes
- `200`: Succès
- `400`: Format de requête invalide
- `503`: Modèles non disponibles
- `500`: Erreur interne du serveur

### POST /add

Ajoute de nouveaux tweets dans la base de données.

#### Request
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
    "tweets": [
        {
            "text": "I love this product",
            "positive": true
        },
        {
            "text": "This is terrible",
            "positive": false
        }
    ]
}
```

#### Response
- Status: `201 Created`
- Content-Type: `application/json`
- Body:
```json
{
    "success": "Tweets ajoutés avec succès"
}
```

#### Status Codes
- `201`: Tweets ajoutés avec succès
- `400`: Format de requête invalide
- `500`: Erreur interne du serveur

## Notes Techniques

- L'API utilise des modèles de machine learning qui sont réentraînés périodiquement (toutes les heures)
- Les tweets sont automatiquement nettoyés avant l'analyse
- L'API utilise une base de données MySQL pour stocker les données d'entraînement
- Le système inclut une gestion des logs complète pour le suivi des opérations