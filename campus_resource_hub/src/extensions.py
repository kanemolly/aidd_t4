"""
Flask extensions initialization.
Separated from app creation to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize extensions without binding to app
db = SQLAlchemy()
login_manager = LoginManager()
csrf_protect = CSRFProtect()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from src.models import User
    return User.query.get(int(user_id))
