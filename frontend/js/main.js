// Main application logic
class EricAI {
  constructor() {
    this.isAuthenticated = false;
    this.isListening = false;
    this.currentUser = null;
    this.conversationHistory = [];
    this.currentEmotion = { emotion: "neutral", confidence: 0.7 };

    this.initialize();
  }

  initialize() {
    this.setupEventListeners();
    this.loadInitialData();
    this.updateUI();

    // Setup periodic updates
    setInterval(() => this.updateStats(), 10000); // Update every 10 seconds
    setInterval(() => this.checkForReminders(), 60000); // Check every minute
  }

  setupEventListeners() {
    // Message input
    const messageInput = document.getElementById("messageInput");
    messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.sendMessage();
      }
    });

    // Voice control
    document.getElementById("voiceBtn").addEventListener("click", () => {
      this.toggleVoiceListening();
    });
  }

  async loadInitialData() {
    try {
      // Load conversation history
      this.conversationHistory = await eel.get_conversation_history()();
      this.updateChatMessages();

      // Load events
      await this.loadUpcomingEvents();

      // Load emotion pattern
      await this.loadEmotionPattern();

      // Update stats
      await this.updateStats();
    } catch (error) {
      console.error("Error loading initial data:", error);
    }
  }

  async sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const message = messageInput.value.trim();

    if (!message) return;

    // Clear input
    messageInput.value = "";

    // Add user message to chat
    this.addMessageToChat(message, "user");

    // Show typing indicator
    this.showTypingIndicator();

    try {
      // Send to backend
      const response = await eel.send_text_command(message)();

      // Remove typing indicator
      this.hideTypingIndicator();

      // Add bot response to chat
      this.addMessageToChat(response.response, "bot");

      // Update emotion if provided
      if (response.emotion) {
        this.updateEmotion(response.emotion, response.emotion_confidence);
      }

      // Store in conversation history
      this.conversationHistory.push({
        user_input: message,
        bot_response: response.response,
        intent: response.intent,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      this.hideTypingIndicator();
      this.addMessageToChat(
        "Sorry, I encountered an error. Please try again.",
        "bot"
      );
      console.error("Error sending message:", error);
    }
  }

  async sendQuickCommand(command) {
    const messageInput = document.getElementById("messageInput");
    messageInput.value = command;
    await this.sendMessage();
  }

  addMessageToChat(message, sender) {
    const chatMessages = document.getElementById("chatMessages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const now = new Date();
    const timeString = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === "user" ? "user" : "robot"}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(message)}</div>
                <div class="message-time">${timeString}</div>
            </div>
        `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  formatMessage(message) {
    // Format message with line breaks and basic formatting
    return message
      .replace(/\n/g, "<br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>");
  }

  showTypingIndicator() {
    const chatMessages = document.getElementById("chatMessages");
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot-message typing-indicator";
    typingDiv.id = "typingIndicator";

    typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  hideTypingIndicator() {
    const typingIndicator = document.getElementById("typingIndicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  updateChatMessages() {
    const chatMessages = document.getElementById("chatMessages");
    // Clear existing messages except welcome message
    const messages = chatMessages.querySelectorAll(
      ".message:not(.bot-message):not(:first-child)"
    );
    messages.forEach((msg) => msg.remove());

    // Add conversation history
    this.conversationHistory.forEach((turn) => {
      this.addMessageToChat(turn.user_input, "user");
      this.addMessageToChat(turn.bot_response, "bot");
    });
  }

  async toggleVoiceListening() {
    const voiceBtn = document.getElementById("voiceBtn");
    const voiceStatus = document.getElementById("voiceStatus");

    if (!this.isListening) {
      try {
        await eel.start_voice_listening()();
        this.isListening = true;
        voiceBtn.innerHTML =
          '<i class="fas fa-microphone-slash"></i><span>Stop Listening</span>';
        voiceBtn.classList.add("listening");
        voiceStatus.innerHTML = "<span>Voice: Active</span>";
        this.showNotification("Voice listening started", "success");
      } catch (error) {
        console.error("Error starting voice listening:", error);
        this.showNotification("Failed to start voice listening", "error");
      }
    } else {
      try {
        await eel.stop_voice_listening()();
        this.isListening = false;
        voiceBtn.innerHTML =
          '<i class="fas fa-microphone"></i><span>Start Listening</span>';
        voiceBtn.classList.remove("listening");
        voiceStatus.innerHTML = "<span>Voice: Inactive</span>";
        this.showNotification("Voice listening stopped", "success");
      } catch (error) {
        console.error("Error stopping voice listening:", error);
      }
    }
  }

  updateEmotion(emotion, confidence) {
    this.currentEmotion = { emotion, confidence };

    const emotionIndicator = document.getElementById("emotionIndicator");
    const emotionIcons = {
      joy: "😊",
      sadness: "😢",
      anger: "😠",
      fear: "😨",
      surprise: "😮",
      neutral: "😐",
    };

    emotionIndicator.innerHTML = `
            <div class="emotion-icon">${emotionIcons[emotion] || "😐"}</div>
            <div class="emotion-text">${
              emotion.charAt(0).toUpperCase() + emotion.slice(1)
            }</div>
            <div class="emotion-confidence">${Math.round(
              confidence * 100
            )}%</div>
        `;
  }

  async loadUpcomingEvents() {
    try {
      const events = await eel.get_upcoming_events()();
      const eventsList = document.getElementById("eventsList");

      if (events.length === 0) {
        eventsList.innerHTML =
          '<div class="no-events">No upcoming events</div>';
        return;
      }

      eventsList.innerHTML = events
        .map(
          (event) => `
                <div class="event-item">
                    <div class="event-time">${this.formatEventDate(
                      event.event_date
                    )}</div>
                    <div class="event-title">${event.title}</div>
                    ${
                      event.description
                        ? `<div class="event-description">${event.description}</div>`
                        : ""
                    }
                </div>
            `
        )
        .join("");
    } catch (error) {
      console.error("Error loading events:", error);
    }
  }

  async loadEmotionPattern() {
    try {
      const emotionPattern = await eel.get_emotion_pattern()();
      // Update emotion chart (simplified version)
      const emotionChart = document.getElementById("emotionChart");

      if (Object.keys(emotionPattern).length === 0) {
        emotionChart.innerHTML =
          '<div class="no-data">No emotion data available</div>';
        return;
      }

      const sortedEmotions = Object.entries(emotionPattern)
        .sort(([, a], [, b]) => b.avg_confidence - a.avg_confidence)
        .slice(0, 3);

      emotionChart.innerHTML = sortedEmotions
        .map(
          ([emotion, data]) => `
                <div class="emotion-trend-item">
                    <span class="emotion-name">${emotion}</span>
                    <div class="emotion-bar">
                        <div class="emotion-bar-fill" style="width: ${
                          data.avg_confidence * 100
                        }%"></div>
                    </div>
                    <span class="emotion-percentage">${Math.round(
                      data.avg_confidence * 100
                    )}%</span>
                </div>
            `
        )
        .join("");
    } catch (error) {
      console.error("Error loading emotion pattern:", error);
    }
  }

  async updateStats() {
    try {
      // Update memory stats (placeholder - you can implement actual counters)
      document.getElementById("totalMemories").textContent =
        this.conversationHistory.length * 2;
      document.getElementById("totalConversations").textContent =
        this.conversationHistory.length;

      // Get events count
      const events = await eel.get_upcoming_events()();
      document.getElementById("totalEvents").textContent = events.length;
    } catch (error) {
      console.error("Error updating stats:", error);
    }
  }

  async checkForReminders() {
    // This will be called by the backend when reminders are due
    // The backend will call showReminder via eel
  }

  formatEventDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === now.toDateString()) {
      return `Today ${date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}`;
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return `Tomorrow ${date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}`;
    } else {
      return (
        date.toLocaleDateString() +
        " " +
        date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    }
  }

  showNotification(message, type = "info") {
    const notificationArea = document.getElementById("notificationArea");
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${
                  type === "success"
                    ? "check-circle"
                    : type === "error"
                    ? "exclamation-circle"
                    : "info-circle"
                }"></i>
                <span>${message}</span>
            </div>
        `;

    notificationArea.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }

  clearChat() {
    const chatMessages = document.getElementById("chatMessages");
    // Keep only the welcome message
    const messages = chatMessages.querySelectorAll(
      ".message:not(:first-child)"
    );
    messages.forEach((msg) => msg.remove());

    // Clear conversation history
    this.conversationHistory = [];
  }

  updateUI() {
    // Update authentication status
    const authStatus = document.getElementById("authStatus");
    const authBtn = document.getElementById("authBtn");

    if (this.isAuthenticated) {
      authStatus.innerHTML = `
                <i class="fas fa-user-check"></i>
                <span>Authenticated as ${this.currentUser}</span>
            `;
      authStatus.classList.add("authenticated");
      authBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i>Logout';
    } else {
      authStatus.innerHTML = `
                <i class="fas fa-user-slash"></i>
                <span>Not Authenticated</span>
            `;
      authStatus.classList.remove("authenticated");
      authBtn.innerHTML = '<i class="fas fa-camera"></i>Authenticate';
    }
  }
}

// Eel exposed functions for backend to call
eel.expose(showReminder);
function showReminder(reminderText, event) {
  // Show reminder notification
  app.showNotification(reminderText, "reminder");

  // Add reminder to chat
  app.addMessageToChat(`🔔 ${reminderText}`, "bot");
}

// Initialize the application
const app = new EricAI();

// Global functions for buttons
function sendMessage() {
  app.sendMessage();
}

function sendQuickCommand(command) {
  app.sendQuickCommand(command);
}

function toggleVoiceListening() {
  app.toggleVoiceListening();
}

function clearChat() {
  app.clearChat();
}

// Add CSS for typing indicator
const style = document.createElement("style");
style.textContent = `
    .typing-dots {
        display: flex;
        gap: 4px;
        padding: 8px 0;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .emotion-trend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .emotion-name {
        flex: 0 0 80px;
        font-size: 0.8rem;
        text-transform: capitalize;
    }
    
    .emotion-bar {
        flex: 1;
        height: 6px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .emotion-bar-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        transition: width 0.3s ease;
    }
    
    .emotion-percentage {
        flex: 0 0 40px;
        font-size: 0.8rem;
        text-align: right;
        color: #666;
    }
    
    .no-events, .no-data {
        text-align: center;
        color: #666;
        font-style: italic;
        padding: 1rem;
    }
`;
document.head.appendChild(style);
