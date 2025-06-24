import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from config import Config

class VoiceHandler:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Voice command queue
        self.command_queue = queue.Queue()
        self.is_listening = False
        
        # Calibrate microphone
        self.calibrate_microphone()
    
    def setup_tts(self):
        """Setup text-to-speech engine."""
        voices = self.tts_engine.getProperty('voices')
        
        # Set voice (prefer female voice for Eric)
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set rate and volume
        self.tts_engine.setProperty('rate', Config.VOICE_RATE)
        self.tts_engine.setProperty('volume', Config.VOICE_VOLUME)
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Microphone calibrated.")
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
    
    def speak(self, text: str):
        """Convert text to speech."""
        try:
            print(f"Eric: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
    
    def listen_for_command(self, timeout: int = 5) -> str:
        """Listen for a single voice command."""
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                print("Processing speech...")
                # Recognize speech using Google Speech Recognition
                command = self.recognizer.recognize_google(audio)
                print(f"User said: {command}")
                return command.lower()
                
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""
    
    def start_continuous_listening(self):
        """Start continuous listening in a separate thread."""
        self.is_listening = True
        listening_thread = threading.Thread(target=self._continuous_listen)
        listening_thread.daemon = True
        listening_thread.start()
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
    
    def _continuous_listen(self):
        """Continuous listening function."""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for wake word or commands
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    command = self.recognizer.recognize_google(audio)
                    command = command.lower()
                    
                    # Check for wake word "Eric"
                    if "eric" in command:
                        # Remove wake word and add to queue
                        command = command.replace("eric", "").strip()
                        if command:
                            self.command_queue.put(command)
                        else:
                            # Just wake word, listen for follow-up command
                            self.speak("Yes, how can I help you?")
                            follow_up = self.listen_for_command(timeout=10)
                            if follow_up:
                                self.command_queue.put(follow_up)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                time.sleep(1)  # Wait before retrying
                continue
            except Exception as e:
                print(f"Error in continuous listening: {e}")
                time.sleep(1)
    
    def get_command(self) -> str:
        """Get command from queue (non-blocking)."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return ""
    
    def has_commands(self) -> bool:
        """Check if there are pending commands."""
        return not self.command_queue.empty()