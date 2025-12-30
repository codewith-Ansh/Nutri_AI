import uuid
import time
from typing import Dict, List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class InMemorySessionStore:
    """Simple in-memory session store for development"""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = f"session_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": time.time(),
            "messages": [],
            "context": {},
            "intent": {}
        }
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def append_message(self, session_id: str, role: str, content: str):
        """Add message to session history"""
        if session_id not in self.sessions:
            self.create_session_if_not_exists(session_id)
        
        self.sessions[session_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
    
    def get_history(self, session_id: str) -> List[dict]:
        """Get conversation history for session"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]["messages"]
    
    def set_context(self, session_id: str, context: dict):
        """Set context for session"""
        if session_id not in self.sessions:
            self.create_session_if_not_exists(session_id)
        
        self.sessions[session_id]["context"].update(context)
    
    def get_context(self, session_id: str) -> dict:
        """Get context for session"""
        if session_id not in self.sessions:
            return {}
        return self.sessions[session_id]["context"]
    
    def set_intent(self, session_id: str, intent: dict):
        """Set intent for session"""
        if session_id not in self.sessions:
            self.create_session_if_not_exists(session_id)
        
        self.sessions[session_id]["intent"] = intent
    
    def get_intent(self, session_id: str) -> dict:
        """Get intent for session"""
        if session_id not in self.sessions:
            return {}
        return self.sessions[session_id]["intent"]
    
    def create_session_if_not_exists(self, session_id: str):
        """Create session if it doesn't exist"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "created_at": time.time(),
                "messages": [],
                "context": {},
                "intent": {}
            }

# Create singleton instance
session_store = InMemorySessionStore()