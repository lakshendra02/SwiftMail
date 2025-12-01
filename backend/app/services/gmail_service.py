import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

async def fetch_latest_emails(creds: Credentials, count: int = 5):
    """Fetches the N latest emails and their full content."""
    service = build('gmail', 'v1', credentials=creds)
    
    # Get message IDs
    result = service.users().messages().list(userId='me', maxResults=count).execute()
    messages = result.get('messages', [])
    
    emails = []
    for msg in messages:
        # Get full message details
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Simple parsing logic 
        headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
        
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown Sender')
        email_id = msg['id']
        
        # Extract body content (simplistic approach: looks for parts)
        body_data = ""
        if 'parts' in msg_detail['payload']:
            for part in msg_detail['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        
        emails.append({
            "id": email_id,
            "sender": sender,
            "subject": subject,
            "body": body_data,
            "snippet": msg_detail.get('snippet')
        })
        
    return emails

# NEW HELPER FUNCTION for reply generation
async def fetch_single_email_content(creds: Credentials, email_id: str):
    """Fetches the full content of a single email for AI processing."""
    service = build('gmail', 'v1', credentials=creds)
    try:
        msg_detail = service.users().messages().get(userId='me', id=email_id).execute()
    except Exception:
        return None 

    headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
    
    body_data = ""
    if 'parts' in msg_detail['payload']:
        for part in msg_detail['payload']['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    
    return {
        "id": email_id,
        "sender": headers.get('From', 'Unknown Sender'),
        "subject": headers.get('Subject', 'No Subject'),
        "body": body_data,
        "snippet": msg_detail.get('snippet')
    }


async def send_reply(creds: Credentials, original_message_id: str, reply_body: str):
    """Sends a reply to a specific email."""
    service = build('gmail', 'v1', credentials=creds)
    
    # 1. Fetch original message headers to get recipient/subject
    original_msg = service.users().messages().get(userId='me', id=original_message_id, format='metadata', metadataHeaders=['From', 'Subject']).execute()
    headers = {h['name']: h['value'] for h in original_msg['payload']['headers']}
    
    # The 'From' header of the original email is the 'To' recipient of the reply
    recipient_header = headers.get('From')
    if not recipient_header: return False

    # Simple attempt to extract email address from "Name <email@example.com>"
    import re
    match = re.search(r'<(.*?)>', recipient_header)
    recipient_email = match.group(1) if match else recipient_header

    subject = f"Re: {headers.get('Subject', 'No Subject')}"
    
    # 2. Create the message
    message = MIMEText(reply_body)
    message['to'] = recipient_email
    message['subject'] = subject
    
    # 3. Create the thread-aware reply
    msg_raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        service.users().messages().send(
            userId='me', 
            body={'raw': msg_raw, 'threadId': original_msg['threadId']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        # Note: Exception is handled by the calling router.
        return False

async def delete_email(creds: Credentials, email_id: str):
    """Deletes a specific email by ID."""
    service = build('gmail', 'v1', credentials=creds)
    try:
        service.users().messages().trash(userId='me', id=email_id).execute()
        return True
    except Exception as e:
        # Crucial: DO NOT suppress the exception here, let the router handle it for error reporting.
        print(f"Gmail Delete API Error: {e}")
        raise e