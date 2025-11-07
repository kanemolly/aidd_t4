# How to Add Your RAG Document to the Concierge Chatbot

## Location & Setup

Your RAG (Retrieval-Augmented Generation) document should be placed at:

```
campus_resource_hub/
└── docs/
    └── context/
        └── DT/
            ├── personas.md          (AI personality & tone)
            ├── rag_knowledge.md     ← YOUR RAG DOCUMENT GOES HERE
            └── instructions.md      (optional: system instructions)
```

## File: `docs/context/DT/rag_knowledge.md`

This is where you should put your RAG document with comprehensive context and directions for the chatbot.

**What to include in your RAG document:**
- Campus resources details (names, locations, hours, policies)
- Service descriptions and availability
- Special instructions or guidelines
- Important dates and schedules
- Frequently asked questions and answers
- Any domain-specific information

## How It Works

The chatbot now loads **3 layers of context**:

```
1. PERSONA CONTEXT (personalities.md)
   ↓ (AI personality, tone, communication style)
   
2. RAG KNOWLEDGE (rag_knowledge.md)  ← YOUR DOCUMENT
   ↓ (Detailed information & directions)
   
3. REAL-TIME DATABASE CONTEXT
   ↓ (Current resources from database)
   
COMBINED → Sent to Gemini AI → Response
```

## Updating Your RAG Document

To update the chatbot's knowledge:

1. **Edit the file:**
   ```bash
   # Location: docs/context/DT/rag_knowledge.md
   ```

2. **Add content** in Markdown format:
   ```markdown
   # Library Services
   - Location: Main Campus, Building 5
   - Hours: Mon-Fri 8am-10pm, Sat 10am-8pm
   - Services: Books, computers, study rooms
   
   # Study Rooms
   - 50 rooms available across campus
   - Book 2 hours max per day
   - First-come, first-served after 6pm
   ```

3. **Save and restart the server:**
   ```bash
   cd campus_resource_hub
   python -u serve.py
   ```

The chatbot automatically reloads the file on each request.

## Example RAG Document Structure

```markdown
# Campus Resource Knowledge Base

## General Information
- Campus location and hours
- Contact information
- Important policies

## Resources by Type
- Study spaces (library, pods, rooms)
- Equipment (computers, printers, projectors)
- Services (tutoring, writing center, tech support)
- Food facilities (cafeteria, coffee shops)
- Recreation (gym, sports facilities)

## Important Policies
- Booking cancellation policy
- Resource reservation rules
- Accessibility information
- Technology requirements

## Special Instructions for AI
- How to describe resources
- What information to prioritize
- How to handle edge cases
```

## Integration with Chatbot

The chatbot uses your RAG document by:

1. **Loading on each request** - Fresh data every time
2. **Combining with database** - Real-time availability + static knowledge
3. **Passing to Gemini AI** - AI uses all context to answer questions
4. **Generating responses** - AI crafts helpful, accurate answers

## Example Conversation Flow

**User asks:** "Where can I study?"

**System:**
1. Loads personas.md (tone: friendly, helpful)
2. Loads rag_knowledge.md (study space details)
3. Queries database (available study rooms today)
4. Combines context
5. Sends to Gemini: "You are Alex, the concierge. Here's info about study spaces and what's available..."
6. Returns: "I found several study options for you! The library has open rooms 8am-10pm today..."

## Testing

After updating your RAG document:

1. **Restart the server:**
   ```bash
   python -u serve.py
   ```

2. **Test in browser:**
   ```
   http://127.0.0.1:5000/concierge
   ```

3. **Ask a question** related to your RAG content
4. **Verify** the response includes information from your document

## File Size Recommendations

- **Optimal:** 5-50 KB (1,000-10,000 words)
- **Maximum:** 500 KB (for performance)

Larger documents work but may slow down response times slightly.

## Common Use Cases

### Study Resources
```markdown
# Study Facilities
- Main Library: 200 study seats, open 24/7 during exams
- Study pods: 50 private pods, 2-hour max
- Quiet areas: Designated silent floors
```

### Equipment
```markdown
# Technology Resources
- Lab computers: 100 stations, Win/Mac/Linux
- Printers: $0.10/page, B&W; $0.50 color
- Projectors: Available for booking, AV support included
```

### Services
```markdown
# Student Services
- Tutoring: Free tutoring in math, writing, chemistry
- Accessibility: Accommodations for disabilities
- Tech support: Help with registration, email, accounts
```

## Troubleshooting

**Issue:** Chatbot doesn't mention my RAG content
- **Solution:** Check file path: `docs/context/DT/rag_knowledge.md`
- **Solution:** Restart server: `python -u serve.py`
- **Solution:** Check for Markdown formatting errors

**Issue:** Response seems generic
- **Solution:** Add more specific details to RAG document
- **Solution:** Use clear headers and structure (# for titles)
- **Solution:** Include examples and specific information

**Issue:** Server logs show error loading RAG
- **Solution:** Check file encoding is UTF-8
- **Solution:** Ensure file has .md extension
- **Solution:** Verify no permission issues

## Support

For questions or issues:
1. Check the server logs in the terminal
2. Review the concierge_debug.log file
3. Verify RAG document formatting (Markdown)
4. Check that API key is set in `.env`

---

**Ready to add your RAG content?**
1. Prepare your document content
2. Save to: `docs/context/DT/rag_knowledge.md`
3. Restart server: `python -u serve.py`
4. Test in chatbot: http://127.0.0.1:5000/concierge
