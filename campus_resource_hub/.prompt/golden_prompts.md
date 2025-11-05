# Golden Prompts - Campus Resource Hub

This document contains high-quality, reusable prompts for AI-assisted development of Campus Resource Hub.

## Architecture & Planning

### Prompt: Design a New Feature
```
For Campus Resource Hub, design a new [FEATURE_NAME] feature that:
1. Follows the existing modular architecture (Controllers/Models/Views/Data Access)
2. Integrates with SQLAlchemy ORM for data persistence
3. Includes proper error handling and validation
4. Requires pytest tests with >80% coverage
5. Maintains security best practices (input validation, CSRF protection)

Context: The application follows Flask best practices with:
- Blueprint-based routing
- Form validation via Flask-WTF
- Database models in src/models
- Business logic in src/controllers
```

## Code Generation

### Prompt: Generate a Database Model
```
Create a SQLAlchemy model for [ENTITY] that:
1. Includes appropriate data types and constraints
2. Has relationships to [RELATED_ENTITIES]
3. Includes timestamps (created_at, updated_at)
4. Follows the naming conventions in src/models/
5. Includes helpful docstrings
6. Is compatible with bcrypt for password fields if needed

Project context: Campus Resource Hub uses SQLAlchemy ORM with Flask.
```

### Prompt: Generate Flask Routes
```
Create Flask routes for [ENTITY] CRUD operations in a new blueprint that:
1. Follows RESTful conventions
2. Includes input validation with Flask-WTF
3. Has proper error handling and HTTP status codes
4. Uses Flask-Login for authentication where needed
5. Returns JSON responses for API routes
6. Includes docstrings explaining each route

Place in src/controllers/ and register in app.py as a blueprint.
```

## Testing

### Prompt: Generate Pytest Tests
```
Write pytest test cases for [FUNCTION/ROUTE] that:
1. Cover happy path and error cases
2. Use fixtures for test data
3. Test database interactions
4. Validate HTTP status codes and response formats
5. Mock external dependencies
6. Achieve >80% code coverage

Use existing test patterns in src/tests/ as reference.
```

## Documentation

### Prompt: Create Architecture Documentation
```
Document the [SUBSYSTEM] architecture for Campus Resource Hub including:
1. Component overview and responsibilities
2. Data flow diagrams (text-based)
3. Integration points with other subsystems
4. Security considerations
5. Performance considerations
6. Example usage code

Save in docs/context/[CATEGORY]/ as markdown.
```

## Best Practices Reminder

When using these prompts:
- Always include project context about the modular architecture
- Reference specific file locations for consistency
- Specify testing requirements upfront
- Include security considerations
- Request comprehensive docstrings
- Ask for error handling details
