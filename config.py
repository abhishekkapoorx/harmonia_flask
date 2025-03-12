"""
Configuration module for the Flask application.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_jwt_secret_key')
    DEBUG = False
    TESTING = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        "postgresql://username:password@host:port/db_name?sslmode=require")
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10,  # Connection timeout in seconds
        }
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True  # Log SQL queries
    }

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test.db')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)

class ProductionConfig(Config):
    """Production configuration."""
    # In production, ensure all secrets are set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Use secure cookies in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Set stricter CORS in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 