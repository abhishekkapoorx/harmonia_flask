"""
Prediction routes blueprint.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import pickle
import numpy as np
import pandas as pd
import os
import traceback
import sys
# Try importing optional dependencies with error handling
try:
    import torch
    import cv2
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: torch or cv2 not available. Image analysis features will be disabled.")

from werkzeug.utils import secure_filename
import json
import uuid
from app.models.user import User
from app.models.pcos_prediction import PCOSPrediction
from app.extensions import db


# Create blueprint
predict_bp = Blueprint('predict', __name__)

# Load the model at blueprint creation
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_models', 'pcos_best_model_pipeline.pkl')
model_pipeline = None

def load_model(model_path=MODEL_PATH):
    """Load the saved model pipeline"""
    with open(model_path, 'rb') as f:
        loaded_pipeline = pickle.load(f)
    print(f"Loaded model: {loaded_pipeline['model_name']}")
    return loaded_pipeline

# Try to load the model
try:
    model_pipeline = load_model()
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model_pipeline = None


def preprocess_input_data(data_dict):
    """
    Preprocess input data from JSON to match the format expected by the model
    """
    # Convert to DataFrame
    df = pd.DataFrame([data_dict])
    
    # Handle missing values for numeric fields
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert any binary Y/N columns to 1/0
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # Try to convert 'Y'/'N' format
                if set(df[col].dropna().unique()).issubset(['Y', 'N']):
                    df[col] = df[col].map({'Y': 1, 'N': 0})
                elif set(df[col].dropna().unique()).issubset(['y', 'n']):
                    df[col] = df[col].map({'y': 1, 'n': 0})
                elif set(df[col].dropna().unique()).issubset(['yes', 'no']):
                    df[col] = df[col].map({'yes': 1, 'no': 0})
                elif set(df[col].dropna().unique()).issubset(['Yes', 'No']):
                    df[col] = df[col].map({'Yes': 1, 'No': 0})
            except:
                pass
    
    return df


@predict_bp.route('/predict-pcos', methods=['POST'])
@jwt_required()
def predict_pcos():
    """Predict PCOS based on general health parameters."""
    try:
        # Verify user
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        # Get data from request
        data = request.get_json() or {}
        
        # Check if model is loaded
        global model_pipeline
        if model_pipeline is None:
            try:
                model_pipeline = load_model()
            except Exception as e:
                return jsonify({
                    "success": False,
                    "msg": "Model not available",
                    "error": str(e)
                }), 500
        
        # Check if required features are in the request
        feature_names = model_pipeline['feature_names']
        missing_features = [feature for feature in feature_names if feature not in data]
        
        if missing_features:
            return jsonify({
                "success": False,
                "msg": "Missing required features",
                "missing_features": missing_features
            }), 400
        
        # Preprocess the input data
        df = preprocess_input_data(data)
        
        # Extract components from the pipeline
        model = model_pipeline['model']
        preprocessor = model_pipeline['preprocessor']
        
        # Ensure all required features are present
        for feature in feature_names:
            if feature not in df.columns:
                df[feature] = 0  # Default value for missing features
        
        # Select only the needed features and in the correct order
        X = df[feature_names]
        
        # Apply preprocessing
        X_processed = preprocessor.transform(X)
        
        # Get probability predictions if the model supports it
        threshold = 0.5
        # print(f"\n\n\nProba: {model.predict_proba(X_processed)}\n\n\n")
        if hasattr(model, 'predict_proba'):
            probability = float(model.predict_proba(X_processed)[0, 1])
            prediction = int(1 if probability >= threshold else 0)
        else:
            prediction = int(model.predict(X_processed)[0])
            probability = None
        
        # Determine risk level and recommendation
        if prediction == 1:
            risk_level = "high" if probability is not None and probability > 0.75 else "moderate"
            recommendation = "Please consult with a healthcare provider for further evaluation and management."
        else:
            risk_level = "low"
            recommendation = "Continue routine health monitoring."
            
        # Store prediction in database
        prediction_record = PCOSPrediction(
            user_id=user.id,
            input_data=data,
            prediction=prediction,
            probability=probability,
            risk_level=risk_level
        )
        
        db.session.add(prediction_record)
        db.session.commit()
        
        # Prepare response
        response = {
            "success": True,
            "prediction": prediction,
            "prediction_label": "PCOS" if prediction == 1 else "No PCOS",
            "probability": probability if probability is not None else "Not available",
            "risk_level": risk_level,
            "recommendation": recommendation,
            "prediction_id": prediction_record.id
        }
        
        return jsonify(response)
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR in predict_pcos: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        return jsonify({
            "success": False,
            "msg": "Failed to predict PCOS",
            "error": str(e)
        }), 500


@predict_bp.route('/predict-pcos-ultrasound', methods=['POST'])
@jwt_required()
def predict_pcos_ultrasound():
    """Predict PCOS based on ultrasound image and related parameters."""
    pass


@predict_bp.route('/model-info', methods=['GET'])
@jwt_required()
def model_info():
    """API endpoint to get information about the model"""
    try:
        # Check if model is loaded
        global model_pipeline
        if model_pipeline is None:
            try:
                model_pipeline = load_model()
            except Exception as e:
                return jsonify({
                    "success": False,
                    "msg": "Model not available",
                    "error": str(e)
                }), 500
        
        info = {
            "success": True,
            "model_type": model_pipeline['model_name'],
            "hyperparameters": model_pipeline['hyperparameters'],
            "features": model_pipeline['feature_names'],
            "sampling_method": model_pipeline.get('sampling_method', 'Unknown'),
            "sampling_ratio": model_pipeline.get('sampling_ratio', 'Unknown')
        }
        
        return jsonify(info)
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR in model_info: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        return jsonify({
            "success": False,
            "msg": "Failed to get model info",
            "error": str(e)
        }), 500


@predict_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_user_predictions():
    """Get all predictions for the current user."""
    try:
        # Verify user
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        # Get predictions
        predictions = PCOSPrediction.query.filter_by(user_id=user.id).order_by(PCOSPrediction.created_at.desc()).all()
        
        # Return predictions
        return jsonify({
            "success": True,
            "predictions": [prediction.to_dict() for prediction in predictions]
        })
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR in get_user_predictions: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        return jsonify({
            "success": False,
            "msg": "Failed to get predictions",
            "error": str(e)
        }), 500