from fastapi import APIRouter, Depends, HTTPException, status
from app.services import ai_service, gmail_service, auth_service
from app.dependencies import get_current_user_credentials

router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)

@router.post("/command")
async def handle_chatbot_command(
    command_data: dict, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    """Processes a natural language command from the user."""
    creds, username = creds_tuple
    command = command_data.get("command")
    
    intent = await ai_service.parse_user_intent(command)
    action = intent.get("action")
    params = intent.get("params", {})

    try:
        if action == "read":
            count = params.get("count", 5)
            emails = await gmail_service.fetch_latest_emails(creds, count=count)
            
            summaries = []
            for email in emails:
                summary = await ai_service.generate_summary(email["body"])
                summaries.append({**email, "summary": summary})


            return {
                "response": f"Found the last {len(summaries)} emails, summarized below:",
                "action": "read_success",
                "data": {"emails": summaries}
            }

        elif action in ["respond", "delete"]:
            return {
                "response": f"I detected the intent to **{action}**. Please refine your command or confirm the next step.",
                "action": "needs_refinement",
                "data": {"intent": intent}
            }

        else:
            return {
                "response": "I didn't understand that command. Try 'Read my last 5 emails' or 'Delete the email from John'.", 
                "action": "unknown"
            }

    except Exception as e:
        print(f"Error processing command: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while contacting Gmail or the AI service.")

@router.post("/delete-email")
async def confirm_delete(
    delete_data: dict, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    creds, _ = creds_tuple
    email_id = delete_data.get("email_id")
    
    if not email_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ID is required for deletion.")

    if await gmail_service.delete_email(creds, email_id):
        return {"status": "success", "response": f"🗑️ Email ID `{email_id[:10]}...` deleted successfully!"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete email from Gmail.")

@router.get("/user/profile")
async def get_user_profile(creds_tuple: tuple = Depends(get_current_user_credentials)):
    _, username = creds_tuple
    return {"name": username}