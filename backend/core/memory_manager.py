import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from config import Config
import pickle

class MemoryManager:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.db_path = Config.DATABASE_PATH
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def store_memory(self, content: str, memory_type: str = "fact", 
                    keywords: List[str] = None, importance_score: float = 1.0,
                    context_tags: List[str] = None) -> bool:
        """Store a memory in the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            keywords_json = json.dumps(keywords) if keywords else "[]"
            context_tags_json = json.dumps(context_tags) if context_tags else "[]"
            
            cursor.execute("""
                INSERT INTO memory (user_id, memory_type, content, keywords, 
                                  importance_score, context_tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.user_id, memory_type, content, keywords_json, 
                  importance_score, context_tags_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def retrieve_memories(self, query: str = None, memory_type: str = None,
                         limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories based on query or type."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM memory WHERE user_id = ?"
            params = [self.user_id]
            
            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)
            
            if query:
                sql += " AND (content LIKE ? OR keywords LIKE ?)"
                query_param = f"%{query}%"
                params.extend([query_param, query_param])
            
            sql += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory = {
                    'id': row[0],
                    'user_id': row[1],
                    'memory_type': row[2],
                    'content': row[3],
                    'keywords': json.loads(row[4]) if row[4] else [],
                    'timestamp': row[5],
                    'importance_score': row[6],
                    'context_tags': json.loads(row[7]) if row[7] else []
                }
                memories.append(memory)
            
            conn.close()
            return memories
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def store_event(self, title: str, event_date: datetime.datetime,
                   description: str = "", reminder_minutes: int = 60) -> bool:
        """Store an event/reminder."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            reminder_date = event_date - datetime.timedelta(minutes=reminder_minutes)
            
            cursor.execute("""
                INSERT INTO events (user_id, title, description, event_date, reminder_date)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user_id, title, description, event_date, reminder_date))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing event: {e}")
            return False
    
    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming events."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            end_date = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
            
            cursor.execute("""
                SELECT * FROM events 
                WHERE user_id = ? AND event_date >= datetime('now') 
                AND event_date <= ? AND is_completed = FALSE
                ORDER BY event_date ASC
            """, (self.user_id, end_date))
            
            rows = cursor.fetchall()
            events = []
            for row in rows:
                event = {
                    'id': row[0],
                    'title': row[2],
                    'description': row[3],
                    'event_date': row[4],
                    'reminder_date': row[5],
                    'is_completed': row[6]
                }
                events.append(event)
            
            conn.close()
            return events
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def store_emotion(self, emotion: str, confidence: float, text_input: str = ""):
        """Store emotion detection result."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO emotion_history (user_id, emotion, confidence, text_input)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, emotion, confidence, text_input))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error storing emotion: {e}")
    
    def get_emotion_pattern(self, days: int = 7) -> Dict[str, float]:
        """Get emotion patterns over time."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            cursor.execute("""
                SELECT emotion, AVG(confidence) as avg_confidence, COUNT(*) as count
                FROM emotion_history 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY emotion
                ORDER BY avg_confidence DESC
            """, (self.user_id, start_date))
            
            rows = cursor.fetchall()
            pattern = {}
            for row in rows:
                pattern[row[0]] = {
                    'avg_confidence': row[1],
                    'count': row[2]
                }
            
            conn.close()
            return pattern
        except Exception as e:
            print(f"Error getting emotion pattern: {e}")
            return {}