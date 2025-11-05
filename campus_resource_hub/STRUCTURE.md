# Project Structure Guide

## Overview

The Campus Resource Hub project has been organized following Flask best practices with clear separation of concerns:

```
campus_resource_hub/
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies  
├── .gitignore                      # Git ignore rules
├── README.md                       # Project overview
├── STRUCTURE.md                    # This file
│
├── scripts/                        # Utility and maintenance scripts
│   ├── init_db.py                 # Initialize database with sample data
│   └── check_db.py                # Check database status and statistics
│
├── instance/                       # Flask instance directory (auto-created)
│   └── campus_hub.db              # SQLite database file
│
├── src/                            # Main application source code
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   ├── extensions.py              # Flask extensions initialization
│   │
│   ├── models/                    # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   └── models.py              # User, Resource, Booking, Message, Review
│   │
│   ├── data_access/               # Data Access Layer (DAL)
│   │   ├── __init__.py
│   │   ├── user_dal.py            # User CRUD operations
│   │   ├── resource_dal.py        # Resource CRUD operations
│   │   ├── booking_dal.py         # Booking CRUD operations
│   │   ├── message_dal.py         # Message CRUD operations
│   │   └── review_dal.py          # Review CRUD operations
│   │
│   ├── controllers/               # Flask blueprints and route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication routes
│   │   ├── resources.py           # Resource management + image upload
│   │   ├── bookings.py            # Booking management
│   │   ├── messages.py            # Messaging system
│   │   ├── reviews.py             # Reviews and ratings
│   │   └── admin.py               # Admin dashboard (if implemented)
│   │
│   ├── views/                     # Template rendering
│   │   ├── __init__.py
│   │   ├── templates/             # HTML templates
│   │   │   ├── base.html          # Base template with layout
│   │   │   ├── auth/
│   │   │   │   ├── login.html
│   │   │   │   └── register.html
│   │   │   ├── resources/
│   │   │   │   ├── list.html      # Resource listing page
│   │   │   │   ├── detail.html    # Resource detail page
│   │   │   │   └── form.html      # Create/Edit resource form
│   │   │   ├── bookings/
│   │   │   │   └── booking_form.html
│   │   │   ├── messages/
│   │   │   │   └── thread.html    # Messaging interface
│   │   │   └── reviews/
│   │   │       └── reviews_component.html
│   │   │
│   │   └── static/
│   │       └── uploads/           # User-uploaded resource images
│   │
│   └── tests/                     # Legacy test configuration
│       └── __init__.py
│
├── tests/                         # Integration tests (centralized)
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration and fixtures
│   └── test_bookings.py          # Booking system tests
│
└── docs/                          # Documentation (if present)
    └── ...                        # Project documentation files
```

## Directory Purposes

### `/scripts/`
Utility scripts for maintenance and setup:
- **init_db.py**: Initializes the database and populates sample data
- **check_db.py**: Inspects database state, counts records, shows statistics

**Usage**:
```bash
# Initialize database
python scripts/init_db.py

# Check database status
python scripts/check_db.py
```

### `/instance/`
Flask instance folder containing:
- **campus_hub.db**: SQLite database file (auto-created on first run)

Note: This folder is gitignored to prevent committing database files.

### `/src/`
Main application code organized by architectural layer:

#### `/src/models/`
SQLAlchemy ORM models defining database schema:
- User, Resource, Booking, Message, Review

#### `/src/data_access/`
Data Access Layer (DAL) providing database operations:
- Each model has a corresponding DAL file (e.g., user_dal.py, resource_dal.py)
- Centralizes all database queries and operations
- Makes testing easier through mocking

#### `/src/controllers/`
Flask blueprints handling HTTP routes and business logic:
- **auth.py**: Login, register, logout routes
- **resources.py**: Resource CRUD + image upload handling
- **bookings.py**: Booking management endpoints
- **messages.py**: Messaging system endpoints
- **reviews.py**: Reviews and rating endpoints
- **admin.py**: Admin dashboard (optional)

#### `/src/views/`
Template rendering and static files:
- **templates/**: Jinja2 HTML templates organized by feature
- **static/uploads/**: Directory for user-uploaded images (created at runtime)

### `/tests/`
Centralized test location:
- **conftest.py**: Pytest configuration, fixtures, app initialization
- **test_*.py**: Test files for each feature area
- All tests run via `pytest tests/`

## Key Features & Their Files

### Image Upload Feature
- **Model**: `src/models/models.py` - `image_path` field on Resource
- **Controller**: `src/controllers/resources.py` - Upload handlers
- **Form**: `src/views/templates/resources/form.html` - Upload UI
- **Detail**: `src/views/templates/resources/detail.html` - Image display
- **List**: `src/views/templates/resources/list.html` - Card images
- **Storage**: `static/uploads/` - Uploaded files

### Messaging System
- **Model**: `src/models/models.py` - Message model
- **DAL**: `src/data_access/message_dal.py` - Message operations
- **Controller**: `src/controllers/messages.py` - Message endpoints
- **Template**: `src/views/templates/messages/thread.html` - UI (917 lines)

### Reviews & Ratings
- **Model**: `src/models/models.py` - Review model
- **DAL**: `src/data_access/review_dal.py` - Review operations
- **Controller**: `src/controllers/reviews.py` - Review endpoints
- **Template**: `src/views/templates/reviews/reviews_component.html` - UI

### Booking System
- **Model**: `src/models/models.py` - Booking model
- **DAL**: `src/data_access/booking_dal.py` - Booking operations
- **Controller**: `src/controllers/bookings.py` - Booking endpoints
- **Template**: `src/views/templates/bookings/booking_form.html` - UI
- **Tests**: `tests/test_bookings.py` - Booking tests

## Development Workflow

### Running the Application
```bash
# 1. Activate virtual environment
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database (first time only)
python scripts/init_db.py

# 4. Run the app
python app.py
```

### Adding a New Feature

1. **Create Model** (if needed)
   - Edit `src/models/models.py`
   - Add SQLAlchemy model class

2. **Create DAL** (if needed)
   - Create new file in `src/data_access/`
   - Implement CRUD operations

3. **Create Controller**
   - Create new file in `src/controllers/` or edit existing
   - Define Flask routes and business logic
   - Register blueprint in `app.py`

4. **Create Templates**
   - Create new folder in `src/views/templates/`
   - Add HTML templates using Jinja2

5. **Write Tests**
   - Add test file in `tests/`
   - Use fixtures from `tests/conftest.py`

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_bookings.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov tests/
```

## File Organization Principles

1. **Separation of Concerns**: Each layer (model, data access, controller, view) has distinct responsibilities
2. **Feature-Based Grouping**: Templates organized by feature (resources/, bookings/, messages/, etc.)
3. **Reusability**: Common functions extracted to utilities
4. **Testing**: Test files colocated with feature implementations
5. **Scripts**: Maintenance tools in dedicated `/scripts/` folder

## Important Notes

### Database
- Stored in `instance/campus_hub.db` (SQLite)
- Auto-created on first run
- Gitignored to prevent committing database state
- Reset with: `rm instance/campus_hub.db && python scripts/init_db.py`

### Uploads
- Images stored in `static/uploads/`
- Subdirectory auto-created on first image upload
- Gitignored to prevent committing user uploads
- Cleaned up automatically when images are replaced/deleted

### Configuration
- Database settings in `src/config.py`
- Upload settings in `src/controllers/resources.py`
- File validation: JPG/PNG/WebP only, max 5MB
- Image display sizes: 800x533px (detail), 200px height (list cards)

## Migration from Old Structure

Previously, the project had files scattered across root and src/:
- Utility scripts (init_db.py, check_db.py) were in root → Now in `/scripts/`
- Test configuration (conftest.py) was in src/tests/ → Now in `/tests/`
- Redundant test files (test_login.py, etc.) were in root → Removed/consolidated

This reorganization improves:
- **Clarity**: Clear purpose for each directory
- **Maintainability**: Easier to find and update code
- **Professionalism**: Follows Flask best practices
- **Scalability**: Easy to add new features in consistent locations

---

**Last Updated**: November 5, 2025
**Current Version**: 2.0 (Post-Reorganization)
