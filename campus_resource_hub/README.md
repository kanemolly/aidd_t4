# Campus Resource Hub

An AI-First Flask full-stack application for Indiana University resource management and discovery.

## Project Overview

Campus Resource Hub is designed to help IU students and staff efficiently discover and access campus resources including academic support, wellness services, technology resources, and more.

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
