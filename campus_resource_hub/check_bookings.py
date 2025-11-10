"""Check booking details."""
import sys
sys.dont_write_bytecode = True

from app import app
from src.models import Booking
from src.data_access.booking_dal import BookingDAL

print("\n=== Checking Bookings ===\n")

with app.app_context():
    # Get all bookings
    all_bookings = BookingDAL.get_all_bookings()
    
    print(f"Total bookings: {len(all_bookings)}")
    
    for booking in all_bookings:
        print(f"\nBooking ID: {booking.id}")
        print(f"  User: {booking.user.full_name if booking.user else 'N/A'}")
        print(f"  Resource: {booking.resource.name if booking.resource else 'N/A'}")
        print(f"  Status: {booking.status}")
        print(f"  Has start_time attribute: {hasattr(booking, 'start_time')}")
        print(f"  Has start_date attribute: {hasattr(booking, 'start_date')}")
        
        if hasattr(booking, 'start_time'):
            print(f"  start_time value: {booking.start_time}")
            print(f"  start_time type: {type(booking.start_time)}")
        
        if hasattr(booking, 'end_time'):
            print(f"  end_time value: {booking.end_time}")
    
    # Check pending bookings specifically
    print("\n--- Pending Bookings ---")
    pending = BookingDAL.get_bookings_by_status('pending', limit=20)
    print(f"Pending count: {len(pending)}")
    
    for p in pending:
        print(f"  Booking {p.id}: start_time={p.start_time}, end_time={p.end_time}")

print("\n" + "="*50 + "\n")
