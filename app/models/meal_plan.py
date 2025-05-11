"""
Meal plan model for the application.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin
from uuid import uuid4
from typing import Dict, Any


class MealPlan(db.Model, SerializerMixin):
    """MealPlan model representing a meal plan for a user"""
    __tablename__ = 'meal_plan'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    plan_data = db.Column(db.JSON, nullable=False)  # Stores the entire meal plan as JSON
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)  # To mark current active meal plan

    # Relationships
    user = db.relationship('User', backref=db.backref('meal_plans', lazy=True))
    
    # Serialization rules
    serialize_rules = ('-user.password', '-user.meal_plans')
    
    def __init__(self, user_id=None, plan_data=None):
        """Initialize a new meal plan."""
        self.user_id = user_id
        self.plan_data = plan_data

    def to_dict(self) -> Dict[str, Any]:
        """Convert meal plan to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_data': self.plan_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        } 