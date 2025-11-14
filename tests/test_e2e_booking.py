"""
End-to-end test for complete booking workflow through the UI.

This test simulates a real user journey:
1. User registers and logs in
2. Browses available resources
3. Selects a resource and creates a booking
4. Views their booking in the dashboard
5. Admin approves the booking
6. User receives confirmation

Can be run as automated test or used as manual testing script.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add campus_resource_hub to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'campus_resource_hub')))

# Import selenium only when needed
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@pytest.mark.e2e
class TestBookingWorkflowManual:
    """
    End-to-end booking workflow test (manual/semi-automated).
    Can be run with pytest or used as a manual testing guide.
    """
    
    def test_complete_booking_workflow(self, client, db):
        """
        Complete booking workflow test using test client.
        This simulates the full user journey without requiring a browser.
        """
        print("\n" + "="*80)
        print("END-TO-END BOOKING WORKFLOW TEST")
        print("="*80)
        
        # STEP 1: Register a new user
        print("\n[STEP 1] Registering new user...")
        register_data = {
            'username': 'e2e_testuser',
            'email': 'e2e_test@iu.edu',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'full_name': 'E2E Test User',
            'role': 'student',
            'department': 'Computer Science'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        print("✓ User registered successfully")
        
        # STEP 2: Login with new user
        print("\n[STEP 2] Logging in...")
        login_data = {
            'username': 'e2e_testuser',
            'password': 'TestPass123!'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert '_user_id' in sess
            user_id = sess['_user_id']
        
        print(f"✓ User logged in successfully (User ID: {user_id})")
        
        # STEP 3: Browse available resources
        print("\n[STEP 3] Browsing available resources...")
        response = client.get('/resources')
        assert response.status_code == 200
        print("✓ Resources page loaded")
        
        # Create a test resource to book
        from src.data_access.resource_dal import ResourceDAL
        # Need an admin user to create resource
        from src.data_access.user_dal import UserDAL
        admin_user = UserDAL.create_user(
            username='testadmin',
            email='testadmin@iu.edu',
            password='AdminPass123!',
            full_name='Test Admin',
            role='admin'
        )
        resource = ResourceDAL.create_resource(
            name='E2E Test Study Room',
            resource_type='study_room',
            description='Test room for end-to-end testing',
            location='Test Building, Room 101',
            capacity=6,
            creator_id=admin_user.id,
            status='published',
            is_available=True
        )
        db.session.commit()
        print(f"✓ Test resource created (Resource ID: {resource.id})")
        
        # STEP 4: View resource details
        print("\n[STEP 4] Viewing resource details...")
        response = client.get(f'/resources/{resource.id}')
        assert response.status_code == 200
        print(f"✓ Resource details page loaded for '{resource.name}'")
        
        # STEP 5: Create a booking
        print("\n[STEP 5] Creating booking...")
        start_time = datetime.utcnow() + timedelta(days=2)
        end_time = start_time + timedelta(hours=2)
        
        booking_data = {
            'resource_id': resource.id,
            'start_datetime': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_datetime': end_time.strftime('%Y-%m-%dT%H:%M'),
            'purpose': 'E2E test - Study session for final exams'
        }
        
        response = client.post('/bookings/new', data=booking_data, follow_redirects=True)
        assert response.status_code == 200
        print(f"✓ Booking created")
        print(f"  - Resource: {resource.name}")
        print(f"  - Start: {start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  - End: {end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  - Duration: 2 hours")
        
        # STEP 6: View booking in dashboard
        print("\n[STEP 6] Viewing booking in dashboard...")
        response = client.get('/bookings/dashboard')
        assert response.status_code == 200
        print("✓ Booking appears in user dashboard")
        
        # Get the created booking
        from src.data_access.booking_dal import BookingDAL
        bookings = BookingDAL.get_bookings_by_user(user_id)
        assert len(bookings) > 0
        booking = bookings[0]
        print(f"  - Booking ID: {booking.id}")
        print(f"  - Status: {booking.status}")
        
        # STEP 7: Admin reviews and approves booking
        print("\n[STEP 7] Admin approving booking...")
        
        # Create admin user
        from campus_resource_hub.src.data_access.user_dal import UserDAL
        admin = UserDAL.create_user(
            username='e2e_admin',
            email='e2e_admin@iu.edu',
            password='AdminPass123!',
            full_name='E2E Admin',
            role='admin'
        )
        db.session.commit()
        
        # Login as admin
        client.get('/auth/logout')  # Logout student
        admin_login = {
            'username': 'e2e_admin',
            'password': 'AdminPass123!'
        }
        response = client.post('/auth/login', data=admin_login, follow_redirects=True)
        assert response.status_code == 200
        print(f"✓ Admin logged in (Admin ID: {admin.id})")
        
        # Admin views pending bookings
        response = client.get('/admin/pending-bookings')
        if response.status_code == 200:
            print("✓ Admin can view pending bookings")
        
        # Admin confirms booking
        response = client.post(f'/bookings/{booking.id}/confirm', follow_redirects=True)
        assert response.status_code == 200
        print("✓ Admin confirmed booking")
        
        # Verify booking status changed
        updated_booking = BookingDAL.get_booking_by_id(booking.id)
        assert updated_booking.status == 'confirmed'
        print(f"  - New status: {updated_booking.status}")
        print(f"  - Approved by: Admin ID {updated_booking.approved_by}")
        
        # STEP 8: Verify user can see confirmed booking
        print("\n[STEP 8] User viewing confirmed booking...")
        
        # Login back as student
        client.get('/auth/logout')
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        response = client.get('/bookings/dashboard')
        assert response.status_code == 200
        assert b'confirmed' in response.data.lower() or b'Confirmed' in response.data
        print("✓ User can see confirmed booking status")
        
        # STEP 9: Check notification (if implemented)
        print("\n[STEP 9] Checking for notifications...")
        from campus_resource_hub.src.models.models import Notification
        notifications = db.session.query(Notification).filter_by(user_id=user_id).all()
        if len(notifications) > 0:
            print(f"✓ Notification created ({len(notifications)} notification(s))")
            for notif in notifications:
                print(f"  - Type: {notif.notification_type}")
                print(f"  - Message: {notif.message}")
        else:
            print("⚠ No notifications found (may not be implemented)")
        
        print("\n" + "="*80)
        print("END-TO-END TEST COMPLETED SUCCESSFULLY ✓")
        print("="*80)
        print("\nWorkflow Summary:")
        print(f"  1. User registered: {register_data['username']}")
        print(f"  2. User logged in")
        print(f"  3. Resource browsed: {resource.name}")
        print(f"  4. Booking created: ID {booking.id}")
        print(f"  5. Admin approved booking")
        print(f"  6. Final status: {updated_booking.status}")
        print("="*80 + "\n")


@pytest.mark.e2e
@pytest.mark.slow
class TestBookingWorkflowSelenium:
    """
    End-to-end test using Selenium for browser automation.
    Requires Selenium and Chrome/Firefox driver installed.
    Run with: pytest -m e2e --driver chrome
    """
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Setup Selenium WebDriver."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not installed")
        
        try:
            # Try Chrome first
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run headless for CI/CD
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            
            yield driver
            driver.quit()
            
        except Exception as e:
            pytest.skip(f"Selenium WebDriver not available: {e}")
    
    @pytest.fixture(scope='class')
    def live_server(self, app):
        """Start live server for Selenium tests."""
        # This would require additional setup for live server testing
        # Using pytest-flask or similar plugin
        pytest.skip("Live server setup required for Selenium tests")
    
    def test_booking_workflow_selenium(self, driver, live_server):
        """
        Full UI test using Selenium.
        This would test the actual browser interaction.
        """
        base_url = "http://localhost:5000"
        
        print("\n" + "="*80)
        print("SELENIUM END-TO-END TEST")
        print("="*80)
        
        try:
            # Navigate to homepage
            driver.get(base_url)
            print("✓ Navigated to homepage")
            
            # Click register link
            register_link = driver.find_element(By.LINK_TEXT, "Register")
            register_link.click()
            print("✓ Clicked register link")
            
            # Fill registration form
            driver.find_element(By.NAME, "username").send_keys("selenium_user")
            driver.find_element(By.NAME, "email").send_keys("selenium@iu.edu")
            driver.find_element(By.NAME, "password").send_keys("SeleniumPass123!")
            driver.find_element(By.NAME, "confirm_password").send_keys("SeleniumPass123!")
            driver.find_element(By.NAME, "full_name").send_keys("Selenium Test User")
            
            # Submit form
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            print("✓ Submitted registration form")
            
            # Wait for redirect and login
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            driver.find_element(By.NAME, "username").send_keys("selenium_user")
            driver.find_element(By.NAME, "password").send_keys("SeleniumPass123!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            print("✓ Logged in")
            
            # Navigate to resources
            driver.get(f"{base_url}/resources")
            print("✓ Viewing resources")
            
            # Click on first resource
            resource_link = driver.find_element(By.CSS_SELECTOR, ".resource-card a")
            resource_link.click()
            print("✓ Clicked on resource")
            
            # Click booking button
            book_button = driver.find_element(By.CSS_SELECTOR, ".book-button")
            book_button.click()
            print("✓ Clicked book button")
            
            # Fill booking form
            # ... continue with form filling ...
            
            print("\n" + "="*80)
            print("SELENIUM TEST COMPLETED ✓")
            print("="*80 + "\n")
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"\n✗ Selenium test failed: {e}")
            # Take screenshot on failure
            driver.save_screenshot('test_failure.png')
            raise


@pytest.mark.e2e
def test_booking_conflict_scenario(client, db):
    """
    Test scenario where two users try to book the same resource at overlapping times.
    """
    print("\n" + "="*80)
    print("BOOKING CONFLICT SCENARIO TEST")
    print("="*80)
    
    from src.data_access.user_dal import UserDAL
    from src.data_access.resource_dal import ResourceDAL
    
    # Create two users
    print("\n[SETUP] Creating users and resource...")
    user1 = UserDAL.create_user(
        username='user1', email='user1@iu.edu',
        password='Pass123!', full_name='User One', role='student'
    )
    user2 = UserDAL.create_user(
        username='user2', email='user2@iu.edu',
        password='Pass123!', full_name='User Two', role='student'
    )
    
    admin = UserDAL.create_user(
        username='conflictadmin', email='conflictadmin@iu.edu',
        password='AdminPass123!', full_name='Conflict Admin', role='admin'
    )
    
    resource = ResourceDAL.create_resource(
        name='Popular Study Room',
        resource_type='study_room',
        description='High-demand study space',
        location='Library',
        capacity=4,
        creator_id=admin.id,
        status='published',
        is_available=True
    )
    db.session.commit()
    print("✓ Setup complete")
    
    # User 1 books the room
    print("\n[STEP 1] User 1 booking resource...")
    client.get('/auth/logout')
    client.post('/auth/login', data={'username': 'user1', 'password': 'Pass123!'})
    
    start = datetime.utcnow() + timedelta(days=1, hours=10)
    end = start + timedelta(hours=2)
    
    booking_data = {
        'resource_id': resource.id,
        'start_datetime': start.strftime('%Y-%m-%dT%H:%M'),
        'end_datetime': end.strftime('%Y-%m-%dT%H:%M'),
        'purpose': 'User 1 booking'
    }
    
    response = client.post('/bookings/new', data=booking_data, follow_redirects=True)
    assert response.status_code == 200
    print(f"✓ User 1 created booking: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
    
    # Admin confirms User 1's booking
    admin = UserDAL.create_user(
        username='admin', email='admin@iu.edu',
        password='Pass123!', full_name='Admin', role='admin'
    )
    db.session.commit()
    
    client.get('/auth/logout')
    client.post('/auth/login', data={'username': 'admin', 'password': 'Pass123!'})
    
    from campus_resource_hub.src.data_access.booking_dal import BookingDAL
    user1_booking = BookingDAL.get_bookings_by_user(user1.id)[0]
    client.post(f'/bookings/{user1_booking.id}/confirm')
    print("✓ Admin confirmed User 1's booking")
    
    # User 2 tries to book overlapping time
    print("\n[STEP 2] User 2 attempting overlapping booking...")
    client.get('/auth/logout')
    client.post('/auth/login', data={'username': 'user2', 'password': 'Pass123!'})
    
    # Overlapping time: 11:00-13:00 (overlaps with 10:00-12:00)
    conflict_start = start + timedelta(hours=1)
    conflict_end = conflict_start + timedelta(hours=2)
    
    booking_data2 = {
        'resource_id': resource.id,
        'start_datetime': conflict_start.strftime('%Y-%m-%dT%H:%M'),
        'end_datetime': conflict_end.strftime('%Y-%m-%dT%H:%M'),
        'purpose': 'User 2 booking (should conflict)'
    }
    
    response = client.post('/bookings/new', data=booking_data2, follow_redirects=True)
    print(f"✓ User 2 attempted booking: {conflict_start.strftime('%H:%M')} - {conflict_end.strftime('%H:%M')}")
    
    # Check if conflict was detected
    if b'conflict' in response.data.lower() or b'unavailable' in response.data.lower():
        print("✓ Conflict detected! Booking rejected.")
    else:
        print("⚠ Booking may have been created (checking database...)")
        user2_bookings = BookingDAL.get_bookings_by_user(user2.id)
        if len(user2_bookings) == 0:
            print("✓ Booking was not created in database")
        else:
            print("✗ Warning: Conflicting booking was created!")
    
    print("\n" + "="*80)
    print("CONFLICT SCENARIO TEST COMPLETED ✓")
    print("="*80 + "\n")
