"""
Booking Data Access Layer (DAL)
Handles all database operations for Booking model with CRUD functions.
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from src.extensions import db
from src.models import Booking


class BookingDAL:
    """Data Access Layer for Booking model."""

    @staticmethod
    def create_booking(user_id: int, resource_id: int, start_time: datetime,
                      end_time: datetime, status: str = 'pending', notes: str = None) -> Booking:
        """
        Create a new booking.

        Args:
            user_id (int): ID of user making the booking
            resource_id (int): ID of resource being booked
            start_time (datetime): Booking start time
            end_time (datetime): Booking end time
            status (str): Booking status - 'pending', 'confirmed', 'cancelled', 'completed'. Default: 'pending'
            notes (str): Optional notes about the booking

        Returns:
            Booking: Created booking object

        Raises:
            ValueError: If start_time is after end_time
            SQLAlchemyError: For database errors
        """
        try:
            if start_time >= end_time:
                raise ValueError("start_time must be before end_time")

            booking = Booking(
                user_id=user_id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                status=status,
                notes=notes
            )
            db.session.add(booking)
            db.session.commit()
            return booking
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error creating booking: {str(e)}")

    @staticmethod
    def get_booking_by_id(booking_id: int) -> Booking:
        """
        Get booking by ID.

        Args:
            booking_id (int): Booking's primary key

        Returns:
            Booking: Booking object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return db.session.get(Booking, booking_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching booking by ID: {str(e)}")

    @staticmethod
    def get_bookings_by_user(user_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get bookings by user ID, ordered by start time (upcoming first).

        Args:
            user_id (int): ID of user making bookings
            limit (int): Maximum number of bookings to return. Optional.
            offset (int): Number of bookings to skip. Default: 0

        Returns:
            list: List of Booking objects ordered by start_time ascending

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.filter_by(user_id=user_id).order_by(Booking.start_time.asc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching bookings by user: {str(e)}")

    @staticmethod
    def get_user_bookings_by_status(user_id: int, status: str, limit: int = None, offset: int = 0) -> list:
        """
        Get bookings for a user filtered by status, ordered by start time (upcoming first).

        Args:
            user_id (int): ID of user making bookings
            status (str): Status to filter by - 'pending', 'confirmed', 'cancelled', 'completed'
            limit (int): Maximum number of bookings to return. Optional.
            offset (int): Number of bookings to skip. Default: 0

        Returns:
            list: List of Booking objects ordered by start_time ascending

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.filter_by(user_id=user_id, status=status).order_by(Booking.start_time.asc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user bookings by status: {str(e)}")

    @staticmethod
    def get_bookings_by_resource(resource_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get bookings for a specific resource.

        Args:
            resource_id (int): ID of resource
            limit (int): Maximum number of bookings to return. Optional.
            offset (int): Number of bookings to skip. Default: 0

        Returns:
            list: List of Booking objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.filter_by(resource_id=resource_id).order_by(Booking.start_time).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching bookings by resource: {str(e)}")

    @staticmethod
    def get_bookings_by_status(status: str, limit: int = None, offset: int = 0) -> list:
        """
        Get bookings by status, ordered by start time (upcoming first).

        Args:
            status (str): Status to filter by - 'pending', 'confirmed', 'cancelled', 'completed'
            limit (int): Maximum number of bookings to return. Optional.
            offset (int): Number of bookings to skip. Default: 0

        Returns:
            list: List of Booking objects ordered by start_time ascending

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.filter_by(status=status).order_by(Booking.start_time.asc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching bookings by status: {str(e)}")

    @staticmethod
    def get_confirmed_bookings_for_resource(resource_id: int, start_time: datetime = None,
                                           end_time: datetime = None) -> list:
        """
        Get confirmed bookings for a resource within optional time range.

        Args:
            resource_id (int): ID of resource
            start_time (datetime): Filter bookings from this time. Optional.
            end_time (datetime): Filter bookings until this time. Optional.

        Returns:
            list: List of confirmed Booking objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.filter_by(
                resource_id=resource_id,
                status='confirmed'
            )

            if start_time and end_time:
                query = query.filter(
                    (Booking.start_time < end_time) & (Booking.end_time > start_time)
                )
            elif start_time:
                query = query.filter(Booking.end_time > start_time)
            elif end_time:
                query = query.filter(Booking.start_time < end_time)

            return query.order_by(Booking.start_time).all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching confirmed bookings: {str(e)}")

    @staticmethod
    def get_all_bookings(limit: int = None, offset: int = 0) -> list:
        """
        Get all bookings with optional pagination, ordered by start time (upcoming first).

        Args:
            limit (int): Maximum number of bookings to return. Optional.
            offset (int): Number of bookings to skip. Default: 0

        Returns:
            list: List of Booking objects ordered by start_time ascending

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Booking.query.order_by(Booking.start_time.asc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching bookings: {str(e)}")

    @staticmethod
    def update_booking(booking_id: int, **kwargs) -> Booking:
        """
        Update booking by ID.

        Args:
            booking_id (int): Booking's primary key
            **kwargs: Fields to update (status, notes, start_time, end_time)

        Returns:
            Booking: Updated booking object

        Raises:
            ValueError: If booking not found or invalid time range
            SQLAlchemyError: For database errors
        """
        try:
            booking = db.session.get(Booking, booking_id)
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} not found")

            # Validate time range if updating times
            if 'start_time' in kwargs and 'end_time' in kwargs:
                if kwargs['start_time'] >= kwargs['end_time']:
                    raise ValueError("start_time must be before end_time")

            allowed_fields = {'status', 'notes', 'start_time', 'end_time'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(booking, key, value)

            db.session.commit()
            return booking
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating booking: {str(e)}")

    @staticmethod
    def confirm_booking(booking_id: int) -> Booking:
        """
        Confirm a pending booking.

        Args:
            booking_id (int): Booking's primary key

        Returns:
            Booking: Updated booking object

        Raises:
            ValueError: If booking not found
            SQLAlchemyError: For database errors
        """
        try:
            booking = db.session.get(Booking, booking_id)
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} not found")

            booking.status = 'confirmed'
            db.session.commit()
            return booking
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error confirming booking: {str(e)}")

    @staticmethod
    def cancel_booking(booking_id: int) -> Booking:
        """
        Cancel a booking.

        Args:
            booking_id (int): Booking's primary key

        Returns:
            Booking: Updated booking object

        Raises:
            ValueError: If booking not found
            SQLAlchemyError: For database errors
        """
        try:
            booking = db.session.get(Booking, booking_id)
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} not found")

            booking.status = 'cancelled'
            db.session.commit()
            return booking
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error cancelling booking: {str(e)}")

    @staticmethod
    def complete_booking(booking_id: int) -> Booking:
        """
        Mark a booking as completed.

        Args:
            booking_id (int): Booking's primary key

        Returns:
            Booking: Updated booking object

        Raises:
            ValueError: If booking not found
            SQLAlchemyError: For database errors
        """
        try:
            booking = db.session.get(Booking, booking_id)
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} not found")

            booking.status = 'completed'
            db.session.commit()
            return booking
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error completing booking: {str(e)}")

    @staticmethod
    def delete_booking(booking_id: int) -> bool:
        """
        Delete booking by ID.

        Args:
            booking_id (int): Booking's primary key

        Returns:
            bool: True if deletion successful, False if booking not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            booking = db.session.get(Booking, booking_id)
            if not booking:
                return False

            db.session.delete(booking)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting booking: {str(e)}")

    @staticmethod
    def booking_count() -> int:
        """
        Get total count of bookings.

        Returns:
            int: Total number of bookings

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Booking.query.count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting bookings: {str(e)}")
