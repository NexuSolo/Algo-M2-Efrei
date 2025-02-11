import os
import logging
from config import LOG_FORMAT, LOG_LEVEL, LOG_FILE

def setup_logger(name):
    """Configure un logger avec handlers pour console et fichier"""
    # Création du dossier log s'il n'existe pas
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Éviter d'ajouter des handlers en double
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler pour le fichier
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger