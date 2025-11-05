# Quick Reference - Database Schema
**Campus Resource Hub — Fast Lookup Guide**

---

## 📊 All Fields at a Glance

### USERS (11 fields)
```
id* | username | email | password_hash | full_name | 
role | is_active | profile_image | department | created_at | updated_at
```
**Indexes:** email*, username*  
**PK:** id* | **FK:** None  
**Relationships:** resources(1:M), bookings(1:M), messages_sent(1:M), messages_received(1:M), reviews(1:M)

### RESOURCES (13 fields)
```
id* | name | description | location | resource_type | 
capacity | is_available | available_from | available_until | 
status | creator_id^ | created_at | updated_at
```
**Indexes:** name*  
**PK:** id* | **FK:** creator_id^  
**Relationships:** bookings(1:M), reviews(1:M), creator→user(M:1)

### BOOKINGS (9 fields)
```
id* | user_id^ | resource_id^ | start_time | end_time | 
status | notes | created_at | updated_at
```
**Indexes:** start_time*  
**PK:** id* | **FK:** user_id^, resource_id^  
**Relationships:** user(M:1), resource(M:1)

### MESSAGES (9 fields)
```
id* | thread_id | sender_id^ | recipient_id^ | subject | 
body | is_read | created_at | read_at
```
**Indexes:** created_at*, thread_id*  
**PK:** id* | **FK:** sender_id^, recipient_id^  
**Relationships:** sender→user(M:1), recipient→user(M:1)

### REVIEWS (8 fields)
```
id* | reviewer_id^ | resource_id^ | rating | title | 
comment | created_at | updated_at
```
**Indexes:** created_at*  
**PK:** id* | **FK:** reviewer_id^, resource_id^  
**Relationships:** reviewer→user(M:1), resource(M:1)

**Legend:** * = Indexed | ^ = Foreign Key | (1:M) = One-to-Many | (M:1) = Many-to-One

---

## 🔑 Enums & Constants

### User Roles
```python
'student'  # Default student role
'staff'    # Staff member with more permissions
'admin'    # Administrator with full access
```

### Resource Status
```python
'draft'       # Not yet published
'published'   # Available for booking (default)
'archived'    # Hidden from listings
```

### Booking Status
```python
'pending'     # Awaiting approval (default)
'confirmed'   # Approved and confirmed
'cancelled'   # Booking cancelled
'completed'   # Booking completed
```

---

## 📐 Relationships Map

```
USER (1) ──────────────> (M) RESOURCE
 ├─ creator
 └─ owns multiple resources

USER (1) ──────────────> (M) BOOKING
 ├─ user
 └─ makes multiple bookings

USER (1) ──────────────> (M) MESSAGE (as sender)
 ├─ messages_sent
 └─ sends multiple messages

USER (1) ──────────────> (M) MESSAGE (as recipient)
 ├─ messages_received
 └─ receives multiple messages

USER (1) ──────────────> (M) REVIEW
 ├─ reviews
 └─ writes multiple reviews

RESOURCE (1) ──────────> (M) BOOKING
 └─ bookings from this resource

RESOURCE (1) ──────────> (M) REVIEW
 └─ reviews of this resource
```

---

## 🔍 Common Queries

### Find user by username
```python
user = User.query.filter_by(username='admin').first()
```

### Find all resources created by staff
```python
staff = User.query.filter_by(role='staff').first()
resources = Resource.query.filter_by(creator_id=staff.id).all()
```

### Get all bookings for a resource
```python
resource = Resource.query.get(1)
bookings = resource.bookings.all()
```

### Find messages in a thread
```python
messages = Message.query.filter_by(thread_id=1).order_by(Message.created_at).all()
```

### Get 5-star reviews only
```python
reviews = Review.query.filter_by(rating=5).all()
```

### Find unread messages for user
```python
user = User.query.get(1)
unread = user.messages_received.filter_by(is_read=False).all()
```

---

## 🛡️ Validation Rules

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| user.username | String(80) | UNIQUE | "admin" |
| user.email | String(120) | UNIQUE | "admin@iu.edu" |
| user.role | String(20) | IN ('student','staff','admin') | "admin" |
| resource.status | String(20) | IN ('draft','published','archived') | "published" |
| booking.status | String(20) | IN ('pending','confirmed','cancelled','completed') | "confirmed" |
| review.rating | Integer | CHECK (1-5) | 5 |
| message.thread_id | Integer | NULL allowed | NULL or 1,2,3... |

---

## 🔐 Security

### Passwords
- Field: `user.password_hash`
- Hashing: BCrypt via werkzeug
- Method: `user.set_password('password')`
- Verify: `user.check_password('password')`

### Role Checking
```python
user.is_admin()    # Check if admin
user.is_staff()    # Check if staff
user.is_student()  # Check if student
```

### Permission Pattern
```python
if user.role == 'admin':
    # Full access
elif user.role == 'staff':
    # Staff access
else:  # student
    # Student access
```

---

## 📅 Timestamps

All models have automatic timestamps:

| Field | Type | Behavior |
|-------|------|----------|
| created_at | DATETIME | Set on INSERT, never changes |
| updated_at | DATETIME | Set on INSERT, updated on every UPDATE |
| read_at | DATETIME | Set when Message marked as read (Message only) |

### Usage
```python
import datetime
# Filter by date range
from_date = datetime.datetime(2025, 1, 1)
to_date = datetime.datetime(2025, 12, 31)
bookings = Booking.query.filter(
    Booking.created_at.between(from_date, to_date)
).all()
```

---

## 📦 JSON Responses (to_dict())

### User.to_dict()
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@iu.edu",
  "full_name": "Administrator User",
  "role": "admin",
  "is_active": true,
  "profile_image": null,
  "department": null,
  "created_at": "2025-11-05T18:21:18.834593",
  "updated_at": "2025-11-05T18:21:18.834600"
}
```

### Resource.to_dict()
```json
{
  "id": 1,
  "name": "Study Room A",
  "description": "Quiet study room for students...",
  "location": "Library Building, Room 201",
  "resource_type": "room",
  "capacity": 4,
  "is_available": true,
  "available_from": "2025-11-05T18:21:18.878695",
  "available_until": "2026-11-05T18:21:18.878909",
  "status": "published",
  "creator_id": 2,
  "created_at": "2025-11-05T18:21:18.890513",
  "updated_at": "2025-11-05T18:21:18.890520"
}
```

### Booking.to_dict()
```json
{
  "id": 1,
  "user_id": 3,
  "resource_id": 1,
  "start_time": "2025-11-05T19:21:18.909246",
  "end_time": "2025-11-05T20:21:18.909246",
  "status": "confirmed",
  "notes": "Study session for upcoming exam",
  "created_at": "2025-11-05T18:21:18.914144",
  "updated_at": "2025-11-05T18:21:18.914148"
}
```

### Message.to_dict()
```json
{
  "id": 1,
  "thread_id": null,
  "sender_id": 2,
  "recipient_id": 3,
  "subject": "Welcome to Campus Resource Hub",
  "body": "Welcome! You can now book campus resources...",
  "is_read": false,
  "created_at": "2025-11-05T18:21:18.937564",
  "read_at": null
}
```

### Review.to_dict()
```json
{
  "id": 1,
  "reviewer_id": 3,
  "resource_id": 1,
  "rating": 5,
  "title": "Great study space!",
  "comment": "Perfect quiet room for studying...",
  "created_at": "2025-11-05T18:21:18.962672",
  "updated_at": "2025-11-05T18:21:18.962677"
}
```

---

## 🚀 API Endpoint Pattern (To Be Implemented)

```python
# Users
GET    /api/users/<id>           # Get user
POST   /api/users/login          # Login
POST   /api/users/register       # Register
PUT    /api/users/<id>           # Update profile

# Resources
GET    /api/resources            # List all
GET    /api/resources/<id>       # Get single
POST   /api/resources            # Create (staff/admin)
PUT    /api/resources/<id>       # Update (owner)
DELETE /api/resources/<id>       # Delete (owner/admin)

# Bookings
GET    /api/bookings             # List user's bookings
POST   /api/bookings             # Create booking
GET    /api/bookings/<id>        # Get booking details
PUT    /api/bookings/<id>        # Update booking status
DELETE /api/bookings/<id>        # Cancel booking

# Messages
GET    /api/messages             # List conversations
GET    /api/messages/<thread_id> # Get thread messages
POST   /api/messages             # Send message
PUT    /api/messages/<id>/read   # Mark as read

# Reviews
GET    /api/resources/<id>/reviews    # List resource reviews
POST   /api/resources/<id>/reviews    # Post review
```

---

## 🧪 Test Data

Pre-seeded database includes:

**Users:**
- admin (admin@iu.edu) - password: admin123 - role: admin
- staff (staff@iu.edu) - password: staff123 - role: staff
- student (student@iu.edu) - password: student123 - role: student

**Resources:**
- Study Room A (created by staff, published, capacity 4)

**Bookings:**
- student → Study Room A (confirmed)

**Messages:**
- staff → student (Welcome message, unread)

**Reviews:**
- student → Study Room A (5 stars)

---

## 🔧 Database File

**Location:** `campus_hub.db`  
**Type:** SQLite 3  
**Size:** ~32 KB (with sample data)  
**Reinitialize:** Run `python init_db.py`

---

## 📚 Related Documentation

- **ERD_ALIGNMENT_ANALYSIS.md** - Gap analysis and recommendations
- **PHASE_1_COMPLETION_SUMMARY.md** - What was implemented
- **ERD_IMPLEMENTATION_COMPARISON.md** - Detailed specifications
- **DATABASE_SCHEMA_DOCS_INDEX.md** - Complete index

---

**Version:** 1.0  
**Last Updated:** November 5, 2025  
**Status:** ✅ Production Ready
