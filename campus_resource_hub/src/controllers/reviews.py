"""
Reviews Blueprint - Rating and review functionality for campus resources
Handles: creating, editing, deleting reviews, and displaying averages
"""

from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, CSRFError
from src.models import Resource, Review, Booking
from src.extensions import db, csrf_protect
from src.data_access.review_dal import ReviewDAL
from src.data_access.resource_dal import ResourceDAL

# Create Blueprint
bp = Blueprint(
    'reviews',
    __name__,
    url_prefix='/reviews',
    template_folder='../views/templates'
)

# Initialize DAL
review_dal = ReviewDAL()
resource_dal = ResourceDAL()


# ==================== FLAGGED REVIEWS PAGE ====================

@bp.route('/flagged-page', methods=['GET'])
@login_required
def flagged_reviews_page():
    """
    Display the flagged reviews management page (staff/admin only).
    """
    # Check authorization
    if current_user.role not in ['staff', 'admin']:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    return render_template('reviews/flagged_reviews.html')


# ==================== CSRF VALIDATION HELPER ====================

def validate_json_csrf():
    """
    Validate CSRF token for JSON requests.
    Checks for token in X-CSRFToken header.
    Raises CSRFError if validation fails.
    """
    token = request.headers.get('X-CSRFToken')
    if not token:
        token = request.form.get('csrf_token')
    
    if not token:
        raise CSRFError('CSRF token is missing')
    
    try:
        validate_csrf(token)
    except CSRFError as e:
        raise CSRFError(f'CSRF validation failed: {str(e)}')


# ==================== CREATE / POST REVIEW ====================

@bp.route('', methods=['POST'])
@csrf_protect.exempt
@login_required
def create_review():
    """
    Create a new review for a resource.
    
    POST data:
    - resource_id (int): ID of resource being reviewed
    - rating (int): Rating 1-5
    - comment (str, optional): Review text
    
    Returns: JSON response
    """
    try:
        # Validate CSRF token for JSON request
        validate_json_csrf()
        
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        resource_id = data.get('resource_id')
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        title = data.get('title', '').strip() if data.get('title') else None
        
        if not resource_id:
            return jsonify({'status': 'error', 'message': 'Resource ID is required'}), 400
        
        if rating is None:
            return jsonify({'status': 'error', 'message': 'Rating is required'}), 400
        
        # Validate rating value
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                return jsonify({'status': 'error', 'message': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Rating must be a valid integer'}), 400
        
        # Validate resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        
        # Check comment length (max 2000 chars)
        if len(comment) > 2000:
            return jsonify({'status': 'error', 'message': 'Comment cannot exceed 2000 characters'}), 400
        
        # Check if user already reviewed this resource
        if review_dal.user_reviewed_resource(current_user.id, resource_id):
            return jsonify({'status': 'error', 'message': 'You have already reviewed this resource'}), 409
        
        # Create review
        try:
            review = review_dal.create_review(
                user_id=current_user.id,
                resource_id=resource_id,
                rating=rating,
                comment=comment if comment else None,
                title=title
            )
            
            return jsonify({
                'status': 'success',
                'message': 'Review posted successfully',
                'review': review.to_dict()
            }), 201
        
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error creating review: {str(e)}'}), 500
    
    except CSRFError as e:
        return jsonify({'status': 'error', 'message': 'CSRF token validation failed'}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


# ==================== GET REVIEWS ====================

@bp.route('/resource/<int:resource_id>', methods=['GET'])
def get_resource_reviews(resource_id):
    """
    Get all reviews for a specific resource.
    
    Query params:
    - limit: Number of reviews to return
    - offset: Number of reviews to skip
    - json: Return JSON (1) or HTML (0, default)
    
    Returns: JSON with reviews and average rating
    """
    try:
        # Verify resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        
        # Get pagination params
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get reviews
        reviews = review_dal.get_resource_reviews(resource_id, limit=limit, offset=offset)
        
        # Get stats
        stats = review_dal.get_review_stats(resource_id)
        
        # Get reviewer info for each review
        reviews_data = []
        for review in reviews:
            review_dict = review.to_dict()
            # Add reviewer name
            review_dict['reviewer_name'] = review.reviewer.full_name if review.reviewer else 'Anonymous'
            review_dict['reviewer_username'] = review.reviewer.username if review.reviewer else 'unknown'
            reviews_data.append(review_dict)
        
        return jsonify({
            'status': 'success',
            'reviews': reviews_data,
            'stats': stats,
            'count': len(reviews_data)
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error fetching reviews: {str(e)}'}), 500


# ==================== GET AVERAGE RATING ====================

@bp.route('/resource/<int:resource_id>/average', methods=['GET'])
def get_average_rating(resource_id):
    """
    Get average rating and stats for a resource.
    
    Returns: JSON with average_rating, total_reviews, distribution
    """
    try:
        # Verify resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        
        # Get stats
        stats = review_dal.get_review_stats(resource_id)
        
        return jsonify({
            'status': 'success',
            'average_rating': stats['average_rating'],
            'total_reviews': stats['total_reviews'],
            'distribution': stats['distribution']
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error fetching rating: {str(e)}'}), 500


# ==================== CHECK IF USER CAN REVIEW ====================

@bp.route('/can-review/<int:resource_id>', methods=['GET'])
@login_required
def can_review_resource(resource_id):
    """
    Check if current user can review a resource.
    User can review if:
    - They haven't already reviewed it
    - They have an active booking for it (optional check)
    
    Returns: JSON with can_review boolean
    """
    try:
        # Verify resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
        
        # Check if already reviewed
        already_reviewed = review_dal.user_reviewed_resource(current_user.id, resource_id)
        
        if already_reviewed:
            return jsonify({
                'status': 'success',
                'can_review': False,
                'reason': 'You have already reviewed this resource'
            }), 200
        
        return jsonify({
            'status': 'success',
            'can_review': True,
            'reason': 'You can review this resource'
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error checking review status: {str(e)}'}), 500


# ==================== UPDATE REVIEW ====================

@bp.route('/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    """
    Update an existing review (must be owner).
    
    PUT data:
    - rating (int, optional): New rating 1-5
    - comment (str, optional): New comment text
    
    Returns: JSON response
    """
    try:
        # Get review
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'status': 'error', 'message': 'Review not found'}), 404
        
        # Check authorization
        if review.reviewer_id != current_user.id and not current_user.is_admin():
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Build update dictionary
        update_data = {}
        
        # Update rating if provided
        if 'rating' in data:
            try:
                rating = int(data['rating'])
                if not (1 <= rating <= 5):
                    return jsonify({'status': 'error', 'message': 'Rating must be between 1 and 5'}), 400
                update_data['rating'] = rating
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': 'Rating must be a valid integer'}), 400
        
        # Update comment if provided
        if 'comment' in data:
            comment = data['comment'].strip() if data['comment'] else None
            if comment and len(comment) > 2000:
                return jsonify({'status': 'error', 'message': 'Comment cannot exceed 2000 characters'}), 400
            update_data['comment'] = comment
        
        # Update if there's data to update
        if not update_data:
            return jsonify({'status': 'error', 'message': 'No fields to update'}), 400
        
        try:
            updated_review = review_dal.update_review(review_id, **update_data)
            return jsonify({
                'status': 'success',
                'message': 'Review updated successfully',
                'review': updated_review.to_dict()
            }), 200
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error updating review: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


# ==================== DELETE REVIEW ====================

@bp.route('/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """
    Delete a review (must be owner, staff, or admin).
    
    Returns: JSON response
    """
    try:
        # Get review
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'status': 'error', 'message': 'Review not found'}), 404
        
        # Check authorization: owner, staff, or admin can delete
        is_owner = review.reviewer_id == current_user.id
        is_staff_or_admin = current_user.role in ['staff', 'admin']
        
        if not (is_owner or is_staff_or_admin):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Delete review
        try:
            success = review_dal.delete_review(review_id)
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Review deleted successfully'
                }), 200
            else:
                return jsonify({'status': 'error', 'message': 'Review not found'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error deleting review: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


# ==================== FLAG / REPORT REVIEW ====================

@bp.route('/<int:review_id>/flag', methods=['POST'])
@login_required
def flag_review(review_id):
    """
    Flag a review for staff/admin attention.
    Students can flag inappropriate content.
    
    POST data:
    - reason (str): Reason for flagging
    
    Returns: JSON response
    """
    try:
        # Get review
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'status': 'error', 'message': 'Review not found'}), 404
        
        # Get flag reason
        data = request.get_json()
        reason = data.get('reason', 'No reason provided')
        
        # Parse existing flagged_by list
        import json
        flagged_by_list = []
        if review.flagged_by:
            try:
                flagged_by_list = json.loads(review.flagged_by)
            except:
                flagged_by_list = []
        
        # Check if user already flagged this review
        if current_user.id in flagged_by_list:
            return jsonify({
                'status': 'error',
                'message': 'You have already flagged this review'
            }), 400
        
        # Add user to flagged_by list
        flagged_by_list.append(current_user.id)
        review.flagged_by = json.dumps(flagged_by_list)
        
        # Update flag information
        review.is_flagged = True
        review.flag_count = len(flagged_by_list)
        
        # Update or append flag reason
        from datetime import datetime
        if review.flag_reason:
            review.flag_reason += f"\n[{current_user.username} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]: {reason}"
        else:
            review.flag_reason = f"[{current_user.username} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]: {reason}"
            review.flagged_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Review flagged for staff review',
            'flag_count': review.flag_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


# ==================== GET FLAGGED REVIEWS (STAFF/ADMIN) ====================

@bp.route('/flagged', methods=['GET'])
@login_required
def get_flagged_reviews():
    """
    Get all flagged reviews (staff/admin only).
    
    Returns: JSON list of flagged reviews
    """
    try:
        # Check authorization
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Get all flagged reviews
        flagged_reviews = Review.query.filter_by(is_flagged=True).order_by(Review.flagged_at.desc()).all()
        
        # Convert to dict with additional info
        reviews_data = []
        for review in flagged_reviews:
            review_dict = review.to_dict()
            review_dict['reviewer_name'] = review.reviewer.username
            review_dict['resource_name'] = review.resource.name
            review_dict['flag_reason'] = review.flag_reason
            reviews_data.append(review_dict)
        
        return jsonify({
            'status': 'success',
            'reviews': reviews_data,
            'count': len(reviews_data)
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


# ==================== UNFLAG / DISMISS FLAG ====================

@bp.route('/<int:review_id>/unflag', methods=['POST'])
@login_required
def unflag_review(review_id):
    """
    Remove flag from a review (staff/admin only).
    
    Returns: JSON response
    """
    try:
        # Check authorization
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Get review
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'status': 'error', 'message': 'Review not found'}), 404
        
        # Clear flag
        review.is_flagged = False
        review.flag_count = 0
        review.flagged_by = None
        review.flag_reason = None
        review.flagged_at = None
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Flag removed successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500
