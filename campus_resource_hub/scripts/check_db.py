"""
Check database status and display basic information.
Useful for debugging and verifying database setup.

Usage:
    python scripts/check_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from src.models import User, Resource, Booking, Message, Review

def check_database():
    """Display database statistics."""
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("DATABASE STATUS")
        print("=" * 60)
        
        models = [
            ('Users', User),
            ('Resources', Resource),
            ('Bookings', Booking),
            ('Messages', Message),
            ('Reviews', Review)
        ]
        
        for name, model in models:
            count = model.query.count()
            status = "✓" if count > 0 else "○"
            print(f"{status} {name:15} {count:5} records")
        
        print("=" * 60)
        
        # Show sample users if any exist
        users = User.query.limit(3).all()
        if users:
            print("\nSample Users:")
            for user in users:
                print(f"  • {user.username:15} ({user.email})")

if __name__ == '__main__':
    check_database()
