import json
from google import genai
from google.genai import types
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def parse_user_intent(command: str) -> dict:
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "action": types.Schema(type=types.Type.STRING, enum=["read", "respond", "delete", "unknown"]),
            "count": types.Schema(type=types.Type.INTEGER),
            "sender": types.Schema(type=types.Type.STRING),
            "subject_keyword": types.Schema(type=types.Type.STRING),
            "email_number": types.Schema(type=types.Type.INTEGER),
            "reply_content": types.Schema(type=types.Type.STRING)
        },
        required=["action"]
    )

    system_prompt = (
        "You are an expert AI Email Assistant. Your goal is to map complex user requests "
        "into structured JSON commands. Analyze the user command and extract all relevant parameters. "
        "If the user wants to reply with specific content (e.g., 'Reply to John that I'm busy'), "
        "extract the entire reply message into 'reply_content'."
        "If the action is 'read', default 'count' to 5 if no number is specified."
        "Only output a single JSON object strictly matching the provided schema. Do not output any text outside the JSON object."
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[system_prompt, command],
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema)
    )
    
    try:
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"JSON Decode Error on AI response: {response.text}")
        return {"action": "unknown", "params": {}}


async def generate_summary(email_body: str) -> str:
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
