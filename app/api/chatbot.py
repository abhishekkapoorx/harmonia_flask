"""
Chatbot routes blueprint.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..utils.validators import validate_numeric_string
from chatbot import chat, get_meal_plan

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
@jwt_required()
async def chats():
    """Handle chat requests."""
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        user_input = data.get("input")
        if not user_input or not isinstance(user_input, str):
            return jsonify({"message": "Valid input text is required"}), 400

        response = await chat(user_input)
        return jsonify({"response": str(response.content)})
    except Exception as e:
        return jsonify({"message": "Chat processing failed", "error": str(e)}), 500



@chatbot_bp.route('/meal-planner', methods=['GET', 'POST'])
@jwt_required()
async def meal_planner():
    """Generate meal plans based on user preferences."""
    try:
        # Support both GET with query params and POST with JSON body
        if request.method == "POST":
            data = request.json
            if not data:
                return jsonify({"message": "No data provided"}), 400
        else:
            data = request.args.to_dict()
            
        # Extract and validate parameters with defaults
        age = data.get("age", "25")
        weight = data.get("weight", "70")
        height = data.get("height", "175")
        veg_or_nonveg = data.get("veg_or_nonveg", "veg")
        disease = data.get("disease", "pcos")
        region = data.get("region", "Indian")
        allergics = data.get("allergics", "")
        
        # Validate numeric fields
        if not validate_numeric_string(age, 1, 120):
            return jsonify({"message": "Invalid age value"}), 400
            
        if not validate_numeric_string(weight, 20, 300):
            return jsonify({"message": "Invalid weight value"}), 400
            
        if not validate_numeric_string(height, 50, 300):
            return jsonify({"message": "Invalid height value"}), 400
            
        # Validate diet type
        if veg_or_nonveg not in ["veg", "nonveg"]:
            return jsonify({"message": "Diet type must be 'veg' or 'nonveg'"}), 400

        meal_plan = await get_meal_plan(
            age=int(age),
            weight=float(weight),
            height=float(height),
            veg_or_nonveg=veg_or_nonveg,
            disease=disease,
            region=region,
            allergics=allergics,
        )
        
        return jsonify(meal_plan)
    except Exception as e:
        return jsonify({"message": "Meal planning failed", "error": str(e)}), 500 