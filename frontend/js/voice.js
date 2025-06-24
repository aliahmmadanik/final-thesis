// Voice handling and speech recognition
class VoiceManager {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isSupported = this.checkSupport();
    this.isListening = false;

    if (this.isSupported) {
      this.setupSpeechRecognition();
    }
  }

  checkSupport() {
    return "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
  }

  setupSpeechRecognition() {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();

    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.lang = "en-US";

    this.recognition.onstart = () => {
      console.log("Speech recognition started");
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      console.log("Speech recognized:", transcript);

      // Check for wake word "Eric"
      if (transcript.toLowerCase().includes("eric")) {
        this.handleWakeWord(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      if (event.error === "not-allowed") {
        app.showNotification("Microphone access denied", "error");
      }
    };

    this.recognition.onend = () => {
      if (this.isListening) {
        // Restart recognition if it should be listening
        setTimeout(() => {
          if (this.isListening) {
            this.recognition.start();
          }
        }, 100);
      }
    };
  }

  handleWakeWord(transcript) {
    // Remove wake word and process command
    const command = transcript.toLowerCase().replace(/eric/g, "").trim();

    if (command) {
      // Add command to chat input
      const messageInput = document.getElementById("messageInput");
      messageInput.value = command;

      // Send the message
      app.sendMessage();
    } else {
      // Just wake word, show listening indicator
      app.addMessageToChat("🎤 Listening for your command...", "bot");
    }
  }

  startListening() {
    if (!this.isSupported) {
      app.showNotification("Speech recognition not supported", "error");
      return false;
    }

    try {
      this.isListening = true;
      this.recognition.start();
      return true;
    } catch (error) {
      console.error("Error starting speech recognition:", error);
      this.isListening = false;
      return false;
    }
  }

  stopListening() {
    if (this.recognition) {
      this.isListening = false;
      this.recognition.stop();
    }
  }

  speak(text) {
    if (this.synthesis) {
      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;

      // Try to use a female voice
      const voices = this.synthesis.getVoices();
      const femaleVoice = voices.find(
        (voice) =>
          voice.name.toLowerCase().includes("female") ||
          voice.name.toLowerCase().includes("zira") ||
          voice.name.toLowerCase().includes("susan")
      );

      if (femaleVoice) {
        utterance.voice = femaleVoice;
      }

      this.synthesis.speak(utterance);
    }
  }

  isCurrentlyListening() {
    return this.isListening;
  }
}

// Initialize voice manager
const voiceManager = new VoiceManager();

// Voice control functions
function startVoiceRecognition() {
  return voiceManager.startListening();
}

function stopVoiceRecognition() {
  voiceManager.stopListening();
}

function speakText(text) {
  voiceManager.speak(text);
}

// Load voices when they're available
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => {
    console.log("Voices loaded:", window.speechSynthesis.getVoices().length);
  };
}
