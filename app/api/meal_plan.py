"""
Meal plan routes blueprint.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.user_detail import UserDetail
from app.models.meal_plan import MealPlan
from app.extensions import db
from app.utils.chatbot import get_meal_plan_llm
from sqlalchemy import desc
from pydantic import BaseModel

# Create blueprint
meal_plan_bp = Blueprint('meal_plan', __name__)


@meal_plan_bp.route('/meal-plans', methods=['GET'])
@jwt_required()
def get_meal_plans():
    """Get all meal plans for the current user."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        meal_plans = MealPlan.query.filter_by(user_id=user.id).order_by(desc(MealPlan.created_at)).all()
        return jsonify({
            "meal_plans": [plan.to_dict() for plan in meal_plans]
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve meal plans", "error": str(e)}), 500


@meal_plan_bp.route('/meal-plans/active', methods=['GET'])
@jwt_required()
def get_active_meal_plan():
    """Get the currently active meal plan for the user."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        active_plan = MealPlan.query.filter_by(user_id=user.id, is_active=True).order_by(desc(MealPlan.created_at)).first()
        
        if not active_plan:
            return jsonify({"msg": "No active meal plan found"}), 404
        
        return jsonify({
            "msg": "Active meal plan retrieved successfully",
            "meal_plan": active_plan.to_dict(),
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve active meal plan", "error": str(e)}), 500


@meal_plan_bp.route('/meal-plans/<plan_id>', methods=['GET'])
@jwt_required()
def get_meal_plan(plan_id):
    """Get a specific meal plan."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
        
        if not meal_plan:
            return jsonify({"msg": "Meal plan not found"}), 404
        
        return jsonify({
            "meal_plan": meal_plan.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve meal plan", "error": str(e)}), 500


@meal_plan_bp.route('/meal-plans/create', methods=['POST'])
@jwt_required()
async def create_custom_meal_plan():
    """Create a custom meal plan with user preferences."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        if not user_details:
            return jsonify({"msg": "User details not found, please add details"}), 404
        
        # Get custom preferences from request
        data = request.json or {}
        user_message = data.get("preferences")
        
        if not user_message or not isinstance(user_message, str):
            return jsonify({"msg": "Valid preferences string is required"}), 400
        
        # Generate a custom meal plan
        user_details_dict = user_details.to_dict()
        meal_plan_data = await get_meal_plan_llm(user_details_dict, user_message)
        
        if isinstance(meal_plan_data, dict) and "error" in meal_plan_data:
            return jsonify({"msg": "Meal planning failed", "error": meal_plan_data["error"]}), 500
        
        # Convert Pydantic object to dictionary if needed
        meal_plan_dict = meal_plan_data
        if isinstance(meal_plan_data, BaseModel):
            # For Pydantic v2
            if hasattr(meal_plan_data, "model_dump"):
                meal_plan_dict = meal_plan_data.model_dump()
            # For Pydantic v1
            elif hasattr(meal_plan_data, "dict"):
                meal_plan_dict = meal_plan_data.dict()
        
        # Deactivate previous meal plans
        MealPlan.query.filter_by(user_id=user.id, is_active=True).update({"is_active": False})
        
        # Save the new meal plan to the database
        new_meal_plan = MealPlan(
            user_id=user.id,
            plan_data=meal_plan_dict
        )
        db.session.add(new_meal_plan)
        db.session.commit()
        
        return jsonify({
            "msg": "Custom meal plan created successfully",
            "data": new_meal_plan.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to create custom meal plan", "error": str(e)}), 500


@meal_plan_bp.route('/meal-plans/<plan_id>/activate', methods=['PUT'])
@jwt_required()
def activate_meal_plan(plan_id):
    """Activate a specific meal plan and deactivate others."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
        
        if not meal_plan:
            return jsonify({"msg": "Meal plan not found"}), 404
        
        # Deactivate all current plans
        MealPlan.query.filter_by(user_id=user.id, is_active=True).update({"is_active": False})
        
        # Activate the selected plan
        meal_plan.is_active = True
        db.session.commit()
        
        return jsonify({
            "msg": "Meal plan activated successfully",
            "meal_plan": meal_plan.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to activate meal plan", "error": str(e)}), 500


@meal_plan_bp.route('/meal-plans/<plan_id>', methods=['DELETE'])
@jwt_required()
def delete_meal_plan(plan_id):
    """Delete a specific meal plan."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=user.id).first()
        
        if not meal_plan:
            return jsonify({"msg": "Meal plan not found"}), 404
        
        db.session.delete(meal_plan)
        db.session.commit()
        
        return jsonify({
            "msg": "Meal plan deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to delete meal plan", "error": str(e)}), 500 