import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# In-memory session storage for Phase 1
# In Phase 2, migrate to Redis
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
    
    def create_session(self) -> str:
        """Create new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "conversation_history": [],
            "context": {}
        }
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session:
            # Update last accessed time
            session["last_accessed"] = datetime.now()
            return session
        return None
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to conversation history"""
        session = self.get_session(session_id)
        if session:
            session["conversation_history"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            logger.info(f"Added {role} message to session {session_id}")
    
    def get_conversation_history(self, session_id: str) -> List[dict]:
        """Get conversation history for session"""
        session = self.get_session(session_id)
        if session:
            return session["conversation_history"]
        return []
    
    def update_context(self, session_id: str, context_updates: dict):
        """Update session context"""
        session = self.get_session(session_id)
        if session:
            session["context"].update(context_updates)
            logger.info(f"Updated context for session {session_id}")
    
    def get_context(self, session_id: str) -> dict:
        """Get session context"""
        session = self.get_session(session_id)
        if session:
            return session["context"]
        return {}
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    def cleanup_expired_sessions(self, max_age_hours: int = 1):
        """Remove expired sessions"""
        now = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            age = now - session["last_accessed"]
            if age > timedelta(hours=max_age_hours):
                expired.append(session_id)
        
        for session_id in expired:
            self.delete_session(session_id)
        
        logger.info(f"Cleaned up {len(expired)} expired sessions")

# Singleton instance
session_manager = SessionManager()
