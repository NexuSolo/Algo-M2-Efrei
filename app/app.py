import os
import re
import pandas as pd
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import kagglehub
from config import DB_URI, BATCH_SIZE
from db_operations import count_tweets, insert_tweets_batch
from algo import cleaningData
from model_scheduler import model_manager
from utils import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def is_valid_tweet(text):
    return bool(re.match(r'^[a-zA-Z0-9\s.,!?\'\"@#-]+$', str(text)))

def download_and_process_kaggle_data():
    try:
        logger.info("Démarrage du téléchargement des données Kaggle")
        path = kagglehub.dataset_download("kazanova/sentiment140")
        csv_file = os.path.join(path, "training.1600000.processed.noemoticon.csv")
        df = pd.read_csv(csv_file, encoding='latin-1', header=None)
        df.columns = ['polarity', 'id', 'date', 'query', 'user', 'text']
        
        total_tweets = len(df)
        logger.info(f"Nombre total de tweets téléchargés: {total_tweets}")
        
        # Filtrer les tweets valides
        valid_mask = df['text'].apply(is_valid_tweet)
        df_filtered = df[valid_mask].copy()
        
        rejected_tweets = total_tweets - len(df_filtered)
        logger.info(f"Tweets rejetés (caractères spéciaux): {rejected_tweets}")
        
        # Préparation des données
        df_filtered.loc[:, 'positive'] = df_filtered['polarity'].apply(lambda x: 1 if x > 2 else 0)
        df_filtered.loc[:, 'negative'] = df_filtered['polarity'].apply(lambda x: 1 if x < 2 else 0)
        df_filtered = df_filtered.sample(frac=1).reset_index(drop=True)
        
        batch_values = []
        total_valid = len(df_filtered)
        accepted_tweets = 0
        
        # Traitement par lots
        for i, row in df_filtered.iterrows():
            # Création d'un tuple avec les données
            tweet_tuple = (str(row['text']), int(row['positive']), int(row['negative']))
            batch_values.append(tweet_tuple)
            
            if len(batch_values) >= BATCH_SIZE or i == total_valid - 1:
                if insert_tweets_batch(batch_values):
                    accepted_tweets += len(batch_values)
                    progress = ((i + 1) / total_valid) * 100
                    if progress % 5 < (BATCH_SIZE / total_valid * 100):
                        logger.info(f"Progression: {progress:.1f}% ({i + 1}/{total_valid} tweets insérés)")
                batch_values = []

        logger.info("\nRésumé final:")
        logger.info(f"Total tweets initiaux: {total_tweets}")
        logger.info(f"Tweets acceptés et insérés: {accepted_tweets}")
        logger.info(f"Tweets rejetés: {rejected_tweets}")
        return accepted_tweets > 0
    except Exception as e:
        logger.error(f"Erreur lors du traitement des données Kaggle: {e}")
        return False

def initialize_app():
    try:
        logger.info("Démarrage de l'initialisation de l'application...")
        with app.app_context():
            tweet_count = count_tweets()
            if tweet_count == 0:
                logger.info("Base de données vide. Démarrage du téléchargement des données...")
                if not download_and_process_kaggle_data():
                    logger.error("Échec de l'initialisation des données")
                    return False

            logger.info("Démarrage de l'entraînement initial des modèles...")
            model_manager.retrain_models()
            model_manager.start_scheduler()
            logger.info("Initialisation de l'application terminée")
            return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de l'application: {e}")
        return False

@app.route('/analyse', methods=['POST'])
def analyse():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid input, expected JSON"}), 400

        data = request.get_json()
        tweets = data.get('tweets', [])

        if not isinstance(tweets, list):
            return jsonify({"error": "Invalid input, expected a list of tweets"}), 400

        models = model_manager.get_models()
        if not all(models.values()):
            return jsonify({"error": "Models not ready. Please wait for training to complete."}), 503

        results = {}
        for tweet in tweets:
            if not isinstance(tweet, str):
                continue

            tweet_cleaned = cleaningData(tweet)
            tweet_vectorized_positive = models['vectorizer_positive'].transform([tweet_cleaned])
            tweet_vectorized_negative = models['vectorizer_negative'].transform([tweet_cleaned])
            
            # Les predict_proba retournent déjà des probabilités entre 0 et 1
            # [0][1] prend la probabilité de la classe positive (1)
            positive_score = models['model_positive'].predict_proba(tweet_vectorized_positive)[0][1]
            negative_score = models['model_negative'].predict_proba(tweet_vectorized_negative)[0][1]
            
            # Si positive_score est élevé (proche de 1) et negative_score est bas (proche de 0)
            # alors tweet_score sera proche de 1
            # Si positive_score est bas (proche de 0) et negative_score est élevé (proche de 1)
            # alors tweet_score sera proche de -1
            tweet_score = positive_score - negative_score

            results[tweet] = tweet_score

        return jsonify(results)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des tweets: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    if initialize_app():
        app.run(host='127.0.0.1', port=5000, debug=False)
    else:
        logger.error("L'application n'a pas pu démarrer à cause d'erreurs d'initialisation")