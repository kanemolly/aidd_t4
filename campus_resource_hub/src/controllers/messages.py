"""
Messages blueprint - user messaging and notifications.
Handles messaging threads, conversations, and notifications.
"""

from flask import Blueprint, request, jsonify, render_template, abort, session
from flask_login import login_required, current_user
from src.data_access.message_dal import MessageDAL
from src.models import User
from src.extensions import db
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('messages', __name__, url_prefix='/messages')


@bp.route('/', methods=['GET'])
@login_required
def list_messages():
    """
    List user's conversations (most recent first).
    Shows last message from each conversation partner.
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conversations = MessageDAL.get_user_conversations(
            current_user.id,
            limit=limit,
            offset=offset
        )
        
        # Format response
        result = []
        seen_partners = set()
        
        for msg in conversations:
            # Determine other user (not current user)
            other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
            
            # Skip if we've already shown this conversation
            if other_user_id in seen_partners:
                continue
            
            seen_partners.add(other_user_id)
            
            # Get other user details
            other_user = db.session.get(User, other_user_id)
            if not other_user:
                continue
            
            result.append({
                'thread_id': msg.thread_id or msg.id,
                'other_user': {
                    'id': other_user.id,
                    'name': other_user.name,
                    'email': other_user.email
                },
                'last_message': msg.body[:100],  # Preview
                'is_read': msg.is_read or msg.sender_id == current_user.id,
                'created_at': msg.created_at.isoformat(),
                'is_from_me': msg.sender_id == current_user.id
            })
        
        return jsonify({
            'status': 'success',
            'conversations': result,
            'count': len(result)
        }), 200
    
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve messages'
        }), 500


@bp.route('/thread/<int:thread_id>', methods=['GET'])
@login_required
def get_thread(thread_id):
    """
    Get all messages in a thread.
    Returns JSON if ?json=1, otherwise returns HTML template.
    """
    try:
        messages = MessageDAL.get_thread_messages(thread_id)
        
        if not messages:
            abort(404)
        
        # Verify current user is part of this thread
        thread_participants = set()
        for msg in messages:
            thread_participants.add(msg.sender_id)
            thread_participants.add(msg.recipient_id)
        
        if current_user.id not in thread_participants:
            abort(403)  # Forbidden
        
        # Check if JSON requested
        if request.args.get('json') == '1':
            return jsonify({
                'status': 'success',
                'messages': [msg.to_dict() for msg in messages]
            }), 200
        
        # Return HTML template
        # Determine other user (the one who isn't current user)
        first_msg = messages[0]
        other_user_id = first_msg.recipient_id if first_msg.sender_id == current_user.id else first_msg.sender_id
        other_user = db.session.get(User, other_user_id)
        
        return render_template('messages/thread.html',
                             thread_id=thread_id,
                             messages=messages,
                             other_user=other_user,
                             current_user=current_user)
    
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve thread'
        }), 500


@bp.route('/<int:message_id>', methods=['GET'])
@login_required
def get_message(message_id):
    """Get a specific message by ID (with authorization check)."""
    try:
        message = MessageDAL.get_message_by_id(message_id)
        
        if not message:
            return jsonify({
                'status': 'error',
                'error': 'Message not found'
            }), 404
        
        # Verify authorization
        if message.sender_id != current_user.id and message.recipient_id != current_user.id:
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized'
            }), 403
        
        return jsonify({
            'status': 'success',
            'message': message.to_dict()
        }), 200
    
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve message'
        }), 500


@bp.route('/', methods=['POST'])
@login_required
def create_message():
    """
    Send a new message.
    
    Required JSON fields:
    - recipient_id (int): User ID to send message to
    - body (str): Message content
    - thread_id (int, optional): Thread ID for conversation grouping
    - subject (str, optional): Message subject
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'No data provided'
            }), 400
        
        recipient_id = data.get('recipient_id')
        body = data.get('body', '').strip()
        thread_id = data.get('thread_id')
        subject = data.get('subject', 'Message')
        
        # Validation
        if not recipient_id:
            return jsonify({
                'status': 'error',
                'error': 'Recipient ID required'
            }), 400
        
        if not body:
            return jsonify({
                'status': 'error',
                'error': 'Message cannot be empty'
            }), 400
        
        if len(body) > 5000:
            return jsonify({
                'status': 'error',
                'error': 'Message too long (max 5000 characters)'
            }), 400
        
        # Verify recipient exists
        recipient = db.session.get(User, recipient_id)
        if not recipient:
            return jsonify({
                'status': 'error',
                'error': 'Recipient not found'
            }), 404
        
        # Send message
        message = MessageDAL.send_message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=subject,
            body=body,
            thread_id=thread_id
        )
        
        return jsonify({
            'status': 'success',
            'message': message.to_dict(),
            'thread_id': message.thread_id or message.id
        }), 201
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to send message'
        }), 500


@bp.route('/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark a message as read (recipient only)."""
    try:
        message = MessageDAL.get_message_by_id(message_id)
        
        if not message:
            return jsonify({
                'status': 'error',
                'error': 'Message not found'
            }), 404
        
        # Verify authorization (only recipient can mark as read)
        if message.recipient_id != current_user.id:
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized'
            }), 403
        
        message.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Message marked as read'
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': 'Failed to mark message as read'
        }), 500


@bp.route('/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete a message (sender or admin only)."""
    try:
        message = MessageDAL.get_message_by_id(message_id)
        
        if not message:
            return jsonify({
                'status': 'error',
                'error': 'Message not found'
            }), 404
        
        # Verify authorization (only sender can delete)
        if message.sender_id != current_user.id and not current_user.is_admin:
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized'
            }), 403
        
        MessageDAL.delete_message(message_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Message deleted'
        }), 204
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete message'
        }), 500


@bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """Get count of unread messages for current user."""
    try:
        count = MessageDAL.get_unread_count(current_user.id)
        return jsonify({
            'status': 'success',
            'unread_count': count
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to get unread count'
        }), 500
