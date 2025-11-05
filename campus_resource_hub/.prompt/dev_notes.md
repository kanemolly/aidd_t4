# Development Notes - Campus Resource Hub

## Project Overview

Campus Resource Hub is an AI-First Flask full-stack application designed for Indiana University.

## Architecture Decisions

### Framework Choice
- **Flask**: Lightweight, flexible, perfect for AI-assisted development with easy customization
- Allows for modular design with blueprints for scaling

### Database Layer
- **SQLAlchemy ORM**: Provides flexibility and type safety
- Supports easy migrations and schema management

### Security
- **Flask-Login**: Industry-standard session management
- **bcrypt**: Secure password hashing
- **Flask-WTF**: CSRF protection for forms

## Development Guidelines

### Code Organization
- Controllers handle HTTP requests and responses
- Models define database schemas
- Views manage template rendering
- Data Access Layer abstracts database operations

### AI-Assisted Development
This project leverages AI assistance for:
- Code generation and scaffolding
- Documentation
- Test writing
- Feature implementation

### Environment Setup
- Use virtual environments for dependency isolation
- Test in development before deploying to production
- Keep sensitive configuration in environment variables

## Future Enhancements

- [ ] OAuth2 integration for IU authentication
- [ ] Real-time notifications
- [ ] Advanced search and filtering
- [ ] Mobile-responsive design
- [ ] Analytics dashboard

## Notes for AI Assistants

When working on this project:
1. Always maintain the modular structure
2. Add comprehensive docstrings
3. Write tests alongside features
4. Update documentation as you add features
5. Follow PEP 8 style guidelines

## Known Limitations

- Currently uses SQLite in development (switch to PostgreSQL for production)
- No database migrations configured yet (consider Alembic)
- Authentication system not yet implemented
