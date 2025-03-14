"""
User details model for storing health and lifestyle information.
"""

from uuid import uuid4
from app.extensions import db
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin


class UserDetail(db.Model, SerializerMixin):
    """User details model for storing health and lifestyle information."""
    
    # Serialization rules
    serialize_rules = (
        '-user.details',  # Prevent recursive serialization
        '-user.password',  # Exclude user password
    )
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("details", lazy=True))

    # Basic Information
    age = db.Column(db.String(3), nullable=False)
    height = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.String(10), nullable=False)

    # Health Information
    periodRegularity = db.Column(db.String(50), nullable=False)
    periodDuration = db.Column(db.String(50), nullable=False)
    heavyBleeding = db.Column(db.String(50), nullable=False)
    severeCramps = db.Column(db.String(50), nullable=False)
    pcosDiagnosis = db.Column(db.String(50), nullable=False)
    hirsutism = db.Column(db.String(50), nullable=False)
    hairLoss = db.Column(db.String(50), nullable=False)
    acneSkinIssues = db.Column(db.String(50), nullable=False)
    weightGain = db.Column(db.String(50), nullable=False)
    fatigue = db.Column(db.String(50), nullable=False)

    # Lifestyle Information
    exerciseFrequency = db.Column(db.String(50), nullable=False)
    dietType = db.Column(db.String(50), nullable=False)
    processedFoodConsumption = db.Column(db.String(50), nullable=False)
    sugarCravings = db.Column(db.String(50), nullable=False)
    waterIntake = db.Column(db.String(50), nullable=False)

    # Sleep and Mental Health
    sleepHours = db.Column(db.String(50), nullable=False)
    sleepDisturbances = db.Column(db.String(50), nullable=False)
    mentalHealthIssues = db.Column(db.String(50), nullable=False)
    stressLevels = db.Column(db.String(50), nullable=False)

    # Additional Information
    medicalHistory = db.Column(db.String(255), nullable=True)
    medications = db.Column(db.String(255), nullable=True)
    fertilityTreatments = db.Column(db.String(255), nullable=True)

    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize UserDetail with provided parameters."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """Convert user details to dictionary."""
        return {
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'periodRegularity': self.periodRegularity,
            'periodDuration': self.periodDuration,
            'heavyBleeding': self.heavyBleeding,
            'severeCramps': self.severeCramps,
            'pcosDiagnosis': self.pcosDiagnosis,
            'hirsutism': self.hirsutism,
            'hairLoss': self.hairLoss,
            'acneSkinIssues': self.acneSkinIssues,
            'weightGain': self.weightGain,
            'fatigue': self.fatigue,
            'exerciseFrequency': self.exerciseFrequency,
            'dietType': self.dietType,
            'processedFoodConsumption': self.processedFoodConsumption,
            'sugarCravings': self.sugarCravings,
            'waterIntake': self.waterIntake,
            'sleepHours': self.sleepHours,
            'sleepDisturbances': self.sleepDisturbances,
            'mentalHealthIssues': self.mentalHealthIssues,
            'stressLevels': self.stressLevels,
            'medicalHistory': self.medicalHistory,
            'medications': self.medications,
            'fertilityTreatments': self.fertilityTreatments,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None
        } 