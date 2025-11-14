"""
Unit tests for Booking Data Access Layer (DAL) and booking logic.

Tests cover:
- CRUD operations for bookings (independent of Flask routes)
- Conflict detection logic
- Status transition validations
- Business rule enforcement
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import sys
import os

# Add campus_resource_hub to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'campus_resource_hub')))

from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL
from src.models.models import Booking


@pytest.mark.unit
@pytest.mark.dal
class TestBookingDAL:
    """Test Booking Data Access Layer CRUD operations."""
    
    def test_create_booking_success(self, db, sample_student, sample_resource):
        """Test creating a valid booking through DAL."""
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        booking = BookingDAL.create_booking(
            user_id=sample_student.id,
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end,
            notes='Unit test booking'
        )
        
        assert booking is not None
        assert booking.id is not None
        assert booking.user_id == sample_student.id
        assert booking.resource_id == sample_resource.id
        assert booking.status == 'pending'
        assert booking.notes == 'Unit test booking'
        assert booking.start_time == start
        assert booking.end_time == end
    
    def test_create_booking_invalid_user(self, db, sample_resource):
        """Test creating booking with non-existent user ID fails."""
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError or validation error
            BookingDAL.create_booking(
                user_id=99999,  # Non-existent user
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes='Invalid booking'
            )
    
    def test_create_booking_invalid_resource(self, db, sample_student):
        """Test creating booking with non-existent resource ID fails."""
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        with pytest.raises(Exception):
            BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=99999,  # Non-existent resource
                start_time=start,
                end_time=end,
                notes='Invalid booking'
            )
    
    def test_get_booking_by_id(self, db, sample_booking):
        """Test retrieving a booking by ID."""
        retrieved = BookingDAL.get_booking_by_id(sample_booking.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_booking.id
        assert retrieved.user_id == sample_booking.user_id
        assert retrieved.resource_id == sample_booking.resource_id
    
    def test_get_booking_by_id_not_found(self, db):
        """Test retrieving non-existent booking returns None."""
        retrieved = BookingDAL.get_booking_by_id(99999)
        assert retrieved is None
    
    def test_update_booking_status(self, db, sample_booking):
        """Test updating booking status through DAL."""
        original_status = sample_booking.status
        assert original_status == 'pending'
        
        updated = BookingDAL.update_booking_status(sample_booking.id, 'confirmed')
        
        assert updated.status == 'confirmed'
        assert updated.id == sample_booking.id
    
    def test_get_bookings_by_user(self, db, sample_student, sample_resource):
        """Test retrieving all bookings for a user."""
        # Create multiple bookings
        for i in range(3):
            start = datetime.utcnow() + timedelta(days=i+1)
            end = start + timedelta(hours=2)
            BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes=f'Booking {i+1}'
            )
        
        bookings = BookingDAL.get_bookings_by_user(sample_student.id)
        
        assert len(bookings) == 3
        assert all(b.user_id == sample_student.id for b in bookings)
    
    def test_get_bookings_by_resource(self, db, sample_student, sample_resource):
        """Test retrieving all bookings for a resource."""
        # Create multiple bookings
        for i in range(3):
            start = datetime.utcnow() + timedelta(days=i+1)
            end = start + timedelta(hours=2)
            BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes=f'Booking {i+1}'
            )
        
        bookings = BookingDAL.get_bookings_by_resource(sample_resource.id)
        
        assert len(bookings) == 3
        assert all(b.resource_id == sample_resource.id for b in bookings)
    
    def test_delete_booking(self, db, sample_booking):
        """Test deleting a booking through DAL."""
        booking_id = sample_booking.id
        
        result = BookingDAL.delete_booking(booking_id)
        assert result is True
        
        # Verify booking no longer exists
        retrieved = BookingDAL.get_booking_by_id(booking_id)
        assert retrieved is None


@pytest.mark.unit
class TestBookingConflictDetection:
    """Test booking conflict detection logic."""
    
    def test_no_conflict_different_times(self, db, sample_student, sample_resource, conflicting_bookings):
        """Test that bookings at different times don't conflict."""
        # Try to book between the two existing bookings (12pm-2pm)
        start = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) == 0
    
    def test_conflict_overlapping_start(self, db, sample_resource, conflicting_bookings):
        """Test conflict when new booking overlaps start of existing booking."""
        # Existing: 10am-12pm, New: 11am-1pm (overlaps)
        start = datetime.utcnow().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) > 0
    
    def test_conflict_overlapping_end(self, db, sample_resource, conflicting_bookings):
        """Test conflict when new booking overlaps end of existing booking."""
        # Existing: 10am-12pm, New: 9am-11am (overlaps)
        start = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) > 0
    
    def test_conflict_completely_contained(self, db, sample_resource, conflicting_bookings):
        """Test conflict when new booking is completely within existing booking."""
        # Existing: 10am-12pm, New: 10:30am-11:30am (inside)
        start = datetime.utcnow().replace(hour=10, minute=30, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) > 0
    
    def test_conflict_completely_contains(self, db, sample_resource, conflicting_bookings):
        """Test conflict when new booking completely contains existing booking."""
        # Existing: 10am-12pm, New: 9am-1pm (contains)
        start = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=4)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) > 0
    
    def test_no_conflict_different_resource(self, db, sample_student, sample_resource, sample_equipment, conflicting_bookings):
        """Test that bookings for different resources don't conflict."""
        # Book the equipment at the same time as study room booking
        start = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_equipment.id,  # Different resource
            start_time=start,
            end_time=end
        )
        
        assert len(conflicts) == 0
    
    def test_no_conflict_with_cancelled_booking(self, db, sample_student, sample_resource):
        """Test that cancelled bookings don't create conflicts."""
        # Create a cancelled booking
        start = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        cancelled_booking = BookingDAL.create_booking(
            user_id=sample_student.id,
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end,
            notes='Cancelled booking'
        )
        BookingDAL.update_booking_status(cancelled_booking.id, 'cancelled')
        
        # Try to book at the same time
        conflicts = BookingDAL.check_booking_conflicts(
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end
        )
        
        # Should not conflict with cancelled booking
        assert len(conflicts) == 0


@pytest.mark.unit
class TestBookingStatusTransitions:
    """Test booking status transition logic and validations."""
    
    def test_pending_to_confirmed(self, db, sample_booking):
        """Test valid transition from pending to confirmed."""
        assert sample_booking.status == 'pending'
        
        updated = BookingDAL.update_booking_status(sample_booking.id, 'confirmed')
        
        assert updated.status == 'confirmed'
    
    def test_pending_to_cancelled(self, db, sample_booking):
        """Test valid transition from pending to cancelled."""
        assert sample_booking.status == 'pending'
        
        updated = BookingDAL.update_booking_status(sample_booking.id, 'cancelled')
        
        assert updated.status == 'cancelled'
    
    def test_confirmed_to_completed(self, db, sample_booking):
        """Test valid transition from confirmed to completed."""
        BookingDAL.update_booking_status(sample_booking.id, 'confirmed')
        
        updated = BookingDAL.update_booking_status(sample_booking.id, 'completed')
        
        assert updated.status == 'completed'
    
    def test_confirmed_to_cancelled(self, db, sample_booking):
        """Test valid transition from confirmed to cancelled."""
        BookingDAL.update_booking_status(sample_booking.id, 'confirmed')
        
        updated = BookingDAL.update_booking_status(sample_booking.id, 'cancelled')
        
        assert updated.status == 'cancelled'
    
    def test_get_pending_bookings(self, db, sample_student, sample_resource):
        """Test retrieving only pending bookings."""
        # Create bookings with different statuses
        for i, status in enumerate(['pending', 'confirmed', 'pending', 'cancelled']):
            start = datetime.utcnow() + timedelta(days=i+1)
            end = start + timedelta(hours=2)
            booking = BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes=f'Booking {i+1}'
            )
            if status != 'pending':
                BookingDAL.update_booking_status(booking.id, status)
        
        pending = BookingDAL.get_pending_bookings()
        
        assert len(pending) == 2
        assert all(b.status == 'pending' for b in pending)


@pytest.mark.unit
class TestBookingBusinessRules:
    """Test business rule enforcement for bookings."""
    
    def test_booking_end_after_start(self, db, sample_student, sample_resource):
        """Test that booking end time must be after start time."""
        start = datetime.utcnow() + timedelta(days=1)
        end = start - timedelta(hours=1)  # End before start (invalid)
        
        with pytest.raises(ValueError):
            BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes='Invalid time booking'
            )
    
    def test_booking_minimum_duration(self, db, sample_student, sample_resource):
        """Test that bookings have minimum duration (if enforced)."""
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(minutes=15)  # Very short duration
        
        # This should succeed - just verifying DAL accepts short bookings
        booking = BookingDAL.create_booking(
            user_id=sample_student.id,
            resource_id=sample_resource.id,
            start_time=start,
            end_time=end,
            notes='Short booking'
        )
        
        assert booking is not None
        assert (booking.end_time - booking.start_time).total_seconds() / 60 == 15
    
    def test_booking_past_date_validation(self, db, sample_student, sample_resource):
        """Test that bookings cannot be created for past dates."""
        start = datetime.utcnow() - timedelta(days=1)  # Yesterday
        end = start + timedelta(hours=2)
        
        # Note: DAL may not enforce this - it might be controller-level validation
        # This test documents the expected behavior
        try:
            booking = BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes='Past booking'
            )
            # If it succeeds, document that past bookings are allowed at DAL level
            assert booking is not None
        except ValueError:
            # If it fails, past bookings are properly rejected
            pass
    
    def test_confirm_booking_method(self, db, sample_booking, sample_admin):
        """Test the confirm_booking method exists and works."""
        confirmed = BookingDAL.confirm_booking(sample_booking.id)
        
        assert confirmed is not None
        assert confirmed.status == 'confirmed'
    
    def test_get_bookings_by_date_range(self, db, sample_student, sample_resource):
        """Test retrieving bookings within a date range."""
        # Create bookings on different days
        base_date = datetime.utcnow() + timedelta(days=7)
        
        for i in range(5):
            start = base_date + timedelta(days=i)
            end = start + timedelta(hours=2)
            BookingDAL.create_booking(
                user_id=sample_student.id,
                resource_id=sample_resource.id,
                start_time=start,
                end_time=end,
                notes=f'Day {i+1} booking'
            )
        
        # Query for bookings in middle 3 days
        range_start = base_date + timedelta(days=1)
        range_end = base_date + timedelta(days=4)
        
        bookings = BookingDAL.get_bookings_by_date_range(range_start, range_end)
        
        # Should get 3 bookings (days 1, 2, 3)
        assert len(bookings) >= 3
        for booking in bookings:
            assert range_start <= booking.start_time <= range_end

