# 🧠 Resource Concierge - Quick Start Guide

## What is it?

The Campus Resource Concierge is an AI chatbot that answers student questions about campus resources using Google Gemini API.

**Example questions:**
- "Do you have study rooms with projectors?"
- "What are your facility hours?"
- "I need a quiet place to study"

---

## Setup (3 Easy Steps)

### 1️⃣ Get Gemini API Key

Visit: https://ai.google.dev/tutorials/python_quickstart

- Click "Get API Key"
- Create API key for "Generative Language API"
- Copy the key

### 2️⃣ Configure Environment

Create a `.env` file in your project root:

```bash
FLASK_ENV=development
GEMINI_API_KEY=your-api-key-here-paste-it
```

**Already created:** `.env.example` (copy and fill it in)

### 3️⃣ Install & Run

```bash
# Install packages
pip install google-generativeai python-dotenv

# Run app
python app.py

# Open in browser
http://127.0.0.1:5000/concierge
```

---

## Features

✅ **AI-Powered Responses** - Uses Google Gemini API  
✅ **Real-Time Database Context** - Knows about your resources  
✅ **Chat Bubble Interface** - Crimson & cream colors  
✅ **Mobile Responsive** - Works on all devices  
✅ **WCAG Accessible** - Keyboard navigation, screen readers  
✅ **Quick Suggestions** - Pre-built questions to click  
✅ **Character Limit** - Max 1000 chars per message  

---

## How It Works

```
User asks: "Do you have study rooms with projectors?"
       ↓
Flask receives message at /concierge/chat
       ↓
Loads system context:
  - Student concierge persona
  - List of available resources from database
       ↓
Calls Google Gemini API with:
  - System prompt (behavior guidelines)
  - Current resource data
  - User's question
       ↓
Gemini generates response
       ↓
Response sent back to browser
       ↓
Displayed in chat bubble
```

---

## File Structure

```
campus_resource_hub/
├── src/
│   ├── controllers/
│   │   └── concierge.py          ← Backend routes
│   └── views/templates/
│       └── concierge.html         ← Chat UI
├── docs/
│   ├── context/DT/
│   │   └── personas.md            ← AI context
│   └── AI_FEATURE_2_RESOURCE_CONCIERGE.md
├── .env                           ← Your config (create this)
├── .env.example                   ← Config template
└── requirements.txt               ← Dependencies
```

---

## Important Notes

⚠️ **API Key Sensitive**
- Never commit `.env` to git
- Keep GEMINI_API_KEY private
- Regenerate key if exposed

💡 **No API Key?**
- Concierge still loads
- Shows helpful message
- "I'm currently offline..."

📊 **Data Privacy**
- Questions sent to Google servers
- Review Google's privacy policy
- Database queries are local only

---

## Testing

### Quick Test

1. Go to http://127.0.0.1:5000/concierge
2. Type: "What resources do you have?"
3. Wait for response (~2-5 seconds)
4. Should see friendly, detailed answer

### Check API Connection

```bash
# In your Flask app, check for errors
# Terminal should show API calls if configured correctly
```

### Debug

If not working:

1. **Check .env file exists** with correct key
2. **Check terminal logs** for errors
3. **Open browser console** (F12) for JavaScript errors
4. **Verify network tab** shows POST to /concierge/chat

---

## Navbar Integration

**Desktop:** Click "🧠 Concierge" in top navbar  
**Mobile:** Tap menu icon, then "🧠 Concierge"  
**Direct URL:** http://127.0.0.1:5000/concierge

---

## Examples

### Question 1
**User:** "I need a quiet study space"

**Concierge Response:**
> Hello! I'd be happy to help! Here are quiet study spaces I recommend:
> - South Tower Quiet Study Room (natural lighting)
> - Library East Wing (individual desks)
> - Academic Center Room 205 (large windows)

### Question 2
**User:** "What equipment can I borrow?"

**Concierge Response:**
> Great question! We offer equipment checkout for:
> - Projectors (portable)
> - Recording equipment
> - Technical devices
> - Assistive technology
> 
> Would you like details on any specific equipment?

---

## Troubleshooting

### Problem: "I'm currently offline" message

**Solution:**
1. Check `.env` file has `GEMINI_API_KEY=xxxx`
2. API key must be valid and active
3. Restart Flask app after adding key

### Problem: No response (hangs)

**Solution:**
1. Check internet connection
2. Wait longer (first call can be slow)
3. Check browser console for errors
4. Verify API key is valid

### Problem: Concierge link missing in navbar

**Solution:**
1. Restart Flask app
2. Hard refresh browser (Ctrl+Shift+R)
3. Check that concierge.py is in `/src/controllers/`

---

## Next Steps

📚 **Read Full Documentation:**  
`docs/AI_FEATURE_2_RESOURCE_CONCIERGE.md`

🔧 **Customize Persona:**  
`docs/context/DT/personas.md`

🚀 **Deploy:**
- Set up production environment
- Use environment variables
- Configure HTTPS
- Set up monitoring

---

## Support

**Gemini API Issues?**
Visit: https://ai.google.dev/tutorials/python_quickstart

**Flask Issues?**
Visit: https://flask.palletsprojects.com/

**Project Issues?**
Check documentation or review logs

---

**Happy Chatting! 🚀**

For detailed information, see `docs/AI_FEATURE_2_RESOURCE_CONCIERGE.md`
