"""Test the dashboard endpoint directly."""
import sys
sys.dont_write_bytecode = True

from app import app
from src.models import User
from flask import url_for

print("\n=== Testing Dashboard Access ===\n")

with app.app_context():
    # Try to access the endpoint with a test client
    with app.test_client() as client:
        # Check if we can build the URL within request context
        with client.application.test_request_context():
            try:
                url = url_for('bookings.dashboard')
                print(f"✓ URL for bookings.dashboard: {url}")
            except Exception as e:
                print(f"✗ Error building URL: {e}")
                sys.exit(1)
        print("\nTest 1: Access without login (should redirect to login)")
        response = client.get('/bookings/dashboard', follow_redirects=False)
        print(f"  Status: {response.status_code}")
        print(f"  Location: {response.headers.get('Location', 'N/A')}")
        
        # Try to login as admin
        print("\nTest 2: Login as admin user")
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"  Found admin: {admin.username} (ID: {admin.id})")
            
            # Actually login via the login endpoint
            print(f"  Attempting login with username: {admin.username}")
            login_response = client.post('/auth/login', data={
                'username': admin.username,
                'password': 'admin123'  # Default admin password
            }, follow_redirects=False)
            print(f"  Login status: {login_response.status_code}")
            
            print("\nTest 3: Access dashboard after login")
            response = client.get('/bookings/dashboard', follow_redirects=False)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ Dashboard loaded successfully!")
                print(f"  Response length: {len(response.data)} bytes")
            elif response.status_code == 302:
                print(f"  Redirect to: {response.headers.get('Location', 'N/A')}")
            else:
                print(f"  Response: {response.data.decode('utf-8')[:500]}")
        else:
            print("  No admin user found in database")

print("\n" + "="*50)
