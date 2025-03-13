"""
User models module.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from sqlalchemy.dialects.postgresql import ENUM
from uuid import uuid4


class User(db.Model):
    """User model for authentication."""

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    role = db.Column(
        ENUM("user", "doctor", "moderator", "pharmacist", "admin", name="user_role"),
        default="user",
    )

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify password hash."""
        return check_password_hash(self.password, password)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "user_id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
