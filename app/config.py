import os
import logging

# Configuration de base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_URI = 'mysql+pymysql://user:userpassword@127.0.0.1:3306/tweets_db'

# Configuration du logging
LOG_FILE = os.path.join(BASE_DIR, 'log', 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# Configuration du scheduler
SCHEDULER_INTERVAL = 3600  # Réentraînement toutes les heures
BATCH_SIZE = 50000  # Taille des lots pour l'insertion en base

# Configuration du modèle
MODEL_FEATURES = 2500  # Nombre maximum de features pour le vectorizer
TEST_SIZE = 0.15  # Proportion du jeu de test
RANDOM_STATE = 50  # Seed pour la reproductibilité