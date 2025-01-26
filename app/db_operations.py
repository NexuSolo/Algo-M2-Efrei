import json
from sqlalchemy import create_engine, text
from config import DB_URI, json_file

def populate_db(url=json_file):
    """
    Remplit la table 'tweets' depuis un fichier JSON.
    
    :param json_file: Chemin du fichier JSON contenant les tweets
    """
    # Charger les données JSON
    try:
        with open(url, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Chargement des données JSON réussi : {data}")
    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON : {e}")
        return

    # Vérifier que le JSON contient une liste de tweets
    if not isinstance(data, list):
        print("Le fichier JSON doit contenir une liste de tweets.")
        return

    # Connexion à la base de données
    engine = create_engine(DB_URI, echo=True)
    try:
        with engine.connect() as connection:
            with connection.begin():  # Transaction explicite
                for tweet in data:
                    query = text(
                        """
                        INSERT INTO tweets (text, positive, negative)
                        VALUES (:text, :positive, :negative)
                        """
                    )
                    connection.execute(query, {
                        'text': tweet['text'],
                        'positive': tweet['positive'],
                        'negative': tweet['negative']
                    })
                    print(f"Tweet inséré : {tweet['text']}")
        print("Les données ont été insérées avec succès dans la base de données.")

    except Exception as e:
        print(f"Erreur lors de l'insertion des données : {e}")

def get_all_tweets():
    """
    Récupère tous les tweets de la base de données et les renvoie sous forme de JSON.
    """
    engine = create_engine(DB_URI, echo=True)
    try:
        with engine.connect() as connection:
            query = text('SELECT * FROM tweets')
            result = connection.execute(query).fetchall()
            tweets = [row[1] for row in result]
            positive = [row[2] for row in result]
            negative = [row[3] for row in result]
            return [{'tweets': tweet, 'positive': pos, 'negative': neg} for tweet, pos, neg in zip(tweets, positive, negative)]
    except Exception as e:
        print(f"Erreur lors de la récupération des tweets : {e}")
        return json.dumps({"error": str(e)})
    
def populate_db_from_file(file_path):
    """
    Remplit la table 'tweets' depuis un fichier texte contenant des tweets et leur polarité.
    
    :param file_path: Chemin du fichier texte contenant les tweets et leur polarité
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"Chargement des données du fichier réussi : {file_path}")
    except Exception as e:
        print(f"Erreur lors du chargement du fichier : {e}")
        return

    # Connexion à la base de données
    engine = create_engine(DB_URI, echo=True)
    try:
        with engine.connect() as connection:
            with connection.begin():  # Transaction explicite
                for line in lines:
                    line = line.rstrip()  # Supprimer les espaces à la fin de la ligne
                    txt = line[:-1].rstrip()  # Le texte du tweet sans le dernier caractère et sans espaces à la fin
                    polarity = line[-1]  # Le dernier caractère de la ligne
                    positive = 1 if polarity == '1' else 0
                    negative = 1 if polarity == '0' else 0
                    query = text(
                        """
                        INSERT INTO tweets (text, positive, negative)
                        VALUES (:text, :positive, :negative)
                        """
                    )
                    print(f"Ligne : {query}")
                    connection.execute(query, {
                        'text': txt,
                        'positive': positive,
                        'negative': negative
                    })
                    print(f"Tweet inséré : {txt}")
        print("Les données ont été insérées avec succès dans la base de données.")

    except Exception as e:
        print(f"Erreur lors de l'insertion des données : {e}")