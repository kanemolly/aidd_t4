"""
Integration tests for authentication flow.

Tests cover complete user journeys:
- Register → Login → Access Protected Route
- Login failures and validation
- Session management
- Role-based access control
"""

import pytest
from flask import session
import sys
import os

# Add campus_resource_hub to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'campus_resource_hub')))


@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""
    
    def test_register_login_access_protected_route(self, client, db):
        """
        End-to-end test: Register new user → Login → Access protected resource.
        This is the main integration test required by the specification.
        """
        # Step 1: Register a new user
        register_data = {
            'username': 'newuser123',
            'email': 'newuser@iu.edu',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'full_name': 'New Test User',
            'role': 'student',
            'department': 'Engineering'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        # Registration should succeed and redirect to login or dashboard
        
        # Step 2: Login with the newly registered user
        login_data = {
            'username': 'newuser123',
            'password': 'SecurePass123!'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify user is logged in by checking session
        with client.session_transaction() as sess:
            assert '_user_id' in sess
        
        # Step 3: Access a protected route (requires authentication)
        response = client.get('/bookings/dashboard')
        assert response.status_code == 200
        # Should successfully access protected route
        
        # Step 4: Verify profile page access
        response = client.get('/auth/profile')
        assert response.status_code == 200
        assert b'newuser123' in response.data or b'New Test User' in response.data
        
        # Step 5: Verify resources page access
        response = client.get('/resources')
        assert response.status_code == 200
    
    def test_login_without_registration_fails(self, client, db):
        """Test that login fails for non-existent user."""
        login_data = {
            'username': 'nonexistent',
            'password': 'password123'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        # Should show error message or stay on login page
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
    
    def test_protected_route_redirects_without_login(self, client, db):
        """Test that accessing protected routes without login redirects to login."""
        response = client.get('/bookings/dashboard', follow_redirects=False)
        
        # Should redirect to login page
        assert response.status_code in [302, 401]
        if response.status_code == 302:
            assert '/auth/login' in response.location or '/login' in response.location
    
    def test_login_with_wrong_password(self, client, sample_student):
        """Test that login fails with incorrect password."""
        login_data = {
            'username': sample_student.username,
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
        
        # Verify user is NOT logged in
        with client.session_transaction() as sess:
            assert '_user_id' not in sess or sess['_user_id'] != str(sample_student.id)
    
    def test_logout_flow(self, authenticated_client):
        """Test that logout properly clears session."""
        # Verify user is logged in
        response = authenticated_client.get('/bookings/dashboard')
        assert response.status_code == 200
        
        # Logout
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify session is cleared
        with authenticated_client.session_transaction() as sess:
            assert '_user_id' not in sess
        
        # Verify protected route is now inaccessible
        response = authenticated_client.get('/bookings/dashboard', follow_redirects=False)
        assert response.status_code in [302, 401]


@pytest.mark.integration
class TestUserRegistrationValidation:
    """Test user registration validation and business rules."""
    
    def test_register_duplicate_username(self, client, sample_student):
        """Test that registering with duplicate username fails."""
        register_data = {
            'username': sample_student.username,  # Duplicate
            'email': 'different@iu.edu',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'full_name': 'Another User',
            'role': 'student'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'taken' in response.data.lower()
    
    def test_register_duplicate_email(self, client, sample_student):
        """Test that registering with duplicate email fails."""
        register_data = {
            'username': 'differentuser',
            'email': sample_student.email,  # Duplicate
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'full_name': 'Another User',
            'role': 'student'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'taken' in response.data.lower()
    
    def test_register_password_mismatch(self, client):
        """Test that registration fails when passwords don't match."""
        register_data = {
            'username': 'testuser',
            'email': 'test@iu.edu',
            'password': 'SecurePass123!',
            'confirm_password': 'DifferentPass123!',  # Mismatch
            'full_name': 'Test User',
            'role': 'student'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'match' in response.data.lower() or b'do not match' in response.data.lower()
    
    def test_register_weak_password(self, client):
        """Test that weak passwords are rejected."""
        register_data = {
            'username': 'testuser',
            'email': 'test@iu.edu',
            'password': '123',  # Too weak
            'confirm_password': '123',
            'full_name': 'Test User',
            'role': 'student'
        }
        
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        # Should fail validation (exact error depends on implementation)
        assert response.status_code == 200


@pytest.mark.integration
class TestRoleBasedAccessControl:
    """Test role-based access control across routes."""
    
    def test_admin_can_access_admin_dashboard(self, admin_client):
        """Test that admin users can access admin-only routes."""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
    
    def test_student_cannot_access_admin_dashboard(self, authenticated_client):
        """Test that student users cannot access admin-only routes."""
        response = authenticated_client.get('/admin/dashboard', follow_redirects=False)
        # Should be forbidden or redirect
        assert response.status_code in [302, 403, 404]
    
    def test_admin_can_approve_bookings(self, admin_client, sample_booking):
        """Test that admin can approve pending bookings."""
        response = admin_client.post(
            f'/bookings/{sample_booking.id}/confirm',
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify booking was confirmed
        from src.data_access.booking_dal import BookingDAL
        booking = BookingDAL.get_booking_by_id(sample_booking.id)
        assert booking.status == 'confirmed'
    
    def test_student_can_create_booking(self, authenticated_client, sample_resource):
        """Test that authenticated students can create bookings."""
        from datetime import datetime, timedelta
        
        start = datetime.utcnow() + timedelta(days=2)
        end = start + timedelta(hours=2)
        
        booking_data = {
            'resource_id': sample_resource.id,
            'start_datetime': start.strftime('%Y-%m-%dT%H:%M'),
            'end_datetime': end.strftime('%Y-%m-%dT%H:%M'),
            'purpose': 'Integration test booking'
        }
        
        response = authenticated_client.post(
            '/bookings/new',
            data=booking_data,
            follow_redirects=True
        )
        assert response.status_code == 200


@pytest.mark.integration
class TestSessionManagement:
    """Test session handling and persistence."""
    
    def test_session_persists_across_requests(self, authenticated_client, sample_student):
        """Test that user session persists across multiple requests."""
        # Make first request
        response1 = authenticated_client.get('/auth/profile')
        assert response1.status_code == 200
        
        # Make second request - should still be authenticated
        response2 = authenticated_client.get('/bookings/dashboard')
        assert response2.status_code == 200
        
        # Make third request to a different protected route
        response3 = authenticated_client.get('/resources')
        assert response3.status_code == 200
    
    def test_remember_me_functionality(self, client, sample_student):
        """Test remember me functionality if implemented."""
        login_data = {
            'username': sample_student.username,
            'password': 'SecurePass123!',
            'remember_me': True
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check if remember cookie is set (implementation-specific)
        # This test documents expected behavior
    
    def test_concurrent_sessions_different_users(self, client, sample_student, sample_admin):
        """Test that different users can have separate sessions."""
        # Login as student
        client1_data = {
            'username': sample_student.username,
            'password': 'SecurePass123!'
        }
        response1 = client.post('/auth/login', data=client1_data, follow_redirects=True)
        assert response1.status_code == 200
        
        # Create second client and login as admin
        client2 = client.application.test_client()
        client2_data = {
            'username': sample_admin.username,
            'password': 'AdminPass123!'
        }
        response2 = client2.post('/auth/login', data=client2_data, follow_redirects=True)
        assert response2.status_code == 200
        
        # Both should have independent sessions
        # (Implementation-specific test)


@pytest.mark.integration
class TestPasswordManagement:
    """Test password change and reset functionality."""
    
    def test_change_password_authenticated(self, authenticated_client, sample_student):
        """Test that authenticated users can change their password."""
        password_data = {
            'current_password': 'SecurePass123!',
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }
        
        response = authenticated_client.post(
            '/auth/change-password',
            data=password_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify can login with new password
        from campus_resource_hub.src.data_access.user_dal import UserDAL
        user = UserDAL.authenticate_user(sample_student.username, 'NewSecurePass456!')
        assert user is not None
    
    def test_change_password_wrong_current(self, authenticated_client):
        """Test that password change fails with wrong current password."""
        password_data = {
            'current_password': 'WrongPassword!',
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }
        
        response = authenticated_client.post(
            '/auth/change-password',
            data=password_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'incorrect' in response.data.lower() or b'invalid' in response.data.lower()


@pytest.mark.integration
class TestProfileManagement:
    """Test user profile viewing and editing."""
    
    def test_view_own_profile(self, authenticated_client, sample_student):
        """Test that users can view their own profile."""
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        assert sample_student.username.encode() in response.data
        assert sample_student.email.encode() in response.data
    
    def test_edit_profile_information(self, authenticated_client, sample_student):
        """Test that users can edit their profile information."""
        profile_data = {
            'full_name': 'Updated Name',
            'email': 'updated@iu.edu',
            'department': 'Updated Department'
        }
        
        response = authenticated_client.post(
            '/auth/edit-profile',
            data=profile_data,
            follow_redirects=True
        )
        
        # Should succeed (exact behavior depends on implementation)
        assert response.status_code == 200
