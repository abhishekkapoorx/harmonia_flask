from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import os
import datetime
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

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

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(name=name, email=email, password=password)
    access_token = create_access_token(identity={"email": new_user.email})
    db.session.add(new_user)
    db.session.commit()

    return (
        jsonify({"message": "Logged in successfully", "access_token": access_token}),
        200,
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity={"email": user.email})
    return (
        jsonify({"message": "Logged in successfully", "access_token": access_token}),
        200,
    )


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f'Hello {current_user["email"]}'}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get("DEPLOYMENT"))
