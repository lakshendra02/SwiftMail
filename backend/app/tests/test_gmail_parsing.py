import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from google.oauth2.credentials import Credentials
from app.services.gmail_service import fetch_latest_emails
import base64
import asyncio

# --- MOCK DATA SETUP ---

# Raw, base64-encoded body content
MOCK_EMAIL_BODY_CONTENT = "This is the body of the test email, detailing the payment due."
MOCK_BODY_BASE64 = base64.urlsafe_b64encode(MOCK_EMAIL_BODY_CONTENT.encode('utf-8')).decode()

# Mock response structure from Gmail API (users().messages().get())
MOCK_RAW_GMAIL_RESPONSE = {
    'id': 'mock_msg_id_123',
    'threadId': 'mock_thread_id_456',
    'snippet': 'This is a short snippet...',
    'payload': {
        'headers': [
            {'name': 'From', 'value': 'John Doe <john.doe@example.com>'},
            {'name': 'Subject', 'value': 'Invoice 789 Due'},
            {'name': 'Date', 'value': 'Fri, 29 Nov 2025 10:00:00 -0500'},
        ],
        'mimeType': 'multipart/alternative',
        'parts': [
            { # HTML Part (will be ignored by our simple parser)
                'mimeType': 'text/html',
                'body': {'size': 1000}
            },
            { # Plain Text Part (what our parser targets)
                'mimeType': 'text/plain',
                'body': {
                    'data': MOCK_BODY_BASE64,
                    'size': len(MOCK_EMAIL_BODY_CONTENT)
                }
            }
        ]
    }
}

# --- TEST FIXTURES AND MOCKS ---

@pytest.fixture
def mock_credentials():
    """Provides a dummy Credentials object for the service functions."""
    return MagicMock(spec=Credentials)

# Mock the entire googleapiclient.discovery.build call
@patch('app.services.gmail_service.build')
@pytest.mark.asyncio
async def test_fetch_latest_emails_parsing(mock_build, mock_credentials):
    """
    Tests that fetch_latest_emails correctly:
    1. Calls the list and get methods.
    2. Decodes base64 content.
    3. Extracts Sender, Subject, and Body correctly.
    """
    
    # 1. Configure the Mocks for the Gmail Service object
    
    # Mock the 'list' call to return one message ID
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        'messages': [{'id': 'mock_msg_id_123'}]
    }
    
    # Mock the 'get' call to return the raw message data
    mock_get = MagicMock()
    mock_get.execute.return_value = MOCK_RAW_GMAIL_RESPONSE
    
    # Chain the calls to simulate the API workflow
    mock_service = MagicMock()
    mock_service.users.return_value.messages.return_value.list.return_value = mock_list
    mock_service.users.return_value.messages.return_value.get.return_value = mock_get
    
    # Ensure the main `build` function returns our mocked service
    mock_build.return_value = mock_service

    # 2. Call the function under test
    emails = await fetch_latest_emails(mock_credentials, count=1)
    
    # 3. Assertions
    
    # Check that the API methods were called as expected
    mock_service.users().messages().list.assert_called_once()
    mock_service.users().messages().get.assert_called_once_with(
        userId='me', id='mock_msg_id_123'
    )

    # Check that the resulting list is not empty
    assert len(emails) == 1
    email = emails[0]

    # Check for correct data extraction and decoding (Part 3.1 requirement)
    assert email['id'] == 'mock_msg_id_123'
    assert email['subject'] == 'Invoice 789 Due'
    assert email['sender'] == 'John Doe <john.doe@example.com>'
    assert email['snippet'] == 'This is a short snippet...'
    assert email['body'] == MOCK_EMAIL_BODY_CONTENT # Crucial: Check if decoding worked