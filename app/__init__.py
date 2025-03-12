"""
Application factory module.
"""

from flask import Flask
from flask_migrate import Migrate
from app.extensions import init_extensions, jwt, db
from app.api.auth import auth_bp
from app.api.UserDetails import user_bp
from app.api.chatbot import chatbot_bp


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

    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")


    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    from app.models.User import User
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        print("x-x"*100, identity, "x-x"*100)
        return User.query.filter_by(email=identity).one_or_none()
    

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return {"message": "Token has expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return {"message": "Invalid token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return {"message": "Authorization header is missing"}, 401

    @jwt.needs_fresh_token_loader
    def fresh_token_callback(jwt_header, jwt_data):
        return {"message": "Fresh token required"}, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return {"message": "Token has been revoked"}, 401

    @jwt.token_verification_failed_loader
    def verification_failed_callback(jwt_header, jwt_data):
        return {"message": "Token verification failed"}, 401

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_data):
        jti = jwt_data["jti"]
        # Here you would check if the token is in your blocklist
        # For now, return False to indicate token is not revoked
        return False


    # Root route
    @app.route("/")
    def index():
        return {"message": "Welcome to the Harmonia API"}, 200

    return app
