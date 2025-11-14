"""
Shared pytest fixtures for Campus Resource Hub tests.

This module provides reusable fixtures for:
- Test Flask app configuration
- Test database setup and teardown
- Sample users, resources, and bookings
- Authentication helpers
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Add project root and campus_resource_hub to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'campus_resource_hub')))

from src.extensions import db as _db
from src.models.models import User, Resource, Booking, Message, Notification
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL

# Enable foreign key constraints for SQLite (must be done before any connections)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite databases."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Import create_app function
def create_app():
    """Create Flask app instance for testing."""
    from flask import Flask
    from src.extensions import db, login_manager
    from src.controllers import auth, resources, bookings, admin, messages, concierge, reviews
    
    app = Flask(__name__,
                template_folder='src/views/templates',
                static_folder='src/views/static')
    
    # Test configuration
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SERVER_NAME': 'localhost.localdomain',
    })
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize CSRF protection with disabled enforcement for testing
    try:
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
    except ImportError:
        # If Flask-WTF not available, provide dummy csrf_token function
        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_token=lambda: '')
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(resources.bp)
    app.register_blueprint(bookings.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(concierge.bp)
    app.register_blueprint(reviews.bp)
    
    # Add application-level routes that exist in app.py
    @app.route('/')
    def home():
        """Home route - redirects to role-appropriate landing page."""
        from flask_login import current_user
        from flask import redirect, url_for
        # Redirect based on user role
        if current_user.is_authenticated:
            if current_user.is_admin() or current_user.is_staff():
                return redirect(url_for('bookings.dashboard'))
            return redirect(url_for('resources.list_resources'))
        # Not logged in - show resources
        return redirect(url_for('resources.list_resources'))
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {"status": "healthy"}, 200
    
    return app


@pytest.fixture(scope='function')
def app():
    """Create and configure a test Flask application instance."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'SERVER_NAME': 'localhost.localdomain',
    }
    
    app = create_app()
    app.config.update(test_config)
    
    # Create application context
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide database instance for tests."""
    with app.app_context():
        yield _db


@pytest.fixture(scope='function')
def client(app):
    """Provide test client for making requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Provide CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_student(db):
    """Create a sample student user."""
    user = UserDAL.create_user(
        username='student1',
        email='student1@iu.edu',
        password='SecurePass123!',
        full_name='Test Student',
        role='student',
        department='Computer Science'
    )
    db.session.commit()
    return user


@pytest.fixture
def sample_admin(db):
    """Create a sample admin user."""
    user = UserDAL.create_user(
        username='admin1',
        email='admin1@iu.edu',
        password='AdminPass123!',
        full_name='Test Admin',
        role='admin',
        department='Administration'
    )
    db.session.commit()
    return user


@pytest.fixture
def sample_staff(db):
    """Create a sample staff user."""
    user = UserDAL.create_user(
        username='staff1',
        email='staff1@iu.edu',
        password='StaffPass123!',
        full_name='Test Staff',
        role='staff',
        department='Facilities'
    )
    db.session.commit()
    return user


@pytest.fixture
def sample_resource(db, sample_admin):
    """Create a sample resource."""
    resource = ResourceDAL.create_resource(
        name='Test Study Room 101',
        location='Luddy Hall, 1st Floor',
        resource_type='study_room',
        creator_id=sample_admin.id,
        description='A quiet study room with whiteboard',
        capacity=6,
        status='published',
        is_available=True
    )
    db.session.commit()
    return resource


@pytest.fixture
def sample_equipment(db, sample_admin):
    """Create a sample equipment resource."""
    equipment = ResourceDAL.create_resource(
        name='Laptop - Dell XPS',
        location='Library Circulation Desk',
        resource_type='equipment',
        creator_id=sample_admin.id,
        description='High-performance laptop for checkout',
        capacity=1,
        status='published',
        is_available=True
    )
    db.session.commit()
    return equipment


@pytest.fixture
def sample_booking(db, sample_student, sample_resource):
    """Create a sample booking."""
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=2)
    
    booking = BookingDAL.create_booking(
        user_id=sample_student.id,
        resource_id=sample_resource.id,
        start_time=start,
        end_time=end,
        notes='Study session for finals'
    )
    db.session.commit()
    return booking


@pytest.fixture
def authenticated_client(client, sample_student):
    """Provide an authenticated test client logged in as student."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_student.id)
    return client


@pytest.fixture
def admin_client(client, sample_admin):
    """Provide an authenticated test client logged in as admin."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_admin.id)
    return client


@pytest.fixture
def multiple_resources(db, sample_admin):
    """Create multiple resources for testing queries."""
    resources = []
    
    # Study rooms
    for i in range(3):
        resource = ResourceDAL.create_resource(
            name=f'Study Room {i+1}',
            location='Luddy Hall',
            resource_type='study_room',
            creator_id=sample_admin.id,
            description=f'Study room number {i+1}',
            capacity=4 + i*2,
            status='published',
            is_available=True
        )
        resources.append(resource)
    
    # Equipment
    for i in range(2):
        equipment = ResourceDAL.create_resource(
            name=f'Laptop {i+1}',
            location='Library',
            resource_type='equipment',
            creator_id=sample_admin.id,
            description=f'Laptop for checkout {i+1}',
            capacity=1,
            status='published',
            is_available=True
        )
        resources.append(equipment)
    
    db.session.commit()
    return resources


@pytest.fixture
def conflicting_bookings(db, sample_student, sample_resource):
    """Create bookings that overlap for conflict testing."""
    bookings = []
    
    # Booking 1: Tomorrow 10am-12pm
    start1 = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end1 = start1 + timedelta(hours=2)
    booking1 = BookingDAL.create_booking(
        user_id=sample_student.id,
        resource_id=sample_resource.id,
        start_time=start1,
        end_time=end1,
        notes='First booking'
    )
    booking1.status = 'confirmed'
    bookings.append(booking1)
    
    # Booking 2: Tomorrow 2pm-4pm (no conflict)
    start2 = datetime.utcnow().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end2 = start2 + timedelta(hours=2)
    booking2 = BookingDAL.create_booking(
        user_id=sample_student.id,
        resource_id=sample_resource.id,
        start_time=start2,
        end_time=end2,
        notes='Second booking'
    )
    booking2.status = 'confirmed'
    bookings.append(booking2)
    
    db.session.commit()
    return bookings


@pytest.fixture
def sample_message(db, sample_student, sample_admin):
    """Create a sample message between users."""
    from campus_resource_hub.src.data_access.message_dal import MessageDAL
    
    message = MessageDAL.send_message(
        sender_id=sample_student.id,
        receiver_id=sample_admin.id,
        body='Hello, I have a question about my booking.',
        booking_id=None
    )
    db.session.commit()
    return message
