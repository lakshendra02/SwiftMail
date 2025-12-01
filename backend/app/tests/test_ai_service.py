import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from app.services.ai_service import parse_user_intent

# Use a mock client response to ensure the test doesn't actually call the Gemini API
@pytest.mark.asyncio
@patch('app.services.ai_service.client')
async def test_parse_user_intent_read(mock_client):
    """Tests the AI service's ability to correctly parse a 'read' command."""
    
    # Configure the mock response object to simulate a successful JSON output from the AI
    mock_response = AsyncMock()
    # Mock the structure expected from the Gemini client
    mock_response.text = json.dumps({"action": "read", "params": {"count": 10}})
    
    # Set up the mock client's generate_content method to return the mock response
    mock_client.models.generate_content.return_value = mock_response

    command = "Show me my last 10 emails"
    intent = await parse_user_intent(command)

    assert intent['action'] == 'read'
    assert intent['params']['count'] == 10
    assert 'sender' not in intent['params']

@pytest.mark.asyncio
@patch('app.services.ai_service.client')
async def test_parse_user_intent_delete(mock_client):
    """Tests the AI service's ability to correctly parse a 'delete by sender' command."""
    
    mock_response = AsyncMock()
    mock_response.text = json.dumps({"action": "delete", "params": {"sender": "John Smith"}})
    mock_client.models.generate_content.return_value = mock_response

    command = "Delete the latest email from John Smith"
    intent = await parse_user_intent(command)

    assert intent['action'] == 'delete'
    assert intent['params']['sender'] == 'John Smith'
    assert 'email_number' not in intent['params']

@pytest.mark.asyncio
@patch('app.services.ai_service.client')
async def test_parse_user_intent_unknown(mock_client):
    """Tests the AI service's ability to handle unknown commands."""
    
    mock_response = AsyncMock()
    mock_response.text = json.dumps({"action": "unknown", "params": {}})
    mock_client.models.generate_content.return_value = mock_response

    command = "Can you order me a pizza?"
    intent = await parse_user_intent(command)

    assert intent['action'] == 'unknown'
    assert intent['params'] == {}