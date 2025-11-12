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
from src.services.notification_service import NotificationService

bp = Blueprint('messages', __name__, url_prefix='/messages')
api_bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/', methods=['GET'])
@login_required
def list_messages():
    """
    List user's conversations (most recent first).
    Shows last message from each conversation partner.
    Returns HTML template by default, JSON if ?json=1.
    """
    try:
        # Get all messages for current user (sent or received)
        from src.models import Message
        
        all_messages = Message.query.filter(
            (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
        ).order_by(Message.created_at.desc()).all()
        
        # Format response
        result = []
        seen_partners = {}  # Map of other_user_id to their latest message
        
        for msg in all_messages:
            # Determine other user (not current user)
            other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
            
            # Keep only the most recent message with each user
            if other_user_id not in seen_partners:
                seen_partners[other_user_id] = msg
        
        # Now convert to result list
        for other_user_id, msg in seen_partners.items():
            # Get other user details
            other_user = db.session.get(User, other_user_id)
            if not other_user:
                continue
            
            result.append({
                'thread_id': msg.thread_id or msg.id,
                'other_user': {
                    'id': other_user.id,
                    'name': other_user.full_name,
                    'email': other_user.email,
                    'profile_image': other_user.profile_image
                },
                'last_message': msg.body[:100],  # Preview
                'is_read': msg.is_read or msg.sender_id == current_user.id,
                'created_at': msg.created_at.isoformat(),
                'is_from_me': msg.sender_id == current_user.id
            })
        
        # Check if JSON requested
        if request.args.get('json') == '1':
            return jsonify({
                'status': 'success',
                'conversations': result,
                'count': len(result)
            }), 200
        
        # Return HTML template (default)
        return render_template('messages/inbox.html',
                             conversations=result,
                             count=len(result))
    
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
    Handles both thread_id (when thread was explicitly set) and message_id (fallback).
    Returns JSON if ?json=1, otherwise returns HTML template.
    """
    try:
        from src.models import Message
        
        # First try to get messages with this thread_id
        messages = MessageDAL.get_thread_messages(thread_id)
        
        # If no messages found with thread_id, it might be a message_id (fallback case)
        if not messages:
            # Try to fetch the message directly
            message = db.session.get(Message, thread_id)
            if not message:
                abort(404)
            
            # Get the other user in the conversation
            other_user_id = message.recipient_id if message.sender_id == current_user.id else message.sender_id
            
            # Get all messages between current user and other user
            messages = MessageDAL.get_conversation_between_users(current_user.id, other_user_id)
            
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
        
        # Create notification for recipient
        try:
            NotificationService.notify_new_message(
                sender_id=current_user.id,
                recipient_id=recipient_id,
                message=message
            )
        except Exception as e:
            # Log error but don't fail the message send
            print(f"Error creating notification: {str(e)}")
        
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


# ============================================================================
# NOTIFICATION ENDPOINTS (API)
# ============================================================================

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """
    Get all notifications for current user.
    Includes stored notifications + upcoming booking reminders.
    Returns JSON with list of notifications (unread first).
    """
    try:
        from src.models import Notification, Booking
        from datetime import datetime, timedelta
        
        # Get stored notifications sorted by unread status and creation date
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).all()
        
        # Also include upcoming bookings as alerts
        upcoming_bookings = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.status.in_(['pending', 'confirmed']),
            Booking.start_time > datetime.utcnow(),
            Booking.start_time <= datetime.utcnow() + timedelta(days=7)  # Next 7 days
        ).all()
        
        # Convert notifications to dicts
        notif_dicts = [n.to_dict() for n in notifications]
        
        # Add upcoming bookings as special notifications
        for booking in upcoming_bookings:
            time_diff = booking.start_time - datetime.utcnow()
            hours_left = time_diff.total_seconds() / 3600
            days_left = int(hours_left / 24)
            
            if days_left == 0:
                time_str = f"in {int(hours_left)} hours"
            elif days_left == 1:
                time_str = "tomorrow"
            else:
                time_str = f"in {days_left} days"
            
            booking_alert = {
                'id': f'booking_{booking.id}',  # Virtual ID
                'user_id': current_user.id,
                'notification_type': 'booking_reminder',
                'title': f'Upcoming: {booking.resource.name}',
                'description': f'Your booking for {booking.resource.name} starts {time_str}',
                'is_read': False,
                'action_url': f'/bookings/{booking.id}/view',
                'sender_id': None,
                'created_at': booking.start_time.isoformat(),
                'read_at': None
            }
            notif_dicts.insert(0, booking_alert)  # Add at the top
        
        return jsonify({
            'status': 'success',
            'notifications': notif_dicts,
            'count': len(notif_dicts)
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve notifications'
        }), 500


@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read (recipient only)."""
    try:
        from src.models import Notification
        from flask import current_app
        
        notification = db.session.get(Notification, notification_id)
        
        if not notification:
            return jsonify({
                'status': 'error',
                'error': 'Notification not found'
            }), 404
        
        # Verify authorization (only recipient can mark as read)
        if notification.user_id != current_user.id:
            current_app.logger.warning(
                f'Authorization failed: Notification {notification_id} belongs to user {notification.user_id}, '
                f'but current user is {current_user.id}'
            )
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized',
                'debug': f'Notification belongs to user {notification.user_id}, current user is {current_user.id}'
            }), 403
        
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Notification marked as read'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': 'Failed to mark notification as read'
        }), 500


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all unread notifications as read for current user."""
    try:
        from src.models import Notification
        
        # Get all unread notifications for current user
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        # Mark as read
        for notification in unread_notifications:
            notification.mark_as_read()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'{len(unread_notifications)} notifications marked as read',
            'count': len(unread_notifications)
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': 'Failed to mark notifications as read'
        }), 500


@api_bp.route('/notifications/unread-count', methods=['GET'])
@login_required
def get_unread_notification_count():
    """Get count of unread notifications for current user."""
    try:
        from src.models import Notification
        
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({
            'status': 'success',
            'unread_count': count
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'error': 'Failed to get unread count'
        }), 500
