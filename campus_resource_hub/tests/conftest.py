"""
Pytest configuration and fixtures for Campus Resource Hub tests.
"""

import pytest
from app import create_app
from src.extensions import db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(config_name='testing')
    
    # Create application context
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI."""
    return app.test_cli_runner()
