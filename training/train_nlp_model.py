import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ..backend.models.nlp_model import NLPModel
from ..backend.models.emotion_detector import EmotionDetector

import json

def train_models():
    """Train all models with sample data."""
    
    # Extended intent training data
    intent_data = {
        "intents": {
            "greeting": [
                "hello", "hi", "hey", "good morning", "good evening", "good afternoon",
                "hello eric", "hi eric", "hey eric", "greetings", "howdy",
                "what's up", "how are you", "nice to meet you"
            ],
            "remember_fact": [
                "remember that", "please remember", "don't forget", "keep in mind",
                "save this information", "remember this", "note that", "store this",
                "I want you to remember", "please save", "commit to memory"
            ],
            "remember_event": [
                "remind me", "schedule", "appointment", "meeting", "set a reminder",
                "remember my exam", "i have a meeting", "don't let me forget",
                "schedule an event", "add to calendar", "set up appointment",
                "book a meeting", "plan for", "remind me about"
            ],
            "retrieve_memory": [
                "what do you remember", "recall", "what did i tell you",
                "do you remember when", "what was that about", "tell me what you know",
                "search your memory", "what do you know about", "remind me about",
                "what information do you have", "look up", "find information about"
            ],
            "play_music": [
                "play song", "play music", "next song", "previous song", "skip song",
                "pause music", "stop music", "play", "start music", "resume music",
                "change song", "shuffle", "repeat", "turn on music", "music on"
            ],
            "question_answering": [
                "what is", "tell me about", "explain", "how does", "what does",
                "who is", "where is", "when did", "why is", "how to",
                "can you explain", "help me understand", "what's the meaning",
                "define", "describe", "give me information about"
            ],
            "goodbye": [
                "goodbye", "bye", "see you later", "talk to you later", "farewell",
                "exit", "quit", "end conversation", "that's all", "thank you",
                "good night", "see you", "catch you later", "until next time"
            ],
            "emotion_query": [
                "how do i feel", "what's my mood", "analyze my emotion", "my current emotion",
                "am i happy", "am i sad", "what emotion am i showing", "detect my mood",
                "how am i feeling", "what's my emotional state", "mood check"
            ],
            "time_query": [
                "what time is it", "current time", "what's the time", "time please",
                "tell me the time", "what time", "clock", "current hour"
            ],
            "weather_query": [
                "what's the weather", "weather today", "how's the weather", "temperature",
                "is it raining", "will it rain", "weather forecast", "climate today"
            ],
            "help": [
                "help", "what can you do", "your capabilities", "how can you help",
                "what are your features", "commands", "instructions", "guide me",
                "what's possible", "your functions", "assistance"
            ]
        }
    }
    
    # Extended emotion training data
    emotion_data = {
        "emotions": {
            "joy": [
                "I'm so happy", "This is great", "Wonderful", "Amazing", "Fantastic",
                "I love this", "Excellent", "Perfect", "Awesome", "Brilliant",
                "I'm thrilled", "This makes me smile", "Feeling great", "Super excited",
                "I'm delighted", "This is fantastic", "Absolutely wonderful", "I'm ecstatic"
            ],
            "sadness": [
                "I'm sad", "This is terrible", "I hate this", "Awful", "Horrible",
                "I'm depressed", "Bad day", "Feel down", "I'm unhappy", "This sucks",
                "I'm disappointed", "Feeling blue", "Not good", "I'm upset",
                "This is depressing", "I'm heartbroken", "Feeling low", "I'm miserable"
            ],
            "anger": [
                "I'm angry", "This is frustrating", "I hate it", "So annoying", "Furious",
                "Makes me mad", "Irritating", "I'm pissed", "This angers me", "Infuriating",
                "I'm outraged", "This is ridiculous", "I'm livid", "Extremely annoyed",
                "This makes me furious", "I'm steaming", "Absolutely frustrated"
            ],
            "fear": [
                "I'm scared", "This is frightening", "Worried about", "Afraid of", "Terrified",
                "Afraid", "Nervous", "Anxious", "I'm worried", "This scares me",
                "I'm terrified", "Feeling anxious", "This is scary", "I'm frightened",
                "Makes me nervous", "I'm panicking", "This worries me", "Feeling fearful"
            ],
            "surprise": [
                "Wow", "Incredible", "Can't believe", "Shocking", "Unbelievable",
                "Surprising", "Didn't expect", "Amazing", "Astonishing", "Remarkable",
                "What a surprise", "Unexpected", "I'm shocked", "That's surprising",
                "Hard to believe", "Startling", "Mind-blowing", "Speechless"
            ],
            "neutral": [
                "Okay", "Sure", "Yes", "No", "Maybe", "I think", "Alright",
                "Probably", "Normal day", "Fine", "Whatever", "Could be", "Perhaps",
                "Possibly", "I suppose", "Seems fine", "Nothing special", "Regular",
                "As usual", "Standard", "Typical", "Ordinary", "Average day"
            ]
        }
    }
    
    # Train NLP model
    print("Training NLP model...")
    nlp_model = NLPModel()
    nlp_model.train_model(intent_data)
    print("NLP model training completed!")
    
    # Train emotion model
    print("Training emotion detection model...")
    emotion_detector = EmotionDetector()
    emotion_detector.train_text_emotion_model(emotion_data)
    print("Emotion model training completed!")
    
    # Test the models
    print("\nTesting models...")
    
    # Test NLP model
    test_phrases = [
        "Hello Eric, how are you?",
        "Please remember that I have a meeting tomorrow",
        "What do you remember about my preferences?",
        "Play some music please",
        "I'm feeling really happy today",
        "Goodbye for now"
    ]
    
    for phrase in test_phrases:
        intent, confidence = nlp_model.predict_intent(phrase)
        emotion, emotion_conf = emotion_detector.detect_text_emotion(phrase)
        print(f"Text: '{phrase}'")
        print(f"  Intent: {intent} (confidence: {confidence:.3f})")
        print(f"  Emotion: {emotion} (confidence: {emotion_conf:.3f})")
        print()

if __name__ == "__main__":
    train_models()