from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_URI
from utils import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

def get_connection():
    """Crée et retourne une connexion à la base de données"""
    try:
        engine = create_engine(DB_URI)
        return engine.connect()
    except SQLAlchemyError as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        raise

def get_all_tweets():
    """
    Récupère tous les tweets de la base de données.
    Returns:
        list: Liste de dictionnaires contenant les tweets et leurs classifications
    """
    try:
        with get_connection() as connection:
            query = text('SELECT * FROM tweets')
            result = connection.execute(query).fetchall()
            tweets_data = [
                {
                    'tweets': row[1],
                    'positive': row[2],
                    'negative': row[3]
                }
                for row in result
            ]
            logger.info(f"Récupération réussie de {len(tweets_data)} tweets")
            return tweets_data
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la récupération des tweets: {e}")
        return []

def count_tweets():
    """
    Compte le nombre de tweets dans la base de données
    Returns:
        int: Nombre de tweets
    """
    try:
        with get_connection() as connection:
            query = text('SELECT COUNT(*) FROM tweets')
            result = connection.execute(query).fetchone()
            count = result[0]
            logger.info(f"Nombre de tweets en base: {count}")
            return count
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors du comptage des tweets: {e}")
        return 0

def insert_tweets_batch(tweets_data):
    """
    Insère un lot de tweets dans la base de données
    Args:
        tweets_data (list): Liste de tuples (text, positive, negative)
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Validation des données
        if not isinstance(tweets_data, list) or not tweets_data:
            logger.error("Les données doivent être une liste non vide")
            return False

        # Vérification basique du format des tuples
        for tweet_tuple in tweets_data:
            if not isinstance(tweet_tuple, tuple) or len(tweet_tuple) != 3:
                logger.error(f"Format invalide pour le tweet: {tweet_tuple}")
                return False

        with get_connection() as connection:
            with connection.begin():
                query = text(
                    "INSERT INTO tweets (text, positive, negative) VALUES (:text, :positive, :negative)"
                )
                
                # Execute the query for each batch of parameters
                connection.execute(
                    query,
                    [
                        {"text": str(text), "positive": int(positive), "negative": int(negative)}
                        for text, positive, negative in tweets_data
                    ]
                )
                
                logger.info(f"Insertion réussie de {len(tweets_data)} tweets")
                return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de l'insertion des tweets: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'insertion des tweets: {e}")
        return False