# User Roles & Permissions Update - Documentation

## Overview
Comprehensive implementation of role-based access control system with proper permissions for 4 user types: Not Logged In, Student, Staff, and Admin.

## Changes Made

### 1. **Fixed Critical Security Vulnerability - Registration**

**Problem**: Users could select any role (including admin) during registration via form manipulation.

**Files Modified**:
- `src/controllers/auth.py` (Line ~33)
- `src/views/templates/auth/register.html` (Lines 318-330)

**Changes**:
- **auth.py**: Removed `role = request.form.get('role', 'student')` and replaced with hardcoded `role = User.ROLE_STUDENT`
- **register.html**: Removed role selection dropdown completely
- **register.html**: Made department field full-width with helpful text

**Result**: All public registrations now create student accounts only. Admin and staff accounts must be created by existing administrators.

---

### 2. **Resource Creation Restrictions**

**Problem**: Students could create, edit, and delete resources when they should only be able to browse and book.

**Files Modified**:
- `src/controllers/resources.py` (Lines 203-218)
- `src/views/templates/resources/list.html` (Line 385)

**Changes**:
- **resources.py**: Added permission check at start of `create_resource()` function:
  ```python
  if not (current_user.is_staff() or current_user.is_admin()):
      flash('You do not have permission to create resources. Please contact staff or admin.', 'error')
      return redirect(url_for('resources.list_resources'))
  ```
- **list.html**: Updated Create Resource button to only show for staff/admin:
  ```jinja2
  {% if current_user.is_authenticated and (current_user.is_staff() or current_user.is_admin()) %}
  ```

**Result**: 
- Students cannot create resources (backend + frontend restriction)
- Students cannot edit/delete resources (existing checks confirmed working)
- Only staff and admin can manage resources

---

### 3. **Role-Based Navigation**

**Problem**: All users saw identical navigation regardless of role/permissions.

**Files Modified**:
- `src/views/templates/base.html` (Lines 249-287 for desktop, 290-318 for mobile)

**Changes**: Created role-specific navigation menus

**Admin Navigation**:
- 📚 All Resources
- 📅 All Bookings (shows ALL system bookings)
- 🧠 Concierge
- 👤 Profile (with visual indicator)
- Logout

**Staff Navigation**:
- 📚 Resources
- ➕ Add Resource
- 📅 My Bookings
- 🧠 Concierge
- Profile
- Logout

**Student Navigation**:
- 📚 Browse Resources
- 📅 My Bookings
- 🧠 Concierge
- Profile
- Logout

**Not Logged In**:
- 📚 Browse Resources
- Login
- Sign Up

**Result**: Users see contextually appropriate navigation based on their role and permissions.

---

### 4. **Admin Dashboard - All Bookings View**

**Problem**: No easy way for admins to view all system bookings.

**Files Created/Modified**:
- `src/controllers/bookings.py` (Lines 43-89) - Modified
- `src/views/templates/bookings/list.html` - Created new file

**Changes**:

**bookings.py**:
- Enhanced `list_bookings()` to support both HTML and JSON responses
- Admins see all bookings, regular users see only their own
- Added format parameter for API compatibility
- Added `is_admin_view` context variable

**list.html** (NEW FILE):
- Full-featured bookings management page
- Status filtering (All, Pending, Confirmed, Completed, Cancelled)
- Admin view shows booking creator information
- Cancel booking functionality
- Responsive design with IU branding
- Empty state handling
- Action buttons contextual to booking status

**Result**: 
- Admins can now click "📅 All Bookings" in nav to see comprehensive booking dashboard
- Students/Staff see "📅 My Bookings" showing only their bookings
- Existing API endpoints still work (JSON format preserved)

---

### 5. **Staff Resource Management**

**Problem**: Staff needed better tools to manage resources.

**Implementation**:
- Staff already see all resources in list view (same as everyone)
- Resources show availability status (`is_available` field)
- Staff navigation includes "➕ Add Resource" shortcut
- Staff can create, edit resources they own
- Admins can edit ANY resource

**Result**: Staff have streamlined access to resource management tools.

---

## User Permissions Summary

### Not Logged In
✅ Browse resources (read-only)
✅ View resource details
❌ Cannot book resources
❌ Cannot create/edit/delete resources
❌ Cannot view bookings

### Student
✅ Browse resources
✅ View resource details
✅ Book resources (create bookings)
✅ View their own bookings
✅ Cancel their own bookings
❌ Cannot create resources
❌ Cannot edit/delete resources (unless they somehow own one)
❌ Cannot view other users' bookings

### Staff
✅ All student permissions, PLUS:
✅ Create new resources
✅ Edit their own resources
✅ Delete their own resources
✅ Quick access to "Add Resource" in navigation
❌ Cannot edit resources created by others (only admin can)
❌ Cannot view all bookings (only their own)

### Admin
✅ All staff permissions, PLUS:
✅ Edit ANY resource (regardless of creator)
✅ Delete ANY resource
✅ View ALL bookings in system
✅ Visual indicators in navigation (crimson name badge)
✅ Access to comprehensive admin dashboard

---

## Security Improvements

1. **Registration Hardening**: Removed client-side role selection; server-side enforcement of student-only registration
2. **Server-Side Validation**: All permission checks happen in controllers before any action
3. **Frontend Hiding**: Buttons/links hidden for unauthorized actions (defense in depth)
4. **Clear Error Messages**: Users get helpful feedback when trying unauthorized actions

---

## Testing Checklist

- [ ] Create new student account (verify no role selection)
- [ ] Login as student (verify cannot see "Create Resource" button)
- [ ] Attempt to access `/resources/create` as student (verify redirect with error)
- [ ] Login as staff (verify can create resources)
- [ ] Login as admin (verify sees "All Bookings" link)
- [ ] Admin clicks "All Bookings" (verify sees all system bookings)
- [ ] Verify navigation shows correct links for each role
- [ ] Verify mobile navigation works correctly

---

## Files Changed Summary

**Modified**:
1. `src/controllers/auth.py` - Registration security fix
2. `src/controllers/resources.py` - Resource creation permission
3. `src/controllers/bookings.py` - Admin bookings view
4. `src/views/templates/base.html` - Role-based navigation
5. `src/views/templates/auth/register.html` - Remove role dropdown
6. `src/views/templates/resources/list.html` - Hide create button for students

**Created**:
1. `src/views/templates/bookings/list.html` - Comprehensive bookings dashboard

**Total Changes**: 6 files modified, 1 file created

---

## Future Enhancements

**Potential Additions**:
- Admin user management page (create staff/admin accounts, view all users)
- Staff analytics/reporting dashboard
- Resource approval workflow (staff creates → admin approves)
- Booking approval system (pending → admin/staff confirms)
- Activity logs for admin (audit trail)
- Role change functionality (admin promotes student to staff)

---

## Migration Notes

**Existing Users**:
- All existing users retain their current roles
- No database migration required
- System remains backward compatible

**New Users**:
- All new registrations create student accounts
- Admins must manually upgrade users to staff/admin roles in database

**Database Command** (for creating admin/staff manually):
```sql
-- Upgrade user to staff
UPDATE users SET role = 'staff' WHERE username = 'username';

-- Upgrade user to admin
UPDATE users SET role = 'admin' WHERE username = 'username';
```

---

## Conclusion

The role-based permissions system is now fully implemented with:
- ✅ Security hardened (no admin self-registration)
- ✅ Clear separation of permissions
- ✅ Intuitive navigation for each role
- ✅ Admin dashboard for system-wide visibility
- ✅ Staff tools for resource management
- ✅ Student-friendly browsing and booking experience

All user types now have logical, role-appropriate views and workflows throughout the application.
