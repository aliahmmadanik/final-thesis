-- Memory table for storing conversations and facts
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    memory_type TEXT NOT NULL, -- 'fact', 'conversation', 'event', 'context'
    content TEXT NOT NULL,
    keywords TEXT, -- JSON array of keywords for search
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 1.0,
    context_tags TEXT, -- JSON array of context tags
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Events and reminders table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    title TEXT NOT NULL,
    description TEXT,
    event_date DATETIME NOT NULL,
    reminder_date DATETIME,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- User profiles
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    face_encoding BLOB, -- Stored face encoding
    preferences TEXT, -- JSON preferences
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Conversation context
CREATE TABLE IF NOT EXISTS conversation_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    context_data TEXT NOT NULL, -- JSON data
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Emotion history
CREATE TABLE IF NOT EXISTS emotion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    emotion TEXT NOT NULL,
    confidence REAL NOT NULL,
    text_input TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);