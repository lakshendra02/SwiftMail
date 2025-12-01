import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import re

async def fetch_latest_emails(creds: Credentials, count: int = 5):
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

async def fetch_single_email_content(creds: Credentials, email_id: str):
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

async def find_email_id_by_query(creds: Credentials, sender: str = None, subject_keyword: str = None) -> str | None:
    service = build('gmail', 'v1', credentials=creds)
    
    query_parts = []
    if sender:
        query_parts.append(f"from:{sender}")
    if subject_keyword:
        query_parts.append(f"subject:{subject_keyword}")
        
    full_query = " ".join(query_parts)
    if not full_query:
        return None

    try:
        result = service.users().messages().list(
            userId='me', 
            maxResults=1, 
            q=full_query
        ).execute()
        
        messages = result.get('messages', [])
        
        if messages:
            return messages[0]['id']
        return None

    except Exception:
        return None

async def send_reply(creds: Credentials, original_message_id: str, reply_body: str):
    service = build('gmail', 'v1', credentials=creds)
    
    original_msg = service.users().messages().get(
        userId='me', 
        id=original_message_id, 
        format='metadata', 
        metadataHeaders=['From', 'Subject']
    ).execute()

    headers = {h['name']: h['value'] for h in original_msg['payload']['headers']}
    
    recipient_header = headers.get('From')
    if not recipient_header: 
        return False

    match = re.search(r'<(.*?)>', recipient_header)
    recipient_email = match.group(1) if match else recipient_header

    subject = f"Re: {headers.get('Subject', 'No Subject')}"
    
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
    except Exception:
        return False

async def delete_email(creds: Credentials, email_id: str):
    service = build('gmail', 'v1', credentials=creds)
    try:
        service.users().messages().trash(userId='me', id=email_id).execute()
        return True
    except Exception as e:
        print(f"Gmail Delete/Trash API Error: {e}")
        raise e
