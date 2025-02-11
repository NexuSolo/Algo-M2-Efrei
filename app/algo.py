import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from config import MODEL_FEATURES
from utils import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

def training(data, positive = True):
    """
    Entraîne un modèle de classification binaire.
    Pour le modèle positif : 1 = positif, 0 = non positif
    Pour le modèle négatif : 1 = négatif, 0 = non négatif
    """
    model_type = "POSITIVE" if positive else "NEGATIVE"
    logger.info(f"\n=== Démarrage de l'entraînement du modèle {model_type} ===")
    
    df = pd.DataFrame(data)
    df['tweets_cleaned'] = df['tweets'].apply(cleaningData)
    
    # Liste enrichie de stopwords
    stopWords = [
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'over', 'after', 'is', 'am', 'are', 'was',
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'me', 'him',
        'her', 'its', 'us', 'them'
    ]
    
    vectorizer = CountVectorizer(stop_words=stopWords, max_features=MODEL_FEATURES)
    X = vectorizer.fit_transform(df['tweets_cleaned'])
    y = df['positive'] if positive else df['negative']

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=50)
    
    logger.info(f"Taille du jeu d'entraînement : {x_train.shape[0]} échantillons")
    logger.info(f"Taille du jeu de test : {x_test.shape[0]} échantillons")
    
    # Ajout du paramètre C pour ajuster la régularisation
    model = LogisticRegression(class_weight='balanced', max_iter=1000, C=1.5)
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    accuracy = model.score(x_test, y_test)
    logger.info(f"Accuracy du modèle {model_type}: {accuracy}")
    logger.info(f"Rapport de classification du modèle {model_type}:")
    logger.info(f"\n{classification_report(y_test, y_pred)}")
    logger.info(f"Matrice de confusion du modèle {model_type}:")
    logger.info(f"\n{confusion_matrix(y_test, y_pred)}")
    logger.info("=" * 50)

    return model, vectorizer

def cleaningData(text):
    # Amélioration du nettoyage
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    # Conserver certains caractères spéciaux significatifs
    text = re.sub(r'[^\w\s!?.]', '', text)
    # Supprimer les URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Supprimer les mentions
    text = re.sub(r'@\w+', '', text)
    # Supprimer les hashtags
    text = re.sub(r'#\w+', '', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()