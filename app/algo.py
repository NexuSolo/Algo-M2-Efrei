import re
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

def training(data, positive = True):
    df = pd.DataFrame(data)
    df['tweets_cleaned'] = df['tweets'].apply(cleaningData)
    stopWords = ['the']
    vectorizer = CountVectorizer(stop_words=stopWords, max_features=100)
    X = vectorizer.fit_transform(df['tweets_cleaned'])
    y = df['positive'] if positive else df['negative']

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    print("Accuracy: ", model.score(x_test, y_test))
    print("Rapport de classification :")
    print(classification_report(y_test, y_pred))
    # Matrice de confusion
    print("Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred))

    return model, vectorizer

def cleaningData(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) # Supprimer les caractères spéciaux
    return text