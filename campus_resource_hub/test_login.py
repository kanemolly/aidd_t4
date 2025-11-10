"""Test login functionality."""
import sys
sys.dont_write_bytecode = True

from app import app
from src.models import User
from src.extensions import db

print("\n=== Testing Login Functionality ===\n")

with app.app_context():
    # Check if admin user exists
    print("1. Checking for admin user...")
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("   ✗ No admin user found!")
        print("\n   Available users:")
        users = User.query.all()
        for user in users:
            print(f"      - {user.username} (role: {user.role})")
    else:
        print(f"   ✓ Found admin user: {admin.username}")
        print(f"     Email: {admin.email}")
        print(f"     Role: {admin.role}")
        print(f"     Active: {admin.is_active}")
        
        # Test password checking
        print("\n2. Testing password verification...")
        test_passwords = ['admin123', 'Admin123', 'password', 'admin']
        
        for pwd in test_passwords:
            try:
                result = admin.check_password(pwd)
                print(f"   Password '{pwd}': {'✓ CORRECT' if result else '✗ incorrect'}")
            except Exception as e:
                print(f"   Password '{pwd}': ERROR - {e}")
        
        # Check password hash
        print(f"\n3. Password hash exists: {bool(admin.password_hash)}")
        print(f"   Hash length: {len(admin.password_hash) if admin.password_hash else 0}")
        
    # Test database connection
    print("\n4. Testing database connection...")
    try:
        from sqlalchemy import text
        result = db.session.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        print(f"   ✓ Database accessible, {result[0]} users found")
    except Exception as e:
        print(f"   ✗ Database error: {e}")

print("\n" + "="*50 + "\n")
