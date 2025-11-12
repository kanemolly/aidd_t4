"""
Message Data Access Layer (DAL)
Handles all database operations for Message model with CRUD functions.
Supports threading with thread_id for conversation grouping.
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from src.extensions import db
from src.models import Message


class MessageDAL:
    """Data Access Layer for Message model."""

    @staticmethod
    def send_message(sender_id: int, recipient_id: int, subject: str, body: str,
                    thread_id: int = None) -> Message:
        """
        Send a new message.

        Args:
            sender_id (int): ID of user sending the message
            recipient_id (int): ID of user receiving the message
            subject (str): Message subject
            body (str): Message body/content
            thread_id (int): Optional thread ID for conversation grouping

        Returns:
            Message: Created message object

        Raises:
            ValueError: If sender and recipient are same user
            SQLAlchemyError: For database errors
        """
        try:
            if sender_id == recipient_id:
                raise ValueError("Sender and recipient cannot be the same user")

            # If no thread_id provided, try to find an existing conversation
            if not thread_id:
                # Look for any message in an existing conversation between these users
                existing_message = Message.query.filter(
                    ((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id)) |
                    ((Message.sender_id == recipient_id) & (Message.recipient_id == sender_id))
                ).first()
                
                # Use existing thread_id if found, otherwise use first message's ID as thread
                if existing_message and existing_message.thread_id:
                    thread_id = existing_message.thread_id
                elif existing_message:
                    # Use the first message's ID as the thread_id for all messages in this conversation
                    thread_id = existing_message.id

            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                subject=subject,
                body=body,
                thread_id=thread_id,
                is_read=False
            )
            db.session.add(message)
            db.session.commit()
            return message
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error sending message: {str(e)}")

    @staticmethod
    def get_message_by_id(message_id: int) -> Message:
        """
        Get message by ID.

        Args:
            message_id (int): Message's primary key

        Returns:
            Message: Message object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return db.session.get(Message, message_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching message by ID: {str(e)}")

    @staticmethod
    def get_user_conversations(user_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get all conversations for a user (both sent and received messages).

        Args:
            user_id (int): ID of user
            limit (int): Maximum number of conversations to return. Optional.
            offset (int): Number of conversations to skip. Default: 0

        Returns:
            list: List of Message objects (most recent from each conversation)

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            # Get distinct conversations (sender and recipient combinations)
            query = Message.query.filter(
                (Message.sender_id == user_id) | (Message.recipient_id == user_id)
            ).order_by(Message.created_at.desc()).offset(offset)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user conversations: {str(e)}")

    @staticmethod
    def get_thread_messages(thread_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get all messages in a thread.

        Args:
            thread_id (int): ID of thread
            limit (int): Maximum number of messages to return. Optional.
            offset (int): Number of messages to skip. Default: 0

        Returns:
            list: List of Message objects in thread, ordered by creation time

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Message.query.filter_by(thread_id=thread_id).order_by(Message.created_at).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching thread messages: {str(e)}")

    @staticmethod
    def get_conversation_between_users(user_id1: int, user_id2: int, limit: int = None,
                                      offset: int = 0) -> list:
        """
        Get all messages exchanged between two users.

        Args:
            user_id1 (int): First user ID
            user_id2 (int): Second user ID
            limit (int): Maximum number of messages to return. Optional.
            offset (int): Number of messages to skip. Default: 0

        Returns:
            list: List of Message objects between the users

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Message.query.filter(
                ((Message.sender_id == user_id1) & (Message.recipient_id == user_id2)) |
                ((Message.sender_id == user_id2) & (Message.recipient_id == user_id1))
            ).order_by(Message.created_at).offset(offset)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching conversation: {str(e)}")

    @staticmethod
    def get_inbox_messages(recipient_id: int, unread_only: bool = False, limit: int = None,
                          offset: int = 0) -> list:
        """
        Get messages received by a user.

        Args:
            recipient_id (int): ID of recipient
            unread_only (bool): If True, return only unread messages. Default: False
            limit (int): Maximum number of messages to return. Optional.
            offset (int): Number of messages to skip. Default: 0

        Returns:
            list: List of Message objects received by user

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Message.query.filter_by(recipient_id=recipient_id)

            if unread_only:
                query = query.filter_by(is_read=False)

            query = query.order_by(Message.created_at.desc()).offset(offset)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching inbox messages: {str(e)}")

    @staticmethod
    def get_sent_messages(sender_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get messages sent by a user.

        Args:
            sender_id (int): ID of sender
            limit (int): Maximum number of messages to return. Optional.
            offset (int): Number of messages to skip. Default: 0

        Returns:
            list: List of Message objects sent by user

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Message.query.filter_by(sender_id=sender_id).order_by(Message.created_at.desc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching sent messages: {str(e)}")

    @staticmethod
    def mark_as_read(message_id: int) -> Message:
        """
        Mark a message as read.

        Args:
            message_id (int): Message's primary key

        Returns:
            Message: Updated message object

        Raises:
            ValueError: If message not found
            SQLAlchemyError: For database errors
        """
        try:
            message = db.session.get(Message, message_id)
            if not message:
                raise ValueError(f"Message with ID {message_id} not found")

            if not message.is_read:
                message.is_read = True
                message.read_at = datetime.utcnow()
                db.session.commit()

            return message
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error marking message as read: {str(e)}")

    @staticmethod
    def mark_as_unread(message_id: int) -> Message:
        """
        Mark a message as unread.

        Args:
            message_id (int): Message's primary key

        Returns:
            Message: Updated message object

        Raises:
            ValueError: If message not found
            SQLAlchemyError: For database errors
        """
        try:
            message = db.session.get(Message, message_id)
            if not message:
                raise ValueError(f"Message with ID {message_id} not found")

            if message.is_read:
                message.is_read = False
                message.read_at = None
                db.session.commit()

            return message
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error marking message as unread: {str(e)}")

    @staticmethod
    def mark_thread_as_read(thread_id: int) -> int:
        """
        Mark all unread messages in a thread as read.

        Args:
            thread_id (int): Thread's ID

        Returns:
            int: Number of messages marked as read

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            messages = Message.query.filter_by(thread_id=thread_id, is_read=False).all()
            count = 0

            for message in messages:
                message.is_read = True
                message.read_at = datetime.utcnow()
                count += 1

            if count > 0:
                db.session.commit()

            return count
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error marking thread as read: {str(e)}")

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread messages for a user.

        Args:
            user_id (int): ID of recipient

        Returns:
            int: Number of unread messages

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Message.query.filter_by(recipient_id=user_id, is_read=False).count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting unread messages: {str(e)}")

    @staticmethod
    def search_messages(user_id: int, search_term: str, limit: int = None, offset: int = 0) -> list:
        """
        Search messages by subject or body for a user.

        Args:
            user_id (int): ID of user (searches both sent and received)
            search_term (str): Term to search for
            limit (int): Maximum number of messages to return. Optional.
            offset (int): Number of messages to skip. Default: 0

        Returns:
            list: List of Message objects matching search term

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            search_pattern = f"%{search_term}%"
            query = Message.query.filter(
                (Message.sender_id == user_id) | (Message.recipient_id == user_id),
                (Message.subject.ilike(search_pattern)) | (Message.body.ilike(search_pattern))
            ).order_by(Message.created_at.desc()).offset(offset)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error searching messages: {str(e)}")

    @staticmethod
    def update_message(message_id: int, **kwargs) -> Message:
        """
        Update message by ID.

        Args:
            message_id (int): Message's primary key
            **kwargs: Fields to update (subject, body, thread_id)

        Returns:
            Message: Updated message object

        Raises:
            ValueError: If message not found
            SQLAlchemyError: For database errors
        """
        try:
            message = db.session.get(Message, message_id)
            if not message:
                raise ValueError(f"Message with ID {message_id} not found")

            allowed_fields = {'subject', 'body', 'thread_id'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(message, key, value)

            db.session.commit()
            return message
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating message: {str(e)}")

    @staticmethod
    def delete_message(message_id: int) -> bool:
        """
        Delete message by ID.

        Args:
            message_id (int): Message's primary key

        Returns:
            bool: True if deletion successful, False if message not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            message = db.session.get(Message, message_id)
            if not message:
                return False

            db.session.delete(message)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting message: {str(e)}")

    @staticmethod
    def message_count() -> int:
        """
        Get total count of messages.

        Returns:
            int: Total number of messages

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Message.query.count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting messages: {str(e)}")
