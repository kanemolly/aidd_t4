# RAG Integration - Quick Start

## Where to Put Your Document

```
📁 docs/context/DT/rag_knowledge.md  ← PUT YOUR RAG DOCUMENT HERE
```

## What's Integrated

✅ **Chatbot now loads 3 sources of context:**

1. **Persona** (AI personality)
   - File: `docs/context/DT/personas.md`
   - What: How the AI acts and communicates

2. **RAG Knowledge** (Your document) ← NEW!
   - File: `docs/context/DT/rag_knowledge.md`
   - What: Campus info, resources, policies, instructions

3. **Database** (Real-time data)
   - From: Resources table
   - What: Current availability, details

## How the Chatbot Uses Your RAG

```
User Question
    ↓
Load All 3 Contexts
    ├─ Persona: "Be friendly and helpful"
    ├─ RAG: "Here's everything about campus resources"
    └─ Database: "Room 101 is available 2pm-4pm"
    ↓
Send to Gemini AI
    ↓
AI Generates Response
    ↓
Display to User
```

## What to Include in Your RAG Document

Use Markdown format with clear structure:

```markdown
# Resource Name
- Location: [address]
- Hours: [hours]
- Description: [what it is]
- Important info: [policies, rules, tips]

# Another Resource
- Similar format...
```

## Example RAG Content

```markdown
# Study Rooms
- Location: Library Building, Rooms 101-150
- Capacity: 2-8 people per room
- Booking: Up to 4 hours, max 1 per day
- Features: Whiteboard, projector, AC
- Peak hours: 2pm-6pm (book early!)

# Computer Labs
- Location: Engineering Building, 1st Floor
- Hours: 7am-11pm weekdays
- Computers: Windows, Mac, Linux available
- Support: Tech help available 9am-5pm
```

## Files Created/Modified

| File | Status | Purpose |
|------|--------|---------|
| `docs/context/DT/rag_knowledge.md` | ✨ NEW | Your RAG document |
| `src/controllers/concierge.py` | 🔄 UPDATED | Loads RAG + persona + database |
| `docs/RAG_INTEGRATION_GUIDE.md` | ✨ NEW | Detailed integration guide |

## Next Step: Add Your Content!

1. **Open the RAG file:**
   ```
   docs/context/DT/rag_knowledge.md
   ```

2. **Replace the placeholder** with your content

3. **Restart the server:**
   ```bash
   python -u serve.py
   ```

4. **Test it:**
   - Go to http://127.0.0.1:5000/concierge
   - Ask a question about resources in your RAG doc
   - The chatbot should mention your content!

## That's It!

Your RAG document is now **fully integrated** with the chatbot. 
Any updates you make will be loaded automatically on each request.
