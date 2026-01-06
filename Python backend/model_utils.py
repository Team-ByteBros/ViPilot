import logging
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Singleton class to manage the SentenceTransformer model.
    Ensures the model is loaded only once across the application.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def get_model(self, model_name='all-MiniLM-L6-v2'):
        """
        Returns the shared model instance. Loads it if not already loaded.
        """
        if self._model is None:
            try:
                logger.info(f"Loading SentenceTransformer model: {model_name}...")
                self._model = SentenceTransformer(model_name)
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                self._model = None
        return self._model
