# Recurring Booking Feature - Implementation Guide

## Overview
Users can now create recurring bookings for resources (e.g., same meeting room every Monday night). All recurring bookings **require admin approval** before they become active, ensuring proper oversight of repetitive resource usage.

## Key Features

### 1. Recurring Booking Patterns
Users can choose from four recurrence patterns:

- **Weekly** - Every week on the same day (e.g., every Monday at 7 PM)
- **Bi-weekly** - Every 2 weeks on the same day (e.g., every other Monday at 7 PM)
- **Daily** - Every weekday (Monday-Friday)
- **Monthly** - Same day each month (e.g., 15th of every month)

### 2. Automatic Admin Approval Requirement
- **All recurring bookings require admin approval**, regardless of resource settings
- Even if a resource normally auto-approves single bookings, recurring requests will be set to "pending" status
- This prevents abuse and ensures proper review of long-term resource commitments

### 3. Intelligent Conflict Detection
- System checks each occurrence against existing confirmed bookings
- **Conflicts are automatically skipped** rather than causing the entire request to fail
- User is notified of:
  - Total bookings created
  - Number of conflicts skipped
  - Specific dates that had conflicts

### 4. Real-Time Preview
- As user selects options, they see a preview showing:
  - Approximate number of bookings to be created
  - Pattern description (e.g., "every Monday")
  - Time range for each booking
  - Date range (start to end)
  - Reminder that admin approval is required

## User Experience Flow

### Creating a Recurring Booking

1. **User navigates to booking form** for desired resource
2. **Fills in first occurrence details:**
   - Start date & time
   - End date & time
   - Notes (optional)

3. **Checks "Make this a recurring booking" checkbox**
   - Recurring options panel appears
   - Warning message displayed: "⚠️ Recurring bookings require admin approval"

4. **Selects recurrence pattern:**
   - Weekly (default)
   - Bi-weekly
   - Daily
   - Monthly

5. **Selects end date** for recurrence (when to stop repeating)
   - Default: 3 months from start date
   - Can be extended as needed

6. **Reviews preview** showing:
   - "This will create approximately X bookings..."
   - Pattern description
   - Time range
   - Date range

7. **Submits booking request**
   - Loading overlay shows "Processing your booking..."
   - System creates all booking instances (skipping conflicts)

8. **Receives confirmation:**
   - Alert shows: "✅ Recurring booking request submitted!"
   - Number of bookings created
   - Number of conflicts skipped (if any)
   - Reminder about admin approval requirement
   - Redirected to booking detail page

### Admin Approval Process

1. **Admin views pending bookings dashboard**
   - Recurring bookings are clearly marked
   - Shows parent booking with count of instances

2. **Admin reviews booking details**
   - Can see all instances in the series
   - Can approve or deny entire series

3. **Admin approves/denies**
   - All instances updated to confirmed/cancelled
   - User receives notification

## Technical Implementation

### Database Schema (Already Exists)
```python
# Booking model fields for recurrence
is_recurring = db.Column(db.Boolean, default=False)
recurrence_pattern = db.Column(db.String(20), nullable=True)  # 'weekly', 'biweekly', 'daily', 'monthly'
recurrence_end_date = db.Column(db.DateTime, nullable=True)
parent_booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
```

### API Endpoint Enhancement
**POST `/bookings/`**

Request with recurring data:
```json
{
  "resource_id": 1,
  "start_datetime": "2025-11-18 19:00:00",
  "end_datetime": "2025-11-18 21:00:00",
  "notes": "Study group meeting",
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_end_date": "2026-02-18"
}
```

Response:
```json
{
  "success": true,
  "message": "Created 14 recurring booking(s). All recurring bookings require admin approval.",
  "booking_id": 123,
  "auto_approved": false,
  "requires_approval": true,
  "is_recurring": true,
  "total_created": 14,
  "conflicts_skipped": 0,
  "conflicted_dates": [],
  "bookings": [...]
}
```

### Conflict Detection Logic

For each occurrence:
1. Calculate start/end time for that date
2. Query existing confirmed bookings for same resource in that time range
3. If conflict found:
   - Skip this occurrence
   - Add date to `conflicted_dates` array
   - Continue with next occurrence
4. If no conflict:
   - Create booking instance
   - Link to parent via `parent_booking_id`
   - Set status to PENDING

### Key Code Changes

#### 1. Booking Form UI (`form.html`)
- Added recurring checkbox
- Added collapsible recurring options panel
- Added pattern selector (weekly/biweekly/daily/monthly)
- Added end date picker
- Added real-time preview calculation
- Added form validation for recurring fields

#### 2. Booking Controller (`bookings.py`)
**Force Pending Status for Recurring:**
```python
# Auto-approve if resource doesn't require approval
# BUT: Recurring bookings ALWAYS require admin approval
if is_recurring:
    booking_status = Booking.STATUS_PENDING  # Always pending for recurring
else:
    booking_status = Booking.STATUS_PENDING if resource.requires_approval else Booking.STATUS_CONFIRMED
```

**Enhanced Response:**
```python
message = f'Created {len(created_bookings)} recurring booking(s). '
if conflicts:
    message += f'{len(conflicts)} dates were skipped due to conflicts. '
message += 'All recurring bookings require admin approval.'
```

## Conflict Detection Examples

### Example 1: Clean Schedule
```
Request: Study group every Monday 7-9 PM for 8 weeks
Existing: No conflicts
Result: 8 bookings created, all pending approval
```

### Example 2: Partial Conflicts
```
Request: Team meeting every Tuesday 3-5 PM for 10 weeks
Existing: Another booking on Nov 26 from 4-6 PM
Result: 9 bookings created (Nov 26 skipped), 1 conflict reported
User sees: "Created 9 bookings. 1 date skipped due to conflicts."
```

### Example 3: All Conflicts
```
Request: Daily booking 10 AM-12 PM for 1 week
Existing: Same resource booked all week 10-11 AM
Result: 0 bookings created (all overlapping)
Error: "Time slot conflicts with an existing confirmed booking" (first occurrence fails)
```

## Business Rules

1. **Admin Approval Required:** All recurring bookings require admin review, no exceptions

2. **Conflict Resolution:** Individual occurrences with conflicts are skipped, not failed

3. **Business Hours:** Each occurrence must respect business hours (8 AM - 8 PM)

4. **Minimum Duration:** No minimum, but each occurrence follows same duration as first

5. **Maximum Duration:** No hard limit on recurrence end date (admin discretion)

6. **Pattern Calculation:**
   - Daily: Skips weekends automatically
   - Weekly: Same weekday every week
   - Bi-weekly: Same weekday every 2 weeks
   - Monthly: Same date of month (e.g., always 15th)

## User Notifications

### On Creation
- Alert dialog showing:
  - Number of bookings created
  - Number of conflicts (if any)
  - Approval requirement reminder
- Redirect to first booking detail page

### On Approval (existing notification system)
- Email notification
- In-app message
- Shows all approved bookings

### On Denial (existing notification system)
- Email with reason
- In-app message
- Explains denial reason

## Admin Dashboard Enhancements (Existing)

Admins can already:
- View all pending bookings
- Filter by recurring bookings
- See parent-child relationships
- Approve/deny entire series
- View individual instances

## Testing Scenarios

### Test 1: Basic Weekly Recurring
1. Create booking for Monday 7-9 PM
2. Enable recurring, pattern: weekly, end date: +3 months
3. Verify ~12-13 bookings created
4. Verify all status = PENDING
5. Verify approval required message shown

### Test 2: Conflict Handling
1. Create confirmed booking for Dec 2, 2025, 3-5 PM
2. Create recurring booking starting Dec 2, same time, weekly for 4 weeks
3. Verify Dec 2 is skipped
4. Verify 3 other weeks created
5. Verify conflict message shows "1 date skipped"

### Test 3: Pattern Variations
1. Test daily pattern (weekdays only)
2. Test bi-weekly pattern (every 2 weeks)
3. Test monthly pattern (same day each month)
4. Verify calculations are correct

### Test 4: Auto-Approval Override
1. Use resource that normally auto-approves
2. Create single booking → should auto-approve
3. Create recurring booking → should require approval
4. Verify recurring status = PENDING despite resource settings

## Files Modified

1. **src/views/templates/bookings/form.html**
   - Added recurring checkbox (line ~410)
   - Added recurring options panel (lines ~415-460)
   - Added preview calculation JavaScript (lines ~580-630)
   - Updated form submission to include recurring data (lines ~520-545)

2. **src/controllers/bookings.py**
   - Modified booking status logic to force PENDING for recurring (line ~300)
   - Enhanced response message for recurring bookings (lines ~365-375)

## Configuration

No additional configuration needed. Feature uses existing:
- Database schema (already supports recurring)
- Business hours validation
- Conflict detection function
- Approval workflow

## Future Enhancements (Optional)

1. **Bulk Approval UI:** Allow admins to approve all instances with one click
2. **Series Editing:** Allow editing all future occurrences at once
3. **Exception Handling:** Allow skipping specific dates (holidays, breaks)
4. **Calendar View:** Show recurring bookings on calendar with different color
5. **Usage Analytics:** Track most popular recurring patterns
6. **Auto-Renewal:** Offer to extend recurring series when nearing end date

## Success Metrics

✅ Recurring checkbox appears on booking form
✅ Recurring options panel shows/hides correctly
✅ Preview updates in real-time
✅ Multiple bookings created on submission
✅ All recurring bookings require approval
✅ Conflicts are detected and skipped
✅ User receives clear feedback about bookings and conflicts
✅ Admin can approve/deny entire series
✅ Database maintains parent-child relationships

## Support & Troubleshooting

**Q: Why is my recurring booking still pending even though the resource auto-approves?**
A: All recurring bookings require admin approval for proper oversight, regardless of individual resource settings.

**Q: Some dates were skipped - why?**
A: The system detected conflicts with existing confirmed bookings on those dates and automatically skipped them to avoid double-booking.

**Q: Can I edit a recurring booking after creation?**
A: Currently, each instance is separate. Admins can use the edit feature on individual bookings. Future updates may allow bulk editing.

**Q: How far in advance can I create recurring bookings?**
A: There's no hard limit, but admins review all requests. Reasonable timeframes (semester, quarter) are recommended.
