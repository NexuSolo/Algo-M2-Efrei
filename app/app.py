import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from config import DB_URI
from db_operations import get_all_tweets
from algo import cleaningData, training
import kagglehub

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def download_and_process_kaggle_data():
    path = kagglehub.dataset_download("kazanova/sentiment140")
    print("Path to dataset files:", path)
    csv_file = os.path.join(path, "training.1600000.processed.noemoticon.csv")
    df = pd.read_csv(csv_file, encoding='latin-1', header=None)
    df.columns = ['polarity', 'id', 'date', 'query', 'user', 'text']
    
    # Convertir les scores de polarité
    df['positive'] = df['polarity'].apply(lambda x: 1 if x > 2 else 0)
    df['negative'] = df['polarity'].apply(lambda x: 1 if x < 2 else 0)
    
    # Mélanger les données
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Insérer les données dans la base de données
    engine = create_engine(DB_URI)
    try:
        with engine.connect() as connection:
            with connection.begin():  # Transaction explicite
                for i, (_, row) in enumerate(df.iterrows()):
                    query = text(
                        """
                        INSERT INTO tweets (text, positive, negative)
                        VALUES (:text, :positive, :negative)
                        """
                    )
                    connection.execute(query, text=row['text'], positive=row['positive'], negative=row['negative'])
        print("Les données Kaggle ont été insérées avec succès dans la base de données.")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données Kaggle : {e}")

@app.route('/analyse', methods=['POST'])
def analyse():
    if not request.is_json:
        return jsonify({"error": "Invalid input, expected JSON"}), 400

    data = request.get_json()
    tweets = data.get('tweets', [])

    if not isinstance(tweets, list):
        return jsonify({"error": "Invalid input, expected a list of tweets"}), 400

    results = {}
    for tweet in tweets:
        if isinstance(tweet, str):
            tweet_text = tweet
        else:
            continue  # Skip invalid entries

        # Logique d'analyse pour calculer le score positif et négatif
        tweet_cleaned = cleaningData(tweet_text)
        tweet_vectorized_positive = vectorizer_positive.transform([tweet_cleaned])
        tweet_vectorized_negative = vectorizer_negative.transform([tweet_cleaned])
        tweet_score_positive = model_positive.predict_proba(tweet_vectorized_positive)[0][1]
        tweet_score_negative = model_negative.predict_proba(tweet_vectorized_negative)[0][1]
        tweet_score = tweet_score_positive - tweet_score_negative
        
        # Normaliser le score entre -1 et 1
        tweet_score = 2 * (tweet_score - 0.5)
        results[tweet_text] = tweet_score

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        # Récupérer les tweets, si aucun tweet n'est trouvé, lancer la fonction populate_db du fichier populate_db.py
        try:
            with db.engine.connect() as connection:
                query = text('SELECT COUNT(*) FROM tweets')
                result = connection.execute(query).fetchone()
                if result[0] == 0:
                    print("Aucun tweet trouvé dans la base de données. Téléchargement des données Kaggle...")
                    download_and_process_kaggle_data()
        except Exception as e:
            print(f"Erreur lors de la vérification des tweets : {e}")

        # Entraînement des modèles
        data = get_all_tweets()
        if not data:
            print("Erreur: Aucun tweet trouvé pour l'entraînement.")
        else:
            global model_positive, vectorizer_positive, model_negative, vectorizer_negative
            model_positive, vectorizer_positive = training(data)
            model_negative, vectorizer_negative = training(data, positive=False)
            print("Entraînement des modèles terminé.")

    app.run(debug=True)