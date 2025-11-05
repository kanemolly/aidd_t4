"""
Bookings blueprint - resource booking and reservation management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.models import Booking

bp = Blueprint('bookings', __name__)


def check_conflict(resource_id: int, start_time: datetime, end_time: datetime) -> bool:
    """
    Check if a booking time slot conflicts with existing confirmed bookings.
    
    Args:
        resource_id (int): Resource ID to check
        start_time (datetime): Proposed booking start time
        end_time (datetime): Proposed booking end time
    
    Returns:
        bool: True if conflict exists, False if slot is available
    
    Note:
        Adjacent bookings (ending exactly when another starts) are allowed.
        Cancelled bookings are ignored in conflict detection.
    """
    try:
        confirmed_bookings = BookingDAL.get_confirmed_bookings_for_resource(
            resource_id, 
            start_time=start_time, 
            end_time=end_time
        )
        return len(confirmed_bookings) > 0
    except Exception:
        return False


@bp.route('/', methods=['GET'])
@login_required
def list_bookings():
    """
    List user's bookings or all bookings (admin).
    
    Query params:
        - status: Filter by status (pending, confirmed, cancelled, completed)
        - limit: Max results to return
        - offset: Results to skip
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Admins can see all bookings, others see only their own
        if current_user.is_admin():
            if status:
                bookings = BookingDAL.get_bookings_by_status(status, limit=limit, offset=offset)
            else:
                bookings = BookingDAL.get_all_bookings(limit=limit, offset=offset)
        else:
            bookings = BookingDAL.get_bookings_by_user(current_user.id, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'bookings': [b.to_dict() for b in bookings],
            'count': len(bookings)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a specific booking by ID."""
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Users can only view their own bookings unless they're admin
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        return jsonify({'success': True, 'booking': booking.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@login_required
def create_booking():
    """
    Create a new booking.
    
    JSON payload:
        - resource_id (int, required): ID of resource to book
        - start_datetime (str, required): ISO format datetime "YYYY-MM-DD HH:MM:SS"
        - end_datetime (str, required): ISO format datetime "YYYY-MM-DD HH:MM:SS"
        - notes (str, optional): Booking notes
    
    Returns:
        201: Created booking with ID on success
        400: Invalid input or validation error
        404: Resource not found
        409: Time slot conflict
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        resource_id = data.get('resource_id')
        start_str = data.get('start_datetime')
        end_str = data.get('end_datetime')
        notes = data.get('notes', '')
        
        if not all([resource_id, start_str, end_str]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: resource_id, start_datetime, end_datetime'
            }), 400
        
        # Validate resource exists
        resource = ResourceDAL.get_resource_by_id(resource_id)
        if not resource:
            return jsonify({'success': False, 'error': 'Resource not found'}), 404
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid datetime format. Use: YYYY-MM-DD HH:MM:SS'
            }), 400
        
        # Validate datetime range
        if start_time >= end_time:
            return jsonify({
                'success': False,
                'error': 'Start time must be before end time'
            }), 400
        
        # Check for conflicts with existing confirmed bookings
        if check_conflict(resource_id, start_time, end_time):
            return jsonify({
                'success': False,
                'error': 'Time slot conflicts with an existing confirmed booking'
            }), 409
        
        # Create the booking
        booking = BookingDAL.create_booking(
            user_id=current_user.id,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            status=Booking.STATUS_PENDING,
            notes=notes if notes else None
        )
        
        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>', methods=['PUT'])
@login_required
def update_booking(booking_id):
    """
    Update a booking (notes, times, or admin status changes).
    
    JSON payload (all optional):
        - start_datetime: ISO format datetime
        - end_datetime: ISO format datetime
        - notes: Updated notes
        - status: New status (admin only)
    
    Returns:
        200: Updated booking
        400: Invalid data
        403: Unauthorized
        404: Booking not found
        409: Time conflict
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only owner or admin can update
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        update_fields = {}
        
        # Handle datetime updates
        if 'start_datetime' in data or 'end_datetime' in data:
            start_time = booking.start_time
            end_time = booking.end_time
            
            if 'start_datetime' in data:
                try:
                    start_time = datetime.fromisoformat(data['start_datetime'])
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid start_datetime format'}), 400
            
            if 'end_datetime' in data:
                try:
                    end_time = datetime.fromisoformat(data['end_datetime'])
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid end_datetime format'}), 400
            
            if start_time >= end_time:
                return jsonify({'success': False, 'error': 'Start time must be before end time'}), 400
            
            # Check for conflicts if times changed
            if start_time != booking.start_time or end_time != booking.end_time:
                if check_conflict(booking.resource_id, start_time, end_time):
                    return jsonify({
                        'success': False,
                        'error': 'Updated time slot conflicts with existing confirmed bookings'
                    }), 409
            
            update_fields['start_time'] = start_time
            update_fields['end_time'] = end_time
        
        # Handle notes update
        if 'notes' in data:
            update_fields['notes'] = data['notes']
        
        # Handle status updates (admin only)
        if 'status' in data:
            if not current_user.is_admin():
                return jsonify({'success': False, 'error': 'Only admins can change status'}), 403
            
            if data['status'] not in Booking.VALID_STATUSES:
                return jsonify({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(Booking.VALID_STATUSES)}'
                }), 400
            
            update_fields['status'] = data['status']
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Update booking
        updated_booking = BookingDAL.update_booking(booking_id, **update_fields)
        
        return jsonify({
            'success': True,
            'message': 'Booking updated successfully',
            'booking': updated_booking.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    """
    Cancel a booking (changes status to cancelled).
    
    Returns:
        200: Cancelled booking
        403: Unauthorized
        404: Booking not found
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only owner or admin can cancel
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        cancelled_booking = BookingDAL.cancel_booking(booking_id)
        
        return jsonify({
            'success': True,
            'message': 'Booking cancelled successfully',
            'booking': cancelled_booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    """
    Confirm a pending booking (admin only).
    
    Returns:
        200: Confirmed booking
        403: Unauthorized or already confirmed
        404: Booking not found
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only admin can confirm
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Only admins can confirm bookings'}), 403
        
        # Can only confirm pending bookings
        if booking.status != Booking.STATUS_PENDING:
            return jsonify({
                'success': False,
                'error': f'Cannot confirm {booking.status} booking. Only pending bookings can be confirmed.'
            }), 400
        
        confirmed_booking = BookingDAL.confirm_booking(booking_id)
        
        return jsonify({
            'success': True,
            'message': 'Booking confirmed successfully',
            'booking': confirmed_booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
