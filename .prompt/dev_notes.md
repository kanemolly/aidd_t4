# Development Notes
10. How did AI tools shape your design or coding decisions?

AI tools ended up playing a pretty big role in how I approached both the design and the implementation. I used them mainly as assistive partners, not as the final source of truth.
They helped me think through architecture choices, break down features into manageable parts, and generate starter code or UI ideas that I could refine.

For example, when designing the messaging system, I used AI to prototype database models and routes, and then iterated on them to fit the requirements and the overall feel of the project.
AI was especially useful in catching edge cases early — things like booking overlap logic, access control for role-based dashboards, or how to structure a RAG file for the chatbot.
So the tools didn’t replace my design work, but they definitely improved my speed and helped me get from idea → implementation more smoothly.

11. What did you learn about verifying and improving AI-generated outputs?

The biggest lesson is that AI-generated code or explanations are only reliable when I actively validate them.
A lot of what AI produces looks great on first read — it’s clean, structured, and confident — but sometimes it’s missing important details, oversimplifies something, or even suggests patterns that don’t actually match Flask’s best practices.

So I learned to:

Test every AI-suggested function myself

Re-run logic with real data (especially booking rules)

Compare outputs against the assignment requirements

Make sure the AI wasn’t hallucinating library functions or mixing frameworks

I also learned to prompt more intentionally: the more context I gave the AI, the better and more accurate the output became.
Essentially, AI accelerates work, but my critical thinking is what ensures the output is correct and production-ready.

12. What ethical or managerial considerations emerged from using AI in your project?

A few things stood out to me:

1. Data accuracy and grounding
Because I used an AI Concierge, I had to make sure it only provided verified IU information. That pushed me to implement a strict RAG approach so the chatbot couldn’t hallucinate or give students incorrect building hours or policies.

2. Transparency
It’s important that users know the AI isn’t a person — it’s an assistant pulling from approved campus data. That avoids misunderstandings and keeps trust in the system.

3. Privacy & security
Since messaging and user accounts are part of the platform, I needed to think about data protection, what gets stored, and ensuring the AI never exposes personal or sensitive information.

4. Managerial responsibility
Using AI in development means managers need to evaluate code quality differently — not just reviewing human work, but ensuring AI-generated code follows standards, is secure, and meets requirements.

Overall, I was consistently aware of how easily AI can drift outside scope or generate misleading content if not supervised.

13. How might these tools change the role of a business technologist or product manager in the next five years?

I think these tools are going to transform the role in a few major ways.

First, business technologists and product managers will gain the ability to prototype ideas extremely fast. Instead of waiting on engineering cycles to see what’s possible, PMs will be able to generate wireframes, data models, user flows, and even working demo code on their own. That means more exploration, more iteration, and better early-stage decision-making.

Second, PMs will shift from creating documentation to evaluating AI-generated artifacts — checking for correctness, completeness, feasibility, and alignment with strategy.

Third, AI will enhance their ability to analyze user behavior, design smarter workflows, and even anticipate stakeholder needs using pattern recognition.

And finally, the PM role will require stronger judgment and ethical awareness. With AI proposed solutions and code being so easy to generate, the responsibility shifts toward deciding what should be built, not just what can be built.

So overall, AI doesn’t replace the business technologist — it amplifies them. The value moves from production to direction, from manual creation to strategic oversight.
## AI Interaction Log

This document tracks all AI-assisted development interactions, outcomes, and lessons learned throughout the project lifecycle.

---

### Session: Project Structure & Organization (2025-11-13)

**Context**: Final project cleanup and restructuring for submission

**AI Interactions**:
- Cleaned up testing and migration scripts
- Removed development documentation files
- Organized project structure to match submission requirements

**Outcomes**:
- Removed: `add_cancellation_fields.py`, `add_modification_fields.py`, `migrate_all_dbs.py`
- Deleted temporary markdown documentation files
- Created AI-First folder structure (.prompt, docs, tests)

**Lessons Learned**:
- Keep development artifacts separate from production code
- Maintain clear separation between temporary and permanent documentation

---

### Session: Notification System Implementation (2025-11-13)

**Context**: Added notification functionality for booking approvals

**AI Interactions**:
- Integrated NotificationService into booking confirmation workflow
- Verified staff permissions for resource creation

**Outcomes**:
- Users now receive notifications when bookings are approved
- Notification records created via NotificationService.notify_booking_confirmed()
- Email notifications sent via email_service
- In-app messages created via MessageDAL

**Lessons Learned**:
- Multiple notification channels improve user experience
- Error handling prevents notification failures from blocking core functionality

---

### Session: UI/UX Enhancement (2025-11-06 to 2025-11-13)

**Context**: Modernized booking interfaces with IU Crimson theme

**AI Interactions**:
- Redesigned booking form with professional styling
- Implemented custom modals to replace system alerts
- Created table-based booking list with upcoming/past separation
- Added bulk admin actions with progress tracking

**Outcomes**:
- Consistent IU Crimson (#990000) and Cream (#EEEDEB) theme
- Improved user experience with styled modals
- Better data organization with table layouts
- Enhanced admin efficiency with bulk operations

**Lessons Learned**:
- CSS variables enable maintainable design systems
- User feedback (modals) improves perceived professionalism
- Table layouts more suitable for data-heavy interfaces than cards

---

### Session: Recurring Booking Feature (2025-11-06)

**Context**: Implemented recurring bookings functionality

**AI Interactions**:
- Added python-dateutil dependency for date calculations
- Created recurring booking logic with conflict detection
- Designed success modal for recurring booking feedback

**Outcomes**:
- Daily, weekly, and monthly recurring patterns supported
- Conflict detection prevents double-booking
- Clear user feedback on successful bookings and skipped conflicts

**Lessons Learned**:
- Date manipulation libraries (python-dateutil) essential for recurring events
- Transaction management crucial for bulk operations
- User communication important when partial failures occur

---

## Template for Future Sessions

### Session: [Feature/Issue Name] (YYYY-MM-DD)

**Context**: [What problem were you solving?]

**AI Interactions**:
- [Key prompts and requests]
- [Approach taken]

**Outcomes**:
- [What was implemented/fixed]
- [Files modified]
- [Features added]

**Lessons Learned**:
- [Key takeaways]
- [What to do differently next time]

---

## Notes

- Keep this file updated after each significant AI interaction
- Include enough context for future developers to understand decisions
- Document both successes and failures
- Track patterns that emerge over time
