# Messaging & Notifications System - Campus Resource Hub

## Overview

A comprehensive messaging and notifications system that enables users to communicate directly with resource owners and receive real-time notifications about important events.

## Features

### 1. **User-to-User Messaging**
- Send and receive messages between users
- Thread-based conversation grouping
- Read status tracking
- Message character limit (5000 characters)
- Auto-thread creation and management

### 2. **Message Inbox**
- View all conversations in one place
- Sort by most recent, unread first
- Search conversations by user name or message content
- Filter by unread messages
- Last message preview with timestamps
- Unread message counter

### 3. **Message Threading**
- Full message history in chronological order
- Auto-scroll to latest messages
- Real-time message status (sent/read indicators)
- Character counter during typing
- Keyboard shortcut: Ctrl+Enter to send

### 4. **Quick Message Modal**
- Message resource owner directly from resource detail page
- Pre-populated with owner name and resource context
- Works seamlessly alongside booking flow
- Beautiful modal UI with animations

### 5. **Notifications System**
- Real-time notification bell in navbar
- Notification dropdown with recent notifications
- Unread count badge
- Notification types:
  - New message from another user
  - Booking requests received
  - Booking confirmation
  - Booking denial
  - Booking cancellation
  - Booking reminders
  - Review flagging notifications

### 6. **Notification Management**
- Mark notifications as read
- Mark all notifications as read at once
- Notification links navigate to relevant pages
- Automatic notification creation on system events
- Persistent notification storage

## Architecture

### Database Models

#### Message Model
```python
class Message(db.Model):
    id: int (Primary Key)
    thread_id: int (Group related messages)
    sender_id: int (Foreign Key → User)
    recipient_id: int (Foreign Key → User)
    subject: str
    body: str (Max 5000 characters)
    is_read: bool
    created_at: datetime (Indexed)
    read_at: datetime
```

#### Notification Model
```python
class Notification(db.Model):
    id: int (Primary Key)
    user_id: int (Foreign Key → User, Indexed)
    message_id: int (Optional, Foreign Key → Message)
    booking_id: int (Optional, Foreign Key → Booking)
    notification_type: str (Indexed)
    title: str
    description: str
    action_url: str (Navigation URL)
    sender_id: int (Foreign Key → User, Optional)
    is_read: bool (Indexed)
    created_at: datetime (Indexed)
    read_at: datetime
```

### API Endpoints

#### Message Endpoints
- `GET /messages/` - List user conversations
- `GET /messages/thread/<id>` - Get messages in a thread
- `GET /messages/<id>` - Get specific message
- `POST /messages/` - Send new message
- `POST /messages/<id>/mark-read` - Mark message as read
- `DELETE /messages/<id>` - Delete message
- `GET /messages/unread-count` - Get unread count

#### Notification Endpoints (JSON API)
- `GET /messages/api/notifications` - Get all notifications
- `POST /messages/api/notifications/<id>/read` - Mark as read
- `POST /messages/api/notifications/read-all` - Mark all as read
- `GET /messages/api/notifications/unread-count` - Get unread count

### Templates

#### `/src/views/templates/messages/inbox.html`
Main messaging interface showing conversation list with:
- Search functionality
- Filter options
- Unread badges
- User avatars
- Last message previews
- Timestamps
- Real-time polling (10-second refresh)

#### `/src/views/templates/messages/thread.html`
Message thread detail view with:
- Full conversation history
- Typing indicators
- Auto-scroll to latest
- Real-time message sending
- Character counter
- Message status indicators
- Auto-reload on new messages

#### Modified `/src/views/templates/resources/detail.html`
Added "Message Owner" button and modal:
- Quick messaging from resource page
- Pre-filled recipient and context
- Integrated with notification system

#### Modified `/src/views/templates/base.html`
Added notification UI:
- Notification bell icon in navbar
- Dropdown with recent notifications
- Unread count badge
- Mark as read functionality
- Quick navigation to messages

### Services

#### NotificationService
Centralized notification management:

```python
class NotificationService:
    # Create notifications
    create_notification()
    
    # Specific notification types
    notify_new_message()
    notify_booking_request()
    notify_booking_confirmed()
    notify_booking_denied()
    notify_booking_cancelled()
    notify_booking_reminder()
    notify_review_flagged()
    
    # Query notifications
    get_unread_count()
    get_recent_notifications()
```

## User Workflows

### Messaging Workflow

1. **Student browses resources**
   - Views resource detail page
   - Sees "Message Owner" button

2. **Student sends message**
   - Clicks "Message Owner" button
   - Modal opens with owner info
   - Types message (max 5000 chars)
   - Clicks "Send Message"
   - Notification created for owner
   - Success message shown

3. **Resource owner receives notification**
   - Sees notification badge in navbar
   - Opens notification dropdown
   - Clicks notification to open thread
   - Reads message in thread view
   - Message marked as read

4. **Conversation continues**
   - Either party can reply in thread
   - Messages appear in real-time (via polling)
   - Both parties see read/sent indicators

### Booking + Messaging Integration

When a booking is created:
1. Notification sent to resource owner
2. Automatic message thread can be created
3. Owner can message requester about booking
4. Requester receives notification

## Styling

### Color Scheme
- Primary: IU Crimson (#990000)
- Received messages: Cream (#EEEDEB)
- Sent messages: Crimson (#990000)
- Accents: Green for success, Red for alerts

### Animation Effects
- Modal slide-up: 300ms ease
- Message bubble pop: 300ms cubic-bezier
- Notification pulse: 2s infinite
- Dropdown slide down: 300ms ease

### Responsive Design
- Desktop: Full 3-column layouts
- Tablet (768px): Adjusted spacing
- Mobile (480px): Single column, compact
- Mobile (360px): Minimal padding

## Technical Highlights

### CSRF Protection
- All POST requests require CSRF token
- Token extracted from meta tag at runtime
- Dynamic extraction pattern: `document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')`

### Real-Time Updates
- Notification auto-refresh: 10-second polling
- Message thread auto-refresh: 5-second polling
- Pauses when tab is hidden (visibility API)
- Resumes when tab becomes visible

### Error Handling
- Comprehensive validation on client and server
- Toast notifications for user feedback
- Graceful fallback if notifications fail
- Error messages in modals and status divs

### Performance
- Indexed database columns for fast queries
- Lazy loading of conversations
- Limited notification display (10 most recent)
- Background sync pauses on hidden tabs

## Integration Points

### With Bookings System
- Notification service methods ready for booking events
- Can trigger notifications on:
  - Booking creation
  - Booking confirmation
  - Booking denial
  - Booking cancellation
  - Booking reminders (future)

### With Reviews System
- Review flagging notifications
- Links to admin review management

### With Resources System
- Message owner from resource detail
- Pre-populated context in messages

## Future Enhancements

### Planned Features
1. **Typing Indicators** - Show when someone is typing
2. **Read Receipts** - More granular read status
3. **Message Reactions** - Emoji reactions to messages
4. **File Attachments** - Share documents/images
5. **Message Search** - Full-text search of messages
6. **Threading improvements** - Nested replies
7. **Push Notifications** - Browser push for new messages
8. **Delivery Confirmation** - Server delivery status

### Performance Optimizations
1. WebSocket replacement for polling
2. Message pagination/lazy loading
3. Notification caching
4. Optimistic UI updates
5. Service worker for offline support

### Admin Features
1. Message moderation/flagging
2. User blocking system
3. Bulk notification management
4. Notification analytics
5. Scheduled notifications

## Testing

### Manual Testing Checklist

- [ ] Create new conversation from resource page
- [ ] Send message and verify notification
- [ ] Open notification and view thread
- [ ] Reply in thread and see auto-refresh
- [ ] Mark individual notification as read
- [ ] Mark all notifications as read
- [ ] Search conversations
- [ ] Filter unread messages
- [ ] Test character counter
- [ ] Test CSRF protection (network tab)
- [ ] Test on mobile devices
- [ ] Test notification refresh every 10s
- [ ] Test message thread refresh every 5s
- [ ] Test tab visibility pause/resume

### Unit Tests (Future)
- Message creation and validation
- Notification creation for each type
- Thread grouping logic
- User authorization checks
- Character limit enforcement
- CSRF token validation

## Security Considerations

1. **Authorization**
   - Only recipients can mark own messages as read
   - Only message senders can delete own messages
   - Only notification recipients can access own notifications
   - Only recipients can mark notifications as read

2. **Input Validation**
   - Message length limit (5000 chars)
   - Subject length limit (255 chars)
   - HTML escaping on display
   - CSRF token required for all mutations

3. **Data Privacy**
   - Messages only visible to sender/recipient
   - Notifications only visible to recipient
   - No message text in notification preview (truncated)
   - Secure database relationships

## Deployment Checklist

- [ ] Run database migrations for Notification model
- [ ] Update User model relationships
- [ ] Add notification service to imports
- [ ] Update message controller imports
- [ ] Verify all endpoints are accessible
- [ ] Test CSRF protection
- [ ] Check notification bell shows in navbar
- [ ] Verify notification dropdown styling
- [ ] Test message modal on resource pages
- [ ] Check responsive design on mobile
- [ ] Monitor for notification creation errors
- [ ] Set up logging for notification service

## Support & Troubleshooting

### Common Issues

**Notification not appearing:**
- Check browser console for errors
- Verify notification service import
- Check database for notification record
- Ensure CSRF token is valid

**Messages not sending:**
- Check CSRF token in network tab
- Verify recipient exists
- Check message length limit
- Look at server logs

**Styling issues:**
- Clear browser cache
- Check CSS file is loading
- Verify color variables are defined
- Test in incognito mode

**Real-time updates slow:**
- Reduce polling interval if needed
- Check database indexes
- Monitor server load
- Check browser performance

## Questions?

Refer to the NotificationService class documentation or the inline code comments for specific implementation details.
