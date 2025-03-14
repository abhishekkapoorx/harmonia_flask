"""
User routes blueprint.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
from app.models.User import User
from app.models.UserDetail import UserDetail
from app.extensions import db
from app.utils.validators import validate_numeric_string


# Create blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/user-details', methods=['POST'])
@jwt_required()
def add_user_details():
    """Add details for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()


        print(user)
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400
            
        # Required fields validation
        required_fields = [
            "age", "height", "weight", "periodRegularity", "periodDuration",
            "heavyBleeding", "severeCramps", "pcosDiagnosis", "hirsutism",
            "hairLoss", "acneSkinIssues", "weightGain", "fatigue",
            "exerciseFrequency", "dietType", "processedFoodConsumption",
            "sugarCravings", "waterIntake", "sleepHours", "sleepDisturbances",
            "mentalHealthIssues", "stressLevels"
        ]
        
        missing_fields = [field for field in required_fields if field not in data or not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400
            
        # Validate numeric fields
        if not validate_numeric_string(data.get("age", ""), 1, 120):
            return jsonify({"msg": "Invalid age value"}), 400
            
        if not validate_numeric_string(data.get("height", "")):
            return jsonify({"msg": "Invalid height value"}), 400
            
        if not validate_numeric_string(data.get("weight", "")):
            return jsonify({"msg": "Invalid weight value"}), 400
            
        # Check for existing user details
        existing_details = UserDetail.query.filter_by(user_id=user.id).first()
        if existing_details:
            return jsonify({"msg": "User details already exist. Please update the details instead."}), 400
            
        # Create new user details
        user_details = UserDetail(
            user_id=user.id,
            age=data.get("age", ""),
            height=data.get("height", ""),
            weight=data.get("weight", ""),
            periodRegularity=data.get("periodRegularity", ""),
            periodDuration=data.get("periodDuration", ""),
            heavyBleeding=data.get("heavyBleeding", ""),
            severeCramps=data.get("severeCramps", ""),
            pcosDiagnosis=data.get("pcosDiagnosis", ""),
            hirsutism=data.get("hirsutism", ""),
            hairLoss=data.get("hairLoss", ""),
            acneSkinIssues=data.get("acneSkinIssues", ""),
            weightGain=data.get("weightGain", ""),
            fatigue=data.get("fatigue", ""),
            exerciseFrequency=data.get("exerciseFrequency", ""),
            dietType=data.get("dietType", ""),
            processedFoodConsumption=data.get("processedFoodConsumption", ""),
            sugarCravings=data.get("sugarCravings", ""),
            waterIntake=data.get("waterIntake", ""),
            sleepHours=data.get("sleepHours", ""),
            sleepDisturbances=data.get("sleepDisturbances", ""),
            mentalHealthIssues=data.get("mentalHealthIssues", ""),
            stressLevels=data.get("stressLevels", ""),
            medicalHistory=data.get("medicalHistory", ""),
            medications=data.get("medications", ""),
            fertilityTreatments=data.get("fertilityTreatments", "")
        )
        
        db.session.add(user_details)
        db.session.commit()
        
        return jsonify({"msg": "User details added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to add user details", "error": str(e)}), 500

@user_bp.route('/user-details', methods=['GET'])
@jwt_required()
def get_user_details():


    """Get details for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
            
        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        
        if not user_details:
            return jsonify({"msg": "User details not found please add details."}), 404
            
        return jsonify({"msg": "User details retrieved successfully", "data": user_details.to_dict()}), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve user details", "error": str(e)}), 500 
    

@user_bp.route('/user-details', methods=['PUT'])
@jwt_required()
def update_user_details():
    """Update details for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400
        
        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        
        if not user_details:
            return jsonify({"msg": "User details not found"}), 404

        # Validate numeric fields if provided
        if "age" in data and not validate_numeric_string(data["age"], 1, 120):
            return jsonify({"msg": "Invalid age value"}), 400
            
        if "height" in data and not validate_numeric_string(data["height"]):
            return jsonify({"msg": "Invalid height value"}), 400
            
        if "weight" in data and not validate_numeric_string(data["weight"]):
            return jsonify({"msg": "Invalid weight value"}), 400

        # Update fields
        user_details.age = data.get("age", user_details.age)
        user_details.height = data.get("height", user_details.height)
        user_details.weight = data.get("weight", user_details.weight)
        user_details.periodRegularity = data.get("periodRegularity", user_details.periodRegularity)
        user_details.periodDuration = data.get("periodDuration", user_details.periodDuration)
        user_details.heavyBleeding = data.get("heavyBleeding", user_details.heavyBleeding)
        user_details.severeCramps = data.get("severeCramps", user_details.severeCramps)
        user_details.pcosDiagnosis = data.get("pcosDiagnosis", user_details.pcosDiagnosis)
        user_details.hirsutism = data.get("hirsutism", user_details.hirsutism)
        user_details.hairLoss = data.get("hairLoss", user_details.hairLoss)
        user_details.acneSkinIssues = data.get("acneSkinIssues", user_details.acneSkinIssues)
        user_details.weightGain = data.get("weightGain", user_details.weightGain)
        user_details.fatigue = data.get("fatigue", user_details.fatigue)
        user_details.exerciseFrequency = data.get("exerciseFrequency", user_details.exerciseFrequency)
        user_details.dietType = data.get("dietType", user_details.dietType)
        user_details.processedFoodConsumption = data.get("processedFoodConsumption", user_details.processedFoodConsumption)
        user_details.sugarCravings = data.get("sugarCravings", user_details.sugarCravings)
        user_details.waterIntake = data.get("waterIntake", user_details.waterIntake)
        user_details.sleepHours = data.get("sleepHours", user_details.sleepHours)
        user_details.sleepDisturbances = data.get("sleepDisturbances", user_details.sleepDisturbances)
        user_details.mentalHealthIssues = data.get("mentalHealthIssues", user_details.mentalHealthIssues)
        user_details.stressLevels = data.get("stressLevels", user_details.stressLevels)
        user_details.medicalHistory = data.get("medicalHistory", user_details.medicalHistory)
        user_details.medications = data.get("medications", user_details.medications)
        user_details.fertilityTreatments = data.get("fertilityTreatments", user_details.fertilityTreatments)

        db.session.commit()
        
        return jsonify({"msg": "User details updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to update user details", "error": str(e)}), 500


