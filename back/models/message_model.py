from pymongo import MongoClient
import os
from datetime import datetime

class Message:
    def __init__(self, content, sender, recipient):
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "content": self.content,
            "sender": self.sender,
            "recipient": self.recipient,
            "timestamp": self.timestamp
        }

# Kết nối đến MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["backend"]
message_collection = db["messages"]

def save_message(message):
    message_collection.insert_one(message.to_dict())