from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
import datetime
from flask_cors import CORS
from dotenv import load_dotenv
from chatbot import chat, get_meal_plan

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

# Configuration for Neon PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://neondb_owner:npg_ljLgbCrK8Bk5@ep-lucky-mouse-a5g8nmxy-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = (
    "your_jwt_secret_key"  # Change this to a random secret key
)

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)


class UserDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("details", lazy=True))

    age = db.Column(db.String(3), nullable=False)
    height = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.String(10), nullable=False)

    periodRegularity = db.Column(db.String(50), nullable=False)
    periodDuration = db.Column(db.String(50), nullable=False)
    heavyBleeding = db.Column(db.String(50), nullable=False)
    severeCramps = db.Column(db.String(50), nullable=False)
    pcosDiagnosis = db.Column(db.String(50), nullable=False)
    hirsutism = db.Column(db.String(50), nullable=False)
    hairLoss = db.Column(db.String(50), nullable=False)
    acneSkinIssues = db.Column(db.String(50), nullable=False)
    weightGain = db.Column(db.String(50), nullable=False)
    fatigue = db.Column(db.String(50), nullable=False)

    exerciseFrequency = db.Column(db.String(50), nullable=False)
    dietType = db.Column(db.String(50), nullable=False)
    processedFoodConsumption = db.Column(db.String(50), nullable=False)
    sugarCravings = db.Column(db.String(50), nullable=False)
    waterIntake = db.Column(db.String(50), nullable=False)

    sleepHours = db.Column(db.String(50), nullable=False)
    sleepDisturbances = db.Column(db.String(50), nullable=False)
    mentalHealthIssues = db.Column(db.String(50), nullable=False)
    stressLevels = db.Column(db.String(50), nullable=False)

    medicalHistory = db.Column(db.String(255), nullable=True)
    medications = db.Column(db.String(255), nullable=True)
    fertilityTreatments = db.Column(db.String(255), nullable=True)

    createdAt = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<UserDetail {self.user_id}>"


@app.route("/")
def index():
    return jsonify({"message": "Hello, World!"})

def validate_email(email):
    import re
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Password should be at least 8 characters and contain at least one digit and one letter
    if not password or len(password) < 8:
        return False
    
    # Check for at least one digit and one letter
    has_digit = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)
    
    return has_digit and has_letter

def validate_name(name):
    # Name should be at least 2 characters and contain only letters, spaces, and hyphens
    if not name or len(name) < 2:
        return False
    
    import re
    return bool(re.match(r'^[A-Za-z\s\-]+$', name))

def validate_numeric_string(value, min_val=None, max_val=None):
    # Validate that a string can be converted to a number and is within range
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return False
        if max_val is not None and num_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error for debugging
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        # Extract fields with defaults to avoid KeyError
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
            return jsonify({"message": "Password must be at least 8 characters and contain at least one letter and one number"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400

        new_user = User(name=name, email=email, password=password)
        access_token = create_access_token(identity={"email": new_user.email})
        refresh_token = create_refresh_token(identity={"email": new_user.email})

        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify({"message": "Registered successfully", "access_token": access_token, "refresh_token": refresh_token}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
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

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity={"email": user.email})
        refresh_token = create_refresh_token(identity={"email": user.email})
        return (
            jsonify({"message": "Logged in successfully", "access_token": access_token, "refresh_token": refresh_token}),
            200,
        )
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Login failed", "error": str(e)}), 500


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f'Hello {current_user["email"]}'}), 200


@app.route("/chat", methods=["POST"])
async def chats():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        user_input = data.get("input")
        if not user_input or not isinstance(user_input, str):
            return jsonify({"message": "Valid input text is required"}), 400

        response = await chat(user_input)

        return jsonify({"response": str(response.content)})
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({"message": "Chat processing failed", "error": str(e)}), 500


@app.route("/meal-planner", methods=["GET", "POST"])
async def meal_planner():
    try:
        # Support both GET with query params and POST with JSON body
        if request.method == "POST":
            data = request.json
            if not data:
                return jsonify({"message": "No data provided"}), 400
        else:
            data = request.args.to_dict()
            
        # Extract and validate parameters with defaults
        age = data.get("age", "25")
        weight = data.get("weight", "70")
        height = data.get("height", "175")
        veg_or_nonveg = data.get("veg_or_nonveg", "veg")
        disease = data.get("disease", "pcos")
        region = data.get("region", "Indian")
        allergics = data.get("allergics", "")
        
        # Validate numeric fields
        if not validate_numeric_string(age, 1, 120):
            return jsonify({"message": "Invalid age value"}), 400
            
        if not validate_numeric_string(weight, 20, 300):
            return jsonify({"message": "Invalid weight value"}), 400
            
        if not validate_numeric_string(height, 50, 300):
            return jsonify({"message": "Invalid height value"}), 400
            
        # Validate diet type
        if veg_or_nonveg not in ["veg", "nonveg"]:
            return jsonify({"message": "Diet type must be 'veg' or 'nonveg'"}), 400

        meal_plan = await get_meal_plan(
            age=int(age),
            weight=float(weight),
            height=float(height),
            veg_or_nonveg=veg_or_nonveg,
            disease=disease,
            region=region,
            allergics=allergics,
        )
        
        return jsonify(meal_plan)
    except Exception as e:
        app.logger.error(f"Meal planner error: {str(e)}")
        return jsonify({"message": "Meal planning failed", "error": str(e)}), 500


@app.route("/user-details", methods=["POST"])
@jwt_required()
def add_user_details():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user["email"]).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        # Required fields validation
        required_fields = [
            "age", "height", "weight", "periodRegularity", "periodDuration",
            "heavyBleeding", "severeCramps", "pcosDiagnosis", "hirsutism",
            "hairLoss", "acneSkinIssues", "weightGain", "fatigue",
            "exerciseFrequency", "dietType", "processedFoodConsumption",
            "sugarCravings", "waterIntake", "sleepHours", "sleepDisturbances",
            "mentalHealthIssues", "stressLevels"
        ]
        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400
            
        # Validate numeric fields
        if not validate_numeric_string(data["age"], 1, 120):
            return jsonify({"message": "Invalid age value"}), 400
            
        if not validate_numeric_string(data["height"]):
            return jsonify({"message": "Invalid height value"}), 400
            
        if not validate_numeric_string(data["weight"]):
            return jsonify({"message": "Invalid weight value"}), 400
            
        # Check for existing user details
        existing_details = UserDetail.query.filter_by(user_id=user.id).first()
        if existing_details:
            return jsonify({"message": "User details already exist"}), 400
            
        # Create new user details
        user_details = UserDetail(
            user_id=user.id,
            age=data["age"],
            height=data["height"],
            weight=data["weight"],
            periodRegularity=data["periodRegularity"],
            periodDuration=data["periodDuration"],
            heavyBleeding=data["heavyBleeding"],
            severeCramps=data["severeCramps"],
            pcosDiagnosis=data["pcosDiagnosis"],
            hirsutism=data["hirsutism"],
            hairLoss=data["hairLoss"],
            acneSkinIssues=data["acneSkinIssues"],
            weightGain=data["weightGain"],
            fatigue=data["fatigue"],
            exerciseFrequency=data["exerciseFrequency"],
            dietType=data["dietType"],
            processedFoodConsumption=data["processedFoodConsumption"],
            sugarCravings=data["sugarCravings"],
            waterIntake=data["waterIntake"],
            sleepHours=data["sleepHours"],
            sleepDisturbances=data["sleepDisturbances"],
            mentalHealthIssues=data["mentalHealthIssues"],
            stressLevels=data["stressLevels"],
            medicalHistory=data.get("medicalHistory", ""),
            medications=data.get("medications", ""),
            fertilityTreatments=data.get("fertilityTreatments", "")
        )
        
        db.session.add(user_details)
        db.session.commit()
        
        return jsonify({"message": "User details added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Add user details error: {str(e)}")
        return jsonify({"message": "Failed to add user details", "error": str(e)}), 500


@app.route("/user-details", methods=["GET"])
@jwt_required()
def get_user_details():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user["email"]).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        user_details = UserDetail.query.filter_by(user_id=user.id).first()
        
        if not user_details:
            return jsonify({"message": "User details not found"}), 404
            
        # Convert user details to dictionary
        details_dict = {
            "age": user_details.age,
            "height": user_details.height,
            "weight": user_details.weight,
            "periodRegularity": user_details.periodRegularity,
            "periodDuration": user_details.periodDuration,
            "heavyBleeding": user_details.heavyBleeding,
            "severeCramps": user_details.severeCramps,
            "pcosDiagnosis": user_details.pcosDiagnosis,
            "hirsutism": user_details.hirsutism,
            "hairLoss": user_details.hairLoss,
            "acneSkinIssues": user_details.acneSkinIssues,
            "weightGain": user_details.weightGain,
            "fatigue": user_details.fatigue,
            "exerciseFrequency": user_details.exerciseFrequency,
            "dietType": user_details.dietType,
            "processedFoodConsumption": user_details.processedFoodConsumption,
            "sugarCravings": user_details.sugarCravings,
            "waterIntake": user_details.waterIntake,
            "sleepHours": user_details.sleepHours,
            "sleepDisturbances": user_details.sleepDisturbances,
            "mentalHealthIssues": user_details.mentalHealthIssues,
            "stressLevels": user_details.stressLevels,
            "medicalHistory": user_details.medicalHistory,
            "medications": user_details.medications,
            "fertilityTreatments": user_details.fertilityTreatments,
            "createdAt": user_details.createdAt.isoformat() if user_details.createdAt else None
        }
        
        return jsonify(details_dict), 200
    except Exception as e:
        app.logger.error(f"Get user details error: {str(e)}")
        return jsonify({"message": "Failed to retrieve user details", "error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000 , debug=True)
