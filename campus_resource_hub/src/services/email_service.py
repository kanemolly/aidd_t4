"""
Email notification service for Campus Resource Hub.
Sends email notifications for booking events or simulates them in development.
"""

import os
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications.
    In development mode, emails are simulated and logged to console/file.
    In production, integrate with actual email service (SendGrid, AWS SES, etc.)
    """
    
    def __init__(self, app=None):
        self.app = app
        self.simulate_mode = True  # Default to simulation
        self.notification_log_path = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize email service with Flask app."""
        self.app = app
        self.simulate_mode = app.config.get('EMAIL_SIMULATE_MODE', True)
        
        # Set up log file for simulated emails
        if self.simulate_mode:
            instance_path = app.instance_path
            os.makedirs(instance_path, exist_ok=True)
            self.notification_log_path = os.path.join(instance_path, 'email_notifications.log')
            logger.info(f"Email simulation enabled. Notifications will be logged to: {self.notification_log_path}")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email or simulate sending.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            to_name: Optional recipient name
            html_body: Optional HTML version of email body
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.simulate_mode:
                return self._simulate_email(to_email, subject, body, to_name)
            else:
                return self._send_real_email(to_email, subject, body, to_name, html_body)
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def _simulate_email(self, to_email: str, subject: str, body: str, to_name: Optional[str] = None) -> bool:
        """Simulate sending email by logging to console and file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        recipient = f"{to_name} <{to_email}>" if to_name else to_email
        
        # Console output
        print("\n" + "="*80)
        print("📧 SIMULATED EMAIL NOTIFICATION")
        print("="*80)
        print(f"Timestamp: {timestamp}")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
        
        # File logging
        if self.notification_log_path:
            try:
                with open(self.notification_log_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"To: {recipient}\n")
                    f.write(f"Subject: {subject}\n")
                    f.write(f"{'-'*80}\n")
                    f.write(f"{body}\n")
                    f.write(f"{'='*80}\n")
            except Exception as e:
                logger.error(f"Error writing to email log file: {str(e)}")
        
        return True
    
    def _send_real_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send real email using configured email service.
        TODO: Implement with SendGrid, AWS SES, or SMTP
        """
        # Placeholder for real email implementation
        logger.warning("Real email sending not implemented yet. Use EMAIL_SIMULATE_MODE=True")
        return self._simulate_email(to_email, subject, body, to_name)
    
    def send_booking_confirmation(self, booking, user) -> bool:
        """Send booking confirmation email to user."""
        subject = f"Booking Confirmed: {booking.resource.name}"
        body = f"""
Hi {user.full_name},

Your booking has been confirmed!

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Location: {booking.resource.location or 'Not specified'}

Date: {booking.start_time.strftime('%A, %B %d, %Y')}
Start Time: {booking.start_time.strftime('%I:%M %p')}
End Time: {booking.end_time.strftime('%I:%M %p')}
Duration: {self._format_duration(booking.start_time, booking.end_time)}

Booking ID: {booking.id}
Status: {booking.status.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._get_booking_notes(booking)}

Please arrive on time for your reservation. If you need to make changes, 
please contact us as soon as possible.

View your booking: http://localhost:5000/bookings/view/{booking.id}
Download calendar event: http://localhost:5000/bookings/{booking.id}/calendar

Best regards,
Campus Resource Hub Team
        """.strip()
        
        return self.send_email(user.email, subject, body, user.full_name)
    
    def send_booking_created(self, booking, user) -> bool:
        """Send notification when booking is created (pending approval)."""
        subject = f"Booking Request Received: {booking.resource.name}"
        body = f"""
Hi {user.full_name},

We've received your booking request!

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Location: {booking.resource.location or 'Not specified'}

Date: {booking.start_time.strftime('%A, %B %d, %Y')}
Start Time: {booking.start_time.strftime('%I:%M %p')}
End Time: {booking.end_time.strftime('%I:%M %p')}
Duration: {self._format_duration(booking.start_time, booking.end_time)}

Booking ID: {booking.id}
Status: PENDING APPROVAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._get_booking_notes(booking)}

Your booking is currently pending approval from our staff. You'll receive 
another email once your booking has been reviewed.

View your booking: http://localhost:5000/bookings/view/{booking.id}

Best regards,
Campus Resource Hub Team
        """.strip()
        
        return self.send_email(user.email, subject, body, user.full_name)
    
    def send_booking_cancelled(self, booking, user, cancelled_by) -> bool:
        """Send notification when booking is cancelled."""
        subject = f"Booking Cancelled: {booking.resource.name}"
        
        cancelled_by_text = "You" if cancelled_by.id == user.id else f"Staff ({cancelled_by.full_name})"
        
        body = f"""
Hi {user.full_name},

Your booking has been cancelled.

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Location: {booking.resource.location or 'Not specified'}

Date: {booking.start_time.strftime('%A, %B %d, %Y')}
Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}

Booking ID: {booking.id}
Cancelled By: {cancelled_by_text}
Status: CANCELLED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you did not request this cancellation or have any questions, 
please contact us immediately.

Best regards,
Campus Resource Hub Team
        """.strip()
        
        return self.send_email(user.email, subject, body, user.full_name)
    
    def send_booking_reminder(self, booking, user, hours_before: int = 24) -> bool:
        """Send reminder email before booking starts."""
        subject = f"Reminder: Upcoming Booking for {booking.resource.name}"
        body = f"""
Hi {user.full_name},

This is a reminder about your upcoming booking in {hours_before} hours.

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Location: {booking.resource.location or 'Not specified'}

Date: {booking.start_time.strftime('%A, %B %d, %Y')}
Start Time: {booking.start_time.strftime('%I:%M %p')}
End Time: {booking.end_time.strftime('%I:%M %p')}

Booking ID: {booking.id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please arrive on time. If you need to cancel, please do so as soon as possible.

View your booking: http://localhost:5000/bookings/view/{booking.id}
Download calendar event: http://localhost:5000/bookings/{booking.id}/calendar

Best regards,
Campus Resource Hub Team
        """.strip()
        
        return self.send_email(user.email, subject, body, user.full_name)
    
    def _format_duration(self, start_time, end_time) -> str:
        """Format duration between two times."""
        duration = end_time - start_time
        hours = duration.total_seconds() / 3600
        
        if hours < 1:
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        elif hours == 1:
            return "1 hour"
        else:
            return f"{hours:.1f} hours"
    
    def _get_booking_notes(self, booking) -> str:
        """Get formatted notes section."""
        if booking.notes:
            return f"Notes: {booking.notes}\n"
        return ""


# Global instance
email_service = EmailService()
