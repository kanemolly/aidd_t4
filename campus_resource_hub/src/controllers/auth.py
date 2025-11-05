"""
Authentication Blueprint
Handles user registration, login, logout, and session management.
Uses Flask-Login for session management and DAL for database operations.
"""

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
        role = request.form.get('role', 'student')
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
                    
                    # Redirect to next page or resources list
                    next_page = request.args.get('next')
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    return redirect(url_for('resources.list_resources'))
            
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
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
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip() or None
        
        if not full_name:
            flash('Full name is required.', 'error')
            return redirect(url_for('auth.edit_profile'))
        
        try:
            user = UserDAL.update_user(
                user_id=current_user.id,
                full_name=full_name,
                department=department
            )
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except SQLAlchemyError as e:
            flash('An error occurred while updating your profile.', 'error')
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


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return UserDAL.get_user_by_id(user_id)
