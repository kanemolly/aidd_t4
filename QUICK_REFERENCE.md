# Quick Reference: Admin Booking Modification Feature

## For Admins - How to Use

### Edit a Booking
1. Go to booking detail page
2. Click blue "✎ Edit Booking" button
3. In modal, modify:
   - Start date/time
   - End date/time
   - Notes (optional)
4. Click "Save Changes"
5. Confirm on success modal
6. Booking is updated and student is notified

### What Students See
- In-app message: "Your booking for [Resource] has been modified"
- Email: Professional notification with changes listed
- Booking detail page: New "Modification Information" section showing:
  - Who modified it
  - When it was modified
  - Exact changes made

## For Developers - Implementation Details

### Database
```python
# New columns in Booking model
modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
modified_at = db.Column(db.DateTime, nullable=True)
change_summary = db.Column(db.Text, nullable=True)

# Relationship
modified_by = db.relationship('User', foreign_keys=[modified_by_id], lazy='joined')
```

### API Endpoint
```
POST /bookings/<booking_id>/edit
Authorization: Admin/Staff only
Content-Type: application/json

Request:
{
  "start_time": "2025-11-13T14:00:00Z",
  "end_time": "2025-11-13T16:00:00Z", 
  "notes": "Updated booking notes"
}

Response:
{
  "success": true,
  "changes": ["Start time: ... → ...", "Notes: ... → ..."],
  "booking": {...}
}
```

### Validation Rules
- ✓ Start time must be before end time
- ✓ No conflicts with other confirmed bookings
- ✓ Current booking excluded from conflict check
- ✓ Both times required
- ✓ Admin/staff only

### Notifications Sent
1. **In-App Message**
   - Recipient: Booking owner (student)
   - Includes: New times, what changed, who changed it

2. **Email**
   - Only if `EMAIL_NOTIFICATIONS_ENABLED = True`
   - Same content as in-app message
   - Professional HTML template

## Change Summary Format

When admin modifies booking, change_summary contains:
```
Start time: 2025-11-13T14:00:00 → 2025-11-13T15:00:00
End time: 2025-11-13T16:00:00 → 2025-11-13T17:00:00
Notes: Lab session extended → Lab session extended (moved 1 hour earlier)
```

Only fields that changed are included.

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 403 | Not authorized | Login as admin/staff |
| 404 | Booking not found | Check booking ID |
| 400 | Invalid input | Check time range and conflicts |
| 500 | Server error | Check logs |

## File Locations

- **Model:** `src/models/models.py` (lines with `modified_by`, `modified_at`, `change_summary`)
- **Endpoint:** `src/controllers/bookings.py` (function `edit_booking()`)
- **Email:** `src/services/email_service.py` (function `send_booking_modified()`)
- **UI:** `src/views/templates/bookings/detail.html` (edit modal + functions)
- **Migration:** `add_modification_fields.py` (root directory)

## Testing Checklist

- [ ] Admin sees Edit button on booking detail
- [ ] Regular user doesn't see Edit button
- [ ] Modal pre-populates with current times
- [ ] Can't set end time before start time
- [ ] Can't create time conflict
- [ ] Changes save to database
- [ ] Student receives notification
- [ ] Email sends (if enabled)
- [ ] Modification info shows on page
- [ ] Can modify again (no limit on edits)

## Performance Notes

- Conflict detection: O(n) where n = confirmed bookings for resource
- Change tracking: Lightweight string operations
- Notifications: Async-ready (use task queue for production)
- No impact on booking retrieval speed

## Security

- ✓ CSRF protected via X-CSRFToken header
- ✓ Authorization checked (admin/staff only)
- ✓ Input validation on times
- ✓ SQL injection prevented (SQLAlchemy)
- ✓ No data leaks in error messages
