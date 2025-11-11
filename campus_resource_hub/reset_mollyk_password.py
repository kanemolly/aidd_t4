"""
Reset password for mollyk user account.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from src.models import User
from src.extensions import db, bcrypt

def reset_mollyk_password():
    """Reset password for mollyk user."""
    app = create_app('development')
    
    with app.app_context():
        # Find mollyk user
        user = User.query.filter_by(username='mollyk').first()
        
        if not user:
            print("❌ User 'mollyk' not found!")
            return
        
        print(f"Found user: {user.username} ({user.full_name})")
        print(f"Current role: {user.role}")
        print(f"Email: {user.email}")
        
        # Set new password
        new_password = "password123"
        user.set_password(new_password)
        
        # Ensure user is active
        user.is_active = True
        
        db.session.commit()
        
        print(f"\n✅ Password successfully reset for user 'mollyk'")
        print(f"New password: {new_password}")
        print(f"\nYou can now login with:")
        print(f"  Username: mollyk")
        print(f"  Password: {new_password}")

if __name__ == '__main__':
    reset_mollyk_password()
