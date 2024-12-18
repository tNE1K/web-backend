from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["backend"]
message_collection = db["messages"]

chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    current_user = get_jwt_identity()
    data = request.json

    message = {
        'content': data['content'],
        'sender': current_user,
        'recipient': data['recipient'],
        'timestamp': datetime.datetime.utcnow(),
        'status': 'sent',
        'type': data.get('type', 'text'),
        'attachment_url': data.get('attachment_url', None)
    }

    message_collection.insert_one(message)
    
    return jsonify({"status": "success", "message": "Message sent!"}), 200

@chat_blueprint.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    current_user = get_jwt_identity()
    recipient = request.args.get('recipient')

    if not recipient:
        return jsonify({"status": "error", "message": "Recipient is required!"}), 400

    messages = message_collection.find({
        '$or': [
            {'sender': current_user, 'recipient': recipient},
            {'sender': recipient, 'recipient': current_user}
        ]
    })
    
    messages_list = []
    for message in messages:
        message['_id'] = str(message['_id'])
        messages_list.append(message)
    
    return jsonify(messages_list), 200

@chat_blueprint.route('/message/<message_id>/read', methods=['PATCH'])
@jwt_required()
def update_message_status(message_id):
    current_user = get_jwt_identity()
    
    message = message_collection.find_one({"_id": ObjectId(message_id)})
    
    if not message:
        return jsonify({"status": "error", "message": "Message not found!"}), 404
    
    if message['sender'] != current_user and message['recipient'] != current_user:
        return jsonify({"status": "error", "message": "Unauthorized action!"}), 403
    
    result = message_collection.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"status": "read"}}
    )

    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Message marked as read!"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update message status!"}), 500
