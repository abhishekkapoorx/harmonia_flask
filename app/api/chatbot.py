"""
Chatbot routes blueprint.
"""

import json
from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.user_detail import UserDetail
from app.extensions import db
from app.utils.validators import validate_numeric_string
from app.utils.chatbot import chat, get_meal_plan

# Create blueprint
chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
@jwt_required()
async def chats():
    """Handle chat requests."""
    try:
        data = request.json
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        user_input = data.get("input")
        if not user_input or not isinstance(user_input, str):
            return jsonify({"msg": "Valid input text is required"}), 400

        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"msg": "User not found"}), 401

        user_details = UserDetail.query.filter_by(user_id=user.id).first()

        if not user_details:
            return jsonify({"msg": "User details not found please add details."}), 404

        user_details_dict = user_details.to_dict()
        response = await chat(user_input, user_details_dict)
        return jsonify({"msg": "Chat processed successfully", "response": response})
    except Exception as e:
        return jsonify({"msg": "Chat processing failed", "error": str(e)}), 500


@chatbot_bp.route("/meal-planner", methods=["GET", "POST"])
@jwt_required()
async def meal_planner():
    """Generate meal plans based on user preferences."""
    try:
        user = get_jwt_identity()
        user = User.query.filter_by(email=user).first()
        if not user:
            return jsonify({"msg": "User not found"}), 401

        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        if not user_details:
            return jsonify({"msg": "User details not found please add details."}), 404

        user_details_dict = user_details.to_dict()
        meal_plan = await get_meal_plan(user_details_dict)

        if "error" in meal_plan:
            return (
                jsonify({"msg": "Meal planning failed", "error": meal_plan["error"]}),
                500,
            )

        return jsonify({"msg": "Meal plan generated successfully", "data": meal_plan})
    except Exception as e:
        return jsonify({"msg": "Meal planning failed", "error": str(e)}), 500
