"""
Database models for Campus Resource Hub.
Includes User, Resource, Booking, Message, and Review models with relationships.
"""

from datetime import datetime
from src.extensions import db, bcrypt
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model with authentication and role-based access."""
    
    __tablename__ = 'users'
    
    # Enum-like roles
    ROLE_STUDENT = 'student'
    ROLE_STAFF = 'staff'
    ROLE_ADMIN = 'admin'
    
    VALID_ROLES = [ROLE_STUDENT, ROLE_STAFF, ROLE_ADMIN]
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    
    # Role and Status
    role = db.Column(db.String(20), default=ROLE_STUDENT, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Profile Information
    profile_image = db.Column(db.String(255), nullable=True)  # Path to profile image
    department = db.Column(db.String(120), nullable=True)  # Department or unit
    
    # User Preferences & Profile Details (for personalized recommendations)
    year_in_school = db.Column(db.String(20), nullable=True)  # Freshman, Sophomore, Junior, Senior, Graduate
    major = db.Column(db.String(120), nullable=True)  # Academic major/program
    interests = db.Column(db.Text, nullable=True)  # JSON: ["music", "coding", "sports"]
    study_preferences = db.Column(db.Text, nullable=True)  # JSON: {"environment": "quiet", "time": "morning"}
    accessibility_needs = db.Column(db.Text, nullable=True)  # JSON: ["wheelchair_access", "quiet_space"]
    preferred_locations = db.Column(db.Text, nullable=True)  # JSON: ["Wells Library", "IMU"]
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    resources = db.relationship('Resource', backref='creator', lazy='dynamic', foreign_keys='Resource.creator_id')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', foreign_keys='Booking.user_id')
    messages_sent = db.relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='recipient', lazy='dynamic', foreign_keys='Message.recipient_id')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic', foreign_keys='Review.reviewer_id')
    
    def set_password(self, password):
        """Hash and set the user's password using bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verify the user's password against bcrypt hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.ROLE_ADMIN
    
    def is_staff(self):
        """Check if user has staff role."""
        return self.role == self.ROLE_STAFF
    
    def is_student(self):
        """Check if user has student role."""
        return self.role == self.ROLE_STUDENT
    
    def to_dict(self):
        """Convert user to dictionary."""
        import json
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'profile_image': self.profile_image,
            'department': self.department,
            'year_in_school': self.year_in_school,
            'major': self.major,
            'interests': json.loads(self.interests) if self.interests else [],
            'study_preferences': json.loads(self.study_preferences) if self.study_preferences else {},
            'accessibility_needs': json.loads(self.accessibility_needs) if self.accessibility_needs else [],
            'preferred_locations': json.loads(self.preferred_locations) if self.preferred_locations else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Resource(db.Model):
    """Campus resource model (rooms, equipment, services, etc.)."""
    
    __tablename__ = 'resources'
    
    # Status constants
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    
    VALID_STATUSES = [STATUS_DRAFT, STATUS_PUBLISHED, STATUS_ARCHIVED]
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Resource Information
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # room, equipment, service, etc.
    capacity = db.Column(db.Integer, nullable=True)  # For rooms/spaces
    
    # Availability
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)  # Available starting date
    available_until = db.Column(db.DateTime, nullable=True)  # Available until date
    
    # Booking Approval
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)  # Require admin approval for bookings
    
    # Resource Status (draft, published, archived)
    status = db.Column(db.String(20), default=STATUS_PUBLISHED, nullable=False)
    
    # Image
    image_path = db.Column(db.String(255), nullable=True)  # Path to uploaded resource image
    
    # Creator (Staff/Admin)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert resource to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'resource_type': self.resource_type,
            'capacity': self.capacity,
            'is_available': self.is_available,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_until': self.available_until.isoformat() if self.available_until else None,
            'status': self.status,
            'image_path': self.image_path,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Resource {self.name}>'


class Booking(db.Model):
    """Resource booking/reservation model."""
    
    __tablename__ = 'bookings'
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    
    VALID_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_CANCELLED, STATUS_COMPLETED]
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    
    # Booking Details
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Recurrence fields (optional)
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    recurrence_pattern = db.Column(db.String(20), nullable=True)  # daily, weekly, monthly
    recurrence_end_date = db.Column(db.DateTime, nullable=True)  # When recurrence stops
    parent_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)  # For recurring instances
    
    # Approval tracking
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Staff/admin who approved
    approved_at = db.Column(db.DateTime, nullable=True)  # When approved
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    recurring_instances = db.relationship('Booking', backref=db.backref('parent_booking', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        """Convert booking to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Booking {self.id}>'


class Message(db.Model):
    """User-to-user messaging model."""
    
    __tablename__ = 'messages'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Conversation Threading
    thread_id = db.Column(db.Integer, nullable=True, index=True)  # Group related messages
    
    # Foreign Keys
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Message Content
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def mark_as_read(self):
        """Mark message as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'subject': self.subject,
            'body': self.body,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id}>'


class Review(db.Model):
    """Resource review/rating model."""
    
    __tablename__ = 'reviews'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    
    # Review Content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(255), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    
    # Flagging System
    is_flagged = db.Column(db.Boolean, default=False, nullable=False, index=True)
    flag_count = db.Column(db.Integer, default=0, nullable=False)
    flag_reason = db.Column(db.Text, nullable=True)
    flagged_by = db.Column(db.Text, nullable=True)  # JSON array of user IDs who flagged
    flagged_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraint: Rating must be 1-5
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def to_dict(self):
        """Convert review to dictionary."""
        return {
            'id': self.id,
            'reviewer_id': self.reviewer_id,
            'resource_id': self.resource_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_flagged': self.is_flagged,
            'flag_count': self.flag_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Review {self.id} - {self.rating} stars>'
