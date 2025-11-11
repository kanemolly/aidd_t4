"""
Campus Resource Hub - Main Application Entry Point
A Flask full-stack application for Indiana University resource management.
"""

import os
from pathlib import Path
from flask import Flask

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars

from src.config import config
from src.extensions import db, login_manager, csrf_protect, bcrypt


def create_app(config_name=None):
    """
    Application factory: Initialize and return the Flask application.
    
    Args:
        config_name (str): Configuration environment ('development', 'testing', 'production').
                          Defaults to environment variable or 'development'.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf_protect.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize email service
    from src.services.email_service import email_service
    email_service.init_app(app)
    
    # Import models to register them with SQLAlchemy
    from src.models import User, Resource, Booking, Message, Review
    
    # Register main routes (must be before blueprints for consistency)
    _register_main_routes(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def _register_blueprints(app):
    """Register all Flask blueprints."""
    from src.controllers import auth, resources, bookings, messages, reviews, admin
    try:
        from src.controllers import concierge
    except ImportError:
        concierge = None
    
    # Register blueprints (they have their own url_prefix defined)
    app.register_blueprint(auth.bp)
    app.register_blueprint(resources.bp)
    app.register_blueprint(bookings.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(admin.bp)
    if concierge:
        app.register_blueprint(concierge.bp)


def _register_error_handlers(app):
    """Register error handlers for the application."""
    from flask import request, render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        # Return HTML for browser requests, JSON for API requests
        if request.path.startswith('/api/') or request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return {"error": "Resource not found", "path": request.path}, 404
        # For regular page requests, show a proper error page
        return render_template('error.html', error=f"Page not found: {request.path}"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        if request.path.startswith('/api/') or request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return {"error": "Internal server error"}, 500
        return render_template('error.html', error="Internal server error occurred"), 500


def _register_main_routes(app):
    """Register main application routes."""
    from flask import redirect, url_for
    
    @app.route('/')
    def home():
        """Home route - redirects to role-appropriate landing page."""
        from flask_login import current_user
        # Redirect based on user role
        if current_user.is_authenticated:
            if current_user.is_admin() or current_user.is_staff():
                return redirect(url_for('bookings.dashboard'))
            return redirect(url_for('resources.list_resources'))
        # Not logged in - show resources (login required will catch them)
        return redirect(url_for('resources.list_resources'))
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {"status": "healthy"}, 200


# Create app instance
app = create_app()


if __name__ == '__main__':
    print("Starting Flask...")
    app.run(debug=False, host='127.0.0.1', port=5001)
