"""
Bookings blueprint - resource booking and reservation management.
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.models import Booking
from src.extensions import csrf_protect
from src.services.email_service import email_service
from src.services.calendar_service import calendar_service
from src.services.notification_service import NotificationService

bp = Blueprint('bookings', __name__, url_prefix='/bookings')


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


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Redirect to the unified admin dashboard.
    This route is deprecated in favor of /admin/dashboard which combines
    all admin, bookings, and moderation functionality in one place.
    """
    if current_user.is_admin() or current_user.is_staff():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('bookings.list_bookings'))


@bp.route('/')
@login_required
def index():
    """Redirect admin/staff to dashboard, others to list."""
    if current_user.is_admin() or current_user.is_staff():
        return redirect(url_for('bookings.dashboard'))
    return redirect(url_for('bookings.list_bookings'))


@bp.route('/list', methods=['GET'])
@login_required
def list_bookings():
    """
    List user's bookings or all bookings (admin).
    
    Query params:
        - status: Filter by status (pending, confirmed, cancelled, completed)
        - limit: Max results to return
        - offset: Results to skip
        - format: 'json' for API response, 'html' (default) for web page
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        response_format = request.args.get('format', 'html')
        
        # Admins can see all bookings, others see only their own
        if current_user.is_admin():
            if status:
                bookings = BookingDAL.get_bookings_by_status(status, limit=limit, offset=offset)
            else:
                bookings = BookingDAL.get_all_bookings(limit=limit, offset=offset)
            is_admin_view = True
        else:
            # For regular users, filter by user and status if provided
            if status:
                bookings = BookingDAL.get_user_bookings_by_status(current_user.id, status, limit=limit, offset=offset)
            else:
                bookings = BookingDAL.get_bookings_by_user(current_user.id, limit=limit, offset=offset)
            is_admin_view = False
        
        # Return JSON for API calls
        if response_format == 'json' or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'bookings': [b.to_dict() for b in bookings],
                'count': len(bookings)
            }), 200
        
        # Return HTML template for web view
        from datetime import datetime
        return render_template(
            'bookings/list.html',
            bookings=bookings,
            is_admin_view=is_admin_view,
            current_status=status,
            now=datetime.now
        )
        
    except Exception as e:
        if response_format == 'json' or request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'error': str(e)}), 500
        return render_template('error.html', error=str(e)), 500


@bp.route('/<int:booking_id>/view', methods=['GET'])
@login_required
def view_booking(booking_id):
    """View detailed booking information in HTML page."""
    import traceback
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return render_template('error.html', error='Booking not found'), 404
        
        # Users can only view their own bookings unless they're admin
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return render_template('error.html', error='Unauthorized'), 403
        
        return render_template('bookings/detail.html', booking=booking, current_user=current_user)
    except Exception as e:
        # Log the full traceback for debugging
        print(f"Error in view_booking: {str(e)}")
        traceback.print_exc()
        return render_template('error.html', error=str(e)), 500


@bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a specific booking by ID (API endpoint)."""
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


@bp.route('/new', methods=['GET'])
@login_required
def booking_form():
    """
    Display booking form for a specific resource.
    
    Query params:
        - resource_id (int, required): ID of resource to book
    
    Returns:
        Rendered booking form template
    """
    resource_id = request.args.get('resource_id', type=int)
    
    if not resource_id:
        return jsonify({'success': False, 'error': 'resource_id is required'}), 400
    
    resource = ResourceDAL.get_resource_by_id(resource_id)
    
    if not resource:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    if not resource.is_available:
        return jsonify({'success': False, 'error': 'Resource is not available for booking'}), 400
    
    return render_template(
        'bookings/form.html',
        resource=resource,
        today=date.today().isoformat()
    )


@bp.route('/', methods=['POST'])
@csrf_protect.exempt
@login_required
def create_booking():
    """
    Create a new booking with optional recurrence.
    
    JSON payload:
        - resource_id (int, required): ID of resource to book
        - start_datetime (str, required): ISO format datetime "YYYY-MM-DD HH:MM:SS"
        - end_datetime (str, required): ISO format datetime "YYYY-MM-DD HH:MM:SS"
        - notes (str, optional): Booking notes
        - is_recurring (bool, optional): Whether this is a recurring booking
        - recurrence_pattern (str, optional): Pattern (daily, weekly, biweekly, monthly)
        - recurrence_end_date (str, optional): End date for recurrence "YYYY-MM-DD"
    
    Returns:
        201: Created booking(s) with ID on success
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
        is_recurring = data.get('is_recurring', False)
        recurrence_pattern = data.get('recurrence_pattern', 'weekly')
        recurrence_end_str = data.get('recurrence_end_date')
        
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
        
        # Validate business hours (8 AM - 8 PM)
        BUSINESS_HOURS_START = 8  # 8 AM
        BUSINESS_HOURS_END = 20   # 8 PM
        
        if start_time.hour < BUSINESS_HOURS_START or start_time.hour >= BUSINESS_HOURS_END:
            return jsonify({
                'success': False,
                'error': f'Start time must be between {BUSINESS_HOURS_START}:00 AM and {BUSINESS_HOURS_END}:00 (8 PM). Business hours only.'
            }), 400
        
        if end_time.hour < BUSINESS_HOURS_START or end_time.hour > BUSINESS_HOURS_END:
            return jsonify({
                'success': False,
                'error': f'End time must be between {BUSINESS_HOURS_START}:00 AM and {BUSINESS_HOURS_END}:00 (8 PM). Business hours only.'
            }), 400
        
        # Allow bookings to end exactly at 8 PM (20:00) if minutes are 0
        if end_time.hour == BUSINESS_HOURS_END and end_time.minute > 0:
            return jsonify({
                'success': False,
                'error': 'Bookings must end by 8:00 PM.'
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
        
        # Auto-approve if resource doesn't require approval
        # BUT: Recurring bookings ALWAYS require admin approval
        if is_recurring:
            booking_status = Booking.STATUS_PENDING  # Always pending for recurring
        else:
            booking_status = Booking.STATUS_PENDING if resource.requires_approval else Booking.STATUS_CONFIRMED
        
        # Handle recurring bookings
        if is_recurring and recurrence_end_str:
            from dateutil.relativedelta import relativedelta
            
            recurrence_end_date = datetime.fromisoformat(recurrence_end_str).date()
            booking_dates = []
            conflicts = []
            current_date = start_time.date()
            
            # Calculate all occurrence dates
            while current_date <= recurrence_end_date:
                booking_dates.append(current_date)
                
                # Increment based on pattern
                if recurrence_pattern == 'daily':
                    current_date += relativedelta(days=1)
                elif recurrence_pattern == 'weekly':
                    current_date += relativedelta(weeks=1)
                elif recurrence_pattern == 'biweekly':
                    current_date += relativedelta(weeks=2)
                elif recurrence_pattern == 'monthly':
                    current_date += relativedelta(months=1)
                else:
                    break
            
            # Create parent booking (first occurrence)
            parent_booking = BookingDAL.create_booking(
                user_id=current_user.id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                status=booking_status,
                notes=notes if notes else None
            )
            
            # Update parent booking with recurrence info
            parent_booking.is_recurring = True
            parent_booking.recurrence_pattern = recurrence_pattern
            parent_booking.recurrence_end_date = datetime.combine(recurrence_end_date, datetime.min.time())
            
            from src.extensions import db
            db.session.commit()
            
            created_bookings = [parent_booking]
            
            # Create recurring instances (skip first date, already created)
            for booking_date in booking_dates[1:]:
                # Create datetime for this occurrence
                recur_start = datetime.combine(booking_date, start_time.time())
                recur_end = datetime.combine(booking_date, end_time.time())
                
                # Check for conflict
                if check_conflict(resource_id, recur_start, recur_end):
                    conflicts.append(booking_date.isoformat())
                    continue
                
                # Create recurring instance
                instance = BookingDAL.create_booking(
                    user_id=current_user.id,
                    resource_id=resource_id,
                    start_time=recur_start,
                    end_time=recur_end,
                    status=booking_status,
                    notes=notes if notes else None
                )
                
                # Link to parent
                instance.parent_booking_id = parent_booking.id
                db.session.commit()
                
                created_bookings.append(instance)
            
            message = f'Created {len(created_bookings)} recurring booking(s). '
            if conflicts:
                message += f'{len(conflicts)} dates were skipped due to conflicts. '
            message += 'All recurring bookings require admin approval.'
            
            return jsonify({
                'success': True,
                'message': message,
                'booking_id': parent_booking.id,
                'auto_approved': False,  # Always false for recurring
                'requires_approval': True,
                'is_recurring': True,
                'total_created': len(created_bookings),
                'conflicts_skipped': len(conflicts),
                'conflicted_dates': conflicts,
                'bookings': [b.to_dict() for b in created_bookings]
            }), 201
        
        # Create single booking (non-recurring)
        booking = BookingDAL.create_booking(
            user_id=current_user.id,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            status=booking_status,
            notes=notes if notes else None
        )
        
        # Send email notification
        if current_app.config.get('EMAIL_NOTIFICATIONS_ENABLED', True):
            try:
                if booking.status == 'confirmed':
                    email_service.send_booking_confirmation(booking, current_user)
                else:
                    email_service.send_booking_created(booking, current_user)
            except Exception as e:
                # Log error but don't fail the booking
                print(f"Error sending booking email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'booking_id': booking.id,
            'auto_approved': not resource.requires_approval,
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
        
        # Send email notification
        if current_app.config.get('EMAIL_NOTIFICATIONS_ENABLED', True):
            try:
                email_service.send_booking_cancelled(cancelled_booking, cancelled_booking.user, current_user)
            except Exception as e:
                print(f"Error sending cancellation email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Booking cancelled successfully',
            'booking': cancelled_booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/confirm', methods=['POST'])
@csrf_protect.exempt  # Temporarily disable CSRF to test
@login_required
def confirm_booking(booking_id):
    """
    Confirm a pending booking (admin/staff only) and notify the user.
    
    Returns:
        200: Confirmed booking
        403: Unauthorized or already confirmed
        404: Booking not found
    """
    try:
        # Debug logging
        print("\n" + "="*60)
        print("CSRF DEBUG INFO:")
        print("="*60)
        print(f"Request Headers: {dict(request.headers)}")
        print(f"Request Method: {request.method}")
        print(f"Request URL: {request.url}")
        
        # Check what Flask-WTF sees
        from flask import session
        print(f"Session keys: {list(session.keys())}")
        print(f"User is admin: {current_user.is_admin()}")
        print(f"User is staff: {current_user.is_staff()}")
        print("="*60 + "\n")
        
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only admin and staff can confirm
        if not (current_user.is_admin() or current_user.is_staff()):
            return jsonify({'success': False, 'error': 'Only admins and staff can confirm bookings'}), 403
        
        # Can only confirm pending bookings
        if booking.status != Booking.STATUS_PENDING:
            return jsonify({
                'success': False,
                'error': f'Cannot confirm {booking.status} booking. Only pending bookings can be confirmed.'
            }), 400
        
        confirmed_booking = BookingDAL.confirm_booking(booking_id)
        
        # Set approval tracking fields
        confirmed_booking.approved_by_id = current_user.id
        confirmed_booking.approved_at = datetime.utcnow()
        from src.extensions import db
        db.session.commit()
        
        # Create notification record
        try:
            notification_service = NotificationService()
            notification_service.notify_booking_confirmed(confirmed_booking)
        except Exception as e:
            print(f"Error creating notification record: {str(e)}")
        
        # Send in-app notification to student
        try:
            from src.data_access.message_dal import MessageDAL
            notification_subject = f"Booking Approved: {booking.resource.name}"
            notification_body = f"""
Your booking for {booking.resource.name} has been approved!

Booking Details:
- Resource: {booking.resource.name}
- Start: {booking.start_time.strftime('%B %d, %Y at %I:%M %p')}
- End: {booking.end_time.strftime('%B %d, %Y at %I:%M %p')}
- Location: {booking.resource.location if booking.resource.location else 'Not specified'}

Your reservation is confirmed. Please arrive on time for your booking.
            """.strip()
            
            MessageDAL.create_message(
                sender_id=current_user.id,
                recipient_id=booking.user_id,
                subject=notification_subject,
                body=notification_body
            )
        except Exception as e:
            # Log error but don't fail the approval
            print(f"Error sending in-app notification: {str(e)}")
        
        # Send email notification
        if current_app.config.get('EMAIL_NOTIFICATIONS_ENABLED', True):
            try:
                email_service.send_booking_confirmation(confirmed_booking, confirmed_booking.user)
            except Exception as e:
                print(f"Error sending booking confirmation email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Booking confirmed successfully',
            'booking': confirmed_booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500




@bp.route('/<int:booking_id>/cancel', methods=['POST'])
@csrf_protect.exempt
@login_required
def cancel_booking_with_reason(booking_id):
    """
    Cancel a booking with a reason.
    - Students can cancel their own bookings
    - Admins/staff can cancel any booking with a denial reason
    
    Returns:
        200: Cancelled booking
        403: Unauthorized
        404: Booking not found
    """
    try:
        print(f"[DEBUG] POST /bookings/{booking_id}/cancel endpoint hit")
        print(f"[DEBUG] Request headers: {dict(request.headers)}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] X-CSRFToken header: {request.headers.get('X-CSRFToken', 'NOT FOUND')}")
        
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Check authorization: allow owner or admin/staff
        is_owner = booking.user_id == current_user.id
        is_admin_or_staff = current_user.is_admin() or current_user.is_staff()
        
        if not (is_owner or is_admin_or_staff):
            return jsonify({'success': False, 'error': 'You can only cancel your own bookings'}), 403
        
        # Get JSON data (optional for student cancellations)
        try:
            data = request.get_json(force=False, silent=True) or {}
        except Exception:
            data = {}
        reason = data.get('reason', 'No reason provided')
        
        # Cancel the booking
        cancelled_booking = BookingDAL.cancel_booking(booking_id)
        
        # Store cancellation reason and who cancelled it
        cancelled_booking.cancellation_reason = reason
        cancelled_booking.cancelled_by_id = current_user.id
        from src.extensions import db
        db.session.commit()
        
        # Send in-app notification
        try:
            from src.data_access.message_dal import MessageDAL
            
            # Different notification based on who cancelled
            if is_admin_or_staff and not is_owner:
                # Admin/staff denying a booking
                notification_subject = f"Booking Denied: {booking.resource.name}"
                notification_body = f"""
Your booking for {booking.resource.name} has been denied.

Booking Details:
- Resource: {booking.resource.name}
- Date: {booking.start_time.strftime('%B %d, %Y')}
- Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}

Reason for denial: {reason}

Please contact the resource administrator if you have questions.
                """.strip()
            else:
                # Student cancelling their own booking
                notification_subject = f"Booking Cancelled: {booking.resource.name}"
                notification_body = f"""
You have successfully cancelled your booking for {booking.resource.name}.

Booking Details:
- Resource: {booking.resource.name}
- Date: {booking.start_time.strftime('%B %d, %Y')}
- Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}

The resource is now available for other students to book.
                """.strip()
            
            MessageDAL.create_message(
                sender_id=current_user.id,
                recipient_id=booking.user_id,
                subject=notification_subject,
                body=notification_body
            )
        except Exception as e:
            # Log error but don't fail the cancellation
            print(f"Error sending in-app notification: {str(e)}")
        
        # Send email notification
        if current_app.config.get('EMAIL_NOTIFICATIONS_ENABLED', True):
            try:
                email_service.send_booking_cancelled(cancelled_booking, cancelled_booking.user, current_user)
            except Exception as e:
                print(f"Error sending cancellation email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Booking denied successfully',
            'booking': cancelled_booking.to_dict()
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/edit', methods=['POST'])
@csrf_protect.exempt
@login_required
def edit_booking(booking_id):
    """
    Edit a booking (admin/staff only).
    Allows modification of start_time, end_time, and notes.
    Notifies the user of changes.
    
    Request body (JSON):
        - start_time (str): ISO format datetime
        - end_time (str): ISO format datetime
        - notes (str, optional): Booking notes
    
    Returns:
        200: Updated booking with change summary
        400: Validation error (conflict, invalid times)
        403: Unauthorized
        404: Booking not found
        500: Server error
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only admin and staff can edit
        if not (current_user.is_admin() or current_user.is_staff()):
            return jsonify({'success': False, 'error': 'Only admins and staff can edit bookings'}), 403
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        # Extract and validate new times
        new_start_str = data.get('start_time')
        new_end_str = data.get('end_time')
        new_notes = data.get('notes', '').strip()
        
        if not new_start_str or not new_end_str:
            return jsonify({'success': False, 'error': 'start_time and end_time are required'}), 400
        
        try:
            # Parse datetime strings (assume ISO format from frontend)
            from dateutil import parser
            new_start_time = parser.isoparse(new_start_str)
            new_end_time = parser.isoparse(new_end_str)
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Invalid datetime format: {str(e)}'}), 400
        
        # Validate time range
        if new_start_time >= new_end_time:
            return jsonify({'success': False, 'error': 'Start time must be before end time'}), 400
        
        # Check for booking conflicts (excluding current booking)
        if booking.status in [Booking.STATUS_CONFIRMED, Booking.STATUS_PENDING]:
            confirmed_bookings = BookingDAL.get_confirmed_bookings_for_resource(
                booking.resource_id,
                start_time=new_start_time,
                end_time=new_end_time
            )
            # Filter out current booking
            conflicting = [b for b in confirmed_bookings if b.id != booking_id]
            if conflicting:
                conflict_list = ', '.join([f"#{b.id} ({b.start_time} - {b.end_time})" for b in conflicting])
                return jsonify({
                    'success': False,
                    'error': f'Time slot conflicts with existing bookings: {conflict_list}'
                }), 400
        
        # Track changes
        changes = []
        if booking.start_time != new_start_time:
            changes.append(f"Start time: {booking.start_time.isoformat()} → {new_start_time.isoformat()}")
            booking.start_time = new_start_time
        
        if booking.end_time != new_end_time:
            changes.append(f"End time: {booking.end_time.isoformat()} → {new_end_time.isoformat()}")
            booking.end_time = new_end_time
        
        if booking.notes != new_notes:
            old_notes = booking.notes or "(empty)"
            changes.append(f"Notes: {old_notes} → {new_notes if new_notes else '(empty)'}")
            booking.notes = new_notes if new_notes else None
        
        if not changes:
            return jsonify({'success': False, 'error': 'No changes provided'}), 400
        
        # Update modification tracking
        booking.modified_by_id = current_user.id
        booking.modified_at = datetime.utcnow()
        booking.change_summary = '\n'.join(changes)
        
        # Commit changes
        from src.extensions import db
        db.session.commit()
        
        # Send in-app notification to student
        try:
            from src.data_access.message_dal import MessageDAL
            notification_subject = f"Booking Modified: {booking.resource.name}"
            notification_body = f"""
Your booking for {booking.resource.name} has been modified by an administrator.

Modified Booking Details:
- Resource: {booking.resource.name}
- Start: {booking.start_time.strftime('%B %d, %Y at %I:%M %p')}
- End: {booking.end_time.strftime('%B %d, %Y at %I:%M %p')}
- Location: {booking.resource.location if booking.resource.location else 'Not specified'}

Changes Made:
{booking.change_summary}

Modified By: {current_user.full_name}

Please review your booking details and contact us if you have any questions.
            """.strip()
            
            MessageDAL.create_message(
                sender_id=current_user.id,
                recipient_id=booking.user_id,
                subject=notification_subject,
                body=notification_body
            )
        except Exception as e:
            # Log error but don't fail the edit
            print(f"Error sending in-app notification: {str(e)}")
        
        # Send email notification
        if current_app.config.get('EMAIL_NOTIFICATIONS_ENABLED', True):
            try:
                email_service.send_booking_modified(booking, booking.user, current_user, changes)
            except Exception as e:
                print(f"Error sending modification email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Booking modified successfully',
            'booking': booking.to_dict(),
            'changes': changes
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error in edit_booking: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/confirmation', methods=['GET'])
@login_required
def confirmation_page(booking_id):
    """Display booking confirmation page."""
    from flask import render_template
    from src.data_access.resource_dal import ResourceDAL
    import traceback
    
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Users can only view their own bookings unless they're admin
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get resource details
        resource = ResourceDAL.get_resource_by_id(booking.resource_id)
        
        # Calculate duration
        duration = booking.end_time - booking.start_time
        duration_hours = duration.total_seconds() / 3600
        
        return render_template(
            'bookings/confirmation.html',
            booking=booking,
            resource=resource,
            duration_hours=f"{duration_hours:.1f}",
            current_user=current_user
        )
    except Exception as e:
        # Log the full traceback for debugging
        print(f"Error in confirmation_page: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/export/gcal', methods=['GET'])
@login_required
def export_to_gcal(booking_id):
    """
    Redirect to Google Calendar with booking details.
    Creates a Google Calendar link that user can click to add to their calendar.
    """
    import urllib.parse
    from src.data_access.resource_dal import ResourceDAL
    
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Users can only export their own bookings unless they're admin
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get resource details
        resource = ResourceDAL.get_resource_by_id(booking.resource_id)
        
        # Format times for Google Calendar (RFC3339 format)
        start_time = booking.start_time.isoformat()
        end_time = booking.end_time.isoformat()
        
        # Create event details
        event_title = f"Campus Booking: {resource.name}"
        event_description = f"""Campus Resource Booking

Resource: {resource.name}
Location: {resource.location}
Booking ID: {booking.id}
Type: {resource.resource_type}

Notes: {booking.notes or 'No notes'}"""
        
        # Build Google Calendar URL
        params = {
            'action': 'TEMPLATE',
            'text': event_title,
            'dates': f"{start_time.replace('-', '').replace(':', '')}/{end_time.replace('-', '').replace(':', '')}",
            'details': event_description,
            'location': resource.location or 'Indiana University'
        }
        
        gcal_url = 'https://calendar.google.com/calendar/render?' + urllib.parse.urlencode(params)
        
        from flask import redirect
        return redirect(gcal_url)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/export/ical', methods=['GET'])
@login_required
def export_to_ical(booking_id):
    """
    Export booking as iCalendar (.ics) file.
    Can be imported into any calendar application (Google, Outlook, Apple, etc).
    """
    from src.data_access.resource_dal import ResourceDAL
    from flask import Response
    
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Users can only export their own bookings unless they're admin
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get resource details
        resource = ResourceDAL.get_resource_by_id(booking.resource_id)
        
        # Create iCalendar content
        ical_content = create_ical(booking, resource, current_user)
        
        # Return as downloadable file
        return Response(
            ical_content,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="booking-{booking.id}.ics"'
            }
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


def create_ical(booking, resource, user):
    """
    Create an iCalendar (.ics) formatted string for a booking.
    
    Args:
        booking: Booking object
        resource: Resource object
        user: User object
    
    Returns:
        str: iCalendar formatted content
    """
    from datetime import datetime, timezone
    import uuid
    
    # Convert to UTC and format as RFC5545
    start = booking.start_time.isoformat().replace('-', '').replace(':', '').split('.')[0] + 'Z'
    end = booking.end_time.isoformat().replace('-', '').replace(':', '').split('.')[0] + 'Z'
    created = datetime.now(timezone.utc).isoformat().replace('-', '').replace(':', '').split('.')[0] + 'Z'
    
    # Generate unique ID
    uid = f"booking-{booking.id}-{uuid.uuid4()}@campusresourcehub.iu.edu"
    
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Campus Resource Hub//IU//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{created}
DTSTART:{start}
DTEND:{end}
SUMMARY:Campus Booking: {resource.name}
DESCRIPTION:Campus Resource Booking\\n\\nResource: {resource.name}\\nLocation: {resource.location}\\nBooking ID: {booking.id}\\nType: {resource.resource_type}\\n\\nNotes: {booking.notes or 'No notes'}
LOCATION:{resource.location or 'Indiana University'}
ORGANIZER;CN=Campus Resource Hub:mailto:resourcehub@iu.edu
ATTENDEE;RSVP=TRUE;PARTSTAT=ACCEPTED;CN={user.name}:mailto:{user.email}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
    
    return ical


@bp.route('/resource/<int:resource_id>/availability', methods=['GET'])
def get_resource_availability(resource_id):
    """
    Get booking availability data for a resource within a date range.
    
    Query params:
        - start_date: ISO format date (YYYY-MM-DD)
        - end_date: ISO format date (YYYY-MM-DD)
    
    Returns:
        JSON with confirmed bookings in the date range
    """
    try:
        from datetime import datetime, timedelta
        
        # Get date range from query params
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Default to current month if not provided
        if not start_date_str:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.fromisoformat(start_date_str)
        
        if not end_date_str:
            # End of current month
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get confirmed bookings for this resource in date range
        bookings = BookingDAL.get_confirmed_bookings_for_resource(
            resource_id,
            start_time=start_date,
            end_time=end_date
        )
        
        # Format bookings for calendar
        events = []
        for booking in bookings:
            events.append({
                'id': booking.id,
                'start': booking.start_time.isoformat(),
                'end': booking.end_time.isoformat(),
                'title': f'Booked by {booking.user.username if booking.user else "Unknown"}',
                'status': booking.status
            })
        
        return jsonify({
            'success': True,
            'events': events,
            'resource_id': resource_id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/check-conflict', methods=['POST'])
@csrf_protect.exempt
@login_required
def check_booking_conflict():
    """
    Check if a booking time slot has conflicts.
    
    JSON payload:
        - resource_id (int): Resource ID
        - date (str): Date in YYYY-MM-DD format
        - start_time (str): Start time in HH:MM format
        - end_time (str): End time in HH:MM format
    
    Returns:
        JSON with has_conflict boolean
    """
    try:
        data = request.get_json()
        
        resource_id = data.get('resource_id')
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not all([resource_id, date_str, start_time_str, end_time_str]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Parse datetime
        start_datetime = datetime.fromisoformat(f"{date_str} {start_time_str}:00")
        end_datetime = datetime.fromisoformat(f"{date_str} {end_time_str}:00")
        
        # Check conflict
        has_conflict = check_conflict(resource_id, start_datetime, end_datetime)
        
        return jsonify({
            'success': True,
            'has_conflict': has_conflict
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/analytics', methods=['GET'])
@login_required
def analytics():
    """
    Admin booking analytics and log page.
    Shows comprehensive insights into booking patterns and history.
    """
    # Only admins can access analytics
    if not current_user.is_admin():
        from flask import flash, redirect, url_for
        flash('You do not have permission to access analytics.', 'error')
        return redirect(url_for('bookings.list_bookings'))
    
    try:
        from src.models import Resource, User
        from sqlalchemy import func
        from datetime import timedelta
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id', type=int)
        
        # Base query
        query = Booking.query
        
        # Apply filters
        if start_date:
            query = query.filter(Booking.start_time >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Booking.end_time <= datetime.strptime(end_date, '%Y-%m-%d'))
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        
        # Get all bookings matching filters
        all_bookings = query.all()
        
        # Filter by resource type if specified
        if resource_type:
            all_bookings = [b for b in all_bookings if b.resource.resource_type == resource_type]
        
        # Calculate statistics
        total_bookings = len(all_bookings)
        confirmed_count = len([b for b in all_bookings if b.status == 'confirmed'])
        pending_count = len([b for b in all_bookings if b.status == 'pending'])
        cancelled_count = len([b for b in all_bookings if b.status == 'cancelled'])
        completed_count = len([b for b in all_bookings if b.status == 'completed'])
        
        # Top users (who books most)
        user_booking_counts = {}
        for booking in all_bookings:
            user_id = booking.user_id
            if user_id not in user_booking_counts:
                user_booking_counts[user_id] = {'user': booking.user, 'count': 0}
            user_booking_counts[user_id]['count'] += 1
        
        top_users = sorted(user_booking_counts.values(), key=lambda x: x['count'], reverse=True)[:10]
        
        # Top resources (most booked)
        resource_booking_counts = {}
        for booking in all_bookings:
            res_id = booking.resource_id
            if res_id not in resource_booking_counts:
                resource_booking_counts[res_id] = {'resource': booking.resource, 'count': 0}
            resource_booking_counts[res_id]['count'] += 1
        
        top_resources = sorted(resource_booking_counts.values(), key=lambda x: x['count'], reverse=True)[:10]
        
        # Bookings by resource type
        type_counts = {}
        for booking in all_bookings:
            r_type = booking.resource.resource_type
            type_counts[r_type] = type_counts.get(r_type, 0) + 1
        
        # Bookings by day of week
        day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for booking in all_bookings:
            day = booking.start_time.weekday()
            day_counts[day] += 1
        
        # Bookings by hour of day
        hour_counts = {hour: 0 for hour in range(24)}
        for booking in all_bookings:
            hour = booking.start_time.hour
            hour_counts[hour] += 1
        
        # Average booking duration
        total_duration = sum([(b.end_time - b.start_time).total_seconds() for b in all_bookings])
        avg_duration_hours = (total_duration / len(all_bookings) / 3600) if all_bookings else 0
        
        # Get all resource types and users for filters
        all_resource_types = sorted(set(r.resource_type for r in Resource.query.all()))
        all_users = User.query.order_by(User.full_name).all()
        
        return render_template(
            'bookings/analytics.html',
            bookings=all_bookings,
            total_bookings=total_bookings,
            confirmed_count=confirmed_count,
            pending_count=pending_count,
            cancelled_count=cancelled_count,
            completed_count=completed_count,
            top_users=top_users,
            top_resources=top_resources,
            type_counts=type_counts,
            day_counts=day_counts,
            hour_counts=hour_counts,
            avg_duration_hours=avg_duration_hours,
            all_resource_types=all_resource_types,
            all_users=all_users,
            # Pass back filter values
            filter_start_date=start_date or '',
            filter_end_date=end_date or '',
            filter_resource_type=resource_type or '',
            filter_user_id=user_id or ''
        )
        
    except Exception as e:
        from flask import flash, redirect, url_for
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('bookings.list_bookings'))


# ============================================================
# Calendar Export Endpoints
# ============================================================

@bp.route('/<int:booking_id>/calendar', methods=['GET'])
@login_required
def export_calendar(booking_id):
    """
    Export booking as iCalendar (.ics) file.
    Can be imported into Google Calendar, Outlook, Apple Calendar, etc.
    
    Returns:
        .ics file download
        403: Unauthorized
        404: Booking not found
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only owner or admin can export
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Generate iCal content
        ical_content = calendar_service.generate_ical(booking, base_url=request.host_url.rstrip('/'))
        
        # Create response with appropriate headers
        filename = f"booking-{booking.id}-{booking.resource.name.replace(' ', '-')}.ics"
        response = Response(ical_content, mimetype='text/calendar')
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/calendar/google', methods=['GET'])
@login_required
def export_google_calendar(booking_id):
    """
    Get Google Calendar add event URL for this booking.
    
    Returns:
        Redirect to Google Calendar with pre-filled event data
        403: Unauthorized
        404: Booking not found
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only owner or admin can export
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Generate Google Calendar URL and redirect
        google_url = calendar_service.generate_google_calendar_url(booking)
        return redirect(google_url)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@bp.route('/<int:booking_id>/calendar/outlook', methods=['GET'])
@login_required
def export_outlook_calendar(booking_id):
    """
    Get Outlook.com calendar add event URL for this booking.
    
    Returns:
        Redirect to Outlook.com calendar with pre-filled event data
        403: Unauthorized
        404: Booking not found
    """
    try:
        booking = BookingDAL.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Only owner or admin can export
        if not current_user.is_admin() and booking.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Generate Outlook URL and redirect
        outlook_url = calendar_service.generate_outlook_url(booking)
        return redirect(outlook_url)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
