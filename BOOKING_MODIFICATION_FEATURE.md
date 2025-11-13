# Booking Modification Feature

## Overview
Admins and staff can now modify existing bookings (start time, end time, and notes), and users are automatically notified of any changes via in-app messages and emails.

## Features Implemented

### 1. Database Modifications
**New Columns Added to `bookings` Table:**
- `modified_by_id` (INTEGER FK → users.id, nullable): Tracks which admin/staff member made the modification
- `modified_at` (DATETIME, nullable): Timestamp of when the modification occurred
- `change_summary` (TEXT, nullable): Detailed text summary of what was changed

**Migration Script:** `add_modification_fields.py`
- Automatically creates the new columns if they don't exist
- Applied to active database: `instance/campus_hub.db`

### 2. Backend API Endpoint

**POST `/bookings/<booking_id>/edit`**
- **Authentication:** Login required (admins/staff only)
- **Request Body (JSON):**
  ```json
  {
    "start_time": "2025-11-13T14:00:00Z",
    "end_time": "2025-11-13T16:00:00Z",
    "notes": "Updated booking notes"
  }
  ```
- **Validation:**
  - Start time must be before end time
  - No time slot conflicts with other confirmed bookings (excludes current booking)
  - Both start_time and end_time are required
- **Response:**
  ```json
  {
    "success": true,
    "message": "Booking modified successfully",
    "booking": { ... },
    "changes": [
      "Start time: 2025-11-13T14:00:00 → 2025-11-13T15:00:00",
      "Notes: Old notes → New notes"
    ]
  }
  ```

**Error Responses:**
- 403: User is not admin/staff
- 404: Booking not found
- 400: Validation error (invalid times, conflicts, missing fields)
- 500: Server error

### 3. User Interface - Booking Detail Page

**Edit Button:**
- Appears only for admin/staff users
- Opens modal dialog with prefilled current booking details
- Button styling: Blue "✎ Edit Booking" button

**Edit Modal Dialog:**
- **Fields Editable:**
  - Start Date & Time (datetime-local input)
  - End Date & Time (datetime-local input)
  - Notes (textarea)
- **Features:**
  - Pre-populates with current booking values
  - Real-time validation showing error messages
  - Clean, accessible form layout
  - Cancel and Save buttons

**Modification Information Display:**
- New section shows when a booking has been modified
- Displays:
  - Admin name who made the modification
  - Date/time of modification
  - Detailed change summary (formatted as code block)

### 4. User Notifications

**In-App Notification Message:**
- **Subject:** "Booking Modified: [Resource Name]"
- **Content:**
  - Clear notification that booking was modified by admin
  - Updated booking details (resource, date, time, location)
  - Detailed list of changes
  - Admin name
  - Call to action to review details

**Email Notification:**
- Same information as in-app message
- Professional formatted email
- Links to view booking details
- Only sent if `EMAIL_NOTIFICATIONS_ENABLED` is True in config

### 5. Change Tracking

The system tracks and displays all changes made:
- **Start time changes:** "Start time: [old] → [new]"
- **End time changes:** "End time: [old] → [new]"
- **Notes changes:** "Notes: [old] → [new] (or empty if blank)"

## User Experience Flow

1. **Admin/Staff Views Booking Detail**
   - Sees blue "✎ Edit Booking" button
   
2. **Admin Clicks Edit Button**
   - Modal opens with current booking times and notes prefilled
   
3. **Admin Modifies Fields**
   - Changes start/end times and/or notes
   - Can see validation errors in real-time (e.g., time conflicts)
   
4. **Admin Saves Changes**
   - Booking is updated in database
   - Modification tracking fields are set (modified_by_id, modified_at, change_summary)
   - Success modal appears
   - Page reloads after 2 seconds to show updated information
   
5. **Student/Booking Owner is Notified**
   - In-app message arrives showing:
     - What was modified
     - New booking details
     - Who made the change
   - Email notification also sent (if configured)
   
6. **Student Views Their Booking**
   - Can see "Modification Information" section on detail page
   - Shows admin name, date of modification, and exact changes made

## Code Files Modified

### Models
- `src/models/models.py`: Added three new columns and relationships to Booking model

### Controllers
- `src/controllers/bookings.py`: Added new `edit_booking()` endpoint with full validation and notification logic

### Services
- `src/services/email_service.py`: Added `send_booking_modified()` method for email notifications

### Templates
- `src/views/templates/bookings/detail.html`:
  - Added Edit button to action buttons section
  - Added edit modal dialog with form inputs
  - Added modification information display section
  - Added JavaScript functions for modal management and API calls
  - Added data attributes to booking details for reading current values

## Technical Details

### Conflict Detection
When modifying booking times, the system checks for conflicts with:
- Other confirmed bookings for the same resource
- Time windows must not overlap with existing bookings
- Adjacent bookings (ending exactly when another starts) are allowed
- Current booking is excluded from conflict check

### Datetime Handling
- Frontend uses HTML5 `datetime-local` input (browser-native, no library needed)
- Converted to ISO 8601 format for API transmission
- API accepts ISO format datetimes
- Database stores as SQLite DATETIME
- Timezone handling: Uses UTC for consistency

### CSRF Protection
- Uses Flask-WTF csrf_protect with X-CSRFToken header
- Token passed from base.html global `window.CSRF_TOKEN`
- Applied consistently across all AJAX calls

## Testing Checklist

- [ ] Admin can open edit modal for a booking
- [ ] Modal pre-populates with current booking details
- [ ] Admin can modify start time
- [ ] Admin can modify end time
- [ ] Admin can modify notes
- [ ] Validation prevents end time before start time
- [ ] Validation detects time slot conflicts
- [ ] Changes are saved to database
- [ ] Booking owner receives in-app notification
- [ ] Booking owner receives email notification (if configured)
- [ ] Modification information appears on booking detail page
- [ ] Regular users cannot see edit button
- [ ] Non-admin users cannot edit bookings (403 error)

## Future Enhancements

1. **Bulk Editing:** Allow editing multiple recurring booking instances at once
2. **Modification History:** Keep full audit log of all modifications with timestamps
3. **Rollback:** Allow admins to undo modifications
4. **Approval:** Allow modification approval workflow if needed
5. **Student Response:** Allow students to confirm or request re-scheduling after modification
6. **Notification Settings:** Let students customize what notifications they receive

## Deployment Notes

1. Run migration script: `python add_modification_fields.py`
2. Verify database columns were added: `PRAGMA table_info(bookings)`
3. Restart Flask application
4. Test edit functionality with admin account
5. Verify email notifications (if sending enabled)

## Configuration

**Email Notifications:** Controlled by `EMAIL_NOTIFICATIONS_ENABLED` in Flask config
```python
EMAIL_NOTIFICATIONS_ENABLED = True  # Default: True
```

**Booking Conflict Window:** Exact time matching (no buffer)
- Can be enhanced to add pre/post-booking buffers if needed
- Currently: booking1.end_time == booking2.start_time is allowed
