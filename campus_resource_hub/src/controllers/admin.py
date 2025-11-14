"""
Admin blueprint - administrative functions and dashboard.
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from src.models import User, Resource, Booking, Review
from src.extensions import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Unified admin dashboard with bookings, analytics, and moderation."""
    try:
        # Check admin or staff permission
        if not (current_user.is_admin() or current_user.is_staff()):
            return jsonify({"error": "Unauthorized"}), 403
        
        from datetime import datetime, timedelta
        from src.data_access.booking_dal import BookingDAL
        
        now = datetime.now()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # ============= ACTION ITEMS: PENDING BOOKINGS =============
        # Get all pending bookings (needs attention first)
        all_pending_bookings = db.session.query(Booking).filter(
            Booking.status == 'pending'
        ).order_by(Booking.created_at.asc()).all()
        
        # Pending bookings requiring approval (only those for resources with approval required)
        pending_for_approval = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            and_(
                Booking.status == 'pending',
                Resource.requires_approval == True
            )
        ).count()
        
        # Currently active bookings
        active_bookings = db.session.query(Booking).filter(
            Booking.status == 'confirmed',
            Booking.start_time <= now,
            Booking.end_time >= now
        ).order_by(Booking.start_time).all()
        
        # Upcoming today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        upcoming_today = db.session.query(Booking).filter(
            Booking.status == 'confirmed',
            Booking.start_time > now,
            Booking.start_time < today_end
        ).order_by(Booking.start_time).limit(5).all()
        
        # ============= BASIC METRICS =============
        total_users = db.session.query(User).count()
        total_resources = db.session.query(Resource).count()
        total_bookings = db.session.query(Booking).count()
        total_reviews = db.session.query(Review).count()
        
        # ============= ENGAGEMENT METRICS =============
        # Active users (users with bookings in last 30 days)
        active_users = db.session.query(User).join(
            Booking, Booking.user_id == User.id
        ).filter(Booking.created_at >= thirty_days_ago).distinct().count()
        
        # Average bookings per resource
        avg_bookings_per_resource = total_bookings / total_resources if total_resources > 0 else 0
        
        # Average rating (reviews)
        avg_rating = db.session.query(func.avg(Review.rating)).scalar()
        if avg_rating:
            avg_rating = round(float(avg_rating), 1)
        else:
            avg_rating = 0
        
        # Flagged reviews count
        flagged_reviews_count = db.session.query(Review).filter(Review.is_flagged == True).count()
        
        # ============= BOOKING STATUS BREAKDOWN =============
        booking_statuses = db.session.query(
            Booking.status,
            func.count(Booking.id).label('count')
        ).group_by(Booking.status).all()
        
        status_breakdown = {item[0]: item[1] for item in booking_statuses}
        
        # ============= BOOKINGS PER RESOURCE TYPE =============
        bookings_by_type = db.session.query(
            Resource.resource_type,
            func.count(Booking.id).label('count')
        ).outerjoin(Booking, Booking.resource_id == Resource.id).group_by(
            Resource.resource_type
        ).all()
        
        chart_data = {
            'types': [item[0] for item in bookings_by_type],
            'counts': [item[1] for item in bookings_by_type]
        }
        
        # ============= TOP 5 MOST BOOKED RESOURCES =============
        top_resources = db.session.query(
            Resource.id,
            Resource.name,
            Resource.resource_type,
            func.count(Booking.id).label('booking_count')
        ).outerjoin(Booking, Booking.resource_id == Resource.id).group_by(
            Resource.id
        ).order_by(func.count(Booking.id).desc()).limit(5).all()
        
        top_bookings = [
            {
                'id': r[0],
                'name': r[1],
                'type': r[2],
                'bookings': r[3] or 0
            }
            for r in top_resources
        ]
        
        # ============= RESOURCE UTILIZATION RATES =============
        # Resources with most reviews
        top_reviewed_resources = db.session.query(
            Resource.id,
            Resource.name,
            func.count(Review.id).label('review_count'),
            func.avg(Review.rating).label('avg_rating')
        ).outerjoin(Review, Review.resource_id == Resource.id).group_by(
            Resource.id
        ).order_by(func.count(Review.id).desc()).limit(5).all()
        
        top_reviewed = [
            {
                'id': r[0],
                'name': r[1],
                'reviews': r[2] or 0,
                'avg_rating': round(float(r[3]), 1) if r[3] else 0
            }
            for r in top_reviewed_resources
        ]
        
        # ============= RECENT FLAGGED REVIEWS =============
        recent_flagged_reviews = db.session.query(Review).filter(
            Review.is_flagged == True
        ).order_by(Review.flagged_at.desc()).limit(5).all()
        
        flagged_reviews_list = []
        for review in recent_flagged_reviews:
            flagged_reviews_list.append({
                'id': review.id,
                'reviewer_name': review.reviewer.full_name or review.reviewer.username,
                'resource_name': review.resource.name,
                'comment_preview': review.comment[:50] + ('...' if len(review.comment) > 50 else ''),
                'flag_count': review.flag_count,
                'reason': review.flag_reason[:100] if review.flag_reason else 'No reason specified',
                'flagged_at': review.flagged_at.strftime('%m/%d/%Y') if review.flagged_at else 'N/A'
            })
        
        # ============= WEEKLY BOOKING TREND =============
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        weekly_bookings = db.session.query(
            func.date(Booking.created_at).label('date'),
            func.count(Booking.id).label('count')
        ).filter(Booking.created_at >= seven_days_ago).group_by(
            func.date(Booking.created_at)
        ).order_by(func.date(Booking.created_at)).all()
        
        weekly_trend = {
            'dates': [str(item[0]) for item in weekly_bookings],
            'counts': [item[1] for item in weekly_bookings]
        }
        
        # ============= USER GROWTH (last 30 days) =============
        users_last_30_days = db.session.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # ============= CALCULATE KPIs =============
        # Utilization rate (confirmed + completed vs pending + cancelled)
        confirmed_bookings = status_breakdown.get('confirmed', 0)
        completed_bookings = status_breakdown.get('completed', 0)
        pending_bookings_count = status_breakdown.get('pending', 0)
        cancelled_bookings = status_breakdown.get('cancelled', 0)
        
        total_confirmed_completed = confirmed_bookings + completed_bookings
        utilization_rate = (total_confirmed_completed / total_bookings * 100) if total_bookings > 0 else 0
        
        return render_template(
            'admin/dashboard.html',
            # Pending bookings (action items - shown first)
            pending_bookings=all_pending_bookings[:15],  # Show top 15 oldest
            active_bookings=active_bookings,
            upcoming_today=upcoming_today,
            action_counts={
                'pending': len(all_pending_bookings),
                'active_now': len(active_bookings),
                'upcoming_today': len(upcoming_today),
            },
            now=now,
            
            # Basic metrics
            total_users=total_users,
            total_resources=total_resources,
            total_bookings=total_bookings,
            total_reviews=total_reviews,
            
            # Engagement metrics
            active_users=active_users,
            avg_bookings_per_resource=round(avg_bookings_per_resource, 1),
            avg_rating=avg_rating,
            users_last_30_days=users_last_30_days,
            
            # Status breakdown
            status_breakdown=status_breakdown,
            confirmed_bookings=confirmed_bookings,
            completed_bookings=completed_bookings,
            pending_bookings_count=pending_bookings_count,
            cancelled_bookings=cancelled_bookings,
            utilization_rate=round(utilization_rate, 1),
            
            # Charts and data
            chart_data=chart_data,
            top_bookings=top_bookings,
            top_reviewed=top_reviewed,
            weekly_trend=weekly_trend,
            
            # Moderation
            flagged_reviews_count=flagged_reviews_count,
            flagged_reviews_list=flagged_reviews_list,
            pending_for_approval=pending_for_approval,
            recent_flagged_reviews=recent_flagged_reviews,
            
            # Template helpers
            enumerate=enumerate
        )
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to load dashboard"}), 500


@bp.route('/bookings/pending', methods=['GET'])
@login_required
def pending_bookings():
    """
    Admin page to view and approve pending bookings.
    Shows only bookings for resources that require approval.
    """
    try:
        from src.data_access.booking_dal import BookingDAL
        
        # Check admin or staff permission
        if not (current_user.is_admin() or current_user.is_staff()):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get all pending bookings for resources that require approval
        pending_bookings = db.session.query(Booking).join(
            Resource, Booking.resource_id == Resource.id
        ).filter(
            and_(
                Booking.status == Booking.STATUS_PENDING,
                Resource.requires_approval == True
            )
        ).order_by(Booking.created_at.desc()).all()
        
        return render_template(
            'admin/pending_bookings.html',
            bookings=pending_bookings
        )
    except Exception as e:
        return jsonify({'error': f'Failed to load pending bookings: {str(e)}'}), 500


@bp.route('/users', methods=['GET'])
def list_users():
    """List all users."""
    return jsonify({"message": "List users endpoint ready"}), 200


@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Admin-only: Create new staff or admin accounts."""
    if not current_user.is_admin():
        flash('Unauthorized access.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        from src.data_access.user_dal import UserDAL
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')
        department = request.form.get('department', '').strip() or None
        
        # Validation
        if not all([username, email, full_name, password, role]):
            flash('All required fields must be filled.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if role not in ['student', 'staff', 'admin']:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('admin.create_user'))
        
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('admin.create_user'))
        
        try:
            # Check if user already exists
            existing_user = UserDAL.get_user_by_username(username)
            if existing_user:
                flash('Username already taken. Please choose another.', 'error')
                return redirect(url_for('admin.create_user'))
            
            existing_email = UserDAL.get_user_by_email(email)
            if existing_email:
                flash('Email already registered. Please use another email.', 'error')
                return redirect(url_for('admin.create_user'))
            
            # Create new user
            user = UserDAL.create_user(
                username=username,
                email=email,
                full_name=full_name,
                password=password,
                role=role,
                department=department
            )
            
            flash(f'{role.capitalize()} account created successfully! Username: {user.username}', 'success')
            return redirect(url_for('admin.dashboard'))
        
        except Exception as e:
            flash(f'Error creating account: {str(e)}', 'error')
            return redirect(url_for('admin.create_user'))
    
    # GET request - show form
    return render_template('admin/create_user.html')


@bp.route('/summary_report', methods=['GET', 'POST'])
@login_required
def summary_report():
    """Generate and display summary report with weekly bookings and top resources."""
    try:
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get weekly bookings aggregated by day
        weekly_bookings = db.session.query(
            func.date(Booking.created_at).label('date'),
            func.count(Booking.id).label('count')
        ).filter(
            and_(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        ).group_by(
            func.date(Booking.created_at)
        ).order_by(
            func.date(Booking.created_at)
        ).all()
        
        # Format for chart
        daily_data = {
            'dates': [str(item[0]) for item in weekly_bookings],
            'counts': [item[1] for item in weekly_bookings]
        }
        
        # Get top 5 resources by bookings
        top_5_resources = db.session.query(
            Resource.id,
            Resource.name,
            Resource.resource_type,
            func.count(Booking.id).label('booking_count')
        ).outerjoin(Booking, Booking.resource_id == Resource.id).group_by(
            Resource.id
        ).order_by(func.count(Booking.id).desc()).limit(5).all()
        
        # Format top resources
        top_resources_data = [
            {
                'rank': idx + 1,
                'name': r[1],
                'type': r[2],
                'bookings': r[3] or 0
            }
            for idx, r in enumerate(top_5_resources)
        ]
        
        # Generate markdown report
        report_content = generate_markdown_report(
            start_date,
            end_date,
            daily_data,
            top_resources_data
        )
        
        # Save report to file
        reports_dir = os.path.join(
            os.path.dirname(__file__),
            '../../static/reports'
        )
        os.makedirs(reports_dir, exist_ok=True)
        
        report_filename = f"summary_{end_date.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Get system totals
        total_users = db.session.query(User).count()
        total_resources = db.session.query(Resource).count()
        total_bookings = db.session.query(Booking).count()
        total_reviews = db.session.query(Review).count()
        
        # Weekly stats
        weekly_total = sum([item[1] for item in weekly_bookings])
        
        return render_template(
            'admin/summary_report.html',
            report_content=report_content,
            daily_data=daily_data,
            top_resources=top_resources_data,
            report_date=end_date,
            start_date=start_date,
            weekly_total=weekly_total,
            total_users=total_users,
            total_resources=total_resources,
            total_bookings=total_bookings,
            total_reviews=total_reviews,
            enumerate=enumerate,
            json=json
        )
    except Exception as e:
        print(f"Summary report error: {e}")
        return jsonify({"error": "Failed to generate report"}), 500


def generate_markdown_report(start_date, end_date, daily_data, top_resources):
    """Generate markdown formatted report."""
    
    week_start = start_date.strftime('%B %d, %Y')
    week_end = end_date.strftime('%B %d, %Y')
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build markdown report
    md_content = f"""# Campus Resource Hub - Weekly Summary Report

**Report Period:** {week_start} to {week_end}  
**Generated:** {generated_at}

---

## 📊 Weekly Bookings Overview

### Daily Bookings Trend

| Date | Bookings |
|------|----------|
"""
    
    # Add daily data rows
    for date, count in zip(daily_data['dates'], daily_data['counts']):
        md_content += f"| {date} | {count} |\n"
    
    # Add summary stats
    total_weekly = sum(daily_data['counts'])
    avg_daily = total_weekly / len(daily_data['dates']) if daily_data['dates'] else 0
    
    md_content += f"""

**Total Weekly Bookings:** {total_weekly}  
**Average Daily Bookings:** {avg_daily:.1f}

---

## 🏆 Top 5 Most Booked Resources

| Rank | Resource Name | Type | Bookings |
|------|---------------|------|----------|
"""
    
    # Add top resources
    for resource in top_resources:
        md_content += f"| #{resource['rank']} | {resource['name']} | {resource['type']} | {resource['bookings']} |\n"
    
    # Add footer with key insights
    md_content += """

---

## 📈 Key Insights

- **Peak Usage:** Review the daily trend above to identify peak usage times
- **Resource Allocation:** Focus on the top 5 resources for maintenance and improvements
- **Trend Analysis:** Use weekly data to plan resource expansion or optimization

---

*This report is automatically generated. For more details, visit the Admin Dashboard.*
"""
    
    return md_content



@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    return jsonify({"message": f"Delete user {user_id} endpoint ready"}), 204


@bp.route('/users/<int:user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """Update user role."""
    return jsonify({"message": f"Update user {user_id} role endpoint ready"}), 200


@bp.route('/statistics', methods=['GET'])
def statistics():
    """Get system statistics."""
    return jsonify({"message": "System statistics endpoint ready"}), 200


@bp.route('/logs', methods=['GET'])
def view_logs():
    """View system logs."""
    return jsonify({"message": "View logs endpoint ready"}), 200


@bp.route('/settings', methods=['GET', 'PUT'])
def settings():
    """Get or update system settings."""
    if request.method == 'GET':
        return jsonify({"message": "Get settings endpoint ready"}), 200
    return jsonify({"message": "Update settings endpoint ready"}), 200
