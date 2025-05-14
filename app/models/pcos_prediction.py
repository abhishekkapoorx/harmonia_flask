"""
PCOS Prediction model module.
"""

from datetime import datetime
from app.extensions import db
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_serializer import SerializerMixin


class PCOSPrediction(db.Model, SerializerMixin):
    """Model for storing PCOS predictions."""

    __tablename__ = 'pcos_predictions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    input_data = db.Column(JSONB, nullable=False)  # Store all input features as JSON
    prediction = db.Column(db.Integer, nullable=False)  # 0 or 1
    probability = db.Column(db.Float, nullable=True)  # Probability might not be available
    risk_level = db.Column(db.String(20), nullable=False)  # low, moderate, high
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('pcos_predictions', lazy=True))

    # Serialization rules
    serialize_rules = ('-user.pcos_predictions',)
    
    def __init__(self, user_id=None, input_data=None, prediction=None, probability=None, risk_level=None, recommendation=None):
        """Initialize a new PCOS prediction."""
        self.user_id = user_id
        self.input_data = input_data
        self.prediction = prediction
        self.probability = probability
        self.risk_level = risk_level

    def __repr__(self):
        return f"<PCOSPrediction {self.id} for user {self.user_id}>"

    def to_dict(self):
        """Convert prediction to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "input_data": self.input_data,
            "prediction": self.prediction,
            "prediction_label": "PCOS" if self.prediction == 1 else "No PCOS",
            "probability": self.probability,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 