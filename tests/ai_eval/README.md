# AI Feature Validation Tests

This directory contains tests for evaluating AI-powered features, specifically the concierge chatbot.

## Purpose

Validate AI-generated responses for accuracy, relevance, and helpfulness in the campus resource context.

## Test Categories

### 1. Response Accuracy
- Verify factual correctness of chatbot responses
- Test resource information retrieval
- Validate booking procedure guidance

### 2. Context Understanding
- Test conversation continuity
- Verify understanding of user intent
- Assess handling of ambiguous queries

### 3. Edge Cases
- Unavailable resources
- Conflicting booking times
- Out-of-scope questions

### 4. User Experience
- Response clarity and helpfulness
- Appropriate tone and language
- Handling of errors gracefully

## Test Structure

Each test should include:
```python
def test_case_name():
    # Arrange: Setup test data
    # Act: Execute AI feature
    # Assert: Verify expected behavior
    # Cleanup: Reset state if needed
```

## Running Tests

```bash
# Run all AI evaluation tests
pytest tests/ai_eval/

# Run specific test file
pytest tests/ai_eval/test_concierge_responses.py

# Run with verbose output
pytest tests/ai_eval/ -v
```

## Example Test

```python
def test_concierge_basic_greeting():
    """Test that concierge responds appropriately to greetings"""
    response = concierge_service.get_response("Hello")
    assert response is not None
    assert len(response) > 0
    assert "hello" in response.lower() or "hi" in response.lower()
```

## Test Data

- Use anonymized or synthetic user data
- Create diverse resource scenarios
- Include edge cases and error conditions

---

*Note: Add actual test files to evaluate your concierge chatbot functionality*
