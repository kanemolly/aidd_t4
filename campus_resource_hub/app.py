"""
Campus Resource Hub - Main Application Entry Point
A Flask full-stack application for Indiana University resource management.
"""

import os
from flask import Flask
from src.config import config
from src.extensions import db, login_manager, csrf_protect


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
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth.bp)
    app.register_blueprint(resources.bp, url_prefix='/resources')
    app.register_blueprint(bookings.bp, url_prefix='/bookings')
    app.register_blueprint(messages.bp, url_prefix='/messages')
    app.register_blueprint(reviews.bp, url_prefix='/reviews')
    app.register_blueprint(admin.bp, url_prefix='/admin')


def _register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        return {"error": "Internal server error"}, 500


def _register_main_routes(app):
    """Register main application routes."""
    from flask import redirect, url_for
    
    @app.route('/')
    def home():
        """Home route - redirects to login or resources."""
        from flask_login import current_user
        # Just redirect to resources list (will require login if needed)
        return redirect(url_for('resources.list_resources'))
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {"status": "healthy"}, 200


# Create app instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
