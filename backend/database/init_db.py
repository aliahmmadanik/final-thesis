import sqlite3
import os
from pathlib import Path
from config import Config

def initialize_database():
    """Initialize the SQLite database with required tables."""
    
    # Create directories if they don't exist
    os.makedirs(Config.DATABASE_DIR, exist_ok=True)
    
    # Read schema file
    schema_path = Config.DATABASE_DIR / "schemas.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect to database and create tables
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(schema_sql)
    
    # Create default user if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, name, preferences) 
        VALUES ('default_user', 'User', '{}')
    """)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()