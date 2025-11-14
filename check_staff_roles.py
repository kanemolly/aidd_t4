"""
Quick script to check and update staff user roles.
"""
import sys
import os

# Add the campus_resource_hub directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'campus_resource_hub'))

from app import create_app
from src.extensions import db
from src.models import User

app = create_app()

with app.app_context():
    print("\n=== USER ROLES CHECK ===\n")
    
    # Get all users
    users = User.query.all()
    
    print(f"Total users: {len(users)}\n")
    
    for user in users:
        print(f"Username: {user.username}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  is_admin(): {user.is_admin()}")
        print(f"  is_staff(): {user.is_staff()}")
        print(f"  is_student(): {user.is_student()}")
        print()
    
    # Ask if user wants to update a staff member's role
    print("\n=== UPDATE STAFF ROLE ===")
    username = input("Enter username to update to 'staff' role (or press Enter to skip): ").strip()
    
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.role = 'staff'
            db.session.commit()
            print(f"✓ Updated {username} to staff role!")
            print(f"  New role: {user.role}")
            print(f"  is_staff(): {user.is_staff()}")
        else:
            print(f"✗ User '{username}' not found!")
