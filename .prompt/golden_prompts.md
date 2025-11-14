# Golden Prompts

High-impact prompts and responses that generated excellent results during development.

---

## UI/UX Design

### Prompt: Modern Professional UI
**Request**: "can u make the form more modern, more professional, more clean"

**Context**: Booking form needed visual overhaul

**Response Highlights**:
- Implemented IU Crimson (#990000) and Cream (#EEEDEB) color scheme
- Added CSS variables for maintainability
- Created card-based layouts with proper spacing
- Used gradients and shadows for depth

**Why It Worked**: Clear intent with multiple descriptive adjectives helped AI understand the aesthetic goal

**Reusable Pattern**: "make [component] more [adjective1], more [adjective2], more [adjective3]"

---

## User Experience

### Prompt: Replace System Alerts
**Request**: "it gave me a system alert, can u make it a nice html popup instead"

**Context**: System alerts felt unprofessional and jarring

**Response Highlights**:
- Created styled modal components with animations
- Added backdrop blur effects
- Implemented multiple close methods (X button, backdrop click, ESC key)
- Used IU Crimson theme for consistency

**Why It Worked**: Specified problem (system alert) and desired solution (html popup) clearly

**Reusable Pattern**: "instead of [current implementation], can you make it [desired approach]"

---

## Data Organization

### Prompt: Time-Based Booking Sort
**Request**: "i want the My Bookings to be ordered in time, have most upcoming ones at the top, and a table at the bottom where the past ones were"

**Context**: Bookings list was difficult to navigate

**Response Highlights**:
- Split into "Upcoming" and "Past" sections
- Changed database queries to order by start_time ascending
- Converted card layout to table layout for better scannability
- Added time-based filtering logic

**Why It Worked**: Specific sorting criteria and visual organization requirements

**Reusable Pattern**: "order [items] by [criteria], with [group1] at [location1] and [group2] at [location2]"

---

## Admin Workflows

### Prompt: Bulk Actions
**Request**: "the admin can click a check box to bulk approve"

**Context**: Admin needed to approve multiple bookings efficiently

**Response Highlights**:
- Added checkbox column with select-all functionality
- Created bulk actions bar
- Implemented sequential processing with progress feedback
- Used custom modals for confirmations

**Why It Worked**: Clear action (bulk approve) with specific UI element (checkbox)

**Reusable Pattern**: "can [user role] [action] to [bulk operation]"

---

## Feature Implementation

### Prompt: Notification System
**Request**: "i want to be notified when one of my bookings gets approved"

**Context**: Users needed feedback on booking status changes

**Response Highlights**:
- Integrated NotificationService into confirmation workflow
- Created multiple notification channels (in-app, email)
- Added error handling to prevent approval failures
- Verified existing notification infrastructure

**Why It Worked**: User-centric statement ("I want to be notified") clearly expressed need

**Reusable Pattern**: "i want to [user action/notification] when [trigger event]"

---

## Role Verification

### Prompt: Permission Check
**Request**: "staff have same views / permissions as users, but they can create resources"

**Context**: Needed to verify role-based access control

**Response Highlights**:
- Verified is_staff() and is_admin() methods exist
- Checked controller authorization logic
- Confirmed staff can create resources (line 484 check)
- Ensured admin routes restricted properly

**Why It Worked**: Clear permission matrix specified

**Reusable Pattern**: "[role] have [permission set], but they can [additional capability]"

---

## Code Quality

### Prompt: Project Cleanup
**Request**: "delete any testing / bug scripts that I have here. delete uneeded markdown files, things like that. clean up the files of the project"

**Context**: Project needed cleanup before submission

**Response Highlights**:
- Identified and removed test scripts
- Deleted development documentation
- Removed archived/temporary directories
- Created proper folder structure for submission

**Why It Worked**: Clear intent (cleanup) with examples of what to remove

**Reusable Pattern**: "delete [category1], delete [category2], clean up [scope]"

---

## Patterns That Work

### 1. **Specific + Context**
Provide specific request with surrounding context about why/when/where

### 2. **Problem → Solution**
State current problem and desired end state

### 3. **Role-Based Requests**
Frame requests from user role perspective ("as a user, I want...")

### 4. **Visual Descriptors**
Use multiple adjectives for UI/styling requests (modern, professional, clean)

### 5. **Component + Action**
Specify exact component and exact action needed

---

## Anti-Patterns (What Doesn't Work)

### Vague Requests
❌ "make it better"
✅ "make the form more modern, professional, and clean"

### Missing Context
❌ "fix the bookings"
✅ "i want the My Bookings to be ordered by time, with upcoming ones at top"

### Assuming Knowledge
❌ "add notifications"
✅ "i want to be notified when one of my bookings gets approved"

---

## Notes for Future Prompts

- Always specify **who** (user role), **what** (feature/component), **when** (trigger), and **where** (location in UI)
- Use examples when possible ("like X but with Y")
- Reference existing patterns ("similar to how X works")
- Be specific about style preferences (colors, layouts, interactions)
- State constraints upfront ("must work with existing Y")



PROMPTS

Prompt for ChatGPT to receive prompts for Co-Pilot: 

Attached is the project description for my final project. i will be using co-pilot in VScode to create the project. I want you to create a complete set of prompts that I can feed co-pilot to complete the project. I want complete prompts, that capture the entire scope of the project. include steps like file structure and creation, also testing- all of the steps needed to satisfy the project. maintain a logical order for the development of the project. As i develop pieces, i will test them and ensure that everything is working. give me a complete set of prompts to give co-pilot to completely do the project. i will not be inserting all of the prompts at one time. I will input them in sections, so divide the prompts into sections that have a logical flow so i can develop piece by piece. 

Also, create an indepth PRD grounded in the assignment description that i could give to co-pilot to develop the project. 

 

1. Project Initialization 

🧠 Prompt 1.1 — Repository Setup 

We are building Campus Resource Hub, a Flask full-stack app for Indiana University. 
Please scaffold this AI-First repository structure: 

campus_resource_hub/ 
├── src/{controllers,models,views,data_access,static,tests}/ 
├── .prompt/{dev_notes.md,golden_prompts.md} 
├── docs/context/{APA,DT,PM,shared}/ 
├── app.py 
├── requirements.txt 
├── .gitignore 
└── README.md 
 

Add baseline dependencies: 
Flask, Flask-Login, Flask-WTF, SQLAlchemy, bcrypt, pytest, gunicorn, plotly, matplotlib. 

Create app.py returning “Campus Resource Hub initialized successfully.” 

 

🧠 Prompt 1.2 — App Factory & Config 

Refactor to use an Application Factory. 

create_app() initializes Flask, SQLAlchemy, LoginManager, CSRFProtect. 

Config: SECRET_KEY, SQLALCHEMY_DATABASE_URI='sqlite:///campus_hub.db'. 

Register blueprints: auth, resources, bookings, messages, admin. 

Verify that running flask run loads / route correctly. 

 

2. Database Layer 

🧠 Prompt 2.1 — Models 

Create SQLAlchemy models: User, Resource, Booking, Message, Review. 
Use schema from the assignment (IDs, timestamps, FKs, roles = student/staff/admin). 
Add relationships and helper to_dict() methods. 

Run init_db.py to seed one admin, staff, student, and sample resource. 

 

🧠 Prompt 2.2 — Data Access Modules 

In /src/data_access/, implement *_dal.py files exposing CRUD functions. 
Include session handling, try/except, and docstrings. 
Controllers should import only these methods, not ORM queries directly. 

 

3. Authentication 

🧠 Prompt 3.1 — Auth Blueprint & Templates 

Build /auth Blueprint with register/login/logout using Flask-Login + bcrypt. 

Templates: 

register.html — cream background, centered crimson card form, role dropdown. 

login.html — similar style. 

UI style: 

Buttons = crimson (#990000), hover = deep crimson (#4B0000), text = white. 

Inputs = rounded, light cream background. 

After Copilot outputs forms, prompt it again to: 

Add client-side validation messages. 

Ensure CSRF token present. 

Improve spacing for mobile. 

 

🧠 Prompt 3.2 — Top Navbar 

Create a responsive top navbar (navbar.html) included in base.html: 

Left: “Campus Resource Hub” text link. 

Right: conditional links (Login/Register or Dashboard/Profile). 

Colors: crimson background #990000, cream text #EEEDEB. 

Collapses to hamburger on mobile. 

 

4. Resources (CRUD + Search) 

🧠 Prompt 4.1 — Resource Controller 

Implement routes: 

/resources (GET) list + search by keyword/category/location. 

/resources/<id> detail. 

/resources/create + /edit + /delete. 
Use DAL functions, flash messages, and validation. 

 

🧠 Prompt 4.2 — UI Iteration 1 : Listing Grid 

Create resources_list.html displaying resource cards: 

Card background: white, border crimson 1 px, hover shadow. 

Header = title (crimson), subtext = category gray. 

Buttons = small crimson “View Details”. 

Add search bar and filters at top. 

Iterate: 

Ask Copilot to add hover lift and equal-height cards. 

Then request cream background section separators. 

Verify layout scales on mobile. 

 

🧠 Prompt 4.3 — UI Iteration 2 : Resource Detail 

Build resource_detail.html: 

Bootstrap carousel for images. 

Tabs: Description | Availability | Reviews. 

Right sidebar card = Booking CTA. 

Visual style: 

Background = cream #EEEDEB. 

Cards = white with crimson title bar. 

Iterate by requesting Copilot to: 

Improve contrast for accessibility. 

Add breadcrumbs and smooth fade-in animation. 

 

5. Booking System 

🧠 Prompt 5.1 — Booking Logic 

Create /bookings Blueprint. 

POST /bookings: create booking with start/end datetime. 

Add check_conflict(resource_id, start, end) helper. 

Manage status transitions: pending → approved → completed. 

Write short unit test verifying conflict prevention. 

 

🧠 Prompt 5.2 — Booking Calendar UI 

Build booking_form.html with date/time picker (Flatpickr). 
Show existing bookings in calendar view: 

Available = cream, Booked = crimson, Hover = dark crimson. 

Add legend and smooth transitions. 

Ask Copilot to refine layout for mobile screens. 

 

 

 

6. Messaging & Reviews 

🧠 Prompt 6.1 — Messaging Threads 

Implement /messages/<thread_id> route and template: 

Two-column chat bubbles: sender = crimson bubble right, receiver = light cream left. 

Include timestamps and small avatars. 

Auto-scroll to newest message (JS). 

After generation, prompt Copilot to test scroll + responsive stacking. 

 

🧠 Prompt 6.2 — Reviews 

Add /reviews routes for posting rating/comment after booking completion. 

UI: star icons (1–5), crimson active stars, gray inactive. 
Show average rating atop resource detail card. 

 

7. Admin Dashboard 

🧠 Prompt 7.1 — Dashboard Overview 

Create /admin/dashboard view with: 

Cards for total Users, Resources, Bookings, Reviews. 

Plotly bar chart “Bookings per Resource Type”. 

Table “Top 5 Most Booked Resources”. 

Theme: cream background, white cards, crimson headers. 

Ask Copilot to: 

Add responsive 3-column layout. 

Color charts using crimson + cream palette. 

Add subtle entry animations. 

 

8. Global Styling & Accessibility 

🧠 Prompt 8.1 — Theme CSS 

Create /static/css/theme.css: 

:root { 
  --iu-crimson: #990000; 
  --iu-cream: #EEEDEB; 
  --iu-dark: #4B0000; 
  --iu-light: #F8F7F5; 
} 
body { 
  background-color: var(--iu-cream); 
  color: var(--iu-dark); 
  font-family: "Open Sans", sans-serif; 
} 
.btn-primary { 
  background-color: var(--iu-crimson); 
  border-color: var(--iu-crimson); 
} 
.btn-primary:hover { 
  background-color: var(--iu-dark); 
} 
 

 

 

 

Apply to all templates; verify WCAG contrast ratios. 

 

🧠 Prompt 8.2 — Base Template 

Create base.html with: 

Navbar (include navbar.html), 

{% block content %}, 

Footer with IU branding. 

Test responsive collapse and spacing. 

 

9. AI Feature 1 — Auto-Summary Reporter 

🧠 Prompt 9.1 — Reporter Logic 

Implement /admin/summary_report: 

Aggregate weekly bookings. 

Compute “Top 5 Resources”. 

Render summary Markdown + save to /static/reports/summary_<date>.md. 

Display preview in dashboard with mini Plotly chart. 

 

10. AI Feature 2 — Resource Concierge 

🧠 Prompt 10.1 — Concierge Assistant 

Build /concierge route with form: 

User enters question (“Which study rooms have projectors?”). 

Backend searches DB + references /docs/context/DT/personas.md. 

Return factual, friendly response (“Hello! As your Student Concierge …”). 

UI: chat bubbles in crimson/cream colors. 

 

 

Add test verifying all output fields match real resources. 

 

11. Testing & Validation 

🧠 Prompt 11.1 — Unit Tests 

Write pytest suites for: 

Auth flow 

CRUD operations 

Booking conflicts 

Admin summary report 

Concierge integrity 

Save results screenshots for documentation. 

Add test verifying all output fields match real resources. 

 

Booking confirmation page 

Ability to export a booking to google calendar 

 

🧠 Prompt 11.2 — Security Tests 

Confirm: 

CSRF tokens present. 

No inline unsanitized JS. 

ORM uses parameterized queries. 

 

12. Documentation 

🧠 Prompt 12.1 — README & Prompt Logs 

Generate README.md covering setup, usage, AI integration, ethics reflection. 

Update .prompt/dev_notes.md with representative prompts + results. 
Update .prompt/golden_prompts.md with your most effective UI prompt. 

 

13. Visual Artifacts 

🧠 Prompt 13.1 — ER Diagram & Wireframes 

Use eralchemy or Draw.io to create ERD (ERD.png). 
Create simple wireframes for Home, Resources, Detail, Dashboard. 
Save to /docs/context/DT/wireframes.pdf. 

 

14. Final Polish & Demo 

🧠 Prompt 14.1 — UI & Performance Sweep 

Ask Copilot to: 

Minify CSS/JS. 

Add loading spinners to buttons. 

Smooth page transitions. 

Confirm all navbar links function. 

Validate mobile responsiveness and accessibility one last time. 

Ensure that areas that users can input are safe from injection attacks 

Go through the three user types and ensure that the flow and views are logical.  Ex: if i am logged in as admin, i want to easily be able to find the admin dashboard and resources. 

 

I created a RAG document that has more context and directions for the chatbot.  where should i put that, and can u link it to the chatbot? 

Can the consirge be a smaller chatbot that is avaliable on the home page/ main bookings page/ a small window (that can be closed) that is featured on every page? 

Can you build out the user profile paths + the ability to change name, set profile picture, etc?  Maybe some information that the user can select about themselves, then the chatbot can consider that when recommending things? 

On the chat interface, can u put the users profile picture? 

 

I cant edit profile 

Ensure that areas that users can input are safe from injection attacks 

Ensure there is no conflicting info between the reservation system, forms, info in RAG, all of those things.  ensure it is all aligned 

 

 

 

Go through the 4 user types (student, staff, admin, not logged in/ un-assigned in) and ensure that the flow and views are logical.  Ex: if i am logged in as admin, i want to easily be able to find the admin dashboard and resources. 

When creating an account/ on the account creation page, Probably should not be able to create an admin account from the same account create as students and staff.   

As a student, i should not be able to edit and delete resources. Students can probably not create resources also. 

As an admin, i should be able to see all of the bookings, who booked it, when their booking is done 

As staff, i should be able to see all of the resources, and if they are available or not. 

 

The page for an individual resource: 

Resource page, viewing more information about it.  have a dyamic calendar where the “avalaibilty” tab is.  improve the overall look and feel of the resources page. Also the resource image doesnt work/load 

 

AI concierge: i don’t like when it calls itself Alex Riveria, it is the CampusConsierge etc.  take out/ dont use the personal name 

Using the RAG and system context, can u populate the resource database with things that could be booked. Once the time has passed for a booking/ the booking has expired, i want the resource to be avaliable for booking again.   

also, i want a log of who has booked, what, and when that admins can reference.  i want to be able to organize the log and gain different insights into the data of the log 

 

Optimize the project, check for redundacies, redudant databases, files that arent being used, .md files that are not critical, look for things like that and remove/ fix them 

 

 

 

I dont see images for the resources, on any of the screens. 

Need a logical way to create Admin accounts, a secure way as admins have more permissions 

The hamburger dropdown (smaller windows) doesnt work 

When i add a photo it does not appear on their profile picture 

For profile preferences, can there be prefilled boxes that i can select instead of having to type.  have the ability to type in unique preferences, but have many prefilled boxes/ things that can be selected.  for preferences, be sure to allow multiple selections, even with dropdown menus, to capture more nuances in preferences 

How do i add a comment to a resource? I dont see any.  also, staff and admin should be able to delete comments. 

Cancel booking- make it a popup that goes with the rest of the site 

 

i want the chatbot to be able to provide the link to specific bookings, that the user can click on to go to the page for that resource and learn about it/ see the booking link. 

  

Ex: if i am chatting with the bot and figure out that I want the solarium, the chatbot provides the (correct) link to that resource so i can see more about i t 

 

 

Resource Listings 
o CRUD operations for resources: title, description, images, category, location, availability 
rules, owner (user/team), capacity, and optional equipment lists. 
o Listing lifecycle: draft, published, archived. 
3. Search & Filter 
o Search by keyword, category, location, availability date/time, and capacity. 
o Sort options (recent, most booked, top rated). 

 

Ensure that passowrds are stored hashed/ encrypted/ bcrypt 

Calendar-based booking flow with start/end time, recurrence option (optional), and conflict detection. 
o Booking approval workflow: automatic approval for open resources, staff/admin approval 
for restricted resources. 
 

examples of resources that would need approval:  solarium, georgian room, AI/ VR studio/ lab, music rehersal hall, rooms that are for more than 10 people. 

  

Also, for things that are only for 1 people, can you write 1 person.  Or for equipment, remove the capacity detail in general. 

  

Also, can you add more resources to the database, relevant to IU like the other ones. 

 

looking at the admin view for bookings: 

  

I want an admin dashboard to be their primary view.  I want to see pending bookings as a primary type of thing, as admins must review and approve/ deny bookings. Then i want to see comments that are flagged as needing review- this doesnt need to be a seperate page. 

  

When viewing All Bookings, I would prefer it to just be a list/ admin can click on it to view more details.  once there are lots of bookings, this view could be hard to navigate.  probably rework the bookings page so that it is more informative and probably serves as their primary dashboard. 

o Email notifications or simulated notifications for booking confirmations and changes 

Calendar sync with Google Calendar (OAuth) or iCal export. 
 

 

Messaging & Notifications 
o Basic message thread between requester and admin accounts.  Admins can probably see and respond to the messages, i imagine it would be like a repository where they can all view and respond to the inquiries of students and staff. 
 

 

Reviews & Ratings 
o After completed bookings, users may rate and leave feedback for resources and hosts. 
o Aggregate rating calculation and top‑rated badges. 
7. Admin Panel 
o Admin dashboard to manage users, resources, bookings, and moderate reviews. 
8. Documentation & Local Runbook 
o README with setup + run instructions, requirements.txt, and database migration steps. 

Waitlist features for fully booked resources. 

 

Server‑Side Validation: All input fields must be validated on the server (types, lengths, date 
ranges). 
• XSS & Injection Protections: Use template escaping, parameterized SQL/ORM queries, and 
sanitize uploads. 
• Password Security: Store hashed + salted passwords (bcrypt). No plaintext passwords in repo. 
• CSRF Protection: Enable CSRF tokens for form submissions. 
• File Uploads: Restrict file types and sizes; store uploads in a safe folder; scan filenames for path 
traversal. 
• Privacy: Avoid storing unnecessary PII; keep minimal user info and allow admins to remove data if 
requested. 
• AI Testing & Verification 
o Projects that include AI features must provide at least one automated or manual test 
verifying that AI‑generated outputs behave predictably and align with factual project data. 
AI components must never return fabricated or unverifiable results. 
o AI feature outputs should be validated both functionally (correct data) and ethically 
(appropriate, non-biased responses). 

 

 
 