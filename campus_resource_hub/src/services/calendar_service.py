"""
Calendar export service for Campus Resource Hub.
Generates iCal (.ics) files for bookings that can be imported into
Google Calendar, Apple Calendar, Outlook, etc.
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid


class CalendarService:
    """Service for generating iCalendar (.ics) files for bookings."""
    
    @staticmethod
    def generate_ical(booking, base_url: str = "http://localhost:5000") -> str:
        """
        Generate iCalendar format string for a booking.
        
        Args:
            booking: Booking object
            base_url: Base URL for the application
        
        Returns:
            iCalendar formatted string
        """
        # Format datetime to iCal format (YYYYMMDDTHHMMSSZ)
        def format_ical_datetime(dt):
            """Format datetime for iCal (UTC)."""
            return dt.strftime('%Y%m%dT%H%M%S')
        
        # Generate unique identifier for this event
        uid = f"booking-{booking.id}@campus-resource-hub"
        
        # Current timestamp for DTSTAMP
        now = datetime.utcnow()
        dtstamp = format_ical_datetime(now)
        
        # Start and end times
        dtstart = format_ical_datetime(booking.start_time)
        dtend = format_ical_datetime(booking.end_time)
        
        # Event summary (title)
        summary = f"{booking.resource.name} - Booking"
        
        # Description with details
        description = CalendarService._generate_description(booking, base_url)
        
        # Location
        location = booking.resource.location or "Campus Resource Hub"
        
        # Organizer (can be customized)
        organizer = "Campus Resource Hub"
        
        # Status based on booking status
        status_map = {
            'pending': 'TENTATIVE',
            'confirmed': 'CONFIRMED',
            'cancelled': 'CANCELLED',
            'completed': 'CONFIRMED'
        }
        status = status_map.get(booking.status, 'CONFIRMED')
        
        # Build iCalendar content
        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Campus Resource Hub//Booking System//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{CalendarService._escape_ical_text(description)}
LOCATION:{CalendarService._escape_ical_text(location)}
STATUS:{status}
ORGANIZER;CN={organizer}:mailto:noreply@campus-resource-hub.edu
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT1H
DESCRIPTION:Booking reminder: {summary}
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR""".strip()
        
        return ical_content
    
    @staticmethod
    def _generate_description(booking, base_url: str) -> str:
        """Generate event description with booking details."""
        duration = booking.end_time - booking.start_time
        hours = duration.total_seconds() / 3600
        
        description_parts = [
            f"Resource: {booking.resource.name}",
            f"Type: {booking.resource.resource_type.title()}",
            f"Duration: {hours:.1f} hours",
            f"Status: {booking.status.upper()}",
            ""
        ]
        
        if booking.resource.location:
            description_parts.append(f"Location: {booking.resource.location}")
        
        if booking.notes:
            description_parts.append(f"Notes: {booking.notes}")
        
        description_parts.extend([
            "",
            f"View details: {base_url}/bookings/view/{booking.id}",
            f"Booking ID: {booking.id}"
        ])
        
        return "\\n".join(description_parts)
    
    @staticmethod
    def _escape_ical_text(text: str) -> str:
        """Escape special characters for iCal format."""
        # Replace special characters
        text = text.replace('\\', '\\\\')
        text = text.replace(',', '\\,')
        text = text.replace(';', '\\;')
        text = text.replace('\n', '\\n')
        return text
    
    @staticmethod
    def generate_google_calendar_url(booking) -> str:
        """
        Generate Google Calendar add event URL.
        
        Args:
            booking: Booking object
        
        Returns:
            Google Calendar URL
        """
        from urllib.parse import quote
        
        # Format datetime for Google Calendar (YYYYMMDDTHHMMSS)
        def format_google_datetime(dt):
            return dt.strftime('%Y%m%dT%H%M%S')
        
        # Event details
        title = quote(f"{booking.resource.name} - Booking")
        start_time = format_google_datetime(booking.start_time)
        end_time = format_google_datetime(booking.end_time)
        location = quote(booking.resource.location or "Campus Resource Hub")
        
        # Description
        description_text = f"""Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Status: {booking.status.upper()}

View details: http://localhost:5000/bookings/view/{booking.id}
Booking ID: {booking.id}"""
        
        if booking.notes:
            description_text += f"\n\nNotes: {booking.notes}"
        
        description = quote(description_text)
        
        # Build Google Calendar URL
        google_url = (
            f"https://calendar.google.com/calendar/render?"
            f"action=TEMPLATE"
            f"&text={title}"
            f"&dates={start_time}/{end_time}"
            f"&details={description}"
            f"&location={location}"
            f"&sf=true"
            f"&output=xml"
        )
        
        return google_url
    
    @staticmethod
    def generate_outlook_url(booking) -> str:
        """
        Generate Outlook.com add event URL.
        
        Args:
            booking: Booking object
        
        Returns:
            Outlook.com calendar URL
        """
        from urllib.parse import quote
        
        # Format datetime for Outlook (ISO 8601)
        start_time = booking.start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time = booking.end_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Event details
        subject = quote(f"{booking.resource.name} - Booking")
        location = quote(booking.resource.location or "Campus Resource Hub")
        
        description_text = f"""Resource: {booking.resource.name}
Type: {booking.resource.resource_type.title()}
Status: {booking.status.upper()}

View details: http://localhost:5000/bookings/view/{booking.id}
Booking ID: {booking.id}"""
        
        if booking.notes:
            description_text += f"\n\nNotes: {booking.notes}"
        
        body = quote(description_text)
        
        # Build Outlook URL
        outlook_url = (
            f"https://outlook.live.com/calendar/0/deeplink/compose?"
            f"path=/calendar/action/compose"
            f"&rru=addevent"
            f"&subject={subject}"
            f"&startdt={start_time}"
            f"&enddt={end_time}"
            f"&location={location}"
            f"&body={body}"
        )
        
        return outlook_url


# Convenience instance
calendar_service = CalendarService()
