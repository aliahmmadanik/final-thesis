
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from Config import Config as Config

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NLPModel:
    def __init__(self):
        self.pipeline = None
        self.intent_labels = []
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load trained model if exists
        self.load_model()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for NLP processing."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) 
                 for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def train_model(self, training_data: dict):
        """Train the NLP model with intent classification."""
        texts = []
        labels = []
        
        for intent, examples in training_data['intents'].items():
            for example in examples:
                texts.append(self.preprocess_text(example))
                labels.append(intent)
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        self.pipeline.fit(X_train, y_train)
        self.intent_labels = list(set(labels))
        
        # Evaluate
        accuracy = self.pipeline.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.4f}")
        
        # Save model
        self.save_model()
    
    def predict_intent(self, text: str) -> tuple:
        """Predict intent from text."""
        if not self.pipeline:
            return "unknown", 0.0
        
        processed_text = self.preprocess_text(text)
        
        # Predict intent
        intent = self.pipeline.predict([processed_text])[0]
        
        # Get confidence scores
        probabilities = self.pipeline.predict_proba([processed_text])[0]
        confidence = max(probabilities)
        
        return intent, confidence
    
    def extract_entities(self, text: str, intent: str) -> dict:
        """Extract entities based on intent."""
        entities = {}
        text_lower = text.lower()
        
        if intent == "remember_event":
            # Extract date patterns
            date_patterns = [
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
                r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
                r'(today|tomorrow|next week|next month)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities['date'] = match.group()
                    break
            
            # Extract event description
            remember_keywords = ['remember', 'remind', 'event', 'appointment']
            for keyword in remember_keywords:
                if keyword in text_lower:
                    # Extract text after the keyword
                    parts = text_lower.split(keyword, 1)
                    if len(parts) > 1:
                        entities['description'] = parts[1].strip()
                        break
        
        elif intent == "play_music":
            # Extract song/artist names
            music_keywords = ['play', 'song', 'music', 'artist']
            for keyword in music_keywords:
                if keyword in text_lower:
                    parts = text_lower.split(keyword, 1)
                    if len(parts) > 1:
                        entities['query'] = parts[1].strip()
                        break
        
        return entities
    
    def save_model(self):
        """Save the trained model."""
        if self.pipeline:
            model_data = {
                'pipeline': self.pipeline,
                'intent_labels': self.intent_labels
            }
            with open(Config.NLP_MODEL_PATH, 'wb') as f:
                pickle.dump(model_data, f)
    
    def load_model(self):
        """Load the trained model."""
        try:
            with open(Config.NLP_MODEL_PATH, 'rb') as f:
                model_data = pickle.load(f)
                self.pipeline = model_data['pipeline']
                self.intent_labels = model_data['intent_labels']
        except FileNotFoundError:
            print("No trained model found. Please train the model first.")