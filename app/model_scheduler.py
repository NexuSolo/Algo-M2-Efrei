from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading

from config import SCHEDULER_INTERVAL
from db_operations import get_all_tweets
from algo import training
from utils import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

class ModelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.model_positive = None
        self.vectorizer_positive = None
        self.model_negative = None
        self.vectorizer_negative = None
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()
        self._is_training = False
        self._training_lock = threading.Lock()

    def setup_scheduler(self):
        """Configure le scheduler pour le réentraînement périodique"""
        self.scheduler.add_job(
            func=self.retrain_models,
            trigger=IntervalTrigger(seconds=SCHEDULER_INTERVAL),
            id='retrain_models',
            name='Retrain models periodically',
            replace_existing=True
        )

    def start_scheduler(self):
        """Démarre le scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")

    def stop_scheduler(self):
        """Arrête le scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def retrain_models(self):
        """Réentraîne les modèles avec les données actuelles"""
        with self._training_lock:
            if self._is_training:
                logger.info("Training already in progress, skipping...")
                return
                
            self._is_training = True
            try:
                logger.info("Starting model retraining...")
                data = get_all_tweets()
                if not data:
                    logger.error("No data available for training")
                    return

                logger.info("Training positive sentiment model...")
                self.model_positive, self.vectorizer_positive = training(data)
                
                logger.info("Training negative sentiment model...")
                self.model_negative, self.vectorizer_negative = training(data, positive=False)
                
                logger.info("Models retrained successfully")
                
            except Exception as e:
                logger.error(f"Error during model retraining: {e}")
            finally:
                self._is_training = False

    def get_models(self):
        """Retourne les modèles et vectorizers actuels"""
        return {
            'model_positive': self.model_positive,
            'vectorizer_positive': self.vectorizer_positive,
            'model_negative': self.model_negative,
            'vectorizer_negative': self.vectorizer_negative
        }

# Instance globale du ModelManager
model_manager = ModelManager()