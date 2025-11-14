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
