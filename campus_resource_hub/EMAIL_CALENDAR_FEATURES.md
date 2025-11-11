# Email Notifications & Calendar Export Features

## Overview
This document describes the email notification and calendar export features added to the Campus Resource Hub booking system.

## Features Implemented

### 1. Email Notifications 📧

The system now sends automatic email notifications for all booking events:

#### Notification Types:
- **Booking Created** - When a user creates a new booking (pending approval)
- **Booking Confirmed** - When an admin approves a booking
- **Booking Cancelled** - When a booking is cancelled by user or admin
- **Booking Reminder** - (Framework ready for future scheduled reminders)

#### Email Configuration:
- **Development Mode**: Emails are simulated and logged to console and file
- **Production Mode**: Ready for integration with SendGrid, AWS SES, or SMTP

#### Email Simulation:
All emails in development mode are:
1. Printed to the console with full formatting
2. Logged to `instance/email_notifications.log` for review
3. Include all booking details, user information, and action links

#### Configuration:
```python
# In src/config.py
EMAIL_SIMULATE_MODE = True  # Set to False for production email service
EMAIL_NOTIFICATIONS_ENABLED = True  # Enable/disable all email notifications
```

### 2. Calendar Export 📅

Users can export their bookings to their preferred calendar application:

#### Export Options:

**1. iCal (.ics) File Download**
- Universal format compatible with all calendar apps
- Works with: Google Calendar, Apple Calendar, Outlook, etc.
- Includes: Event details, location, reminders
- Endpoint: `/bookings/<id>/calendar`

**2. Google Calendar Direct Add**
- One-click add to Google Calendar
- Opens in new tab with pre-filled event data
- Endpoint: `/bookings/<id>/calendar/google`

**3. Outlook Calendar Direct Add**
- One-click add to Outlook.com calendar
- Opens in new tab with pre-filled event data
- Endpoint: `/bookings/<id>/calendar/outlook`

#### Calendar Event Features:
- Automatic reminder set for 1 hour before event
- Full booking details in description
- Resource location as event location
- Link back to booking details page
- Status tracking (confirmed/tentative/cancelled)

## Implementation Details

### File Structure:
```
src/
├── services/
│   ├── __init__.py
│   ├── email_service.py      # Email notification service
│   └── calendar_service.py   # iCal & calendar URL generation
├── controllers/
│   └── bookings.py           # Updated with email & calendar endpoints
└── config.py                 # Email configuration settings
```

### New Endpoints:

```
GET  /bookings/<id>/calendar          - Download .ics file
GET  /bookings/<id>/calendar/google   - Redirect to Google Calendar
GET  /bookings/<id>/calendar/outlook  - Redirect to Outlook Calendar
```

### Email Service API:

```python
from src.services.email_service import email_service

# Send booking confirmation
email_service.send_booking_confirmation(booking, user)

# Send booking created (pending)
email_service.send_booking_created(booking, user)

# Send cancellation notice
email_service.send_booking_cancelled(booking, user, cancelled_by)

# Send reminder
email_service.send_booking_reminder(booking, user, hours_before=24)
```

### Calendar Service API:

```python
from src.services.calendar_service import calendar_service

# Generate iCal file content
ical_content = calendar_service.generate_ical(booking)

# Generate Google Calendar URL
google_url = calendar_service.generate_google_calendar_url(booking)

# Generate Outlook Calendar URL
outlook_url = calendar_service.generate_outlook_url(booking)
```

## Usage Examples

### For Users:

1. **View Booking Details**: Go to any confirmed or pending booking
2. **Add to Calendar Section**: Find the "📅 Add to Calendar" section
3. **Choose Export Method**:
   - Click "Download .ics File" to save the event file
   - Click "Add to Google Calendar" to add directly
   - Click "Add to Outlook" to add directly

### For Administrators:

**Check Email Log**:
```bash
# View simulated emails
cat instance/email_notifications.log

# Or tail for real-time viewing
tail -f instance/email_notifications.log
```

## Testing

### Test Email Notifications:

1. **Create a Booking**:
   - User receives "Booking Request Received" email
   - Email logged to console and file

2. **Approve a Booking** (Admin):
   - User receives "Booking Confirmed" email
   - Includes calendar export links

3. **Cancel a Booking**:
   - User receives "Booking Cancelled" email
   - Shows who cancelled (user or staff)

### Test Calendar Export:

1. **Download .ics File**:
   - Go to booking details
   - Click "Download .ics File"
   - Open in calendar app to verify

2. **Add to Google Calendar**:
   - Click "Add to Google Calendar"
   - Verify event details pre-populate
   - Confirm to add

3. **Add to Outlook**:
   - Click "Add to Outlook"
   - Verify event details pre-populate
   - Confirm to add

## Email Notification Content

### Booking Created Email Example:
```
Subject: Booking Request Received: Computer Lab A

Hi John Doe,

We've received your booking request!

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: Computer Lab A
Type: Facility
Location: Luddy Hall, Room 101

Date: Monday, November 10, 2025
Start Time: 02:00 PM
End Time: 04:00 PM
Duration: 2.0 hours

Booking ID: 42
Status: PENDING APPROVAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your booking is currently pending approval from our staff.
You'll receive another email once your booking has been reviewed.

View your booking: http://localhost:5000/bookings/view/42

Best regards,
Campus Resource Hub Team
```

## Future Enhancements

### Planned Features:
1. **Scheduled Reminders**: Background job to send reminders 24h/1h before bookings
2. **Email Templates**: HTML email templates with branding
3. **Real Email Integration**: Configure SendGrid or AWS SES for production
4. **Email Preferences**: Let users choose notification settings
5. **SMS Notifications**: Optional text message alerts
6. **Google Calendar OAuth**: Direct two-way sync with Google Calendar
7. **Recurring Event Support**: Better handling of recurring bookings in calendar

### Production Email Setup:

To use real email in production:

1. **Update config.py**:
```python
EMAIL_SIMULATE_MODE = False
```

2. **Implement in email_service.py**:
```python
def _send_real_email(self, to_email, subject, body, to_name, html_body):
    # Add SendGrid, AWS SES, or SMTP implementation
    pass
```

3. **Add Environment Variables**:
```bash
EMAIL_API_KEY=your_sendgrid_api_key
EMAIL_FROM_ADDRESS=noreply@campus-hub.edu
EMAIL_FROM_NAME=Campus Resource Hub
```

## Troubleshooting

### Email Not Sending:
- Check `EMAIL_NOTIFICATIONS_ENABLED` in config
- Verify booking status triggers notification
- Check console output for errors
- Review `instance/email_notifications.log`

### Calendar Export Not Working:
- Ensure user is logged in
- Verify user owns the booking or is admin
- Check booking status (confirmed/pending only)
- Test .ics file with different calendar apps

### iCal File Won't Import:
- Some calendar apps require specific formatting
- Try downloading and opening with different app
- Check generated .ics content for syntax errors

## Security Considerations

1. **Authorization**: All calendar export endpoints check user ownership
2. **Email Privacy**: User emails never exposed to other users
3. **Link Security**: Booking view links require authentication
4. **Data Validation**: All inputs sanitized for email and calendar content

## Support

For issues or questions:
- Check application logs
- Review email notification log file
- Test with different browsers/calendar apps
- Contact system administrator

---

**Version**: 1.0.0  
**Last Updated**: November 10, 2025  
**Author**: Campus Resource Hub Development Team
