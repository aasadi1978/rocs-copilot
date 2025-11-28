import logging
from typing import List, Dict, Any
from api.chat_state import ChatState
from utils.deserialization import deserialize_messages, serialize_messages
from initialize_app.create_app import SQLALCHEMY_DB
from sqlalchemy import JSON, Column, DateTime, Integer, String
from langchain_core.messages import BaseMessage 

import uuid
from datetime import datetime
from os import getlogin


class ChatStateRepository(SQLALCHEMY_DB.Model):
    """
    SQLAlchemy ORM for managing ChatState persistence.
    Stores conversation state including messages, metadata, and timestamps.
    """

    __tablename__ = "chat_states"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), default=lambda: str(getlogin()))
    messages = Column(JSON, nullable=False)  # LangChain messages serialized to JSON
    timestamp = Column(DateTime, default=datetime.now, nullable=False)  # Renamed from created_at
    source = Column(String(2000), nullable=True)

    def __init__(self, **kwargs):
        self.conversation_id = kwargs.get("conversation_id", str(uuid.uuid4()))
        self.user_id = kwargs.get("user_id", str(getlogin()))
        self.messages = kwargs.get("messages", [])
        self.timestamp = kwargs.get("timestamp", datetime.now())
        self.source = kwargs.get("source", '')


    def to_chat_state(self) -> Dict[str, Any]:
        """
        Convert DB row into ChatState-compatible dict.
        Output: {'messages': List[BaseMessage], 'conversation_id': str, 'user_id': str, 'timestamp': str}
        """
        return {
            "messages": deserialize_messages(self.messages),
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        }

    @classmethod
    def initialize_chat_session(cls, user_id: str | None = None) -> ChatState:
        """Create a new chat session with initial empty state."""
        record = cls(
            user_id=user_id or str(getlogin()),
            messages=[]
        )
        SQLALCHEMY_DB.session.add(record)
        SQLALCHEMY_DB.session.commit()
        SQLALCHEMY_DB.session.refresh(record)
        return record
    
    @classmethod
    def get_conversation_history(cls, conversation_id: str, limit: int | None = None):
        """Get all state snapshots for a conversation, ordered chronologically."""
        query = cls.query.filter(
            cls.conversation_id == conversation_id
        ).order_by(cls.timestamp.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    @classmethod
    def from_chat_state(cls, state: Dict[str, Any]):
        """
        Create a DB record from ChatState.
        Expects state dict with: messages, conversation_id, user_id, timestamp
        """
        return cls(
            conversation_id=state.get("conversation_id", str(uuid.uuid4())),
            user_id=state.get("user_id", str(getlogin())),
            messages=serialize_messages(state.get("messages", [])),
            timestamp=state.get("timestamp", datetime.now())
        )

    def save_state_snapshot(self, state: Dict[str, Any]):
        """
        Save a new snapshot of the ChatState.
        Creates a new row for history tracking - does NOT update existing row.
        """
        new_record = ChatStateRepository(
            conversation_id=state.get("conversation_id", self.conversation_id),
            user_id=state.get("user_id", self.user_id),
            messages=serialize_messages(state.get("messages", [])),
            timestamp=state.get("timestamp", datetime.now())
        )
        SQLALCHEMY_DB.session.add(new_record)
        SQLALCHEMY_DB.session.commit()
        SQLALCHEMY_DB.session.refresh(new_record)
        return new_record

    @classmethod
    def load_chat_state(cls, conversation_id: str | None = None, 
                        source: str | None = None) -> Dict[str, Any] | None:
        """
        Load the most recent ChatState snapshot for a conversation.
        Returns ChatState dict or None if not found.
        """
        try:
            
            if conversation_id:
                record: ChatStateRepository  = cls.query.filter(
                    cls.conversation_id == conversation_id
                ).order_by(cls.timestamp.desc()).first()

            elif source:
                record: ChatStateRepository  = cls.query.filter(
                    cls.source == source
                ).order_by(cls.timestamp.desc()).first()
            else:
                return None

            if record:
                SQLALCHEMY_DB.session.refresh(record)
                return record.to_chat_state() if record else None
        
        except Exception as e:
            logging.error(f"Error loading chat state for conversation {conversation_id} or source {source}: {e}")
        
        return None

    @classmethod
    def save_chat_state(cls, state: Dict[str, Any]) -> 'ChatStateRepository':
        """
        Save a new ChatState to database.
        Creates new record from state dict.
        """
        record = cls.from_chat_state(state)
        SQLALCHEMY_DB.session.add(record)
        SQLALCHEMY_DB.session.commit()
        SQLALCHEMY_DB.session.refresh(record)
        return record
