import pickle
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
import cv2
from config import Config

class EmotionDetector:
    def __init__(self):
        self.text_pipeline = None
        self.emotion_labels = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']
        self.load_model()
    
    def detect_text_emotion(self, text: str) -> tuple:
        """Detect emotion from text."""
        # Use TextBlob for basic sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Map polarity to emotion
        if polarity > 0.3:
            emotion = "joy"
            confidence = min(polarity * 2, 1.0)
        elif polarity < -0.3:
            emotion = "sadness"
            confidence = min(abs(polarity) * 2, 1.0)
        elif subjectivity > 0.7:
            emotion = "surprise"
            confidence = subjectivity
        else:
            emotion = "neutral"
            confidence = 0.7
        
        # If we have a trained model, use it for better accuracy
        if self.text_pipeline:
            try:
                predicted_emotion = self.text_pipeline.predict([text])[0]
                confidence_scores = self.text_pipeline.predict_proba([text])[0]
                max_confidence = max(confidence_scores)
                
                if max_confidence > confidence:
                    emotion = predicted_emotion
                    confidence = max_confidence
            except Exception as e:
                print(f"Error using trained emotion model: {e}")
        
        return emotion, confidence
    
    def detect_face_emotion(self, frame) -> tuple:
        """Detect emotion from facial expression."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # For now, return a simple emotion based on face detection
                # In a real implementation, you would use a trained emotion detection model
                return "neutral", 0.8
            else:
                return "unknown", 0.0
                
        except Exception as e:
            print(f"Error detecting face emotion: {e}")
            return "unknown", 0.0
    
    def train_text_emotion_model(self, training_data: dict):
        """Train emotion detection model."""
        texts = []
        labels = []
        
        for emotion, examples in training_data['emotions'].items():
            for example in examples:
                texts.append(example)
                labels.append(emotion)
        
        # Create pipeline
        self.text_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', SVC(probability=True, kernel='linear'))
        ])
        
        # Train model
        self.text_pipeline.fit(texts, labels)
        
        # Save model
        self.save_model()
    
    def save_model(self):
        """Save the emotion model."""
        if self.text_pipeline:
            with open(Config.EMOTION_MODEL_PATH, 'wb') as f:
                pickle.dump(self.text_pipeline, f)
    
    def load_model(self):
        """Load the emotion model."""
        try:
            with open(Config.EMOTION_MODEL_PATH, 'rb') as f:
                self.text_pipeline = pickle.load(f)
        except FileNotFoundError:
            print("No trained emotion model found.")