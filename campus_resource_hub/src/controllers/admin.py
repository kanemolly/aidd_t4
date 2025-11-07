"""
Admin blueprint - administrative functions and dashboard.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from src.models import User, Resource, Booking, Review
from src.extensions import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('admin', __name__)


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Admin dashboard with system statistics and visualizations."""
    try:
        # Get total counts
        total_users = db.session.query(User).count()
        total_resources = db.session.query(Resource).count()
        total_bookings = db.session.query(Booking).count()
        total_reviews = db.session.query(Review).count()
        
        # Get bookings per resource type
        bookings_by_type = db.session.query(
            Resource.resource_type,
            func.count(Booking.id).label('count')
        ).join(Booking, Booking.resource_id == Resource.id).group_by(
            Resource.resource_type
        ).all()
        
        # Format for chart
        chart_data = {
            'types': [item[0] for item in bookings_by_type],
            'counts': [item[1] for item in bookings_by_type]
        }
        
        # Get top 5 most booked resources
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
        
        return render_template(
            'admin/dashboard.html',
            total_users=total_users,
            total_resources=total_resources,
            total_bookings=total_bookings,
            total_reviews=total_reviews,
            chart_data=chart_data,
            top_bookings=top_bookings,
            enumerate=enumerate
        )
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({"error": "Failed to load dashboard"}), 500


@bp.route('/users', methods=['GET'])
def list_users():
    """List all users."""
    return jsonify({"message": "List users endpoint ready"}), 200


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
