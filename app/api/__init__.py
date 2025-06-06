"""
API package initialization.
"""
from .chatbot import chatbot_bp
from .auth import auth_bp
from .user_details import user_bp
from .chat import chat_bp

__all__ = ["chatbot_bp", "auth_bp", "user_bp", "chat_bp"]
