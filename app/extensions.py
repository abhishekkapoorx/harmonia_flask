"""
Shared extensions module.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

def init_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}}) 