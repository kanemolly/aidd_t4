"""
Booking Expiration Service
Automatically marks bookings as 'completed' when their end_time has passed.
This frees up resources for new bookings.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from src.extensions import db
from src.models import Booking

app = create_app()


def expire_past_bookings():
    """
    Mark all bookings with end_time in the past as 'completed'.
    This should be run periodically (e.g., every hour via cron job or scheduler).
    
    Returns:
        int: Number of bookings marked as completed
    """
    with app.app_context():
        current_time = datetime.now()
        
        # Find all confirmed or pending bookings that have ended
        expired_bookings = Booking.query.filter(
            Booking.end_time < current_time,
            Booking.status.in_(['confirmed', 'pending'])
        ).all()
        
        count = 0
        for booking in expired_bookings:
            booking.status = 'completed'
            count += 1
        
        if count > 0:
            db.session.commit()
            print(f"✅ Marked {count} booking(s) as completed")
        else:
            print("ℹ️  No bookings to expire")
        
        return count


def get_expiring_soon(hours=24):
    """
    Get bookings that will expire within the specified number of hours.
    Useful for sending reminder notifications.
    
    Args:
        hours (int): Number of hours to look ahead
        
    Returns:
        list: List of Booking objects expiring soon
    """
    with app.app_context():
        from datetime import timedelta
        
        current_time = datetime.now()
        future_time = current_time + timedelta(hours=hours)
        
        expiring = Booking.query.filter(
            Booking.end_time >= current_time,
            Booking.end_time <= future_time,
            Booking.status.in_(['confirmed', 'pending'])
        ).all()
        
        return expiring


if __name__ == '__main__':
    print("🔄 Running booking expiration service...")
    expired_count = expire_past_bookings()
    
    # Show bookings expiring in next 24 hours
    expiring = get_expiring_soon(24)
    if expiring:
        print(f"\n⏰ {len(expiring)} booking(s) will expire in next 24 hours:")
        for booking in expiring:
            print(f"   - {booking.resource.name} (ends at {booking.end_time.strftime('%Y-%m-%d %I:%M %p')})")
