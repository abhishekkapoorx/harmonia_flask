"""
Application factory module.
"""

import os
from flask import Flask
from flask_cors import CORS

from app import User
from .extensions import init_extensions, jwt
from .api.auth import auth_bp
from .api.user import user_bp
from .api.chatbot import chatbot_bp


def create_app(config_name="default"):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration to use (default, development, testing, production)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    from config import config_by_name

    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")

    # Register JWT error handlers
    # from flask_jwt_extended import jwt_required
    # from flask_jwt_extended.exceptions import (
    #     JWTDecodeError,
    #     NoAuthorizationError,
    #     InvalidHeaderError,
    #     WrongTokenError,
    #     RevokedTokenError,
    #     FreshTokenRequired,
    #     CSRFError
    # )
    # from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

    # @app.errorhandler(NoAuthorizationError)
    # def handle_no_auth_error(e):
    #     return {"message": "Authorization header is missing"}, 401

    # @app.errorhandler(JWTDecodeError)
    # def handle_jwt_decode_error(e):
    #     return {"message": "Invalid token"}, 401

    # @app.errorhandler(InvalidHeaderError)
    # def handle_invalid_header_error(e):
    #     return {"message": "Invalid JWT header"}, 401

    # @app.errorhandler(WrongTokenError)
    # def handle_wrong_token_error(e):
    #     return {"message": "Wrong token type"}, 401

    # @app.errorhandler(ExpiredSignatureError)
    # def handle_expired_signature_error(e):
    #     return {"message": "Token has expired"}, 401

    # @app.errorhandler(InvalidTokenError)
    # def handle_invalid_token_error(e):
    #     return {"message": "Token is invalid"}, 401

    # @app.errorhandler(RevokedTokenError)
    # def handle_revoked_token_error(e):
    #     return {"message": "Token has been revoked"}, 401

    # @app.errorhandler(FreshTokenRequired)
    # def handle_fresh_token_required(e):
    #     return {"message": "Fresh token required"}, 401

    # @app.errorhandler(CSRFError)
    # def handle_csrf_error(e):
    #     return {"message": "CSRF protection error"}, 401

    # Register a callback function that loads a user from your database whenever


# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    # Root route
    @app.route("/")
    def index():
        return {"message": "Welcome to the Harmonia API"}, 200

    return app
