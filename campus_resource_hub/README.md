# Campus Resource Hub 🎓

> Indiana University's intelligent resource booking and management platform with AI-powered concierge assistance.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/sqlite-3-orange.svg)](https://www.sqlite.org/)
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG-2.1%20AA-success.svg)](https://www.w3.org/WAI/WCAG21/quickref/)

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd campus_resource_hub

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run the server
python serve.py
```

Visit **http://127.0.0.1:5000** 🎉

📖 **Detailed Guide**: See [START_HERE.md](START_HERE.md)

---

## Project Overview

Campus Resource Hub is an AI-first Flask full-stack application for Indiana University resource management and discovery.

## Project Structure

```
campus_resource_hub/
├── src/                          # Main application code
│   ├── controllers/              # Route handlers and business logic
│   ├── models/                   # Database models
│   ├── views/                    # Template rendering logic
│   ├── data_access/              # Database access layer
│   ├── static/                   # Static files (CSS, JS, images)
│   └── tests/                    # Unit and integration tests
├── .prompt/                      # AI prompt documentation
│   ├── dev_notes.md              # Development notes and decisions
│   └── golden_prompts.md         # High-quality prompts for AI features
├── docs/                         # Project documentation
│   └── context/                  # Context documents
│       ├── APA/                  # Application Architecture
│       ├── DT/                   # Data & Technology
│       ├── PM/                   # Product & Management
│       └── shared/               # Shared documentation
├── app.py                        # Flask application entry point
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Technology Stack

- **Backend Framework**: Flask
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Database ORM**: SQLAlchemy
- **Security**: bcrypt
- **Testing**: pytest
- **WSGI Server**: gunicorn
- **Visualization**: plotly, matplotlib

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd campus_resource_hub
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

The project includes comprehensive test coverage including unit tests, integration tests, security tests, and end-to-end scenarios.

### Quick Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests (DAL/business logic)
python run_unit_tests.py

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test categories
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests only
pytest tests/ -m security      # Security tests only
pytest tests/ -m e2e           # End-to-end tests only
```

### Test Suite Overview

#### 1. Unit Tests (`test_booking_unit.py`)
Tests Data Access Layer (DAL) CRUD operations independently from Flask routes:
- **Booking CRUD**: Create, read, update, delete operations
- **Conflict Detection**: Overlapping booking detection logic
- **Status Transitions**: Valid booking state changes (pending→confirmed→completed)
- **Business Rules**: Time validation, capacity checks

```bash
# Run unit tests only
pytest tests/test_booking_unit.py -v
```

#### 2. Integration Tests (`test_auth_integration.py`)
Tests complete user workflows across multiple components:
- **Registration → Login → Access Protected Route**: Full auth flow
- **Role-Based Access Control**: Admin vs. student permissions
- **Session Management**: Persistence and security
- **Password Management**: Change password, validation

```bash
# Run integration tests
pytest tests/test_auth_integration.py -v
```

#### 3. Security Tests (`test_security.py`)
Verifies security measures and vulnerability protection:
- **SQL Injection Prevention**: Parameterized queries validation
- **XSS Prevention**: Template escaping for user input
- **Input Validation**: Email, password, and form validation
- **Password Security**: Hashing, verification, timing attack resistance
- **Authorization**: Resource access control

```bash
# Run security tests
pytest tests/test_security.py -v
```

#### 4. End-to-End Tests (`test_e2e_booking.py`)
Complete booking workflow simulation:
- **User Registration & Login**
- **Resource Browsing**
- **Booking Creation**
- **Admin Approval**
- **Conflict Scenarios**

```bash
# Run E2E tests
pytest tests/test_e2e_booking.py::TestBookingWorkflowManual -v -s
```

### Test Configuration

Tests use `pytest.ini` for configuration with custom markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.dal` - Data Access Layer tests

### Fixtures and Test Data

All tests use fixtures defined in `tests/conftest.py`:
- In-memory SQLite database (no setup required)
- Sample users (student, admin, staff)
- Sample resources (study rooms, equipment)
- Sample bookings
- Authenticated test clients

### Taking Screenshots for Verification

1. Run tests with verbose output:
```bash
python run_unit_tests.py > test_output.txt
```

2. The output includes:
   - Test names and descriptions
   - Pass/fail status for each test
   - Error messages with line numbers
   - Summary statistics

3. Screenshot the terminal output showing:
   - Test execution progress
   - Number of tests passed/failed
   - Specific test results

### Troubleshooting Tests

**Common Issues:**

1. **Import Errors**: Ensure you're in the project root and venv is activated
```bash
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

2. **Missing Dependencies**: Install test dependencies
```bash
pip install pytest pytest-flask pytest-cov
```

3. **Database Errors**: Tests use in-memory DB, but ensure write permissions in test directory

4. **CSRF Token Errors**: These are expected in integration tests with WTF_CSRF_ENABLED=True

###3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Running Tests

```bash
pytest
```

## Development

### Adding New Features

- **Controllers**: Add route handlers in `src/controllers/`
- **Models**: Define database models in `src/models/`
- **Views**: Create templates in `src/views/`
- **Tests**: Add tests in `src/tests/`

### AI-First Development

This project uses AI-assisted development practices:
- Review `.prompt/dev_notes.md` for development context
- Refer to `.prompt/golden_prompts.md` for effective AI prompts
- Check `docs/context/` folders for comprehensive architecture documentation

## Deployment

To run in production:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

To be determined

## Support

For support, please contact the Campus Resource Hub team.


AI Integration, Ethical Considerations & Technical Overview
AI Integration Overview

The Campus Resource Hub includes an AI Concierge chatbot that assists users by answering questions about Indiana University buildings, resource availability, accessibility accommodations, campus spaces, and general usage guidelines.
The chatbot is powered by the Gemini API with a Retrieval-Augmented Generation (RAG) workflow to ensure factual accuracy and scoped responses.

How the AI Concierge Works

The system uses a custom RAG knowledge base containing verified IU data:

Building hours and locations

Accessibility notes

Quiet study spaces vs. group collaboration spaces

Campus policies related to resource reservations

Instructions for using the Campus Resource Hub itself

When a user asks a question:

The query is embedded and matched against the RAG document.

Relevant sections are retrieved and passed to the Gemini model.

The model is instructed to respond only using provided data, preventing hallucination.

User preferences (e.g., “quiet study areas”) are included to personalize suggestions.

AI Use Cases in This System

Answering campus-related questions grounded in IU data

Helping students choose appropriate study spaces

Providing building hours, directions, and accessibility details

Offering resource usage guidance (how to book, approval steps, etc.)

Summarizing administrative or usage information when requested

The AI does not perform decision-making (e.g., it cannot approve bookings) and does not access personal or sensitive user data.

Ethical and Managerial Considerations
Data Accuracy & Minimizing Harm

AI-generated responses are strictly grounded in the RAG knowledge base to avoid misinformation. The chatbot cannot answer questions outside its verified dataset.
This ensures students receive accurate building hours, correct accessibility info, and safe campus directions.

Transparency

The system clearly communicates that:

The Concierge is AI, not a human.

Responses come from IU-provided or developer-curated sources.

AI outputs should be used as guidance, not official policy.

User Privacy

The AI is not given access to private messages, personal data, or booking history.

Only non-sensitive user preferences (e.g., preferred study environment) are used to personalize responses.

All sensitive keys (Gemini API keys, SECRET_KEY) are stored using environment variables, not committed to source control.

Responsible Development

During development, AI tools were used as assistants (for brainstorming, code scaffolding, and documentation) but every output was manually validated, tested, and aligned with project requirements.
This ensured code quality, security compliance, and correct functionality.

Technical AI Architecture
Core Components

Gemini API client (google-generativeai)

RAG document stored locally and loaded at runtime

Retriever module:

Splits knowledge content

Computes semantic similarity

Returns relevant sections

Prompt template controlling model behavior:

“Use only the provided RAG content.”

“Do not invent IU policies.”

“Provide concise, campus-appropriate responses.”

Implementation Structure
src/
 ├── ai/
 │    ├── concierge.py           # Chatbot logic + Gemini client
 │    ├── rag_loader.py          # Loads and indexes RAG dataset
 │    ├── retriever.py           # Semantic search over campus knowledge
 │    └── prompts.py             # Safety + grounding prompts

Performance & Safety Controls

Token limits applied to prevent overly long outputs

Content filtering enforced in prompts

Guardrails ensure the AI cannot:

Create new campus rules

Generate building hours that don’t exist

Give safety, medical, or emergency advice

Summary

The AI Concierge enhances the Campus Resource Hub by giving students and staff immediate, personalized access to IU-specific information in a grounded, safe, and transparent manner.
All AI interactions are intentionally limited to verified content and designed to respect user privacy, accuracy requirements, and ethical development standards.

Throughout this project, AI tools became an active part of my development workflow—not as replacements for my own design decisions or problem-solving, but as collaborative partners that accelerated my thinking and helped me explore solutions more efficiently. Using AI this way changed how I approached architecture, feature planning, and documentation, and it ultimately reshaped my expectations for what a single developer can accomplish in a short time.

One of the biggest lessons I learned was how much value comes from giving AI clear, detailed context. Vague prompts produced vague solutions, but when I supplied structure—like my ERD, role definitions, and UI constraints—the AI responded with far more accurate, useful suggestions. This taught me that prompting is a critical skill, almost like writing requirements for another engineer on the team. AI thrives on direction.

I also learned very quickly that AI-generated output absolutely must be verified. While it often produced clean code and convincing explanations, it sometimes introduced errors, skipped edge cases, or used patterns that weren’t idiomatic for Flask. To address this, I adopted a process of using AI for scaffolding and idea generation, then manually reviewing, rewriting, and testing every piece. That verification step was where I built real understanding—ensuring booking logic worked, role permissions were correct, and the RAG-based chatbot was fully grounded in IU data. In a way, AI pushed me to be more intentional about testing and validation than I might have been otherwise.

Ethically, the project made me more aware of the responsibilities that come with integrating AI into real systems. I had to think carefully about transparency, avoiding hallucination, and protecting user privacy. For the AI Concierge, I realized it was essential to constrain outputs to verified data and to be explicit about what the system does and doesn’t know. This shaped not just the technical design but the tone and instructions used in the chatbot itself. The experience reminded me that AI is not just a tool—it introduces managerial and ethical considerations that affect users directly.

Overall, collaborating with AI tools taught me that the role of a developer or technologist is shifting. The value is no longer in writing every line of code manually, but in shaping direction, validating correctness, and understanding the system deeply enough to judge when the AI is right—and when it isn’t. I left this project with a stronger sense of how to guide AI effectively, how to challenge its assumptions, and how to integrate it responsibly into a product. Those lessons will carry forward into my future work, regardless of the tools or technologies I use.