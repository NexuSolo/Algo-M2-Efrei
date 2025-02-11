import json
from sqlalchemy import create_engine, text
from config import DB_URI

def get_all_tweets():
    """
    Récupère tous les tweets de la base de données et les renvoie sous forme de JSON.
    """
    engine = create_engine(DB_URI)
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