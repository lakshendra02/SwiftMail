from pydantic import BaseModel, Field
from typing import List, Optional


class CommandRequest(BaseModel):
    """Schema for the user's input command."""
    command: str = Field(..., description="The natural language command from the user.")

class EmailData(BaseModel):
    """Schema for a single email item returned to the frontend."""
    id: str = Field(..., description="Gmail message ID.")
    sender: str
    subject: str
    body: str = Field(..., description="Full email body content.")
    snippet: str
    summary: str = Field(..., description="AI-generated summary (Part 3.1).")
    
class ChatResponse(BaseModel):
    """Schema for the AI Assistant's response to the frontend."""
    response: str = Field(..., description="The natural language message to display to the user.")
    action: str = Field(..., description="The type of action required (e.g., read_success, needs_refinement, unknown).")
    data: Optional[dict] = Field(None, description="Structured data related to the action (e.g., list of emails).")

class ActionConfirmationRequest(BaseModel):
    """Schema for sending replies or confirming deletion."""
    email_id: str = Field(..., description="ID of the email being acted upon.")
    reply_body: Optional[str] = None

class IntentParams(BaseModel):
    count: Optional[int] = None
    sender: Optional[str] = None
    subject_keyword: Optional[str] = None
    email_number: Optional[int] = None
    reply_content: Optional[str] = None

class AIIntent(BaseModel):
    action: str = Field(..., enum=["read", "respond", "delete", "unknown"])
    params: IntentParams