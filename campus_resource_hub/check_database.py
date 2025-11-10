"""Check database content."""
import sys
sys.dont_write_bytecode = True

from app import app
from src.models import User, Resource, Booking

print("\n=== Database Content Check ===\n")

with app.app_context():
    # Count records
    user_count = User.query.count()
    resource_count = Resource.query.count()
    booking_count = Booking.query.count()
    
    print(f"Users: {user_count}")
    print(f"Resources: {resource_count}")
    print(f"Bookings: {booking_count}")
    
    print("\n--- Published Resources ---")
    published = Resource.query.filter_by(status='published').all()
    if published:
        for r in published[:5]:  # Show first 5
            print(f"  • {r.name} ({r.resource_type}) - {r.location}")
    else:
        print("  (No published resources found)")
    
    print("\n--- All Resources ---")
    all_resources = Resource.query.all()
    if all_resources:
        for r in all_resources[:10]:  # Show first 10
            print(f"  • {r.name} - Status: {r.status}")
    else:
        print("  (No resources in database)")

print("\n" + "="*50 + "\n")
