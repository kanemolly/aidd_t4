"""Reset admin password."""
import sys
sys.dont_write_bytecode = True

from app import app
from src.models import User
from src.extensions import db

print("\n=== Resetting Admin Password ===\n")

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("✗ Admin user not found!")
        sys.exit(1)
    
    print(f"Found admin user: {admin.username}")
    print(f"Old password hash length: {len(admin.password_hash)}")
    
    # Set new password
    new_password = 'admin123'
    admin.set_password(new_password)
    
    print(f"New password hash length: {len(admin.password_hash)}")
    print(f"New password: {new_password}")
    
    # Save to database
    try:
        db.session.commit()
        print("\n✓ Password reset successfully!")
        
        # Test the new password
        print("\nTesting new password...")
        if admin.check_password(new_password):
            print("✓ Password verification successful!")
        else:
            print("✗ Password verification failed!")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Error saving password: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*50 + "\n")
