import json
import datetime
from typing import Dict, List, Any, Optional
from core.memory_manager import MemoryManager

class ContextManager:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.current_context = {}
        self.conversation_history = []
        self.max_history_length = 50
        
    def set_context(self, key: str, value: Any, expires_minutes: int = 60):
        """Set context with expiration."""
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=expires_minutes)
        
        self.current_context[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.datetime.now()
        }
        
        # Store in database for persistence
        context_data = {
            'key': key,
            'value': value,
            'expires_at': expires_at.isoformat()
        }
        
        try:
            conn = self.memory_manager._get_connection()
            cursor = conn.cursor()
            
            # Remove existing context with same key
            cursor.execute("""
                DELETE FROM conversation_context 
                WHERE user_id = ? AND JSON_EXTRACT(context_data, '$.key') = ?
            """, (self.memory_manager.user_id, key))
            
            # Insert new context
            cursor.execute("""
                INSERT INTO conversation_context (user_id, context_data, expires_at)
                VALUES (?, ?, ?)
            """, (self.memory_manager.user_id, json.dumps(context_data), expires_at))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error storing context: {e}")
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get context value if not expired."""
        if key in self.current_context:
            context_item = self.current_context[key]
            if datetime.datetime.now() < context_item['expires_at']:
                return context_item['value']
            else:
                # Remove expired context
                del self.current_context[key]
        
        return None
    
    def has_context(self, key: str) -> bool:
        """Check if context exists and is not expired."""
        return self.get_context(key) is not None
    
    def clear_context(self, key: str = None):
        """Clear specific context or all context."""
        if key:
            if key in self.current_context:
                del self.current_context[key]
        else:
            self.current_context.clear()
    
    def add_to_conversation(self, user_input: str, bot_response: str, intent: str = None):
        """Add conversation turn to history."""
        conversation_turn = {
            'timestamp': datetime.datetime.now().isoformat(),
            'user_input': user_input,
            'bot_response': bot_response,
            'intent': intent
        }
        
        self.conversation_history.append(conversation_turn)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
        
        # Store important conversations in memory
        if intent in ['remember_fact', 'remember_event', 'important_info']:
            self.memory_manager.store_memory(
                content=f"User said: {user_input}. Eric responded: {bot_response}",
                memory_type="conversation",
                importance_score=2.0
            )
    
    def get_conversation_context(self, turns_back: int = 3) -> List[Dict[str, Any]]:
        """Get recent conversation turns for context."""
        return self.conversation_history[-turns_back:] if self.conversation_history else []
    
    def load_context_from_db(self):
        """Load unexpired context from database."""
        try:
            conn = self.memory_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT context_data FROM conversation_context 
                WHERE user_id = ? AND expires_at > datetime('now')
            """, (self.memory_manager.user_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                context_data = json.loads(row[0])
                self.current_context[context_data['key']] = {
                    'value': context_data['value'],
                    'expires_at': datetime.datetime.fromisoformat(context_data['expires_at']),
                    'created_at': datetime.datetime.now()
                }
            
            conn.close()
        except Exception as e:
            print(f"Error loading context from database: {e}")
    
    def cleanup_expired_context(self):
        """Remove expired context items."""
        current_time = datetime.datetime.now()
        expired_keys = []
        
        for key, context_item in self.current_context.items():
            if current_time >= context_item['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.current_context[key]
        
        # Cleanup database
        try:
            conn = self.memory_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM conversation_context 
                WHERE user_id = ? AND expires_at <= datetime('now')
            """, (self.memory_manager.user_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error cleaning up expired context: {e}")