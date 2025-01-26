import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import DB_URI, txt_repository
from db_operations import get_all_tweets, populate_db, populate_db_from_file
from algo import cleaningData, training

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

phrases = [
        # Phrases positives
        "This service is absolutely amazing, I love it!",
        "I'm thrilled with how well this worked for me!",
        "Best experience I've had in a long time!",
        "I can't stop recommending this to my friends!",
        "The quality of this product is top-notch!",
        "I'm so happy I gave this a try!",
        "This app has made my life so much easier!",
        "Everything about this is just perfect!",
        "Exceptional! I'll definitely come back again.",
        "This exceeded all of my expectations!",
        "I'm beyond satisfied with the results!",
        "The customer support was phenomenal!",
        "This product solved all of my problems!",
        "What a fantastic value for the price!",
        "This event was incredibly well-organized.",
        "I feel so lucky to have found this!",
        "This was exactly what I needed, thank you!",
        "Highly efficient and incredibly user-friendly!",
        "Such a wonderful surprise, totally worth it!",
        "This turned out to be even better than I expected!",

        # Phrases négatives
        "This was an absolute waste of time.",
        "I'm so disappointed with how this turned out.",
        "Terrible quality, I expected much better.",
        "This product broke after just one use.",
        "I can't believe I paid for this garbage.",
        "The service was extremely slow and unhelpful.",
        "Nothing about this works as advertised.",
        "This app is full of bugs and glitches.",
        "I've never been so frustrated with a purchase.",
        "This company clearly doesn't value its customers.",
        "Completely unreliable, wouldn't recommend.",
        "This was a total failure from start to finish.",
        "I'm returning this as soon as possible.",
        "Worst experience I've had in years.",
        "This is overpriced and underdelivers.",
        "The event was poorly managed and chaotic.",
        "I wish I had never tried this out.",
        "Such a letdown, I'm extremely dissatisfied.",
        "This caused me nothing but trouble.",
        "I regret trusting the reviews, it's awful."
    ]

@app.route('/test_db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Database connected successfully!"
    except Exception as e:
        return str(e)

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
        # logique d'analyse pour calculer le score de chaque tweet
        score = len(tweet)
        results[tweet] = score

    return jsonify(results)

@app.route('/tweets', methods=['GET'])
def get_tweets():
    try:
        query = text('SELECT * FROM tweets')
        result = db.session.execute(query).fetchall()
        tweets = [{'id': row[0], 'text': row[1], 'positive': row[2], 'negative': row[3]} for row in result]
        return jsonify(tweets)
    except Exception as e:
        return str(e)
    
@app.route('/training')
def essaie():
    data = get_all_tweets()
    if not data:
        return jsonify({"error": "No data found"}), 404
    
    # Entraînement des modèles
    model_positive, vectorizer_positive = training(data)
    model_negative, vectorizer_negative = training(data, positive=False)

    # Analyse des phrases
    results = {}
    for phrase in phrases:
        # Calcul du score positif et négatif
        phrase_cleaned = cleaningData(phrase)
        phrase_vector = vectorizer_positive.transform([phrase_cleaned])
        score_positive = model_positive.predict_proba(phrase_vector)[0][1]
        
        phrase_vector = vectorizer_negative.transform([phrase_cleaned])
        score_negative = model_negative.predict_proba(phrase_vector)[0][1]
        
        # Calcul du score final
        score = score_positive - score_negative
        results[phrase] = score
        
        # Détermination de la polarité
        polarite = "positive" if score >= 0 else "negative"
        print(f"Phrase: {phrase}\nScore: {score}\nPolarité: {polarite}\n")

    return jsonify({"message": "Training and analysis completed successfully", "results": results})



if __name__ == '__main__':
    with app.app_context():
        # Récupérer les tweets, si aucun tweet n'est trouvé, lancer la fonction populate_db du fichier populate_db.py
        try:
            with db.engine.connect() as connection:
                query = text('SELECT COUNT(*) FROM tweets')
                result = connection.execute(query).fetchone()
                if result[0] == 0:
                    print("Aucun tweet trouvé dans la base de données. Remplissage de la base de données...")
                    populate_db()
                else:
                    print("Les tweets sont déjà présents dans la base de données.")
                    # Parcourir tous les fichiers dans le répertoire txt_repository
                    # for filename in os.listdir(txt_repository):
                    #     file_path = os.path.join(txt_repository, filename)
                    #     if os.path.isfile(file_path):
                    #         print(f"Traitement du fichier : {file_path}")
                    #         populate_db_from_file(file_path)
        except Exception as e:
            print(f"Erreur lors de la vérification des tweets : {e}")
    app.run(debug=True)