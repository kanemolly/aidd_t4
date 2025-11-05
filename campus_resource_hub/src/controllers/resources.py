"""
Resources Blueprint - CRUD operations and search functionality for campus resources
Handles: listing, searching, creating, editing, deleting resources
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models import Resource, User
from src.extensions import db
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL
from werkzeug.utils import secure_filename
import os
from datetime import datetime

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
    - resource_type: filter by type
    - location: filter by location
    - page: pagination (default: 1)
    """
    try:
        # Get query parameters
        keyword = request.args.get('keyword', '').strip()
        resource_type = request.args.get('resource_type', '').strip()
        location = request.args.get('location', '').strip()
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
            all_resources = [r for r in all_resources if r.location == location]
        
        total = len(all_resources)
        resources = all_resources[offset:offset + per_page]
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        # Get unique types and locations for filters
        all_published = Resource.query.filter_by(status='published').all()
        types = sorted(set(r.resource_type for r in all_published if r.resource_type))
        locations = sorted(set(r.location for r in all_published if r.location))
        
        return render_template(
            'resources/list.html',
            resources=resources,
            keyword=keyword,
            resource_type=resource_type,
            location=location,
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
        print(f'Error loading resources: {str(e)}')
        flash(f'Error loading resources', 'error')
        return render_template(
            'resources/list.html',
            resources=[],
            keyword='',
            resource_type='',
            location='',
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
        
        # Get owner information
        owner = User.query.get(resource.creator_id)
        
        # Check if current user is owner or admin
        is_owner = current_user.is_authenticated and current_user.id == resource.creator_id
        is_admin = current_user.is_authenticated and current_user.is_admin
        
        return render_template(
            'resources/detail.html',
            resource=resource,
            owner=owner,
            is_owner=is_owner,
            is_admin=is_admin
        )
    
    except Exception as e:
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
    """
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
