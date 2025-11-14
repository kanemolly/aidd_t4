# Campus Resource Hub

A comprehensive web platform for managing campus resources, bookings, and student services at Indiana University.

## 🎯 Project Overview

Campus Resource Hub is a Flask-based web application that streamlines resource management and booking processes for students, staff, and administrators. The platform features an intelligent concierge chatbot, real-time notifications, and role-based access control.

## 🏗️ Project Structure

```
aidd_t4/
├── .prompt/                          # AI-First Development
│   ├── dev_notes.md                 # Log of all AI interactions
│   └── golden_prompts.md            # High-impact prompts and patterns
│
├── campus_resource_hub/             # Main Application
│   ├── src/
│   │   ├── controllers/            # Flask routes and blueprints
│   │   ├── models/                 # ORM classes and schema definitions
│   │   ├── views/                  # HTML/Jinja templates
│   │   ├── data_access/            # Encapsulated CRUD logic
│   │   └── services/               # Business logic layer
│   ├── static/                     # CSS, JavaScript, uploads
│   ├── instance/                   # SQLite database
│   └── scripts/                    # Database initialization
│
├── docs/                            # Documentation
│   ├── context/
│   │   ├── DT/                     # Design Thinking artifacts
│   │   ├── PM/                     # Product Management materials
│   │   └── shared/                 # Common items (personas, glossary)
│   ├── README.md                   # Application documentation
│   └── SECURITY.md                 # Security guidelines
│
└── tests/                          # Test Suite
    └── ai_eval/                    # AI feature validation tests
```

## ✨ Key Features

### 🔐 Role-Based Access Control
- **Students**: Browse resources, make bookings, receive notifications
- **Staff**: All student permissions + create/manage resources
- **Admin**: Full system access, booking approvals, analytics dashboard

### 📅 Smart Booking System
- Real-time availability checking
- Recurring bookings (daily, weekly, monthly)
- Conflict detection and prevention
- Approval workflow with notifications

### 🤖 AI-Powered Concierge
- Natural language resource queries
- Booking assistance
- Campus information retrieval
- Context-aware responses

### 🔔 Multi-Channel Notifications
- In-app notification bell
- Email notifications
- Real-time status updates
- Notification history

### 💬 Messaging System
- User-to-user messaging
- Admin announcements
- Thread-based conversations
- Unread message tracking

### 📊 Admin Dashboard
- Pending booking management
- Bulk approval/rejection
- Analytics and reporting
- User management

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aidd_t4
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r campus_resource_hub/requirements.txt
   ```

4. **Initialize database**
   ```bash
   cd campus_resource_hub
   python scripts/init_db.py
   python seed_database.py  # Optional: Load sample data
   ```

5. **Configure environment**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Set SECRET_KEY, DATABASE_URL, EMAIL_CONFIG, etc.
   ```

6. **Run the application**
   ```bash
   python serve.py
   ```

7. **Access the application**
   - Open browser to `http://localhost:5000`
   - Default admin credentials in seed data

## 🛠️ Technology Stack

### Backend
- **Flask 2.3.3**: Web framework
- **SQLAlchemy 2.0.43**: ORM
- **Flask-Login**: Authentication
- **Flask-WTF**: Form handling
- **python-dateutil**: Date manipulation

### Frontend
- **Jinja2**: Template engine
- **Vanilla JavaScript**: Client-side interactions
- **CSS3**: Styling (IU Crimson theme)
- **Fetch API**: Asynchronous requests

### Database
- **SQLite**: Development database
- Easily upgradable to PostgreSQL/MySQL for production

## 📖 Documentation

- **[Application README](docs/README.md)**: Detailed feature documentation
- **[Security Guidelines](docs/SECURITY.md)**: Security best practices
- **[Dev Notes](.prompt/dev_notes.md)**: AI interaction logs
- **[Golden Prompts](.prompt/golden_prompts.md)**: Effective AI prompts

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# AI evaluation tests only
pytest tests/ai_eval/

# With coverage
pytest --cov=campus_resource_hub
```

### AI Feature Validation
Tests for concierge chatbot in `tests/ai_eval/` validate:
- Response accuracy
- Context understanding
- Edge case handling
- User experience quality

## 🎨 Design System

### IU Crimson Theme
- **Primary**: #990000 (IU Crimson)
- **Secondary**: #EEEDEB (IU Cream)
- **Accent**: #006298 (IU Blue)
- **Neutrals**: Gray scale from #2c3e50 to #ecf0f1

### UI Components
- Card-based layouts
- Gradient headers
- Custom modals with animations
- Responsive table designs
- Icon-enhanced buttons

## 🔄 Development Workflow

### AI-First Approach
This project follows an AI-assisted development workflow:

1. **Document Intent**: Record feature requests in `.prompt/dev_notes.md`
2. **Craft Prompts**: Use patterns from `.prompt/golden_prompts.md`
3. **Implement**: AI-assisted code generation and refinement
4. **Test**: Validate functionality and AI features
5. **Document**: Update dev notes with outcomes

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- Feature branches: `feature/feature-name`

## 📝 Contributing

1. Check existing issues or create new one
2. Create feature branch
3. Follow code style guidelines
4. Write/update tests
5. Update documentation
6. Submit pull request

## 🔒 Security

- Passwords hashed with bcrypt
- CSRF protection enabled
- SQL injection prevention via ORM
- Role-based access control
- Session management
- See [SECURITY.md](docs/SECURITY.md) for details

## 📄 License

This project is developed for educational purposes as part of Indiana University coursework.

## 👥 Team

- **Developer**: Molly Kane
- **Course**: AI-Driven Development
- **Institution**: Indiana University
- **Semester**: Fall 2025

## 🙏 Acknowledgments

- Indiana University for brand guidelines
- Flask community for excellent documentation
- AI tools (GitHub Copilot, ChatGPT) for development assistance

## 📞 Support

For issues or questions:
1. Check documentation in `docs/`
2. Review dev notes in `.prompt/dev_notes.md`
3. Create GitHub issue
4. Contact course instructor

---

**Built with ❤️ and 🤖 at Indiana University**
