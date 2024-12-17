from pymongo import MongoClient
from utils.token_utils import is_token_expired
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["backend"]
user_collection = db["users"]


class User:
    @staticmethod
    def find_by_email(email):
        return user_collection.find_one({"email": email})

    @staticmethod
    def find_by_id(id):
        return user_collection.find_one({"_id": id})

    @staticmethod
    def set_verify_token(email, token):
        return user_collection.update_one(
            {"email": email}, {"$set": {"email_verify_token": token}}
        )

    @staticmethod
    def check_verify_token(email):
        user = user_collection.find_one(
            {"email": email}, {"email_verify_token": 1, "_id": 0}
        )
        token = user["email_verify_token"]
        return is_token_expired(token)

    @staticmethod
    def del_verify_token(email):
        return user_collection.update_one(
            {"email": email}, {"$unset": {"email_verify_token": ""}}
        )

    @staticmethod
    def get_all_user():
        users = user_collection.find()
        users_list = [doc for doc in users]
        for user in users_list:
            user["_id"] = str(user["_id"])
        return users_list

    @staticmethod
    def insert_user(user):
        user_collection.insert_one(user)

    @staticmethod
    def update_user_field(email, update_data):
        return user_collection.update_one({"email": email}, {"$set": update_data})
