"""
Notification Service - Handles creation and management of notifications.
Provides centralized methods for triggering notifications on system events.
"""

from datetime import datetime
from src.extensions import db
from src.models import Notification, Message, Booking, User


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    def create_notification(user_id: int, notification_type: str, title: str, 
                           description: str, action_url: str = None, 
                           sender_id: int = None, message_id: int = None, 
                           booking_id: int = None) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            user_id (int): ID of user receiving the notification
            notification_type (str): Type of notification (from Notification.VALID_TYPES)
            title (str): Short title of the notification
            description (str): Detailed description of the notification
            action_url (str, optional): URL to navigate to when clicked
            sender_id (int, optional): ID of user who triggered the notification
            message_id (int, optional): Associated message ID
            booking_id (int, optional): Associated booking ID
            
        Returns:
            Notification: The created notification object
        """
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                description=description,
                action_url=action_url,
                sender_id=sender_id,
                message_id=message_id,
                booking_id=booking_id,
                is_read=False
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating notification: {str(e)}")
    
    @staticmethod
    def notify_new_message(sender_id: int, recipient_id: int, message: Message) -> Notification:
        """
        Create notification for a new message.
        
        Args:
            sender_id (int): ID of message sender
            recipient_id (int): ID of message recipient
            message (Message): The message object
            
        Returns:
            Notification: The created notification
        """
        sender = db.session.get(User, sender_id)
        sender_name = sender.full_name if sender else "Unknown User"
        
        return NotificationService.create_notification(
            user_id=recipient_id,
            notification_type=Notification.TYPE_NEW_MESSAGE,
            title=f"New message from {sender_name}",
            description=message.body[:100] + ('...' if len(message.body) > 100 else ''),
            action_url=f"/messages/thread/{message.thread_id or message.id}",
            sender_id=sender_id,
            message_id=message.id
        )
    
    @staticmethod
    def notify_booking_request(booking: Booking) -> Notification:
        """
        Create notification for a new booking request (sent to resource owner).
        
        Args:
            booking (Booking): The booking object
            
        Returns:
            Notification: The created notification
        """
        user = db.session.get(User, booking.user_id)
        user_name = user.full_name if user else "Unknown User"
        resource_name = booking.resource.name if booking.resource else "A Resource"
        
        return NotificationService.create_notification(
            user_id=booking.resource.creator_id,
            notification_type=Notification.TYPE_BOOKING_REQUEST,
            title=f"Booking request for {resource_name}",
            description=f"{user_name} has requested to book your resource.",
            action_url=f"/bookings/pending",
            sender_id=booking.user_id,
            booking_id=booking.id
        )
    
    @staticmethod
    def notify_booking_confirmed(booking: Booking) -> Notification:
        """
        Create notification for confirmed booking (sent to requester).
        
        Args:
            booking (Booking): The booking object
            
        Returns:
            Notification: The created notification
        """
        resource_name = booking.resource.name if booking.resource else "A Resource"
        
        return NotificationService.create_notification(
            user_id=booking.user_id,
            notification_type=Notification.TYPE_BOOKING_CONFIRMED,
            title=f"Booking confirmed for {resource_name}",
            description=f"Your booking for {resource_name} has been confirmed!",
            action_url=f"/bookings/{booking.id}",
            sender_id=booking.resource.creator_id,
            booking_id=booking.id
        )
    
    @staticmethod
    def notify_booking_denied(booking: Booking, reason: str = "") -> Notification:
        """
        Create notification for denied booking (sent to requester).
        
        Args:
            booking (Booking): The booking object
            reason (str, optional): Reason for denial
            
        Returns:
            Notification: The created notification
        """
        resource_name = booking.resource.name if booking.resource else "A Resource"
        description = f"Your booking for {resource_name} was denied."
        if reason:
            description += f" Reason: {reason}"
        
        return NotificationService.create_notification(
            user_id=booking.user_id,
            notification_type=Notification.TYPE_BOOKING_DENIED,
            title=f"Booking denied for {resource_name}",
            description=description,
            action_url=f"/bookings",
            sender_id=booking.resource.creator_id,
            booking_id=booking.id
        )
    
    @staticmethod
    def notify_booking_cancelled(booking: Booking, cancelled_by_id: int, reason: str = "") -> list:
        """
        Create notifications for cancelled booking (sent to both parties).
        
        Args:
            booking (Booking): The booking object
            cancelled_by_id (int): ID of user who cancelled
            reason (str, optional): Reason for cancellation
            
        Returns:
            list: List of created notifications
        """
        resource_name = booking.resource.name if booking.resource else "A Resource"
        reason_text = f" Reason: {reason}" if reason else ""
        
        notifications = []
        
        # Notify requester
        notifications.append(NotificationService.create_notification(
            user_id=booking.user_id,
            notification_type=Notification.TYPE_BOOKING_CANCELLED,
            title=f"Booking cancelled for {resource_name}",
            description=f"Your booking for {resource_name} has been cancelled.{reason_text}",
            action_url=f"/bookings",
            sender_id=cancelled_by_id,
            booking_id=booking.id
        ))
        
        # Notify resource owner if not the one who cancelled
        if cancelled_by_id != booking.resource.creator_id:
            notifications.append(NotificationService.create_notification(
                user_id=booking.resource.creator_id,
                notification_type=Notification.TYPE_BOOKING_CANCELLED,
                title=f"Booking cancelled for {resource_name}",
                description=f"A booking for {resource_name} has been cancelled.{reason_text}",
                action_url=f"/bookings",
                sender_id=cancelled_by_id,
                booking_id=booking.id
            ))
        
        return notifications
    
    @staticmethod
    def notify_booking_reminder(booking: Booking) -> Notification:
        """
        Create reminder notification for upcoming booking (sent to requester).
        
        Args:
            booking (Booking): The booking object
            
        Returns:
            Notification: The created notification
        """
        resource_name = booking.resource.name if booking.resource else "A Resource"
        
        return NotificationService.create_notification(
            user_id=booking.user_id,
            notification_type=Notification.TYPE_BOOKING_REMINDER,
            title=f"Reminder: Your booking is coming up",
            description=f"Your booking for {resource_name} is scheduled to begin soon.",
            action_url=f"/bookings/{booking.id}",
            booking_id=booking.id
        )
    
    @staticmethod
    def notify_review_flagged(review) -> Notification:
        """
        Create notification for flagged review (sent to resource owner).
        
        Args:
            review: The review object
            
        Returns:
            Notification: The created notification
        """
        resource_name = review.resource.name if review.resource else "A Resource"
        
        return NotificationService.create_notification(
            user_id=review.resource.creator_id,
            notification_type=Notification.TYPE_REVIEW_FLAGGED,
            title=f"Review flagged for {resource_name}",
            description=f"A review for your resource has been flagged as inappropriate.",
            action_url=f"/admin/flagged-reviews",
            sender_id=review.reviewer_id
        )
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id (int): ID of user
            
        Returns:
            int: Count of unread notifications
        """
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def get_recent_notifications(user_id: int, limit: int = 10) -> list:
        """
        Get recent notifications for a user (unread first).
        
        Args:
            user_id (int): ID of user
            limit (int): Maximum number of notifications to return
            
        Returns:
            list: List of notification objects
        """
        return Notification.query.filter_by(user_id=user_id).order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).limit(limit).all()
