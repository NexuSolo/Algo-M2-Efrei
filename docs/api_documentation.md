# Documentation de l'API d'Analyse de Sentiments

Cette API permet d'analyser le sentiment de tweets en utilisant des modèles d'apprentissage automatique.

## Configuration

L'API est accessible à l'adresse suivante :
```
http://127.0.0.1:5000
```

## Endpoints

### Analyse de Sentiments

**Endpoint:** `/analyse`  
**Méthode:** POST  
**Content-Type:** application/json

#### Description
Analyse le sentiment de un ou plusieurs tweets et retourne un score pour chacun.

#### Corps de la Requête
```json
{
    "tweets": [
        "I love this new product!",
        "This is terrible service"
    ]
}
```

#### Paramètres
- `tweets` (array de strings): Liste des tweets à analyser

#### Réponse
```json
{
    "I love this new product!": 0.7111955103717886,
    "This is terrible service": -0.651521278220373
}
```

Le score retourné est compris entre -1 et 1 :
- Proche de 1 : Sentiment très positif
- Proche de 0 : Sentiment neutre
- Proche de -1 : Sentiment très négatif

#### Codes de Statut
- 200 : Succès
- 400 : Format de requête invalide
- 503 : Modèles en cours d'entraînement
- 500 : Erreur interne du serveur

#### Exemple de Requête avec cURL
```bash
curl -X POST \
  http://127.0.0.1:5000/analyse \
  -H 'Content-Type: application/json' \
  -d '{
    "tweets": [
        "I am really happy today!",
        "This weather is awful"
    ]
}'
```

## Notes Techniques

- L'API utilise des modèles de machine learning qui sont réentraînés périodiquement (toutes les heures)
- Les tweets sont automatiquement nettoyés avant l'analyse
- L'API utilise une base de données MySQL pour stocker les données d'entraînement
- Le système inclut une gestion des logs complète pour le suivi des opérations