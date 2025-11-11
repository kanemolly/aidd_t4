"""
Direct password reset script for mollyk user
Run this standalone (NOT while server is running)
"""
import sys
import os

# Add the campus_resource_hub directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from src.models.models import User

with app.app_context():
    # Find the user
    user = User.query.filter_by(username='mollyk').first()
    
    if not user:
        print("ERROR: User 'mollyk' not found!")
        sys.exit(1)
    
    print(f"Found user: {user.username} (ID: {user.id})")
    print(f"Current password_hash: {user.password_hash[:50]}...")
    
    # Set new password
    new_password = "password123"
    user.set_password(new_password)
    user.is_active = True
    
    # Commit changes
    db.session.commit()
    
    print(f"\n✓ Password reset successfully!")
    print(f"Username: {user.username}")
    print(f"New password: {new_password}")
    print(f"Is active: {user.is_active}")
    print(f"New password_hash: {user.password_hash[:50]}...")
    print("\nYou can now login with:")
    print(f"  Username: mollyk")
    print(f"  Password: password123")
