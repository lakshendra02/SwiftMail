from fastapi import APIRouter, Depends, HTTPException, status
from app.services import ai_service, gmail_service
from app.dependencies import get_current_user_credentials
from app.models.chat import CommandRequest, ActionConfirmationRequest # Import CommandRequest

router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)

async def find_target_email_id(creds, params):
    """Helper function to find the email ID based on parsed NLP parameters."""
    sender = params.get("sender")
    subject = params.get("subject_keyword")
    
    if sender or subject:
        return await gmail_service.find_email_id_by_query(creds, sender=sender, subject_keyword=subject)
    
    # NOTE: We skip 'email_number' parsing here, as that is only reliable for previously listed emails.
    return None

@router.post("/command")
async def handle_chatbot_command(
    command_data: CommandRequest, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    """Processes a natural language command from the user."""
    creds, username = creds_tuple
    command = command_data.command
    
    # 1. AI Intent Parsing (Now more powerful)
    intent = await ai_service.parse_user_intent(command)
    action = intent.get("action")
    params = intent.get("params", {})
    
    # ----------------------------------------------------
    # PHASE 2: NLP Execution (Direct Actions)
    # ----------------------------------------------------
    
    if action == "delete":
        email_id = await find_target_email_id(creds, params)
        if email_id:
            # Found the target, now immediately ask for confirmation (Part 3.3 requirement)
            return {
                "response": f"I found an email matching your request. Are you sure you want to delete it?",
                "action": "confirm_delete",
                "data": {"email_id": email_id}
            }
        
    elif action == "respond" and params.get("reply_content"):
        email_id = await find_target_email_id(creds, params)
        reply_content = params.get("reply_content")
        
        if email_id:
            # Found the target and the reply content, now present the draft for confirmation
            return {
                "response": f"I drafted the following reply for the email from '{params.get('sender', 'the recipient')}'. Confirm sending?",
                "action": "confirm_send",
                "data": {
                    "original_email_id": email_id,
                    "reply_body": reply_content
                }
            }
    
    # ----------------------------------------------------
    # PHASE 1: Simple/Default Actions (Read, Errors)
    # ----------------------------------------------------
    
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
                "response": f"I detected the intent to **{action}** but couldn't find a target email using the keywords you provided (sender/subject). Please be more specific or click a button next to a listed email.",
                "action": "needs_refinement",
                "data": {"intent": intent}
            }

        else:
            return {
                "response": "I didn't understand that command. Try 'Read my last 5 emails' or 'Reply to John that I'll be late'.", 
                "action": "unknown"
            }

    except Exception as e:
        print(f"Error processing command: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while contacting Gmail or the AI service.")


@router.post("/suggest-reply")
async def suggest_reply(
    request_data: ActionConfirmationRequest, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    """Fetches an email and generates a proposed reply using AI."""
    creds, _ = creds_tuple
    email_id = request_data.email_id
    
    try:
        # 1. Fetch the full email content
        email_data = await gmail_service.fetch_single_email_content(creds, email_id)
        
        if not email_data:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found or access denied.")
             
        # 2. Generate the reply
        proposed_reply = await ai_service.generate_proposed_reply(email_data["body"])
        
        return {
            "response": f"Proposed reply for subject '{email_data['subject']}':",
            "action": "reply_suggested",
            "data": {
                "original_email_id": email_id,
                "proposed_reply": proposed_reply
            }
        }
    except Exception as e:
        print(f"Error suggesting reply: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate AI reply.")


# UPDATED ENDPOINT: Confirm Delete with explicit 403 scope handling
@router.post("/delete-email")
async def confirm_delete(
    delete_data: ActionConfirmationRequest, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    creds, _ = creds_tuple
    email_id = delete_data.email_id
    
    if not email_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ID is required for deletion.")

    try:
        if await gmail_service.delete_email(creds, email_id):
            return {"status": "success", "response": f"🗑️ Email ID `{email_id[:10]}...` deleted successfully!"}
        else:
            # Generic 500 for non-specific API errors
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete email from Gmail (API issue).")
            
    except Exception as e:
        print(f"Error deleting email: {e}")
        # Intercept the specific 403 insufficient scope error
        if "insufficientPermissions" in str(e):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Authentication scope issue: Your Google credentials lack the necessary permissions (modify/delete). Please log out and log back in, ensuring all permissions are granted."
            )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during deletion.")

# Endpoint to get the currently logged-in user profile (for greeting)
@router.get("/user/profile")
async def get_user_profile(creds_tuple: tuple = Depends(get_current_user_credentials)):
    _, username = creds_tuple
    return {"name": username}

# Endpoint for confirming and sending the reply (called from a button in the React UI)
@router.post("/send-reply")
async def send_email_reply(
    reply_data: ActionConfirmationRequest, 
    creds_tuple: tuple = Depends(get_current_user_credentials)
):
    creds, _ = creds_tuple
    email_id = reply_data.email_id
    reply_body = reply_data.reply_body
    
    try:
        if await gmail_service.send_reply(creds, email_id, reply_body):
            return {"response": "✅ Reply sent successfully!", "action": "status"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send reply via Gmail API.")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during email sending.")