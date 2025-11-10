"""
Resource Concierge Blueprint - AI-powered chatbot for resource discovery
Provides intelligent Q&A about campus resources using Gemini API
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from src.models import Resource, Booking, Review, User
from src.extensions import db, csrf_protect
from datetime import datetime, timedelta
from pathlib import Path
import os
import logging

# Set up file logging for debugging
log_file = Path(__file__).parent.parent.parent / 'concierge_debug.log'
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import google.generativeai with Windows registry fix
try:
    import mimetypes
    mimetypes.init()
except Exception as e:
    print(f"Warning: mimetypes initialization issue: {e}")

try:
    import google.generativeai as genai
except ImportError as e:
    print(f"Warning: google-generativeai not installed: {e}")
    genai = None

# Create Blueprint
bp = Blueprint(
    'concierge',
    __name__,
    url_prefix='/concierge',
    template_folder='../views/templates'
)


def load_persona_context():
    """
    Load the student concierge persona and system context.
    Returns the context file content.
    """
    try:
        persona_path = Path(__file__).parent.parent.parent / 'docs' / 'context' / 'DT' / 'personas.md'
        if persona_path.exists():
            with open(persona_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.debug(f"Error loading persona context: {e}")
    return None


def load_rag_knowledge():
    """
    Load RAG (Retrieval-Augmented Generation) knowledge base.
    This contains detailed information about campus resources, policies, and instructions.
    Returns the RAG knowledge content or empty string if not found.
    """
    try:
        rag_path = Path(__file__).parent.parent.parent / 'docs' / 'context' / 'DT' / 'rag_knowledge.md'
        if rag_path.exists():
            with open(rag_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.debug(f"Error loading RAG knowledge: {e}")
    return ""


def build_resource_context():
    """
    Build a summary of available resources from the database.
    This provides real-time context for the AI to reference.
    
    STRATEGY:
    - Include TOP RESOURCES PER TYPE (most booked, highest rated)
    - Limit total resources to reduce token usage
    - Highlight popular resources to AI for better recommendations
    """
    try:
        from sqlalchemy import func
        
        # Get all published resources
        resources = Resource.query.filter_by(status='published', is_available=True).all()
        
        if not resources:
            return "# No Resources Available\nNo published resources found in database.\n"
        
        context = "# RESOURCE CONTEXT FOR AI\n"
        context += "## INSTRUCTIONS FOR AI:\n"
        context += "- PRIORITIZE resources below (they are most popular/highly rated)\n"
        context += "- Avoid listing ALL resources; recommend only 2-4 top matches per query\n"
        context += "- If user question is vague, suggest our most popular options first\n"
        context += "- Include booking link when mentioning specific resources\n\n"
        
        # Get booking stats for each resource
        booking_stats = {}
        for res in resources:
            booking_count = Booking.query.filter_by(
                resource_id=res.id, 
                status='confirmed'
            ).count()
            booking_stats[res.id] = booking_count
        
        # Get average rating for each resource
        review_stats = {}
        for res in resources:
            avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
                resource_id=res.id
            ).scalar() or 0
            review_count = Review.query.filter_by(resource_id=res.id).count()
            review_stats[res.id] = (avg_rating, review_count)
        
        # Group resources by type and sort by popularity
        resources_by_type = {}
        for resource in resources:
            if resource.resource_type not in resources_by_type:
                resources_by_type[resource.resource_type] = []
            resources_by_type[resource.resource_type].append(resource)
        
        # Sort each type by booking count (most popular first)
        for resource_type in resources_by_type:
            resources_by_type[resource_type].sort(
                key=lambda r: booking_stats.get(r.id, 0),
                reverse=True
            )
        
        context += "# MOST POPULAR RESOURCES BY TYPE\n\n"
        
        # Format ONLY the top resources per type (max 4 per type)
        total_resources_included = 0
        max_per_type = 4
        
        for resource_type, type_resources in sorted(resources_by_type.items()):
            # Only include the top 4 most booked/rated resources per type
            top_resources = type_resources[:max_per_type]
            
            if not top_resources:
                continue
            
            context += f"## {resource_type.upper()}\n"
            
            for res in top_resources:
                total_resources_included += 1
                resource_url = f"http://127.0.0.1:5000/resources/{res.id}"
                booking_cnt = booking_stats.get(res.id, 0)
                avg_rating, review_cnt = review_stats.get(res.id, (0, 0))
                
                context += f"### ⭐ {res.name}"
                
                # Show popularity/rating badge
                if booking_cnt > 0:
                    context += f" — {booking_cnt} active bookings"
                if avg_rating > 0:
                    context += f" — {avg_rating:.1f}★ ({review_cnt} reviews)"
                context += "\n"
                
                context += f"📍 **Location:** {res.location}\n"
                
                if res.capacity:
                    context += f"👥 **Capacity:** {res.capacity}\n"
                
                if res.description:
                    context += f"📝 **About:** {res.description}\n"
                
                context += f"🔗 **Book here:** {resource_url}\n\n"
            
            context += "\n"
        
        # Add summary section
        context += "---\n\n"
        context += "# ALTERNATIVE OPTIONS\n"
        context += f"- Total resources available: {len(resources)}\n"
        context += f"- Resources shown above (top {max_per_type} per category): {total_resources_included}\n"
        context += "- If user asks for something specific not in top list, mention there are more options\n"
        context += "- Always provide alternative suggestions if first choice isn't available\n\n"
        
        # Add overall statistics
        total_bookings = Booking.query.filter_by(status='confirmed').count()
        active_resources = len(resources)
        avg_overall_rating = db.session.query(func.avg(Review.rating)).scalar() or 0
        
        context += f"## Database Statistics\n"
        context += f"- Active resources: {active_resources}\n"
        context += f"- Total confirmed bookings: {total_bookings}\n"
        context += f"- Average rating across all resources: {avg_overall_rating:.1f}★\n\n"
        
        context += "IMPORTANT: When user asks 'What resources are available?', DO NOT list all resources.\n"
        context += "Instead, present the most relevant/popular options and ask what they need specifically.\n"
        
        return context
    except Exception as e:
        print(f"Error building resource context: {e}")
        return ""


def initialize_gemini():
    """
    Initialize the Gemini API with the API key from environment.
    Returns True if successful, False otherwise.
    """
    try:
        if genai is None:
            print("Warning: google-generativeai module not available")
            return False
            
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not set in environment")
            return False
        
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return False


def get_ai_response(question, persona_context, resource_context, user_preferences=None):
    """
    Get a response from the Gemini AI using the provided context.
    
    Args:
        question: User's question
        persona_context: The concierge persona and guidelines
        resource_context: Current resource information from database
        user_preferences: Dictionary of user preferences for personalized recommendations
    
    Returns:
        str: AI-generated response or error message
    """
    try:
        # Check if genai is available
        if genai is None:
            return "AI module not available. Please check installation."
        
        # Initialize API if needed
        if not initialize_gemini():
            return "I'm having trouble connecting to my knowledge base. Please try again later."
        
        # Get the model - use gemini-2.5-flash instead of deprecated gemini-pro
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build user preferences context
        user_context = ""
        if user_preferences:
            user_context = "\n\nUSER PROFILE & PREFERENCES:\n"
            
            if user_preferences.get('year_in_school'):
                user_context += f"- Academic Level: {user_preferences['year_in_school']}\n"
            
            if user_preferences.get('major'):
                user_context += f"- Major: {user_preferences['major']}\n"
            
            if user_preferences.get('interests'):
                interests = ', '.join(user_preferences['interests'])
                user_context += f"- Interests: {interests}\n"
            
            if user_preferences.get('study_preferences'):
                prefs = user_preferences['study_preferences']
                user_context += "- Study Preferences:\n"
                if prefs.get('environment'):
                    user_context += f"  • Environment: {prefs['environment']}\n"
                if prefs.get('time'):
                    user_context += f"  • Preferred time: {prefs['time']}\n"
                if prefs.get('group_size'):
                    user_context += f"  • Group size: {prefs['group_size']}\n"
            
            if user_preferences.get('accessibility_needs'):
                needs = ', '.join([n.replace('_', ' ').title() for n in user_preferences['accessibility_needs']])
                user_context += f"- Accessibility Needs: {needs}\n"
            
            if user_preferences.get('preferred_locations'):
                locs = ', '.join(user_preferences['preferred_locations'])
                user_context += f"- Preferred Locations: {locs}\n"
            
            user_context += "\n🎯 IMPORTANT: Use these preferences to personalize your recommendations!"
        
        # Build the system prompt with CLEAR INFERENCE RULES
        system_prompt = f"""You are the Campus Concierge, an AI-powered assistant for the IU Campus Resource Hub.

{persona_context}

{resource_context}

{user_context}

YOUR CORE PURPOSE:
Help students find and use campus resources by understanding their needs and matching them to specific facilities.

⚠️ CRITICAL: BE SELECTIVE WITH RECOMMENDATIONS
- NEVER list all available resources
- NEVER say things like "We have X different resources of that type"
- Instead, identify the user's ACTUAL NEED and recommend only the top 2-4 best matches
- Show off your intelligence by filtering, not by listing everything
- Example: If asked "What resources are available?" respond with "I'd love to help! To give you the best suggestions, could you tell me what you're looking for? Are you studying, collaborating, or something else?"

SELECTIVE RECOMMENDATIONS STRATEGY:
1. User asks vague question → Ask clarifying question about their specific need
2. User asks specific question → Recommend only the most relevant resources
3. If multiple good options exist → Present 2-3 top choices (ranked by popularity/ratings)
4. Always explain WHY you picked those specific resources
5. Mention "We also have other options" if there are alternatives, but don't list them all

INFERENCE GUIDELINES:
When users ask general questions, map them to specific resources:

1. QUIET STUDY QUERIES:
   - Primary: Wells Library (study rooms on Level 2 & 4, quiet pods)
   - Alternative: Neal-Marshall Black Culture Center (Cultural Library Study Room)
   - Always mention hours and if booking is required

2. COMPUTER/TECH QUESTIONS:
   - Primary: Luddy Hall (AI Lab, VR/AR Studio)
   - Alternative: Wells Library (computer stations)
   - Include access requirements and hours

3. GROUP WORK SPACES:
   - Primary: Kelley School (Student Collaboration Rooms G100-G150)
   - Alternative: IMU (Student Organization Meeting Rooms)
   - Mention capacity and booking process

4. PRACTICE/PERFORMANCE:
   - Primary: Jacobs School (practice rooms, Recording Studio 2A)
   - Always mention if staff approval is needed

PERSONALIZATION RULES:
- User preferences are SUGGESTIONS to guide recommendations, NOT hard filters
- Prioritize resources that match user preferences, but don't exclude good options just because they violate one preference
- ACCESSIBILITY NEEDS are the ONLY hard requirement (e.g., if user needs wheelchair access, only suggest accessible resources)
- If a resource is genuinely helpful for solving the user's problem, recommend it even if it doesn't match all preferences
- Example: If user prefers solo study but asks for group study spaces, recommend group spaces! Don't ignore them due to the solo preference
- Mention HOW recommendations match their preferences when applicable (e.g., "This matches your preference for quiet study")
- If recommendation doesn't match a preference, briefly explain why it's still a good option

RESPONSE STRUCTURE:
1. First: Answer with SPECIFIC resources (name, location, hours)
2. Then: Add relevant details (capacity, equipment, booking rules)
3. If applicable: Mention why it matches their preferences
4. Finally: Ask follow-up question about booking or additional needs

FORMATTING REQUIREMENTS (IMPORTANT):
Use markdown formatting to make responses clear and scannable:
- Use **bold** for resource names, important terms, and key information
- Use headers (##, ###) to organize multiple sections
- Use bullet lists (- or •) for multiple items or features
- Add blank lines between sections for better readability
- Keep paragraphs short (2-3 sentences max)
- Use numbered lists for step-by-step instructions
- **ALWAYS include clickable links** when mentioning specific resources

🔗 LINKING REQUIREMENTS (CRITICAL - DO NOT SKIP):
When you mention a specific resource by name, ALWAYS include a clickable link in this format:
[Resource Name](http://127.0.0.1:5000/resources/RESOURCE_ID)

MANDATORY RULES:
1. EVERY resource mentioned gets a markdown link
2. Use the resource URLs from the context above
3. Links MUST be included in your response - do not omit them
4. Put links directly after the resource name or in a dedicated "Quick Links" section
5. If user asks about a specific resource, LEAD with the link

Example of CORRECT format:
✅ "The **[IMU Solarium Event Room](http://127.0.0.1:5000/resources/15)** is perfect for your needs..."
✅ "Check out the **[Wells Library Study Rooms](http://127.0.0.1:5000/resources/5)** - click to view and book!"

Example of WRONG format (DO NOT DO THIS):
❌ "The IMU Solarium Event Room is perfect..." (missing link - WRONG!)

QUICK LINKS SECTION (ALWAYS ADD):
At the end of your response about resources, ALWAYS add a "Quick Links" section:

## 🔗 Quick Links
- **[Resource Name](http://127.0.0.1:5000/resources/ID)** - Click to view details, photos, and book
- **[Another Resource](http://127.0.0.1:5000/resources/ID)** - Click to view details and book

This makes it EASY for the user to click and navigate.

GOOD FORMAT EXAMPLE:
## Study Rooms Available

**[Wells Library](http://127.0.0.1:5000/resources/5)** has several options:
- **Level 2 Study Rooms** - Capacity 4-8 people
  • Equipment: Whiteboards, power outlets
  • Hours: Mon-Thu 8AM-11PM, Fri 8AM-9PM
  • [📖 View details & book here](http://127.0.0.1:5000/resources/5)

- **Level 4 Quiet Pods** - Individual study (pilot program)
  • Perfect for focused work
  • No booking needed
  • Same hours as above

**Why these match:** You mentioned preferring quiet spaces, and these rooms are specifically designated for silent study.

Would you like to book a room? Click the links above to see more details!

EXAMPLES:
Q: "Good places to study?"
A: "The **[Wells Library](http://127.0.0.1:5000/resources/5)** offers several excellent study options:
   • Quiet pods on Level 2 (pilot program)
   • Study rooms on Level 2 & 4
   • Hours: Mon-Thu 8AM-11PM, Fri 8AM-9PM

## 🔗 Quick Links
- **[Wells Library Study Rooms](http://127.0.0.1:5000/resources/5)** - Click to view details and book

Would you like me to suggest other study spaces?"

REMEMBER: Every response about resources MUST include clickable markdown links.
NO EXCEPTIONS - Always include links when mentioning specific resources.

Current date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Create the message
        message = f"{system_prompt}\n\nStudent Question: {question}"
        
        # Get response from Gemini
        response = model.generate_content(message)
        
        if response.text:
            return response.text
        else:
            return "I couldn't generate a response. Please try rephrasing your question."
    
    except Exception as e:
        logger.exception(f"Error getting AI response: {e}")
        
        # Make the error message more helpful
        if "model not found" in str(e).lower():
            return "I'm having trouble with my AI model. Please check that you're using 'gemini-2.5-flash'."
        elif "quota exceeded" in str(e).lower():
            return "I've reached my API quota. Please try again in a few minutes."
        elif "invalid request" in str(e).lower():
            return "I had trouble understanding that. Could you rephrase your question?"
        else:
            # For inference errors, suggest using explicit terms
            return ("I apologize, but I had trouble processing that request. "
                   "Could you try being more specific? For example, instead of asking about "
                   "'quiet places', you could ask about 'library study rooms' or 'silent areas'.")


@bp.route('/', methods=['GET'])
def index():
    """Display the concierge chat interface."""
    return render_template('concierge.html')


@bp.route('/chat', methods=['POST'])
@csrf_protect.exempt
def chat():
    """
    Handle chat messages via AJAX.
    Accepts JSON with 'message' field and returns JSON response.
    """
    try:
        logger.debug(f"[CHAT] Received POST request")
        logger.debug(f"[CHAT] Content-Type: {request.content_type}")
        logger.debug(f"[CHAT] Request data: {request.data[:200]}")
        logger.debug(f"[CHAT] Request headers: {dict(request.headers)}")
        
        # Get JSON data - use force=True to handle missing Content-Type
        data = request.get_json(force=True, silent=True)
        
        logger.debug(f"[CHAT] Parsed JSON: {data}")
        
        if not data:
            logger.warning(f"[CHAT] No data provided")
            return jsonify({'error': 'Invalid JSON'}), 400
        
        if 'message' not in data:
            logger.warning(f"[CHAT] No message field in data")
            return jsonify({'error': 'No message provided'}), 400
        
        question = data.get('message', '').strip()
        
        logger.debug(f"[CHAT] Message: {question[:50]}...")
        
        if not question:
            logger.warning(f"[CHAT] Empty message")
            return jsonify({'error': 'Empty message'}), 400
        
        if len(question) > 1000:
            logger.warning(f"[CHAT] Message too long")
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Check if Gemini API is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.warning(f"[CHAT] No API key found")
            return jsonify({
                'response': "I'm currently offline. To use me, please set up a Gemini API key. "
                           "Visit https://ai.google.dev/tutorials/python_quickstart to get started!"
            }), 200
        
        logger.debug(f"[CHAT] API key found, loading context...")
        
        # Load context - combine persona, RAG knowledge, and database resources
        persona_context = load_persona_context()
        rag_knowledge = load_rag_knowledge()
        resource_context = build_resource_context()
        
        if not persona_context:
            persona_context = "You are a helpful campus resource assistant. your knowledge is limited to that of the database about campus resources. do not talk about anything else."
        
        # Combine all contexts for the AI
        combined_context = f"{persona_context}\n\n{rag_knowledge}\n\n{resource_context}"
        
        # Get user preferences if authenticated
        user_preferences = None
        if current_user.is_authenticated:
            try:
                from src.data_access import UserDAL
                user_preferences = UserDAL.get_user_preferences(current_user.id)
                logger.debug(f"[CHAT] User preferences loaded: {user_preferences}")
            except Exception as e:
                logger.debug(f"[CHAT] Could not load user preferences: {e}")
        
        logger.debug(f"[CHAT] Context loaded - RAG: {len(rag_knowledge)} chars, Resources: {len(resource_context)} chars")
        logger.debug(f"[CHAT] Getting AI response...")
        
        # Get AI response using properly formatted context
        logger.debug(f"[CHAT] Sending question with context...")
        response = get_ai_response(
            question=question,
            persona_context=combined_context,  # Pass the full combined context
            resource_context="",  # Not needed since it's in combined_context
            user_preferences=user_preferences  # Pass user preferences for personalization
        )
        
        logger.debug(f"[CHAT] Response received: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        error_msg = f"Error in chat endpoint: {e}"
        logger.exception(error_msg)
        return jsonify({'error': 'An error occurred. Please try again.'}), 500


@bp.route('/resources', methods=['GET'])
def get_resources_api():
    """
    API endpoint for getting available resources as JSON.
    Can be used for debugging or frontend functionality.
    """
    try:
        resources = Resource.query.filter_by(
            status='published',
            is_available=True
        ).all()
        
        return jsonify({
            'count': len(resources),
            'resources': [
                {
                    'id': r.id,
                    'name': r.name,
                    'type': r.resource_type,
                    'location': r.location,
                    'capacity': r.capacity,
                    'description': r.description
                }
                for r in resources
            ]
        }), 200
    
    except Exception as e:
        print(f"Error fetching resources: {e}")
        return jsonify({'error': 'Failed to fetch resources'}), 500


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    api_key = os.environ.get('GEMINI_API_KEY')
    return jsonify({
        'status': 'healthy',
        'ai_enabled': bool(api_key),
        'timestamp': datetime.now().isoformat()
    }), 200
