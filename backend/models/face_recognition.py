import face_recognition
import cv2
import numpy as np
import pickle
from config import Config
import os

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_face_encodings()
    
    def register_face(self, image_path: str, user_name: str) -> bool:
        """Register a new face."""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                # Use the first face found
                face_encoding = face_encodings[0]
                
                # Add to known faces
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(user_name)
                
                # Save encodings
                self.save_face_encodings()
                
                return True
            else:
                print("No face found in the image.")
                return False
                
        except Exception as e:
            print(f"Error registering face: {e}")
            return False
    
    def authenticate_face(self, frame) -> tuple:
        """Authenticate face from camera frame."""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding, 
                    tolerance=Config.FACE_RECOGNITION_TOLERANCE
                )
                
                name = "Unknown"
                confidence = 0.0
                
                if True in matches:
                    # Find the best match
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, face_encoding
                    )
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
                
                return name, confidence, face_locations
            
            return "No face detected", 0.0, []
            
        except Exception as e:
            print(f"Error authenticating face: {e}")
            return "Error", 0.0, []
    
    def save_face_encodings(self):
        """Save face encodings to file."""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            
            os.makedirs(Config.MODEL_DIR, exist_ok=True)
            with open(Config.FACE_ENCODINGS_PATH, 'wb') as f:
                pickle.dump(data, f)
                
        except Exception as e:
            print(f"Error saving face encodings: {e}")
    
    def load_face_encodings(self):
        """Load face encodings from file."""
        try:
            with open(Config.FACE_ENCODINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                
        except FileNotFoundError:
            print("No face encodings found. Please register faces first.")
        except Exception as e:
            print(f"Error loading face encodings: {e}")