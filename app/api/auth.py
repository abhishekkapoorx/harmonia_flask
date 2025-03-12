"""
Authentication routes blueprint.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    get_jwt_identity,
)
from app.models.User import User
from app.extensions import db
from app.utils.validators import validate_email, validate_password, validate_name

# Create blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        data = request.json
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        # Extract fields with defaults
        name = data.get("name", "")
        email = data.get("email", "")
        password = data.get("password", "")

        # Validate all fields
        if not name or not email or not password:
            return jsonify({"msg": "Missing required fields"}), 400

        if not validate_name(name):
            return jsonify({"msg": "Invalid name format"}), 400

        if not validate_email(email):
            return jsonify({"msg": "Invalid email format"}), 400

        if not validate_password(password):
            return (
                jsonify(
                    {
                        "msg": "Password must be at least 8 characters and contain at least one letter and one number"
                    }
                ),
                400,
            )

        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "Email already registered"}), 400

        new_user = User(name=name, email=email, password=password)
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "msg": "Registered successfully",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": new_user.to_dict(),
                    }
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login an existing user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        if not validate_email(email):
            return jsonify({"msg": "Invalid email format"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({"msg": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        return (
            jsonify(
                {
                    "msg": "Logged in successfully",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": user.to_dict(),
                    }
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"msg": "Login failed", "error": str(e)}), 500


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """Test protected route."""
    get_identity = get_jwt_identity()
    user = current_user
    return jsonify({"msg": f"Hello {get_identity}", "user": user.to_dict()}), 200
