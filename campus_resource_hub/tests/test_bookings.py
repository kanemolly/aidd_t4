"""
Unit tests for Booking System
Tests for POST /bookings endpoint with conflict detection and status transitions.
"""

import unittest
from datetime import datetime, timedelta
from app import create_app
from src.extensions import db
from src.models import User, Resource, Booking
from src.data_access.booking_dal import BookingDAL


class BookingTestCase(unittest.TestCase):
    """Test cases for booking system."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
            
            # Store IDs (not objects) for use in tests
            self.admin_id = self.admin.id
            self.student_id = self.student.id
            self.student2_id = self.student2.id
            self.resource_id = self.resource.id
            self.resource2_id = self.resource2.id
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_data(self):
        """Create test users and resources."""
        # Create admin user
        admin = User(
            username='admin_test',
            email='admin@test.edu',
            full_name='Admin User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular student user
        student = User(
            username='student_test',
            email='student@test.edu',
            full_name='Student User',
            role='student'
        )
        student.set_password('student123')
        db.session.add(student)
        
        # Create another student
        student2 = User(
            username='student2_test',
            email='student2@test.edu',
            full_name='Student User 2',
            role='student'
        )
        student2.set_password('student234')
        db.session.add(student2)
        
        db.session.commit()
        
        # Store object references for use in _create_test_data
        self.admin = admin
        self.student = student
        self.student2 = student2
        
        # Create test resource
        resource = Resource(
            name='Conference Room A',
            description='Large conference room',
            resource_type='room',
            location='Building A, 2nd Floor',
            capacity=20,
            creator_id=admin.id,
            status='published'
        )
        db.session.add(resource)
        
        # Create another resource
        resource2 = Resource(
            name='Projector B',
            description='Portable projector',
            resource_type='equipment',
            location='Building B',
            capacity=1,
            creator_id=admin.id,
            status='published'
        )
        db.session.add(resource2)
        db.session.commit()
        
        self.resource = resource
        self.resource2 = resource2
    
    def _login(self, username, password):
        """Helper to login a user."""
        response = self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=False)
        # The login should either succeed or redirect
        return response
    
"""
Unit tests for Booking System
Tests for POST /bookings endpoint with conflict detection and status transitions.
"""

import unittest
from datetime import datetime, timedelta
from app import create_app
from src.extensions import db
from src.models import User, Resource, Booking
from src.data_access.booking_dal import BookingDAL
from src.controllers.bookings import check_conflict


class BookingConflictDetectionTestCase(unittest.TestCase):
    """Test cases for booking conflict detection logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_data(self):
        """Create test data."""
        # Create user
        user = User(
            username='test_user',
            email='test@test.edu',
            full_name='Test User',
            role='student'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.flush()  # Flush to get the ID without committing
        
        # Create resource with user ID
        resource = Resource(
            name='Test Room',
            description='Test room for bookings',
            resource_type='room',
            location='Building A',
            capacity=20,
            creator_id=user.id,  # Now ID is available
            status='published'
        )
        db.session.add(resource)
        db.session.commit()
        
        self.user_id = user.id
        self.resource_id = resource.id
    
    def test_check_conflict_with_overlapping_booking(self):
        """Test that overlapping bookings are detected."""
        with self.app.app_context():
            # Create first confirmed booking: 2:00 PM to 4:00 PM
            start1 = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            end1 = start1 + timedelta(hours=2)
            
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='confirmed'
            )
            
            # Try to check conflict for overlapping time: 3:00 PM to 5:00 PM
            start2 = start1 + timedelta(hours=1)
            end2 = start2 + timedelta(hours=2)
            
            has_conflict = check_conflict(self.resource_id, start2, end2)
            
            self.assertTrue(has_conflict, "Should detect overlapping bookings")
    
    def test_check_conflict_no_overlap(self):
        """Test that non-overlapping bookings don't conflict."""
        with self.app.app_context():
            # Create first booking: 2:00 PM to 4:00 PM
            start1 = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            end1 = start1 + timedelta(hours=2)
            
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='confirmed'
            )
            
            # Check conflict for later time: 5:00 PM to 7:00 PM
            start2 = start1 + timedelta(hours=3)
            end2 = start2 + timedelta(hours=2)
            
            has_conflict = check_conflict(self.resource_id, start2, end2)
            
            self.assertFalse(has_conflict, "Should not detect conflict for non-overlapping times")
    
    def test_check_conflict_adjacent_bookings_allowed(self):
        """Test that adjacent bookings don't conflict."""
        with self.app.app_context():
            # Create first booking: 2:00 PM to 4:00 PM
            start1 = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            end1 = start1 + timedelta(hours=2)
            
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='confirmed'
            )
            
            # Check conflict for booking starting exactly when first ends: 4:00 PM to 6:00 PM
            start2 = end1
            end2 = start2 + timedelta(hours=2)
            
            has_conflict = check_conflict(self.resource_id, start2, end2)
            
            self.assertFalse(has_conflict, "Adjacent bookings should not conflict")
    
    def test_check_conflict_cancelled_bookings_ignored(self):
        """Test that cancelled bookings don't block new bookings."""
        with self.app.app_context():
            # Create cancelled booking: 2:00 PM to 4:00 PM
            start1 = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            end1 = start1 + timedelta(hours=2)
            
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='cancelled'
            )
            
            # Check conflict for same time
            has_conflict = check_conflict(self.resource_id, start1, end1)
            
            self.assertFalse(has_conflict, "Cancelled bookings should not cause conflicts")
    
    def test_check_conflict_pending_bookings_ignored(self):
        """Test that pending bookings don't block new bookings (only confirmed do)."""
        with self.app.app_context():
            # Create pending booking: 2:00 PM to 4:00 PM
            start1 = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
            end1 = start1 + timedelta(hours=2)
            
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='pending'  # Not confirmed
            )
            
            # Check conflict for same time
            has_conflict = check_conflict(self.resource_id, start1, end1)
            
            self.assertFalse(has_conflict, "Pending bookings should not cause conflicts")
    
    def test_check_conflict_multiple_bookings(self):
        """Test conflict detection with multiple bookings."""
        with self.app.app_context():
            # Create two non-overlapping confirmed bookings
            base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            
            # Booking 1: 10:00 AM to 11:00 AM
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=base_time,
                end_time=base_time + timedelta(hours=1),
                status='confirmed'
            )
            
            # Booking 2: 2:00 PM to 3:00 PM
            BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=base_time + timedelta(hours=4),
                end_time=base_time + timedelta(hours=5),
                status='confirmed'
            )
            
            # Test: Should conflict with first booking
            has_conflict = check_conflict(
                self.resource_id,
                base_time + timedelta(minutes=30),
                base_time + timedelta(hours=1, minutes=30)
            )
            self.assertTrue(has_conflict)
            
            # Test: Should conflict with second booking
            has_conflict = check_conflict(
                self.resource_id,
                base_time + timedelta(hours=3, minutes=30),
                base_time + timedelta(hours=4, minutes=30)
            )
            self.assertTrue(has_conflict)
            
            # Test: Should not conflict (gap between bookings)
            has_conflict = check_conflict(
                self.resource_id,
                base_time + timedelta(hours=1, minutes=30),
                base_time + timedelta(hours=3, minutes=30)
            )
            self.assertFalse(has_conflict)


class BookingDALTestCase(unittest.TestCase):
    """Test cases for BookingDAL methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_data(self):
        """Create test data."""
        user = User(
            username='dal_test',
            email='dal@test.edu',
            full_name='DAL Test',
            role='student'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.flush()  # Flush to get the ID
        
        resource = Resource(
            name='Test Room',
            description='Test',
            resource_type='room',
            location='Test',
            capacity=10,
            creator_id=user.id,
            status='published'
        )
        db.session.add(resource)
        db.session.commit()
        
        self.user_id = user.id
        self.resource_id = resource.id
    
    def test_create_booking_success(self):
        """Test BookingDAL.create_booking() with valid data."""
        with self.app.app_context():
            start = datetime.now() + timedelta(days=1)
            end = start + timedelta(hours=1)
            
            booking = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                notes='Test booking'
            )
            
            self.assertIsNotNone(booking.id)
            self.assertEqual(booking.status, 'pending')
            self.assertEqual(booking.notes, 'Test booking')
            self.assertEqual(booking.user_id, self.user_id)
            self.assertEqual(booking.resource_id, self.resource_id)
    
    def test_create_booking_invalid_time_range(self):
        """Test that create_booking rejects invalid time range."""
        with self.app.app_context():
            start = datetime.now() + timedelta(days=1)
            end = start - timedelta(hours=1)  # End before start
            
            with self.assertRaises(ValueError):
                BookingDAL.create_booking(
                    user_id=self.user_id,
                    resource_id=self.resource_id,
                    start_time=start,
                    end_time=end
                )
    
    def test_get_confirmed_bookings_filters_correctly(self):
        """Test that get_confirmed_bookings_for_resource only returns confirmed bookings."""
        with self.app.app_context():
            base_time = datetime.now() + timedelta(days=1)
            
            # Create confirmed booking
            confirmed = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=base_time,
                end_time=base_time + timedelta(hours=2),
                status='confirmed'
            )
            
            # Create pending booking (same time)
            pending = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=base_time,
                end_time=base_time + timedelta(hours=2),
                status='pending'
            )
            
            # Create cancelled booking
            cancelled = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=base_time + timedelta(days=1),
                end_time=base_time + timedelta(days=1, hours=2),
                status='cancelled'
            )
            
            # Get confirmed bookings
            bookings = BookingDAL.get_confirmed_bookings_for_resource(
                self.resource_id,
                start_time=base_time,
                end_time=base_time + timedelta(hours=2)
            )
            
            # Should only get confirmed
            self.assertEqual(len(bookings), 1)
            self.assertEqual(bookings[0].id, confirmed.id)
    
    def test_booking_status_transitions(self):
        """Test booking status transitions."""
        with self.app.app_context():
            # Create pending booking
            start = datetime.now() + timedelta(days=1)
            booking = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=start + timedelta(hours=1),
                status='pending'
            )
            booking_id = booking.id
            
            # Confirm it
            confirmed = BookingDAL.confirm_booking(booking_id)
            self.assertEqual(confirmed.status, 'confirmed')
            
            # Cancel it
            cancelled = BookingDAL.cancel_booking(booking_id)
            self.assertEqual(cancelled.status, 'cancelled')
            
            # Complete it (note: this might not make logical sense, but tests the method)
            completed = BookingDAL.complete_booking(booking_id)
            self.assertEqual(completed.status, 'completed')
    
    def test_get_bookings_by_user(self):
        """Test retrieving bookings by user."""
        with self.app.app_context():
            # Create another user
            user2 = User(
                username='user2',
                email='user2@test.edu',
                full_name='User 2',
                role='student'
            )
            user2.set_password('password')
            db.session.add(user2)
            db.session.commit()
            
            # Create bookings for both users
            start = datetime.now() + timedelta(days=1)
            
            booking1 = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            
            booking2 = BookingDAL.create_booking(
                user_id=user2.id,
                resource_id=self.resource_id,
                start_time=start + timedelta(days=1),
                end_time=start + timedelta(days=1, hours=1)
            )
            
            # Get bookings for first user
            user1_bookings = BookingDAL.get_bookings_by_user(self.user_id)
            self.assertEqual(len(user1_bookings), 1)
            self.assertEqual(user1_bookings[0].id, booking1.id)
            
            # Get bookings for second user
            user2_bookings = BookingDAL.get_bookings_by_user(user2.id)
            self.assertEqual(len(user2_bookings), 1)
            self.assertEqual(user2_bookings[0].id, booking2.id)
    
    def test_update_booking(self):
        """Test updating booking notes."""
        with self.app.app_context():
            start = datetime.now() + timedelta(days=1)
            booking = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=start + timedelta(hours=1),
                notes='Original'
            )
            booking_id = booking.id
            
            # Update notes
            updated = BookingDAL.update_booking(booking_id, notes='Updated')
            self.assertEqual(updated.notes, 'Updated')
    
    def test_delete_booking(self):
        """Test deleting a booking."""
        with self.app.app_context():
            start = datetime.now() + timedelta(days=1)
            booking = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=start + timedelta(hours=1)
            )
            booking_id = booking.id
            
            # Delete it
            result = BookingDAL.delete_booking(booking_id)
            self.assertTrue(result)
            
            # Verify it's gone
            deleted = BookingDAL.get_booking_by_id(booking_id)
            self.assertIsNone(deleted)


if __name__ == '__main__':
    unittest.main()
    
    def test_booking_requires_login(self):
        """Test that bookings endpoint requires authentication."""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat()
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_booking_missing_required_fields(self):
        """Test booking creation with missing required fields."""
        self._login('student_test', 'student123')
        
        # Missing resource_id
        response = self.client.post('/bookings/', json={
            'start_datetime': (datetime.now() + timedelta(days=1)).isoformat(),
            'end_datetime': (datetime.now() + timedelta(days=1, hours=2)).isoformat()
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('required fields', data['error'].lower())
    
    def test_booking_resource_not_found(self):
        """Test booking with non-existent resource."""
        self._login('student_test', 'student123')
        
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        response = self.client.post('/bookings/', json={
            'resource_id': 99999,  # Non-existent
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat()
        })
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_booking_invalid_datetime_format(self):
        """Test booking with invalid datetime format."""
        self._login('student_test', 'student123')
        
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': 'not-a-date',
            'end_datetime': 'also-not-a-date'
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('datetime', data['error'].lower())
    
    def test_booking_start_after_end_time(self):
        """Test booking where start time is after end time."""
        self._login('student_test', 'student123')
        
        end = datetime.now() + timedelta(days=1)
        start = end + timedelta(hours=2)  # Start is after end
        
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat()
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('before end', data['error'].lower())
    
    def test_overlapping_bookings_detected(self):
        """Test that overlapping bookings are detected and prevented."""
        self._login('student_test', 'student123')
        
        # Create first confirmed booking
        start1 = datetime.now() + timedelta(days=2)
        end1 = start1 + timedelta(hours=2)
        
        with self.app.app_context():
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='confirmed'
            )
        
        # Try to create overlapping booking
        start2 = start1 + timedelta(minutes=30)  # Overlaps with first
        end2 = start2 + timedelta(hours=2)
        
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start2.isoformat(),
            'end_datetime': end2.isoformat()
        })
        
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('conflict', data['error'].lower())
    
    def test_adjacent_bookings_allowed(self):
        """Test that adjacent bookings (no overlap) are allowed."""
        self._login('student_test', 'student123')
        
        # Create first confirmed booking
        start1 = datetime.now() + timedelta(days=3)
        end1 = start1 + timedelta(hours=2)
        
        with self.app.app_context():
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='confirmed'
            )
        
        # Create booking that starts exactly when first ends
        start2 = end1  # Exactly at end of first booking
        end2 = start2 + timedelta(hours=2)
        
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start2.isoformat(),
            'end_datetime': end2.isoformat()
        })
        
        # Should succeed
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    def test_cancelled_bookings_dont_block(self):
        """Test that cancelled bookings don't block new bookings."""
        self._login('student_test', 'student123')
        
        # Create cancelled booking
        start1 = datetime.now() + timedelta(days=4)
        end1 = start1 + timedelta(hours=2)
        
        with self.app.app_context():
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='cancelled'  # Cancelled status
            )
        
        # Try to create booking at same time
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start1.isoformat(),
            'end_datetime': end1.isoformat()
        })
        
        # Should succeed because cancelled booking doesn't block
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    def test_pending_bookings_dont_block(self):
        """Test that pending bookings don't block new bookings (only confirmed do)."""
        self._login('student_test', 'student123')
        
        # Create pending booking
        start1 = datetime.now() + timedelta(days=5)
        end1 = start1 + timedelta(hours=2)
        
        with self.app.app_context():
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start1,
                end_time=end1,
                status='pending'  # Pending, not confirmed
            )
        
        # Try to create booking at same time
        response = self.client.post('/bookings/', json={
            'resource_id': self.resource_id,
            'start_datetime': start1.isoformat(),
            'end_datetime': end1.isoformat()
        })
        
        # Should succeed because pending doesn't block
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    def test_confirm_booking_admin_only(self):
        """Test that only admins can confirm bookings."""
        # Create a booking as student
        start = datetime.now() + timedelta(days=6)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            booking = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                status='pending'
            )
            booking_id = booking.id
        
        # Try to confirm as student
        self._login('student_test', 'student123')
        response = self.client.post(f'/bookings/{booking_id}/confirm')
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data['success'])
        
        # Confirm as admin
        self._login('admin_test', 'admin123')
        response = self.client.post(f'/bookings/{booking_id}/confirm')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['booking']['status'], 'confirmed')
    
    def test_cancel_booking_by_owner(self):
        """Test that booking owner can cancel their own booking."""
        start = datetime.now() + timedelta(days=7)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            booking = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                status='pending'
            )
            booking_id = booking.id
        
        # Cancel as owner
        self._login('student_test', 'student123')
        response = self.client.delete(f'/bookings/{booking_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['booking']['status'], 'cancelled')
    
    def test_cancel_booking_unauthorized(self):
        """Test that other users cannot cancel someone else's booking."""
        start = datetime.now() + timedelta(days=8)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            booking = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                status='pending'
            )
            booking_id = booking.id
        
        # Try to cancel as different student
        self._login('student2_test', 'student234')
        response = self.client.delete(f'/bookings/{booking_id}')
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_list_bookings_user_sees_own(self):
        """Test that users see only their own bookings."""
        start = datetime.now() + timedelta(days=9)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            # Create booking for student1
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end
            )
            
            # Create booking for student2
            booking2 = BookingDAL.create_booking(
                user_id=self.student2_id,
                resource_id=self.resource2_id,
                start_time=start + timedelta(days=1),
                end_time=end + timedelta(days=1)
            )
            booking1_id = booking1.id
        
        # Login as student1
        self._login('student_test', 'student123')
        response = self.client.get('/bookings/')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Should only see their own booking
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['bookings'][0]['id'], booking1_id)
    
    def test_list_bookings_admin_sees_all(self):
        """Test that admins see all bookings."""
        start = datetime.now() + timedelta(days=10)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            # Create bookings for different students
            booking1 = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end
            )
            
            booking2 = BookingDAL.create_booking(
                user_id=self.student2_id,
                resource_id=self.resource2_id,
                start_time=start + timedelta(days=1),
                end_time=end + timedelta(days=1)
            )
        
        # Login as admin
        self._login('admin_test', 'admin123')
        response = self.client.get('/bookings/')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Should see all bookings
        self.assertEqual(data['count'], 2)
    
    def test_update_booking_notes(self):
        """Test updating booking notes."""
        start = datetime.now() + timedelta(days=11)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            booking = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                notes='Original notes'
            )
            booking_id = booking.id
        
        self._login('student_test', 'student123')
        response = self.client.put(f'/bookings/{booking_id}', json={
            'notes': 'Updated notes'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['booking']['notes'], 'Updated notes')
    
    def test_get_booking_by_id(self):
        """Test retrieving a specific booking."""
        start = datetime.now() + timedelta(days=12)
        end = start + timedelta(hours=2)
        
        with self.app.app_context():
            booking = BookingDAL.create_booking(
                user_id=self.student_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=end,
                notes='Test booking'
            )
            booking_id = booking.id
        
        self._login('student_test', 'student123')
        response = self.client.get(f'/bookings/{booking_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['booking']['id'], booking_id)
        self.assertEqual(data['booking']['notes'], 'Test booking')


class BookingDALTestCase2(unittest.TestCase):
    """Test cases for BookingDAL methods - additional methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_data(self):
        """Create test data."""
        user = User(
            username='dal_test2',
            email='dal2@test.edu',
            full_name='DAL Test 2',
            role='student'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.flush()
        
        resource = Resource(
            name='Test Room 2',
            description='Test 2',
            resource_type='room',
            location='Test 2',
            capacity=10,
            creator_id=user.id,
            status='published'
        )
        db.session.add(resource)
        db.session.commit()
        
        self.user_id = user.id
        self.resource_id = resource.id
    
    def test_additional_status_transitions(self):
        """Test additional booking status transitions."""
        with self.app.app_context():
            # Create pending booking
            start = datetime.now() + timedelta(days=1)
            booking = BookingDAL.create_booking(
                user_id=self.user_id,
                resource_id=self.resource_id,
                start_time=start,
                end_time=start + timedelta(hours=1),
                status='pending'
            )
            booking_id = booking.id
            
            # Transition to completed
            completed = BookingDAL.complete_booking(booking_id)
            self.assertEqual(completed.status, 'completed')


if __name__ == '__main__':
    unittest.main()
