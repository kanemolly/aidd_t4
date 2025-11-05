"""
Initialize database with sample data.
Run this script to set up the database schema and load initial data.

Usage:
    python scripts/init_db.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from src.models import User, Resource, Booking, Message, Review
from datetime import datetime, timedelta

def init_database():
    """Initialize database with schema."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database schema created")

def load_sample_data():
    """Load sample data into database."""
    app = create_app()
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("✓ Database already has data. Skipping sample load.")
            return

        # Create sample users
        admin = User(
            username='admin',
            email='admin@campus.edu',
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')

        staff = User(
            username='staff',
            email='staff@campus.edu',
            full_name='Staff Member',
            role='staff',
            is_active=True
        )
        staff.set_password('staff123')

        student = User(
            username='student',
            email='student@campus.edu',
            full_name='Student User',
            role='student',
            is_active=True
        )
        student.set_password('student123')

        db.session.add_all([admin, staff, student])
        db.session.commit()
        print(f"✓ Created {User.query.count()} sample users")

        # Create sample resources
        resource1 = Resource(
            name='Conference Room A',
            description='Large conference room with projector and whiteboard',
            location='Building A, Floor 2, Room 201',
            resource_type='room',
            capacity=20,
            is_available=True,
            status='published',
            creator_id=staff.id
        )

        resource2 = Resource(
            name='Projector #5',
            description='High-quality projector for presentations',
            location='Equipment Lab, Building B',
            resource_type='equipment',
            capacity=1,
            is_available=True,
            status='published',
            creator_id=staff.id
        )

        db.session.add_all([resource1, resource2])
        db.session.commit()
        print(f"✓ Created {Resource.query.count()} sample resources")

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    load_sample_data()
    print("\n✅ Database initialization complete!")
