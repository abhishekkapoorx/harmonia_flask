"""
Chat routes blueprint.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.chat import Chat, Message, SenderType
from app.extensions import db
from app.utils.chatbot import chat as chat_with_ai
import uuid
from sqlalchemy import func

# Create blueprint
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/get-chats', methods=['GET'])
@jwt_required()
def get_chats():
    """Get all chats for the current user."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        chats = Chat.query.filter_by(user_id=user.id).all()
        return jsonify({
            "chats": [chat.to_dict() for chat in chats]
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve chats", "error": str(e)}), 500


@chat_bp.route('/get-chat/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    """Get a specific chat with all messages."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
        
        if not chat:
            return jsonify({"msg": "Chat not found"}), 404
        
        return jsonify({
            "chat": chat.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve chat", "error": str(e)}), 500


@chat_bp.route('/<chat_id>/get-messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    """Get all messages for a specific chat."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
        
        if not chat:
            return jsonify({"msg": "Chat not found"}), 404
        
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
        
        return jsonify({
            "chat_id": chat_id,
            "messages": [message.to_dict() for message in messages]
        }), 200
    except Exception as e:
        return jsonify({"msg": "Failed to retrieve messages", "error": str(e)}), 500


@chat_bp.route('/create-chat', methods=['POST'])
@jwt_required()
def create_chat():
    """Create a new chat."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        # data = request.get_json() or {}
        # title = data.get('title', f"Chat {uuid.uuid4().hex[:8]}")
        title = f"Chat {uuid.uuid4().hex[:8]}"

        # Create new chat with constructor parameters
        new_chat = Chat(
            user_id=user.id,
            title=title
        )
        
        db.session.add(new_chat)
        db.session.commit()
        
        return jsonify({
            "msg": "Chat created successfully",
            "chat": new_chat.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to create chat", "error": str(e)}), 500


@chat_bp.route('/delete-chat/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    """Delete a chat and all its messages."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
        
        if not chat:
            return jsonify({"msg": "Chat not found"}), 404
        
        db.session.delete(chat)
        db.session.commit()
        
        return jsonify({
            "msg": "Chat deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to delete chat", "error": str(e)}), 500


@chat_bp.route('/send-message/<chat_id>', methods=['POST'])
@jwt_required()
async def send_message(chat_id):
    """Send a message in a chat and get AI response."""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"msg": "User not found"}), 401
        
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
        
        if not chat:
            return jsonify({"msg": "Chat not found"}), 404
        
        data = request.get_json() or {}
        user_message_content = data.get('message')
        
        if not user_message_content:
            return jsonify({"msg": "Message content is required"}), 400
        
        # Create user message with constructor parameters
        user_message = Message(
            chat_id=chat.id,
            content=user_message_content,
            sent_by=SenderType.USER
        )
        
        db.session.add(user_message)
        
        # Get user details for context
        user_details = user.user_details[0] if hasattr(user, 'user_details') and user.user_details else None
        user_details_dict = user_details.to_dict() if user_details else {}
        
        # Get AI response
        ai_response_content = await chat_with_ai(user_message_content, user_details_dict)
        
        # Create AI message with constructor parameters
        ai_message = Message(
            chat_id=chat.id,
            content=str(ai_response_content),  # Ensure content is a string
            sent_by=SenderType.AI
        )
        
        db.session.add(ai_message)
        
        # Update chat timestamp
        chat.updated_at = func.now()
        
        db.session.commit()
        
        return jsonify({
            "user_message": user_message.to_dict(),
            "ai_message": ai_message.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to send message", "error": str(e)}), 500


