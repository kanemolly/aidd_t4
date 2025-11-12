"""
Authentication Blueprint
Handles user registration, login, logout, and session management.
Uses Flask-Login for session management and DAL for database operations.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from src.extensions import login_manager
from src.data_access import UserDAL
from src.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../views/templates')

# Alias for compatibility with app.py
bp = auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('resources.list_resources'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        # Public registration always creates student accounts
        # Staff and Admin accounts must be created by existing admins
        role = User.ROLE_STUDENT
        department = request.form.get('department', '').strip() or None
        
        # Validation
        if not all([username, email, full_name, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))
        
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            # Check if user already exists
            existing_user = UserDAL.get_user_by_username(username)
            if existing_user:
                flash('Username already taken. Please choose another.', 'error')
                return redirect(url_for('auth.register'))
            
            existing_email = UserDAL.get_user_by_email(email)
            if existing_email:
                flash('Email already registered. Please login or use another email.', 'error')
                return redirect(url_for('auth.register'))
            
            # Create new user
            user = UserDAL.create_user(
                username=username,
                email=email,
                full_name=full_name,
                password=password,
                role=role,
                department=department
            )
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        except SQLAlchemyError as e:
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login to user account."""
    if current_user.is_authenticated:
        return redirect(url_for('resources.list_resources'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('auth.login'))
        
        try:
            from src.extensions import db
            from src.models import User
            from sqlalchemy import text
            
            # Get user by username
            db.session.rollback()
            result = db.session.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username}
            ).fetchone()
            
            user = None
            if result:
                user = db.session.query(User).filter(User.id == result[0]).first()
            
            if user:
                pwd_check = user.check_password(password)
                
                if pwd_check:
                    if not user.is_active:
                        flash('Your account has been deactivated. Please contact support.', 'error')
                        return redirect(url_for('auth.login'))
                    
                    login_user(user, remember=remember)
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    
                    # Redirect to next page or role-appropriate landing page
                    next_page = request.args.get('next')
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    
                    # Admins and staff go to unified admin dashboard, students to resources
                    if user.is_admin() or user.is_staff():
                        return redirect(url_for('admin.dashboard'))
                    return redirect(url_for('resources.list_resources'))
            
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            import traceback
            print(f"LOGIN ERROR: {str(e)}")
            print(traceback.format_exc())
            flash(f'An error occurred during login: {str(e)}', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user."""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile."""
    from src.extensions import db
    from sqlalchemy import text
    
    # Debug: Check what's in the database
    result = db.session.execute(
        text("SELECT id, username, profile_image FROM users WHERE id = :user_id"),
        {"user_id": current_user.id}
    ).fetchone()
    print(f"[PROFILE VIEW] Database has for user {current_user.id}: profile_image = {result[2] if result else 'None'}")
    
    # Refresh current_user to get latest data from database
    db.session.expire_all()
    db.session.refresh(current_user)
    
    print(f"[PROFILE VIEW] current_user.profile_image after refresh: {current_user.profile_image}")
    
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip() or None
        year_in_school = request.form.get('year_in_school', '').strip() or None
        major = request.form.get('major', '').strip() or None
        
        if not full_name:
            flash('Full name is required.', 'error')
            return redirect(url_for('auth.edit_profile'))
        
        try:
            user = UserDAL.update_user(
                user_id=current_user.id,
                full_name=full_name,
                department=department,
                year_in_school=year_in_school,
                major=major
            )
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            # Log the actual error for debugging
            print(f"Error updating profile: {type(e).__name__}: {str(e)}")
            flash(f'An error occurred while updating your profile: {str(e)}', 'error')
            return redirect(url_for('auth.edit_profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('auth.change_password'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('auth.change_password'))
        
        if current_password == new_password:
            flash('New password must be different from current password.', 'error')
            return redirect(url_for('auth.change_password'))
        
        try:
            UserDAL.update_user_password(
                user_id=current_user.id,
                new_password=new_password
            )
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except SQLAlchemyError as e:
            flash('An error occurred while changing your password.', 'error')
            return redirect(url_for('auth.change_password'))
    
    return render_template('auth/change_password.html')


@auth_bp.route('/profile/picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload profile picture."""
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    # CSRF is automatically validated by Flask-WTF for POST requests
    
    if 'profile_picture' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('auth.profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    filename = secure_filename(file.filename)
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image.', 'error')
        return redirect(url_for('auth.profile'))
    
    # Validate file size (5MB max)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > 5 * 1024 * 1024:  # 5MB in bytes
        flash('File too large. Maximum size is 5MB.', 'error')
        return redirect(url_for('auth.profile'))
    file.seek(0)  # Reset file pointer
    
    try:
        # Get the absolute path to the static folder
        static_folder = current_app.static_folder
        upload_folder = os.path.join(static_folder, 'uploads', 'profiles')
        
        print(f"[PROFILE PIC UPLOAD] Current working directory: {os.getcwd()}")
        print(f"[PROFILE PIC UPLOAD] App root path: {current_app.root_path}")
        print(f"[PROFILE PIC UPLOAD] Static folder: {static_folder}")
        print(f"[PROFILE PIC UPLOAD] Upload folder: {upload_folder}")
        print(f"[PROFILE PIC UPLOAD] Upload folder exists: {os.path.exists(upload_folder)}")
        
        # Create uploads directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        print(f"[PROFILE PIC UPLOAD] Upload folder created/verified")
        
        # Generate unique filename
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
        filepath = os.path.join(upload_folder, new_filename)
        
        print(f"[PROFILE PIC UPLOAD] Full file path: {filepath}")
        print(f"[PROFILE PIC UPLOAD] File path is absolute: {os.path.isabs(filepath)}")
        
        # Save file
        file.save(filepath)
        print(f"[PROFILE PIC UPLOAD] File.save() completed")
        
        # Verify file was saved
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"[PROFILE PIC UPLOAD] ✓ File saved successfully! Size: {file_size} bytes")
            print(f"[PROFILE PIC UPLOAD] ✓ File exists at: {filepath}")
        else:
            print(f"[PROFILE PIC UPLOAD] ✗ File NOT found at: {filepath}")
            raise Exception("File was not saved to disk")
        
        # Update user profile (store relative path from static folder)
        profile_image_path = f"uploads/profiles/{new_filename}"
        print(f"[PROFILE PIC UPLOAD] Updating user {current_user.id} with path: {profile_image_path}")
        
        from src.extensions import db
        
        try:
            # Update via DAL
            updated_user = UserDAL.update_user(user_id=current_user.id, profile_image=profile_image_path)
            print(f"[PROFILE PIC UPLOAD] UserDAL.update_user returned successfully")
            print(f"[PROFILE PIC UPLOAD] Updated user profile_image in DB: {updated_user.profile_image}")
            
            # Force commit to ensure changes are saved
            db.session.commit()
            print(f"[PROFILE PIC UPLOAD] Session committed")
            
            # Verify in database
            from sqlalchemy import text
            result = db.session.execute(
                text("SELECT profile_image FROM users WHERE id = :user_id"),
                {"user_id": current_user.id}
            ).fetchone()
            print(f"[PROFILE PIC UPLOAD] Direct DB query result: {result[0] if result else 'None'}")
            
        except Exception as dal_error:
            print(f"[PROFILE PIC UPLOAD ERROR] UserDAL.update_user failed: {dal_error}")
            import traceback
            traceback.print_exc()
            raise
        
        flash('Profile picture updated successfully! Refresh the page to see your new picture.', 'success')
        return redirect(url_for('auth.profile'))
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[PROFILE PIC UPLOAD ERROR] {type(e).__name__}: {str(e)}")
        print(error_trace)
        flash(f'An error occurred while uploading your picture. Please try again.', 'error')
        return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Manage user preferences for personalized recommendations."""
    import json
    
    if request.method == 'POST':
        # Get form data - handle checkboxes (getlist) and custom inputs
        interests = request.form.getlist('interests')
        interests_custom = request.form.get('interests_custom', '').strip()
        if interests_custom:
            interests.extend([i.strip() for i in interests_custom.split(',') if i.strip()])
        
        # Study environment - multiple selections
        study_envs = request.form.getlist('study_environment')
        study_times = request.form.getlist('study_time')
        group_sizes = request.form.getlist('group_size')
        
        study_preferences = {}
        if study_envs:
            study_preferences['environment'] = study_envs
        if study_times:
            study_preferences['time'] = study_times
        if group_sizes:
            study_preferences['group_size'] = group_sizes
        
        accessibility_raw = request.form.getlist('accessibility_needs')
        accessibility_needs = [a for a in accessibility_raw if a]
        
        # Preferred locations - checkboxes + custom
        preferred_locations = request.form.getlist('preferred_locations')
        locations_custom = request.form.get('preferred_locations_custom', '').strip()
        if locations_custom:
            preferred_locations.extend([l.strip() for l in locations_custom.split(',') if l.strip()])
        
        try:
            UserDAL.update_preferences(
                user_id=current_user.id,
                interests=interests,
                study_preferences=study_preferences,
                accessibility_needs=accessibility_needs,
                preferred_locations=preferred_locations
            )
            flash('Preferences updated successfully! The chatbot will use these to personalize recommendations.', 'success')
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            flash('An error occurred while updating preferences.', 'error')
            return redirect(url_for('auth.preferences'))
    
    # GET request - show preferences form
    try:
        prefs = UserDAL.get_user_preferences(current_user.id)
        return render_template('auth/preferences.html', user=current_user, prefs=prefs)
    except Exception:
        return render_template('auth/preferences.html', user=current_user, prefs={})


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return UserDAL.get_user_by_id(user_id)
