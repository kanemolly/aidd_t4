"""
Resources Blueprint - CRUD operations and search functionality for campus resources
Handles: listing, searching, creating, editing, deleting resources
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models import Resource, User, Booking, Review
from src.extensions import db
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL
from src.data_access.booking_dal import BookingDAL
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

# Create Blueprint
bp = Blueprint(
    'resources',
    __name__,
    url_prefix='/resources',
    template_folder='../views/templates'
)

# Initialize DAL
resource_dal = ResourceDAL()
user_dal = UserDAL()

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_personalized_recommendations(user):
    """
    Generate personalized resource recommendations based on:
    - User's previous bookings (book again, same location, similar type)
    - User preferences (preferred locations, interests)
    - Available resources at preferred locations
    
    Returns a list of up to 5 recommended resources
    """
    recommendations = []
    recommended_ids = set()
    
    if not user:
        return []
    
    try:
        # 1. Get user's booking history
        user_bookings = BookingDAL.get_bookings_by_user(user.id, limit=50)
        booked_resource_ids = set()
        booked_locations = {}  # resource_type -> location mapping
        booked_types = set()
        
        for booking in user_bookings:
            if booking.resource:
                booked_resource_ids.add(booking.resource_id)
                booked_types.add(booking.resource.resource_type)
                if booking.resource.location:
                    if booking.resource.resource_type not in booked_locations:
                        booked_locations[booking.resource.resource_type] = []
                    booked_locations[booking.resource.resource_type].append(booking.resource.location)
        
        # Parse user preferences
        preferred_locations = []
        if user.preferred_locations:
            try:
                preferred_locations = json.loads(user.preferred_locations)
            except:
                pass
        
        # Get all published resources
        all_resources = Resource.query.filter_by(status='published').all()
        
        # Strategy 1: "Book Again" - same resource they've booked before
        if booked_resource_ids:
            for resource in all_resources:
                if resource.id in booked_resource_ids and resource.id not in recommended_ids and len(recommendations) < 5:
                    recommendations.append({
                        'resource': resource,
                        'reason': f'📌 Book Again - You\'ve used this before'
                    })
                    recommended_ids.add(resource.id)
        
        # Strategy 2: Same location as previous bookings
        if booked_locations and not preferred_locations:
            # Get most common location from bookings
            all_booked_locations = []
            for locs in booked_locations.values():
                all_booked_locations.extend(locs)
            
            if all_booked_locations:
                common_location = max(set(all_booked_locations), key=all_booked_locations.count)
                for resource in all_resources:
                    if (resource.location == common_location and 
                        resource.id not in recommended_ids and 
                        resource.id not in booked_resource_ids and 
                        len(recommendations) < 5):
                        recommendations.append({
                            'resource': resource,
                            'reason': f'📍 At {common_location} - Your frequent location'
                        })
                        recommended_ids.add(resource.id)
        
        # Strategy 3: User's preferred locations
        if preferred_locations:
            for resource in all_resources:
                if (resource.location in preferred_locations and 
                    resource.id not in recommended_ids and 
                    len(recommendations) < 5):
                    recommendations.append({
                        'resource': resource,
                        'reason': f'⭐ At {resource.location} - Your preferred location'
                    })
                    recommended_ids.add(resource.id)
        
        # Strategy 4: Similar resource type to previous bookings
        if booked_types:
            for resource in all_resources:
                if (resource.resource_type in booked_types and 
                    resource.id not in recommended_ids and 
                    resource.id not in booked_resource_ids and 
                    len(recommendations) < 5):
                    recommendations.append({
                        'resource': resource,
                        'reason': f'🏷️ {resource.resource_type} - Similar to your bookings'
                    })
                    recommended_ids.add(resource.id)
        
        # Strategy 5: Popular resources (highly booked)
        if len(recommendations) < 5:
            resource_booking_count = {}
            for resource in all_resources:
                count = db.session.query(Booking).filter_by(resource_id=resource.id).count()
                resource_booking_count[resource.id] = count
            
            popular = sorted(resource_booking_count.items(), key=lambda x: x[1], reverse=True)
            for resource_id, _ in popular[:10]:
                resource = Resource.query.get(resource_id)
                if (resource and resource.id not in recommended_ids and len(recommendations) < 5):
                    recommendations.append({
                        'resource': resource,
                        'reason': '⭐ Popular - Frequently booked'
                    })
                    recommended_ids.add(resource.id)
        
        return recommendations[:5]  # Return top 5 recommendations
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return []


def save_uploaded_file(file):
    """
    Save uploaded file and return the filename.
    Returns None if file is invalid.
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return None
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"resource_{timestamp}_{secure_filename(file.filename)}"
    
    # Save file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return filename


def delete_old_image(image_path):
    """Delete old image file if it exists."""
    if image_path:
        filepath = os.path.join(UPLOAD_FOLDER, image_path)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting old image: {e}")


# ==================== LIST & SEARCH ====================

@bp.route('', methods=['GET'])
def list_resources():
    """
    List all resources with search and filter capabilities
    Query parameters:
    - keyword: search in name/description
    - resource_type: filter by type (category)
    - location: filter by location
    - min_capacity: filter by minimum capacity
    - available_date: filter by availability date
    - sort: sort order (recent, most_booked, top_rated)
    - page: pagination (default: 1)
    """
    try:
        # Get query parameters
        keyword = request.args.get('keyword', '').strip()
        resource_type = request.args.get('resource_type', '').strip()
        location = request.args.get('location', '').strip()
        min_capacity = request.args.get('min_capacity', '').strip()
        available_date = request.args.get('available_date', '').strip()
        sort_by = request.args.get('sort', 'recent').strip()
        page = request.args.get('page', 1, type=int)
        
        # Pagination settings
        per_page = 12
        offset = (page - 1) * per_page
        
        # Get total count
        all_resources = Resource.query.filter_by(status='published').all()
        
        # Apply filters
        if keyword:
            all_resources = [r for r in all_resources if keyword.lower() in r.name.lower() or (r.description and keyword.lower() in r.description.lower())]
        
        if resource_type:
            all_resources = [r for r in all_resources if r.resource_type == resource_type]
        
        if location:
            # Match by simplified building name (with same normalization as dropdown)
            def extract_building_name(address):
                """Extract and normalize building name from full address"""
                if not address:
                    return None
                if ',' in address:
                    building = address.split(',')[0].strip()
                else:
                    import re
                    match = re.match(r'^([^\d]+)', address)
                    building = match.group(1).strip() if match else address.strip()
                
                # Apply same normalization as in dropdown generation
                if 'herman b wells library' in building.lower() or building.lower() == 'wells library':
                    return 'Wells Library'
                elif 'kelley school of business' in building.lower():
                    return 'Kelley School of Business'
                elif 'indiana memorial union' in building.lower() or building.lower() == 'imu':
                    return 'Indiana Memorial Union (IMU)'
                elif 'luddy hall' in building.lower():
                    return 'Luddy Hall'
                elif 'wright education' in building.lower():
                    return 'Wright Education Building'
                elif 'jacobs school of music' in building.lower():
                    return 'Jacobs School of Music'
                elif 'multidisciplinary science building' in building.lower() or 'msb' in building.lower():
                    return 'Multidisciplinary Science Building II'
                elif 'chemistry building' in building.lower():
                    return 'Chemistry Building'
                elif 'student center' in building.lower():
                    return 'Student Center'
                elif 'student recreational sports center' in building.lower() or 'srsc' in building.lower():
                    return 'Student Recreational Sports Center'
                else:
                    return building
            
            all_resources = [r for r in all_resources if r.location and extract_building_name(r.location) == location]
        
        # Filter by minimum capacity
        if min_capacity:
            try:
                min_cap = int(min_capacity)
                all_resources = [r for r in all_resources if r.capacity and r.capacity >= min_cap]
            except ValueError:
                pass
        
        # Filter by availability date (only show available resources)
        if available_date:
            try:
                # Parse the date
                from datetime import datetime as dt
                date_obj = dt.strptime(available_date, '%Y-%m-%d').date()
                # For now, just show available resources (can be enhanced with actual booking checks)
                all_resources = [r for r in all_resources if r.is_available]
            except ValueError:
                pass
        
        # Apply sorting
        if sort_by == 'most_booked':
            # Count bookings for each resource
            booking_counts = {}
            for resource in all_resources:
                count = db.session.query(Booking).filter_by(resource_id=resource.id, status='confirmed').count()
                booking_counts[resource.id] = count
            all_resources.sort(key=lambda r: booking_counts.get(r.id, 0), reverse=True)
        elif sort_by == 'top_rated':
            # Sort by average rating (if reviews exist)
            def get_avg_rating(resource):
                reviews = db.session.query(Review).filter_by(resource_id=resource.id).all()
                if not reviews:
                    return 0
                return sum(r.rating for r in reviews) / len(reviews)
            all_resources.sort(key=get_avg_rating, reverse=True)
        else:  # 'recent' or default
            # Sort by creation date, most recent first
            all_resources.sort(key=lambda r: r.created_at or dt.min, reverse=True)
        
        total = len(all_resources)
        resources = all_resources[offset:offset + per_page]
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        # Get unique types and locations for filters
        all_published = Resource.query.filter_by(status='published').all()
        types = sorted(set(r.resource_type for r in all_published if r.resource_type))
        
        # Extract simplified building names from full addresses
        def extract_building_name(address):
            """Extract and normalize building name from full address"""
            if not address:
                return None
            # Common patterns: "Building Name, Street Address" or just "Building Name"
            # Take everything before the first comma, or before numbers if no comma
            if ',' in address:
                building = address.split(',')[0].strip()
            else:
                # If no comma, take everything before the first digit
                import re
                match = re.match(r'^([^\d]+)', address)
                building = match.group(1).strip() if match else address.strip()
            
            # Normalize common building name variations
            # Wells Library variations
            if 'herman b wells library' in building.lower() or building.lower() == 'wells library':
                return 'Wells Library'
            # Kelley School variations
            elif 'kelley school of business' in building.lower():
                return 'Kelley School of Business'
            # Indiana Memorial Union variations
            elif 'indiana memorial union' in building.lower() or building.lower() == 'imu':
                return 'Indiana Memorial Union (IMU)'
            # Luddy Hall variations
            elif 'luddy hall' in building.lower():
                return 'Luddy Hall'
            # Wright Education variations
            elif 'wright education' in building.lower():
                return 'Wright Education Building'
            # Jacobs School of Music variations
            elif 'jacobs school of music' in building.lower():
                return 'Jacobs School of Music'
            # MSB-II variations
            elif 'multidisciplinary science building' in building.lower() or 'msb' in building.lower():
                return 'Multidisciplinary Science Building II'
            # Chemistry Building variations
            elif 'chemistry building' in building.lower():
                return 'Chemistry Building'
            # Student Center variations
            elif 'student center' in building.lower():
                return 'Student Center'
            # SRSC variations
            elif 'student recreational sports center' in building.lower() or 'srsc' in building.lower():
                return 'Student Recreational Sports Center'
            else:
                return building
        
        # Get unique simplified building names
        building_names = set()
        for r in all_published:
            if r.location:
                building = extract_building_name(r.location)
                if building:
                    building_names.add(building)
        locations = sorted(building_names)
        
        # Get personalized recommendations for authenticated users (only on first page, no filters)
        recommendations = []
        if current_user.is_authenticated and page == 1 and not keyword and not resource_type and not location:
            recommendations = get_personalized_recommendations(current_user)
        
        return render_template(
            'resources/list.html',
            resources=resources,
            recommendations=recommendations,
            keyword=keyword,
            resource_type=resource_type,
            location=location,
            min_capacity=min_capacity,
            available_date=available_date,
            sort_by=sort_by,
            types=types,
            locations=locations,
            page=page,
            total_pages=total_pages,
            total=total,
            has_prev=has_prev,
            has_next=has_next,
            per_page=per_page
        )
    
    except Exception as e:
        import traceback
        print(f'=== RESOURCES ERROR ===')
        print(f'Error loading resources: {str(e)}')
        traceback.print_exc()
        print(f'======================')
        flash(f'Error loading resources: {str(e)}', 'error')
        return render_template(
            'resources/list.html',
            resources=[],
            recommendations=[],
            keyword='',
            resource_type='',
            location='',
            min_capacity='',
            available_date='',
            sort_by='recent',
            types=[],
            locations=[],
            page=1,
            total_pages=1,
            total=0,
            has_prev=False,
            has_next=False,
            per_page=12
        )


# ==================== DETAIL ====================

@bp.route('/<int:resource_id>', methods=['GET'])
def detail_resource(resource_id):
    """
    Get detailed view of a single resource
    """
    try:
        resource = Resource.query.get(resource_id)
        
        if not resource:
            flash('Resource not found', 'warning')
            return redirect(url_for('resources.list_resources'))
        
        return render_template(
            'resources/detail.html',
            resource=resource
        )
    
    except Exception as e:
        print(f'DETAIL PAGE ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        flash(f'Error loading resource: {str(e)}', 'error')
        return redirect(url_for('resources.list_resources'))


# ==================== CREATE ====================

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    """
    Create a new resource
    GET: Show create form
    POST: Process form submission
    Only staff and admin users can create resources.
    """
    # Only staff and admin can create resources
    if not (current_user.is_staff() or current_user.is_admin()):
        flash('You do not have permission to create resources. Please contact staff or admin.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    try:
        if request.method == 'GET':
            return render_template('resources/form.html', resource=None, action='Create')
        
        # POST: Process form submission
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        resource_type = request.form.get('resource_type', '').strip()
        location = request.form.get('location', '').strip()
        capacity = request.form.get('capacity', '')
        is_available = request.form.get('is_available') == 'on'
        
        # Validation
        errors = []
        
        if not name or len(name) < 3:
            errors.append('Resource name must be at least 3 characters')
        
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters')
        
        if not resource_type:
            errors.append('Resource type is required')
        
        if not location:
            errors.append('Location is required')
        
        # Validate capacity if provided
        cap = None
        if capacity:
            try:
                cap = int(capacity)
                if cap < 1:
                    errors.append('Capacity must be at least 1')
            except (ValueError, TypeError):
                errors.append('Capacity must be a valid number')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                image_path = save_uploaded_file(file)
                if not image_path:
                    errors.append('Invalid image file. Only JPG, PNG, and WebP allowed. Max 5MB.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'resources/form.html',
                resource={
                    'name': name,
                    'description': description,
                    'resource_type': resource_type,
                    'location': location,
                    'capacity': capacity,
                    'is_available': is_available
                },
                action='Create'
            )
        
        # Create resource
        resource = Resource(
            name=name,
            description=description,
            resource_type=resource_type,
            location=location,
            capacity=cap,
            is_available=is_available,
            status='published',
            creator_id=current_user.id,
            image_path=image_path
        )
        
        db.session.add(resource)
        db.session.commit()
        
        flash(f'Resource "{name}" created successfully!', 'success')
        return redirect(url_for('resources.detail_resource', resource_id=resource.id))
    
    except Exception as e:
        flash(f'Error creating resource: {str(e)}', 'error')
        return render_template('resources/form.html', resource=None, action='Create')


# ==================== EDIT ====================

@bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    """
    Edit an existing resource
    GET: Show edit form
    POST: Process form submission
    """
    try:
        resource = Resource.query.get(resource_id)
        
        if not resource:
            flash('Resource not found', 'warning')
            return redirect(url_for('resources.list_resources'))
        
        # Check authorization
        if resource.creator_id != current_user.id and not current_user.is_admin:
            flash('You do not have permission to edit this resource', 'error')
            return redirect(url_for('resources.detail_resource', resource_id=resource_id))
        
        if request.method == 'GET':
            return render_template(
                'resources/form.html',
                resource=resource,
                action='Edit'
            )
        
        # POST: Process form submission
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        resource_type = request.form.get('resource_type', '').strip()
        location = request.form.get('location', '').strip()
        capacity = request.form.get('capacity', '')
        is_available = request.form.get('is_available') == 'on'
        
        # Validation
        errors = []
        
        if not name or len(name) < 3:
            errors.append('Resource name must be at least 3 characters')
        
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters')
        
        if not resource_type:
            errors.append('Resource type is required')
        
        if not location:
            errors.append('Location is required')
        
        # Validate capacity if provided
        cap = resource.capacity
        if capacity:
            try:
                cap = int(capacity)
                if cap < 0:
                    errors.append('Capacity cannot be negative')
            except (ValueError, TypeError):
                errors.append('Capacity must be a valid number')
        
        # Handle file upload
        image_path = resource.image_path
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                new_image_path = save_uploaded_file(file)
                if not new_image_path:
                    errors.append('Invalid image file. Only JPG, PNG, and WebP allowed. Max 5MB.')
                else:
                    # Delete old image if upload successful
                    delete_old_image(image_path)
                    image_path = new_image_path
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'resources/form.html',
                resource={
                    **resource.__dict__,
                    'name': name,
                    'description': description,
                    'resource_type': resource_type,
                    'location': location,
                    'capacity': capacity,
                    'is_available': is_available
                },
                action='Edit'
            )
        
        # Update resource
        resource.name = name
        resource.description = description
        resource.resource_type = resource_type
        resource.location = location
        resource.capacity = cap
        resource.is_available = is_available
        resource.image_path = image_path
        
        db.session.commit()
        flash(f'Resource "{name}" updated successfully!', 'success')
        return redirect(url_for('resources.detail_resource', resource_id=resource.id))
    
    except Exception as e:
        flash(f'Error updating resource: {str(e)}', 'error')
        return redirect(url_for('resources.list_resources'))


# ==================== DELETE ====================

@bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id):
    """
    Delete a resource (POST only to prevent accidental deletion)
    """
    try:
        resource = Resource.query.get(resource_id)
        
        if not resource:
            flash('Resource not found', 'warning')
            return redirect(url_for('resources.list_resources'))
        
        # Check authorization
        if resource.creator_id != current_user.id and not current_user.is_admin:
            flash('You do not have permission to delete this resource', 'error')
            return redirect(url_for('resources.detail_resource', resource_id=resource_id))
        
        resource_name = resource.name
        db.session.delete(resource)
        db.session.commit()
        
        flash(f'Resource "{resource_name}" deleted successfully!', 'success')
        return redirect(url_for('resources.list_resources'))
    
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}', 'error')
        return redirect(url_for('resources.detail_resource', resource_id=resource_id))


# ==================== HELPER ROUTES ====================

@bp.route('/type/<resource_type>')
def by_type(resource_type):
    """
    Filter resources by type
    """
    return redirect(url_for('resources.list_resources', resource_type=resource_type))


@bp.route('/location/<location>')
def by_location(location):
    """
    Filter resources by location
    """
    return redirect(url_for('resources.list_resources', location=location))


@bp.route('/api/search', methods=['GET'])
def api_search():
    """
    API endpoint for AJAX search (returns JSON)
    Used for real-time search suggestions
    """
    try:
        keyword = request.args.get('q', '').strip()
        resource_type = request.args.get('resource_type', '').strip()
        
        if not keyword or len(keyword) < 2:
            return jsonify({'results': []})
        
        query = Resource.query.filter_by(status='published')
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        resources = query.filter(
            (Resource.name.ilike(f'%{keyword}%')) |
            (Resource.description.ilike(f'%{keyword}%'))
        ).limit(10).all()
        
        return jsonify({
            'results': [
                {
                    'id': r.id,
                    'name': r.name,
                    'resource_type': r.resource_type,
                    'location': r.location
                }
                for r in resources
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
