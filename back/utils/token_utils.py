import datetime
import jwt
import os
from functools import wraps
from flask import request, jsonify

JWT_SECRET = os.getenv("JWT_SECRET")


def create_jwt_token(user):
    if user["role"] == "admin":
        expiration_time = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) + datetime.timedelta(hours=1)
        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "exp": int(expiration_time.timestamp()),
            "isVerify": user["isVerify"],
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token
    else:
        expiration_time = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) + datetime.timedelta(days=3)
        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "exp": int(expiration_time.timestamp()),
            "isVerify": user["isVerify"],
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token


def is_token_expired(token: str) -> bool:
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return False
    except jwt.ExpiredSignatureError:
        return True
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def decode_and_get_role(token):
    decoded_role = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    if decoded_role.get("role") == "admin":
        return "admin"
    else:
        return "user"


def create_email_verify_token(user):
    expiration_time = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(minutes=5)
    payload = {
        "email": user["email"],
        "exp": int(expiration_time.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not token:
            return jsonify({"message": "A valid token is missing!"}), 401
        try:
            decoded_payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return f(decoded_payload, *args, **kwargs)

    return decorated
