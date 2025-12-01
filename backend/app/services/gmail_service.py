import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

async def fetch_latest_emails(creds: Credentials, count: int = 5):
    """Fetches the N latest emails and their full content."""
    service = build('gmail', 'v1', credentials=creds)
    
    result = service.users().messages().list(userId='me', maxResults=count).execute()
    messages = result.get('messages', [])
    
    emails = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
        
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown Sender')
        email_id = msg['id']
        
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

async def send_reply(creds: Credentials, original_message_id: str, reply_body: str):
    """Sends a reply to a specific email."""
    service = build('gmail', 'v1', credentials=creds)
    
    original_msg = service.users().messages().get(userId='me', id=original_message_id, format='metadata', metadataHeaders=['From', 'Subject']).execute()
    headers = {h['name']: h['value'] for h in original_msg['payload']['headers']}
    
    recipient_email = headers['From']
    subject = f"Re: {headers['Subject']}"
    
    message = MIMEText(reply_body)
    message['to'] = recipient_email
    message['subject'] = subject
    
    msg_raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        service.users().messages().send(
            userId='me', 
            body={'raw': msg_raw, 'threadId': original_msg['threadId']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

async def delete_email(creds: Credentials, email_id: str):
    """Deletes a specific email by ID."""
    service = build('gmail', 'v1', credentials=creds)
    try:
        service.users().messages().delete(userId='me', id=email_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting email: {e}")
        return False