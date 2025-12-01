import json
from google import genai
from google.genai import types
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def parse_user_intent(command: str) -> dict:
    """Uses Gemini to classify the user's command and extract parameters."""
    
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "action": types.Schema(type=types.Type.STRING, enum=["read", "respond", "delete", "unknown"], description="The core email operation."),
            "count": types.Schema(type=types.Type.INTEGER, description="Number of emails to fetch (default 5)."),
            "sender": types.Schema(type=types.Type.STRING, description="Sender's name or email address."),
            "subject_keyword": types.Schema(type=types.Type.STRING, description="A keyword or phrase in the subject line."),
            "email_number": types.Schema(type=types.Type.INTEGER, description="Reference number for a listed email (e.g., 'email number 2' -> 2)."),
            "reply_content": types.Schema(type=types.Type.STRING, description="Content the user wants to reply with.")
        }
    )

    system_prompt = "You are an expert AI Email Assistant. Analyze the user's command and output a single JSON object strictly matching the provided schema. Do not output any text outside the JSON object. Default 'count' to 5 if action is 'read' and no number is specified."

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[system_prompt, command],
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema)
    )
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"action": "unknown", "params": {}}


async def generate_summary(email_body: str) -> str:
    """Generates a concise summary for a single email."""
    prompt = (
        "Condense the following email body into a single, short, and concise summary "
        "of the main topic and required action (if any). Do not exceed two sentences."
        f"\n\nEMAIL CONTENT:\n---\n{email_body}"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text.strip()


async def generate_proposed_reply(original_email_content: str) -> str:
    """Generates a professional, context-aware reply."""
    prompt = (
        "Based on the following email content, generate a professional, clear, "
        "and ready-to-send reply. Assume a standard closing (e.g., 'Best regards, [Your Name]'). "
        "Only output the body of the email."
        f"\n\n--- ORIGINAL EMAIL ---\n{original_email_content}"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text.strip()