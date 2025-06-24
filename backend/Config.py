import os
from pathlib import Path

class Config:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    BACKEND_DIR = BASE_DIR / "backend"
    FRONTEND_DIR = BASE_DIR / "frontend"
    DATA_DIR = BACKEND_DIR / "data"
    MODEL_DIR = DATA_DIR / "models"
    DATABASE_DIR = BACKEND_DIR / "database"
    
    # Database
    DATABASE_PATH = DATABASE_DIR / "eric_memory.db"
    
    # Models
    NLP_MODEL_PATH = MODEL_DIR / "nlp_model.pkl"
    EMOTION_MODEL_PATH = MODEL_DIR / "emotion_model.pkl"
    FACE_ENCODINGS_PATH = MODEL_DIR / "face_encodings.pkl"
    
    # Voice settings
    VOICE_RATE = 150
    VOICE_VOLUME = 0.9
    
    # Security
    FACE_RECOGNITION_TOLERANCE = 0.6
    MAX_LOGIN_ATTEMPTS = 3
    
    # API Keys (set as environment variables)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "logs" / "eric.log"