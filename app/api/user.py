"""
User routes blueprint.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserDetail
from ..extensions import db
from ..utils.validators import validate_numeric_string

# Create blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/user-details', methods=['POST'])
@jwt_required()
def add_user_details():
    """Add details for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user["email"]).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        # Required fields validation
        required_fields = [
            "age", "height", "weight", "periodRegularity", "periodDuration",
            "heavyBleeding", "severeCramps", "pcosDiagnosis", "hirsutism",
            "hairLoss", "acneSkinIssues", "weightGain", "fatigue",
            "exerciseFrequency", "dietType", "processedFoodConsumption",
            "sugarCravings", "waterIntake", "sleepHours", "sleepDisturbances",
            "mentalHealthIssues", "stressLevels"
        ]
        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400
            
        # Validate numeric fields
        if not validate_numeric_string(data["age"], 1, 120):
            return jsonify({"message": "Invalid age value"}), 400
            
        if not validate_numeric_string(data["height"]):
            return jsonify({"message": "Invalid height value"}), 400
            
        if not validate_numeric_string(data["weight"]):
            return jsonify({"message": "Invalid weight value"}), 400
            
        # Check for existing user details
        existing_details = UserDetail.query.filter_by(user_id=user.id).first()
        if existing_details:
            return jsonify({"message": "User details already exist"}), 400
            
        # Create new user details
        user_details = UserDetail(
            user_id=user.id,
            age=data["age"],
            height=data["height"],
            weight=data["weight"],
            periodRegularity=data["periodRegularity"],
            periodDuration=data["periodDuration"],
            heavyBleeding=data["heavyBleeding"],
            severeCramps=data["severeCramps"],
            pcosDiagnosis=data["pcosDiagnosis"],
            hirsutism=data["hirsutism"],
            hairLoss=data["hairLoss"],
            acneSkinIssues=data["acneSkinIssues"],
            weightGain=data["weightGain"],
            fatigue=data["fatigue"],
            exerciseFrequency=data["exerciseFrequency"],
            dietType=data["dietType"],
            processedFoodConsumption=data["processedFoodConsumption"],
            sugarCravings=data["sugarCravings"],
            waterIntake=data["waterIntake"],
            sleepHours=data["sleepHours"],
            sleepDisturbances=data["sleepDisturbances"],
            mentalHealthIssues=data["mentalHealthIssues"],
            stressLevels=data["stressLevels"],
            medicalHistory=data.get("medicalHistory", ""),
            medications=data.get("medications", ""),
            fertilityTreatments=data.get("fertilityTreatments", "")
        )
        
        db.session.add(user_details)
        db.session.commit()
        
        return jsonify({"message": "User details added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to add user details", "error": str(e)}), 500

@user_bp.route('/user-details', methods=['GET'])
@jwt_required()
def get_user_details():
    """Get details for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user["email"]).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        
        if not user_details:
            return jsonify({"message": "User details not found"}), 404
            
        return jsonify(user_details.to_dict()), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve user details", "error": str(e)}), 500 