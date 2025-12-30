from typing import Optional, List
from app.memory import session_store
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        pass
    
    def create_session(self) -> str:
        """Create new session and return session ID"""
        return session_store.create_session()
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID"""
        return session_store.get_session(session_id)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to conversation history"""
        session_store.append_message(session_id, role, content)
    
    def get_conversation_history(self, session_id: str) -> List[dict]:
        """Get conversation history for session"""
        return session_store.get_history(session_id)
    
    def update_context(self, session_id: str, context_updates: dict):
        """Update session context"""
        session_store.set_context(session_id, context_updates)
    
    def get_context(self, session_id: str) -> dict:
        """Get session context"""
        return session_store.get_context(session_id)
    
    def get_intent(self, session_id: str) -> dict:
        """Get intent data for session"""
        return session_store.get_intent(session_id)
    
    def set_intent(self, session_id: str, intent_json: dict):
        """Set intent data for session"""
        session_store.set_intent(session_id, intent_json)

# Singleton instance
session_manager = SessionManager()
