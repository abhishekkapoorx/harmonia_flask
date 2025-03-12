"""
User models module.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db

class User(db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

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
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserDetail(db.Model):
    """User details model for storing health and lifestyle information."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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