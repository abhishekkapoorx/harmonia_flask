"""
Chat models for the application.
"""

import enum
from datetime import datetime
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin
from uuid import uuid4
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Dict, Any


class SenderType(enum.Enum):
    """Enum for message sender types"""
    USER = "user"
    AI = "ai"


class Chat(db.Model, SerializerMixin):
    """Chat model representing a conversation between a user and the AI"""
    __tablename__ = 'chat'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    messages = db.relationship('Message', backref=db.backref('chat', lazy=True), lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('chats', lazy=True))
    
    # Serialization rules
    serialize_rules = ('-user.password', '-user.chat', '-message.chat')
    
    def __init__(self, user_id=None, title=None):
        """Initialize a new chat."""
        self.user_id = user_id
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        """Convert chat to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'messages': [message.to_dict() for message in self.messages or []]
        }


class Message(db.Model, SerializerMixin):
    """Message model representing a single message in a chat"""
    __tablename__ = 'message'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    chat_id = db.Column(db.String(36), db.ForeignKey('chat.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_by = db.Column(SQLAlchemyEnum(SenderType), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Serialization rules
    serialize_rules = ('-chat.message',)
    
    def __init__(self, chat_id=None, content=None, sent_by=None):
        """Initialize a new message."""
        self.chat_id = chat_id
        self.content = content
        self.sent_by = sent_by

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'content': self.content,
            'sent_by': self.sent_by.value if self.sent_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
