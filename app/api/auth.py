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
            return jsonify({"message": "No data provided"}), 400

        # Extract fields with defaults
        name = data.get("name", "")
        email = data.get("email", "")
        password = data.get("password", "")

        # Validate all fields
        if not name or not email or not password:
            return jsonify({"message": "Missing required fields"}), 400

        if not validate_name(name):
            return jsonify({"message": "Invalid name format"}), 400

        if not validate_email(email):
            return jsonify({"message": "Invalid email format"}), 400

        if not validate_password(password):
            return (
                jsonify(
                    {
                        "message": "Password must be at least 8 characters and contain at least one letter and one number"
                    }
                ),
                400,
            )

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400

        new_user = User(name=name, email=email, password=password)
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Registered successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login an existing user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        if not validate_email(email):
            return jsonify({"message": "Invalid email format"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        return (
            jsonify(
                {
                    "message": "Logged in successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """Test protected route."""
    get_identity = get_jwt_identity()
    user = current_user
    return jsonify({"message": f"Hello {get_identity}", "user": user.to_dict()}), 200
