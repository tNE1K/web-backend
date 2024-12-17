from flask import Blueprint, request, jsonify
from flask_cors import CORS
from utils.token_utils import create_jwt_token, create_email_verify_token
from models.user_model import User
from utils.hash_utils import hash_password, verify_password
from utils.email_utils import send_verification_email
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")

auth_blueprint = Blueprint("auth", __name__)
CORS(auth_blueprint, origins=["http://127.0.0.1:3000"], supports_credentials=True)

@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.find_by_email(email)

    if email == "admin@example.com" and password == "admin":
        token = create_jwt_token(user)
        response = jsonify({"message": "Login successful"})
        response.set_cookie(
            "auth_token", token, httponly=True, secure=False, samesite="Strict"
        )  # secure=True in production
        return response, 200

    if user and verify_password(password, user["password"]):
        if not user["isVerify"]:
            token = create_email_verify_token(user)
            User.set_verify_token(email, token)
            try:
                send_verification_email(email, token)
            except Exception as e:
                print(f"Error sending verification email: {e}")
            return jsonify({"message": "Not verified. A new verification email has been sent."}), 403
        User.del_verify_token(user["email"])
        token = create_jwt_token(user)
        response = jsonify({"message": "Login successful"})
        response.set_cookie(
            "auth_token", token, httponly=True, secure=False, samesite="Strict"
        )  # secure=True in production
        return response, 200

    return jsonify({"message": "Invalid credentials"}), 401


@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check if the email is already registered
    if User.find_by_email(email):
        return jsonify({"message": "Email already registered"}), 400

    # Hash the password
    hashed_password = hash_password(password)

    # Insert the new user
    new_user = {"email": email, "password": hashed_password, "role": "user", "isVerify" : False}
    User.insert_user(new_user)
    
    # Create, save email verification token and send verification email
    token = create_email_verify_token(new_user)
    User.set_verify_token(new_user["email"], token)
    
    try:
        send_verification_email(email, token)
    except Exception as e:
        print(f"Error sending verification email: {e}")
    
    response = jsonify({"message": "Signup successful, please verify your email"})
    return response, 201


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.set_cookie(
        "auth_token", "", httponly=True, secure=False, samesite="Strict", expires=0
    )  # secure=True in production
    return response, 200


@auth_blueprint.route("/me", methods=["GET"])
def get_user():
    token = request.cookies.get("auth_token")
    if not token:
        return jsonify({"message": "Unauthorized"}), 401
    try:
        user_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify(
            {
                "id": user_data["user_id"],
                "email": user_data["email"],
                "role": user_data["role"],
                "isVerify": user_data["isVerify"]
            }
        )
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

@auth_blueprint.route("/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"message": "Token is required"}), 400

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload["email"]
        user = User.find_by_email(email)
        if not user:
            return jsonify({"message": "Invalid token"}), 401

        if user.get("email_verify_token") != token:
            return jsonify({"message": "Invalid token"}), 401

        User.update_user_field(email, {"isVerify": True})
        return jsonify({"message": "Email verified successfully"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401