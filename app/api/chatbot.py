"""
Chatbot routes blueprint.
"""

import json
from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.user_detail import UserDetail
from app.models.meal_plan import MealPlan
from app.extensions import db
from app.utils.validators import validate_numeric_string
from app.utils.chatbot import chat, get_meal_plan_llm

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
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return jsonify({"msg": "User not found"}), 401

        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        if not user_details:
            return jsonify({"msg": "User details not found please add details."}), 404

        # For GET requests, try to return existing meal plan
        if request.method == "GET":
            existing_plan = MealPlan.query.filter_by(user_id=user.id, is_active=True).order_by(MealPlan.created_at.desc()).first()
            if existing_plan:
                return jsonify({
                    "msg": "Retrieved existing meal plan",
                    "data": existing_plan.to_dict(),
                })

        # For POST requests, check for user message
        user_message = None
        if request.method == "POST":
            data = request.json or {}
            user_message = data.get("message")
            
            # Validate message if provided
            if user_message is not None and not isinstance(user_message, str):
                return jsonify({"msg": "Message must be a valid string"}), 400

        # Generate a new meal plan
        user_details_dict = user_details.to_dict()
        meal_plan_data = await get_meal_plan_llm(user_details_dict, user_message)

        if isinstance(meal_plan_data, dict) and "error" in meal_plan_data:
            return (
                jsonify({"msg": "Meal planning failed", "error": meal_plan_data["error"]}),
                500,
            )

        # Deactivate previous meal plans
        MealPlan.query.filter_by(user_id=user.id, is_active=True).update({"is_active": False})
        
        # Save the new meal plan to the database
        new_meal_plan = MealPlan(
            user_id=user.id,
            plan_data=meal_plan_data
        )
        db.session.add(new_meal_plan)
        db.session.commit()

        return jsonify({
            "msg": "Meal plan generated successfully", 
            "data": meal_plan_data,
            "plan_id": new_meal_plan.id,
            "created_at": new_meal_plan.created_at.isoformat() if new_meal_plan.created_at else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Meal planning failed", "error": str(e)}), 500
