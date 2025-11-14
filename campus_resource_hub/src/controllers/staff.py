"""
Staff blueprint - staff-specific dashboard and features.
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from src.models import User, Resource, Booking, Message, Review
from src.extensions import db
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

bp = Blueprint('staff', __name__, url_prefix='/staff')


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Staff dashboard with their resources, bookings, and messages."""
    try:
        # Check staff permission
        if not current_user.is_staff():
            flash('Unauthorized access.', 'error')
            return redirect(url_for('resources.list_resources'))
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # ============= MY RESOURCES =============
        # Get all resources created by this staff member
        my_resources = db.session.query(Resource).filter(
            Resource.creator_id == current_user.id
        ).order_by(Resource.created_at.desc()).all()
        
        # Count active resources
        active_resources_count = db.session.query(Resource).filter(
            and_(
                Resource.creator_id == current_user.id,
                Resource.is_available == True
            )
        ).count()
        
        # ============= BOOKINGS FOR MY RESOURCES =============
        # Get pending bookings for my resources that require approval
        pending_bookings = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            and_(
                Resource.creator_id == current_user.id,
                Booking.status == 'pending',
                Resource.requires_approval == True
            )
        ).order_by(Booking.created_at.desc()).limit(10).all()
        
        # Count total bookings for my resources (last 30 days)
        total_bookings_count = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            and_(
                Resource.creator_id == current_user.id,
                Booking.created_at >= thirty_days_ago
            )
        ).count()
        
        # Upcoming bookings for my resources
        upcoming_bookings = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            and_(
                Resource.creator_id == current_user.id,
                Booking.status == 'confirmed',
                Booking.start_time >= now
            )
        ).order_by(Booking.start_time.asc()).limit(10).all()
        
        # ============= MESSAGES ABOUT MY RESOURCES =============
        # Get recent messages where students are asking about my resources
        # This includes messages sent TO me
        recent_messages = db.session.query(Message).filter(
            Message.recipient_id == current_user.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Count unread messages
        unread_messages_count = db.session.query(Message).filter(
            and_(
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        ).count()
        
        # ============= REVIEWS FOR MY RESOURCES =============
        # Get recent reviews on my resources
        recent_reviews = db.session.query(Review).join(
            Resource, Review.resource_id == Resource.id
        ).filter(
            Resource.creator_id == current_user.id
        ).order_by(Review.created_at.desc()).limit(5).all()
        
        # Calculate average rating for my resources
        avg_rating = db.session.query(
            func.avg(Review.rating)
        ).join(
            Resource, Review.resource_id == Resource.id
        ).filter(
            Resource.creator_id == current_user.id
        ).scalar() or 0.0
        
        # ============= RESOURCE POPULARITY =============
        # Get most booked resources (last 30 days)
        popular_resources = db.session.query(
            Resource.id,
            Resource.name,
            func.count(Booking.id).label('booking_count')
        ).join(
            Booking, Resource.id == Booking.resource_id
        ).filter(
            and_(
                Resource.creator_id == current_user.id,
                Booking.created_at >= thirty_days_ago
            )
        ).group_by(
            Resource.id, Resource.name
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(5).all()
        
        return render_template(
            'staff/dashboard.html',
            my_resources=my_resources,
            active_resources_count=active_resources_count,
            pending_bookings=pending_bookings,
            total_bookings_count=total_bookings_count,
            upcoming_bookings=upcoming_bookings,
            recent_messages=recent_messages,
            unread_messages_count=unread_messages_count,
            recent_reviews=recent_reviews,
            avg_rating=round(avg_rating, 1),
            popular_resources=popular_resources
        )
        
    except Exception as e:
        import traceback
        print(f"STAFF DASHBOARD ERROR: {str(e)}")
        print(traceback.format_exc())
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('resources.list_resources'))


@bp.route('/resources', methods=['GET'])
@login_required
def my_resources():
    """View all resources created by this staff member."""
    if not current_user.is_staff():
        flash('Unauthorized access.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    try:
        my_resources = db.session.query(Resource).filter(
            Resource.creator_id == current_user.id
        ).order_by(Resource.created_at.desc()).all()
        
        return render_template(
            'staff/my_resources.html',
            resources=my_resources
        )
    except Exception as e:
        flash(f'Error loading resources: {str(e)}', 'error')
        return redirect(url_for('staff.dashboard'))


@bp.route('/bookings', methods=['GET'])
@login_required
def my_bookings():
    """View all bookings for my resources."""
    if not current_user.is_staff():
        flash('Unauthorized access.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        
        # Base query
        query = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            Resource.creator_id == current_user.id
        )
        
        # Apply status filter
        if status_filter != 'all':
            query = query.filter(Booking.status == status_filter)
        
        bookings = query.order_by(Booking.start_time.desc()).all()
        
        return render_template(
            'staff/my_bookings.html',
            bookings=bookings,
            status_filter=status_filter
        )
    except Exception as e:
        flash(f'Error loading bookings: {str(e)}', 'error')
        return redirect(url_for('staff.dashboard'))


@bp.route('/messages', methods=['GET'])
@login_required
def my_messages():
    """View messages related to my resources."""
    if not current_user.is_staff():
        flash('Unauthorized access.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    try:
        # Get all messages where I'm the recipient
        messages = db.session.query(Message).filter(
            Message.recipient_id == current_user.id
        ).order_by(Message.created_at.desc()).all()
        
        return render_template(
            'staff/my_messages.html',
            messages=messages
        )
    except Exception as e:
        flash(f'Error loading messages: {str(e)}', 'error')
        return redirect(url_for('staff.dashboard'))
