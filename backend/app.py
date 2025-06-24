import eel
import threading
import time
import cv2
import base64
import json
import datetime
from pathlib import Path

# Import our modules
from config import Config
from database.init_db import initialize_database
from core.memory_manager import MemoryManager
from core.voice_handler import VoiceHandler
from core.scheduler import TaskScheduler
from core.context_manager import ContextManager
from models.nlp_model import NLPModel
from models.emotion_detector import EmotionDetector
from models.face_recognition import FaceRecognitionSystem

class EricAIAssistant:
    def __init__(self):
        # Initialize database
        initialize_database()
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.voice_handler = VoiceHandler()
        self.scheduler = TaskScheduler(self.memory_manager)
        self.context_manager = ContextManager(self.memory_manager)
        self.nlp_model = NLPModel()
        self.emotion_detector = EmotionDetector()
        self.face_recognition = FaceRecognitionSystem()
        
        # State management
        self.is_authenticated = False
        self.current_user = "default_user"
        self.is_listening = False
        self.camera = None
        
        # Load training data and train models if needed
        self.train_models_if_needed()
        
        # Setup scheduler callbacks
        self.scheduler.add_reminder_callback(self.handle_reminder)
        
    def train_models_if_needed(self):
        """Train models if they don't exist."""
        # Training data for intents
        intent_data = {
            "intents": {
                "greeting": [
                    "hello", "hi", "hey", "good morning", "good evening",
                    "hello eric", "hi eric", "hey eric"
                ],
                "remember_fact": [
                    "remember that", "please remember", "don't forget",
                    "save this information", "remember this"
                ],
                "remember_event": [
                    "remind me", "schedule", "appointment", "meeting",
                    "remember my exam", "i have a meeting", "set reminder"
                ],
                "retrieve_memory": [
                    "what do you remember", "recall", "what did i tell you",
                    "do you remember when", "what was that about"
                ],
                "play_music": [
                    "play song", "play music", "next song", "previous song",
                    "pause music", "stop music", "play"
                ],
                "question_answering": [
                    "what is", "tell me about", "explain", "how does",
                    "who is", "where is", "when did"
                ],
                "goodbye": [
                    "goodbye", "bye", "see you later", "talk to you later",
                    "exit", "quit"
                ],
                "emotion_query": [
                    "how do i feel", "what's my mood", "analyze my emotion",
                    "am i happy", "am i sad"
                ]
            }
        }
        
        # Train NLP model
        try:
            self.nlp_model.train_model(intent_data)
        except Exception as e:
            print(f"Error training NLP model: {e}")
        
        # Emotion training data
        emotion_data = {
            "emotions": {
                "joy": [
                    "I'm so happy", "This is great", "Wonderful", "Amazing",
                    "I love this", "Fantastic", "Excellent", "Perfect"
                ],
                "sadness": [
                    "I'm sad", "This is terrible", "I hate this", "Awful",
                    "I'm depressed", "Horrible", "Bad day", "Feel down"
                ],
                "anger": [
                    "I'm angry", "This is frustrating", "I hate it",
                    "So annoying", "Makes me mad", "Furious", "Irritating"
                ],
                "fear": [
                    "I'm scared", "This is frightening", "Worried about",
                    "Afraid of", "Nervous", "Anxious", "Terrified"
                ],
                "surprise": [
                    "Wow", "Incredible", "Can't believe", "Shocking",
                    "Unbelievable", "Surprising", "Didn't expect"
                ],
                "neutral": [
                    "Okay", "Sure", "Yes", "No", "Maybe", "I think",
                    "Probably", "Normal day"
                ]
            }
        }
        
        # Train emotion model
        try:
            self.emotion_detector.train_text_emotion_model(emotion_data)
        except Exception as e:
            print(f"Error training emotion model: {e}")
    
    def start(self):
        """Start the Eric AI Assistant."""
        print("Starting Eric AI Assistant...")
        
        # Start scheduler
        self.scheduler.start_scheduler()
        
        # Load context from database
        self.context_manager.load_context_from_db()
        
        # Start voice listening in background
        self.voice_handler.start_continuous_listening()
        
        # Start main processing loop
        self.start_processing_loop()
        
        print("Eric AI Assistant started successfully!")
    
    def start_processing_loop(self):
        """Start the main processing loop."""
        def processing_loop():
            while True:
                try:
                    # Check for voice commands
                    if self.voice_handler.has_commands():
                        command = self.voice_handler.get_command()
                        if command:
                            self.process_command(command, source="voice")
                    
                    # Cleanup expired context periodically
                    self.context_manager.cleanup_expired_context()
                    
                    time.sleep(0.1)  # Small delay to prevent high CPU usage
                    
                except Exception as e:
                    print(f"Error in processing loop: {e}")
                    time.sleep(1)
        
        processing_thread = threading.Thread(target=processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_command(self, command: str, source: str = "text") -> dict:
        """Process a command and return response."""
        try:
            # Detect emotion from text
            emotion, emotion_confidence = self.emotion_detector.detect_text_emotion(command)
            self.memory_manager.store_emotion(emotion, emotion_confidence, command)
            
            # Get intent and confidence
            intent, intent_confidence = self.nlp_model.predict_intent(command)
            
            # Extract entities
            entities = self.nlp_model.extract_entities(command, intent)
            
            # Generate response based on intent
            response = self.generate_response(command, intent, entities, emotion)
            
            # Add to conversation history
            self.context_manager.add_to_conversation(command, response, intent)
            
            # Speak response if from voice
            if source == "voice":
                self.voice_handler.speak(response)
            
            return {
                "response": response,
                "intent": intent,
                "intent_confidence": intent_confidence,
                "emotion": emotion,
                "emotion_confidence": emotion_confidence,
                "entities": entities
            }
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            if source == "voice":
                self.voice_handler.speak(error_msg)
            return {"response": error_msg, "error": True}
    
    def generate_response(self, command: str, intent: str, entities: dict, emotion: str) -> str:
        """Generate appropriate response based on intent and context."""
        
        # Adjust response tone based on emotion
        emotion_prefix = ""
        if emotion == "sadness":
            emotion_prefix = "I sense you might be feeling down. "
        elif emotion == "anger":
            emotion_prefix = "I understand you might be frustrated. "
        elif emotion == "joy":
            emotion_prefix = "I'm glad you seem happy! "
        
        if intent == "greeting":
            responses = [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! I'm Eric, your AI assistant. How may I assist you?"
            ]
            return emotion_prefix + responses[hash(command) % len(responses)]
        
        elif intent == "remember_fact":
            # Extract the fact to remember
            fact_markers = ["remember that", "remember", "don't forget", "save this"]
            fact = command
            for marker in fact_markers:
                if marker in command.lower():
                    fact = command.lower().split(marker, 1)[1].strip()
                    break
            
            if fact:
                success = self.memory_manager.store_memory(
                    content=fact,
                    memory_type="fact",
                    importance_score=2.0
                )
                if success:
                    return f"Got it! I'll remember that {fact}"
                else:
                    return "I had trouble storing that information. Please try again."
            else:
                return "What would you like me to remember?"
        
        elif intent == "remember_event":
            # Parse event details
            event_title = entities.get('description', command)
            event_date_str = entities.get('date', '')
            
            if event_date_str:
                try:
                    # Simple date parsing (you can enhance this)
                    if "tomorrow" in event_date_str:
                        event_date = datetime.datetime.now() + datetime.timedelta(days=1)
                    elif "today" in event_date_str:
                        event_date = datetime.datetime.now()
                    else:
                        # Try to parse date (basic implementation)
                        event_date = datetime.datetime.now() + datetime.timedelta(days=1)
                    
                    success = self.memory_manager.store_event(
                        title=event_title,
                        event_date=event_date,
                        reminder_minutes=1440  # 24 hours before
                    )
                    
                    if success:
                        return f"I've scheduled a reminder for {event_title} on {event_date.strftime('%B %d, %Y')}"
                    else:
                        return "I had trouble scheduling that event. Please try again."
                        
                except Exception as e:
                    return "I couldn't understand the date. Please specify when the event is."
            else:
                return "When is this event? Please specify a date."
        
        elif intent == "retrieve_memory":
            # Search memories
            query_terms = command.split()
            memories = self.memory_manager.retrieve_memories(
                query=" ".join(query_terms), 
                limit=3
            )
            
            if memories:
                response = "Here's what I remember:\n"
                for memory in memories:
                    response += f"- {memory['content']}\n"
                return response.strip()
            else:
                return "I don't have any relevant memories about that."
        
        elif intent == "play_music":
            # Music control
            if "next" in command or "skip" in command:
                return "Skipping to the next song."
            elif "previous" in command or "back" in command:
                return "Going back to the previous song."
            elif "pause" in command:
                return "Pausing music."
            elif "stop" in command:
                return "Stopping music."
            else:
                query = entities.get('query', 'your favorite playlist')
                return f"Playing {query}. Enjoy the music!"
        
        elif intent == "question_answering":
            # Check if we have context about this topic
            context_memories = self.memory_manager.retrieve_memories(query=command, limit=1)
            if context_memories:
                return f"Based on what I remember: {context_memories[0]['content']}"
            else:
                return "I don't have specific information about that, but I can help you remember it if you tell me."
        
        elif intent == "emotion_query":
            # Get emotion pattern
            emotion_pattern = self.memory_manager.get_emotion_pattern(days=7)
            if emotion_pattern:
                dominant_emotion = max(emotion_pattern.keys(), 
                                     key=lambda x: emotion_pattern[x]['avg_confidence'])
                return f"Based on our recent conversations, you seem to be feeling mostly {dominant_emotion}."
            else:
                return f"Right now, you seem to be feeling {emotion}."
        
        elif intent == "goodbye":
            return "Goodbye! It was nice talking with you. Feel free to call me anytime!"
        
        else:
            # Default response
            return "I'm not sure how to help with that, but I'm learning! Can you rephrase or ask something else?"
    
    def handle_reminder(self, reminder_text: str, event: dict):
        """Handle triggered reminders."""
        print(f"REMINDER: {reminder_text}")
        
        # Speak the reminder
        self.voice_handler.speak(reminder_text)
        
        # Send to frontend if connected
        try:
            eel.show_reminder(reminder_text, event)
        except:
            pass  # Frontend might not be connected

# Initialize the assistant
eric = EricAIAssistant()

# Eel exposed functions for frontend communication
@eel.expose
def send_text_command(command):
    """Process text command from frontend."""
    return eric.process_command(command, source="text")

@eel.expose
def start_voice_listening():
    """Start voice listening."""
    eric.is_listening = True
    return {"status": "Voice listening started"}

@eel.expose
def stop_voice_listening():
    """Stop voice listening."""
    eric.voice_handler.stop_listening()
    eric.is_listening = False
    return {"status": "Voice listening stopped"}

@eel.expose
def authenticate_with_face(image_data):
    """Authenticate user with face recognition."""
    try:
        # Decode base64 image
        import base64
        import numpy as np
        
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Convert to cv2 image
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Authenticate
        name, confidence, face_locations = eric.face_recognition.authenticate_face(frame)
        
        if confidence > 0.7:
            eric.is_authenticated = True
            eric.current_user = name
            return {
                "authenticated": True,
                "user": name,
                "confidence": confidence
            }
        else:
            return {
                "authenticated": False,
                "message": "Face not recognized"
            }
            
    except Exception as e:
        return {
            "authenticated": False,
            "message": f"Authentication error: {str(e)}"
        }

@eel.expose
def register_face(image_data, user_name):
    """Register a new face."""
    try:
        # Save image temporarily
        import tempfile
        import base64
        
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name
        
        # Register face
        success = eric.face_recognition.register_face(temp_path, user_name)
        
        # Clean up temp file
        import os
        os.unlink(temp_path)
        
        return {"success": success}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_conversation_history():
    """Get recent conversation history."""
    return eric.context_manager.get_conversation_context(turns_back=10)

@eel.expose
def get_upcoming_events():
    """Get upcoming events."""
    return eric.memory_manager.get_upcoming_events()

@eel.expose
def get_emotion_pattern():
    """Get emotion pattern."""
    return eric.memory_manager.get_emotion_pattern()

def main():
    """Main function to start the application."""
    # Initialize Eel
    eel.init(str(Config.FRONTEND_DIR))
    
    # Start Eric AI Assistant
    eric.start()
    
    # Start the web interface
    eel.start('index.html', size=(1200, 800), port=8080)

if __name__ == "__main__":
    main()